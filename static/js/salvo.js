/* A working salvo, in the page.

   This is not a recording and not a mock: it parses the arguments you type,
   plans the jobs, resolves each one against the estate in data/demos.py, and
   renders the matrix with the same rules the tool uses. The constants below
   are transcribed from salvo.py — the verdict buckets, the NT status map, the
   severity order, what `Pwn3d!` proves per protocol — because every one of
   them is a decision the real tool makes and getting any of them wrong would
   make this a lie rather than a demo.

   Progressive enhancement, same rule as main.js: the section already contains
   a real recorded run. The prompt is only revealed once the engine is behind
   it, and any failure here leaves that transcript on screen. */
(function () {
  "use strict";

  var raw = document.getElementById("salvo-data");
  var host = document.querySelector("[data-shell]");
  if (!raw || !host) return;

  var DATA = JSON.parse(raw.textContent);
  var ESTATE = DATA.estate;
  var NXC = DATA.nxc;
  var PS1 = DATA.ps1;
  /* The command the terminal opens on. It is the same one already rendered
     above as a transcript, so the live replay and the no-script fallback
     never disagree. */
  var OPENING = DATA.opening;

  /* ── Verdict buckets ──────────────────────────────────────────────
     salvo.py's status constants and their glyphs. Three buckets that
     matter: the credential worked, the credential is correct and this
     path is shut, and we genuinely cannot tell. */

  var ADMIN = "ADMIN", EXEC = "EXEC", VALID = "VALID", BLOCKED = "BLOCKED",
      UNKNOWN = "UNKNOWN", INVALID = "INVALID", LOCKED = "LOCKED",
      NOSVC = "NOSVC", ERROR = "ERROR", USAGE = "USAGE", NOTRUN = "NOTRUN";

  var GLYPH = {};
  GLYPH[ADMIN] = "ADMIN"; GLYPH[EXEC] = "exec"; GLYPH[VALID] = "ok";
  GLYPH[BLOCKED] = "VALID*"; GLYPH[UNKNOWN] = "?"; GLYPH[INVALID] = ".";
  GLYPH[LOCKED] = "LOCK!"; GLYPH[NOSVC] = "-"; GLYPH[ERROR] = "err";
  GLYPH[USAGE] = "!CMD"; GLYPH[NOTRUN] = "n/a";

  var SEVERITY = {};
  SEVERITY[ADMIN] = 100; SEVERITY[EXEC] = 95; SEVERITY[VALID] = 90;
  SEVERITY[BLOCKED] = 80; SEVERITY[LOCKED] = 75; SEVERITY[UNKNOWN] = 50;
  SEVERITY[USAGE] = 30; SEVERITY[ERROR] = 20; SEVERITY[INVALID] = 10;
  SEVERITY[NOSVC] = 0; SEVERITY[NOTRUN] = -1;

  var PROTO_RANK = {winrm: 0, smb: 1, mssql: 2, ssh: 3, rdp: 4, wmi: 5, ftp: 6, ldap: 7};

  /* Ordered, first match wins — exactly as in salvo.py. The top group ends
     a run; the middle group all mean the password is RIGHT. */
  var STATUS_MAP = [
    ["STATUS_ACCOUNT_LOCKED_OUT", LOCKED, "account is LOCKED OUT - stop spraying now"],
    ["KDC_ERR_CLIENT_REVOKED", LOCKED, "kerberos: account locked or disabled"],
    ["STATUS_LOGON_TYPE_NOT_GRANTED", BLOCKED, "password correct, account denied this logon type"],
    ["STATUS_ACCOUNT_DISABLED", BLOCKED, "password correct, account disabled"],
    ["STATUS_ACCOUNT_EXPIRED", BLOCKED, "password correct, account expired"],
    ["STATUS_PASSWORD_EXPIRED", BLOCKED, "password correct but expired - can often still be changed"],
    ["STATUS_PASSWORD_MUST_CHANGE", BLOCKED, "password correct, must be changed at next logon"],
    ["STATUS_ACCOUNT_RESTRICTION", BLOCKED, "password correct, workstation/time restriction"],
    ["STATUS_INVALID_LOGON_HOURS", BLOCKED, "password correct, outside permitted logon hours"],
    ["STATUS_INVALID_WORKSTATION", BLOCKED, "password correct, not allowed from this host"],
    ["STATUS_NOT_SUPPORTED", BLOCKED, "auth mechanism refused, not a credential failure"],
    ["STATUS_ACCESS_DENIED", UNKNOWN, "authenticated then authorization denied - cred may be live"],
    ["STATUS_TRUSTED_RELATIONSHIP", UNKNOWN, "machine trust issue, not a credential verdict"],
    ["STATUS_NO_LOGON_SERVERS", UNKNOWN, "no DC reachable - retest, not a credential verdict"],
    ["STATUS_NETWORK_SESSION_EXPIRED", UNKNOWN, "session expired mid-auth - retest"],
    ["STATUS_IO_TIMEOUT", NOSVC, "timed out"],
    ["STATUS_CONNECTION_RESET", NOSVC, "connection reset"],
    ["STATUS_LOGON_FAILURE", INVALID, "wrong username or password"],
    ["KDC_ERR_PREAUTH_FAILED", INVALID, "kerberos pre-auth failed - wrong password"],
    ["KDC_ERR_C_PRINCIPAL_UNKNOWN", INVALID, "no such principal in this domain"],
    ["STATUS_NO_SUCH_USER", INVALID, "no such user"]
  ];

  /* Where a bare [-] with no status code is genuinely ambiguous. */
  var AMBIGUOUS = ["winrm", "rdp", "wmi", "ldap", "mssql"];

  var LEGEND = [
    "  ADMIN  = provably administrative (smb admin-share write, mssql sysadmin)",
    "  exec   = code execution, NOT admin - check the smb column before assuming",
    "  ok     = authenticated    VALID* = password correct, this access path blocked",
    "  ?      = cannot tell, retest elsewhere    . = refused    - = no service / no answer",
    "  !CMD   = nxc REJECTED the command salvo built - this cell was never tested",
    "  n/a    = salvo ran NO job here - a fact about salvo, not about the host",
    "  err    = salvo could not run this job - also not a verdict",
    "  <      = this host answered on at least one protocol"
  ];

  var NO_ADMIN_NOTE = "   # NOT local admin here - expect to land as a standard user";

  function has(list, x) { return list.indexOf(x) >= 0; }
  function pad(s, n) { s = String(s); while (s.length < n) s += " "; return s; }
  function lpad(s, n) { s = String(s); while (s.length < n) s = " " + s; return s; }

  /* shlex.quote's own safe set, so a pasted command is a correct command. */
  var SAFE = /^[A-Za-z0-9_@%+=:,.\/-]+$/;
  function q(s) {
    if (s === "" || s == null) return "''";
    if (SAFE.test(s)) return s;
    return "'" + String(s).replace(/'/g, "'\"'\"'") + "'";
  }

  function ipKey(ip) {
    var p = ip.split(".");
    if (p.length !== 4) return [1, ip];
    return [0, (+p[0] << 24 >>> 0) + (+p[1] << 16) + (+p[2] << 8) + (+p[3])];
  }
  function byIp(a, b) {
    var x = ipKey(a), y = ipKey(b);
    if (x[0] !== y[0]) return x[0] - y[0];
    return x[1] > y[1] ? 1 : (x[1] < y[1] ? -1 : 0);
  }

  /* ── Targets ──────────────────────────────────────────────────────
     What nxc accepts and salvo therefore has to count: a literal
     address, its octet-range form, and CIDR. The count is not cosmetic
     — it is the multiplier in the lockout arithmetic. */

  var RANGE_RE = /^(\d{1,3}(?:\.\d{1,3}){2})\.(\d{1,3})-(\d{1,3})$/;
  var CIDR_RE = /^(\d{1,3}(?:\.\d{1,3}){3})\/(\d{1,2})$/;
  var IP_RE = /^\d{1,3}(?:\.\d{1,3}){3}$/;

  function expand(targets) {
    var out = [], seen = {};
    targets.forEach(function (t) {
      var m;
      if ((m = CIDR_RE.exec(t))) {
        var bits = +m[2];
        if (bits < 16) return;                       // absurd for a lab
        var o = m[1].split(".").map(Number);
        var base = (o[0] << 24 >>> 0) + (o[1] << 16) + (o[2] << 8) + o[3];
        var size = Math.pow(2, 32 - bits);
        base = base - (base % size);
        for (var i = 0; i < size; i++) {
          var v = base + i;
          out.push([(v >>> 24) & 255, (v >>> 16) & 255, (v >>> 8) & 255, v & 255].join("."));
        }
      } else if ((m = RANGE_RE.exec(t))) {
        for (var k = +m[2]; k <= +m[3]; k++) out.push(m[1] + "." + k);
      } else {
        out.push(t);
      }
    });
    return out.filter(function (ip) {
      if (seen[ip]) return false;
      seen[ip] = 1;
      return true;
    });
  }

  function hostMap() {
    var m = {};
    ESTATE.hosts.forEach(function (h) { m[h[0]] = {name: h[1], os: h[2], svcs: h[3]}; });
    return m;
  }

  /* ── One job's answer ─────────────────────────────────────────────
     The estate decides the raw outcome; classify() turns it into a
     verdict the same way salvo turns an nxc line into one. */

  function outcomeFor(user, secret, ip, proto) {
    var hosts = hostMap();
    var h = hosts[ip];
    if (!h) return null;                       // not in the estate at all
    if (!has(h.svcs, proto)) return null;      // nothing listening
    var c = ESTATE.creds[user];
    if (!c || c.secret !== secret) return "bad";
    if (c.lockout) return "STATUS_ACCOUNT_LOCKED_OUT";
    return (c.on[ip] || {})[proto] || "bad";
  }

  function classify(proto, outcome) {
    if (outcome === "ok") return [VALID, "authenticated"];
    if (outcome === "pwn") {
      var m = NXC.pwn_means[proto] || [EXEC, "elevated access reported by nxc"];
      return [m[0], m[1]];
    }
    if (outcome === "bad" || outcome === "refused") {
      /* nxc's winrm never prints a status, so a wrong password and a valid
         account outside Remote Management Users arrive identically. */
      if (outcome === "bad" && proto !== "winrm") {
        return [INVALID, "wrong username or password"];
      }
      if (has(AMBIGUOUS, proto)) {
        return [UNKNOWN, "refused with no status code - on " + proto +
          " this cannot be told apart from an authorization denial. " +
          "Do not write the cred off."];
      }
      return [INVALID, "authentication refused"];
    }
    for (var i = 0; i < STATUS_MAP.length; i++) {
      if (outcome.indexOf(STATUS_MAP[i][0]) >= 0) {
        return [STATUS_MAP[i][1], STATUS_MAP[i][2]];
      }
    }
    return [INVALID, "authentication refused"];
  }

  /* ── The nxc command line ─────────────────────────────────────────
     Generic options before the protocol, protocol options after. A flag
     the sub-parser does not define is never sent: the cost of getting
     that wrong is not an error, it is a silent '-'. */

  function buildCmd(cred, proto, targets, tune, dropped) {
    var c = ["nxc", "-t", String(tune.threads)];
    if (tune.jitter) c.push("--jitter", tune.jitter);
    c.push("--no-progress", proto);
    targets.forEach(function (t) { c.push(q(t)); });
    if (NXC.timeout_flag[proto]) c.push(NXC.timeout_flag[proto], String(tune.timeout));
    c.push("-u", q(cred.user), cred.isHash ? "-H" : "-p", q(cred.secret));
    if (cred.local) {
      if (has(NXC.local_auth_capable, proto)) c.push("--local-auth");
    } else if (cred.domain) {
      if (has(NXC.domain_capable, proto)) c.push("-d", q(cred.domain));
      else if (dropped && !has(dropped, proto)) dropped.push(proto);
    }
    c.push("--continue-on-success");
    return c.join(" ");
  }

  /* ── Matrix ───────────────────────────────────────────────────────
     Fixed width, sorted by address, never in arrival order — two runs
     have to diff cleanly. */

  function renderMatrix(out, hits, protocols, cred, overlay) {
    var best = {}, names = {}, ips = {};
    hits.forEach(function (h) {
      var k = h.ip + "|" + h.proto, cur = best[k];
      if (!cur || SEVERITY[h.status] > SEVERITY[cur.status]) best[k] = h;
      if (h.host && h.host !== "-" && h.host !== h.ip) names[h.ip] = h.host;
      if (h.ip !== "-") ips[h.ip] = 1;
    });
    var order = Object.keys(ips).sort(byIp);

    function reasonLines(indent) {
      var grouped = {}, lines = [];
      protocols.forEach(function (p) {
        var e = overlay[p];
        if (!e) return;
        var key = e[0] + "|" + e[1];
        (grouped[key] = grouped[key] || {st: e[0], why: e[1], ps: []}).ps.push(p);
      });
      Object.keys(grouped).map(function (k) { return grouped[k]; })
        .sort(function (a, b) {
          /* salvo keys this on (status, the protocols themselves) - not on the
             reason text, which would order them differently. */
          if (a.st !== b.st) return a.st < b.st ? -1 : 1;
          return a.ps.join(",") < b.ps.join(",") ? -1 : 1;
        })
        .forEach(function (g) {
          lines.push(indent + pad(GLYPH[g.st], 5) + " " + pad(g.ps.join(", "), 20) + " " + g.why);
        });
      return lines;
    }

    if (!order.length) {
      if (!Object.keys(overlay).length) { out("plain", "no results."); return; }
      out("plain", "");
      out("plain", "No host produced a result. Nothing here is a verdict:");
      reasonLines("  ").forEach(function (l) { out("plain", l); });
      return;
    }

    var rows = order.map(function (ip) {
      var label = names[ip] && names[ip] !== ip ? ip + " (" + names[ip] + ")" : ip;
      var cells = [], signal = false;
      protocols.forEach(function (p) {
        var h = best[ip + "|" + p];
        if (h) {
          cells.push(GLYPH[h.status]);
          if ([ADMIN, EXEC, VALID, BLOCKED, UNKNOWN, LOCKED].indexOf(h.status) >= 0) signal = true;
        } else if (overlay[p]) {
          cells.push(GLYPH[overlay[p][0]]);
        } else {
          cells.push(GLYPH[NOSVC]);
        }
      });
      return {label: label, cells: cells, signal: signal};
    });

    var width = Math.max(12, Math.max.apply(null, rows.map(function (r) { return r.label.length; })));
    var header = pad("host", width) + protocols.map(function (p) { return lpad(p, 8); }).join("");
    out("plain", "");
    out("rule", new Array(79).join("="));
    out("plain", " " + cred.label);
    out("rule", new Array(79).join("="));
    out("plain", header);
    out("rule", new Array(header.length + 1).join("-"));
    rows.forEach(function (r) {
      out("plain", pad(r.label, width) +
        r.cells.map(function (c) { return lpad(c, 8); }).join("") + (r.signal ? " <" : ""));
    });
    reasonLines("  ").forEach(function (l) { out("plain", l); });
    out("plain", "");
    LEGEND.forEach(function (l) { out("plain", l); });
    out("plain", "");
  }

  /* ── Follow-up commands ───────────────────────────────────────────
     Only ADMIN / exec / ok earn one. A blocked result means that exact
     path is closed, so handing back a command for it would be a lie. */

  function secretFlag(c) { return c.isHash ? "-H " + c.secret : "-p " + q(c.secret); }

  function commandsFor(h, c, adminHere) {
    var dom = c.domain || ".", sec = q(c.secret), note = adminHere ? "" : NO_ADMIN_NOTE;
    var o = [];
    if (h.proto === "winrm") {
      o.push(c.isHash
        ? "evil-winrm -i " + h.ip + " -u " + c.user + " -H " + c.secret + note
        : "evil-winrm -i " + h.ip + " -u " + c.user + " -p " + sec + note);
    } else if (h.proto === "smb") {
      if (h.status === ADMIN) {
        if (c.isHash) {
          o.push("impacket-psexec  -hashes :" + c.secret + " " + dom + "/" + c.user + "@" + h.ip);
          o.push("impacket-wmiexec -hashes :" + c.secret + " " + dom + "/" + c.user + "@" + h.ip);
        } else {
          o.push("impacket-psexec  " + dom + "/" + c.user + ":" + sec + "@" + h.ip);
          o.push("impacket-wmiexec " + dom + "/" + c.user + ":" + sec + "@" + h.ip);
        }
      } else {
        o.push("nxc smb " + h.ip + " -u " + c.user + " " + secretFlag(c) +
               " --shares   # non-admin still reads shares");
      }
    } else if (h.proto === "mssql") {
      o.push(c.isHash
        ? "impacket-mssqlclient " + c.user + "@" + h.ip + " -hashes :" + c.secret + " -windows-auth"
        : "impacket-mssqlclient " + c.user + ":" + sec + "@" + h.ip + " -windows-auth");
    } else if (h.proto === "rdp") {
      o.push("xfreerdp3 /u:" + c.user + " /p:" + sec + " /v:" + h.ip +
             " /cert:ignore /drive:kali,/home/kali" + note);
    } else if (h.proto === "ssh") {
      o.push("ssh " + c.user + "@" + h.ip + note);
    } else if (h.proto === "ftp") {
      o.push("ftp " + h.ip + "   # login " + c.user + " / " + c.secret);
    } else if (h.proto === "wmi" && h.status === ADMIN) {
      o.push("impacket-wmiexec " + dom + "/" + c.user + ":" + sec + "@" + h.ip);
    }
    return o;
  }

  function nextMoves(hits, cred) {
    var best = {}, byHost = {}, ldap = [];
    hits.forEach(function (h) {
      var k = h.ip + "|" + h.proto;
      if (!best[k] || SEVERITY[h.status] > SEVERITY[best[k].status]) best[k] = h;
    });
    Object.keys(best).forEach(function (k) {
      var h = best[k];
      if ([ADMIN, EXEC, VALID].indexOf(h.status) < 0) return;
      if (h.proto === "ldap") { ldap.push(h); return; }
      (byHost[h.ip] = byHost[h.ip] || []).push(h);
    });

    var blocks = [];
    var ips = Object.keys(byHost).sort(function (a, b) {
      var sa = Math.max.apply(null, byHost[a].map(function (x) { return SEVERITY[x.status]; }));
      var sb = Math.max.apply(null, byHost[b].map(function (x) { return SEVERITY[x.status]; }));
      if (sa !== sb) return sb - sa;
      return byIp(a, b);
    });
    ips.forEach(function (ip) {
      var hs = byHost[ip];
      hs.sort(function (a, b) {
        if (SEVERITY[a.status] !== SEVERITY[b.status]) return SEVERITY[b.status] - SEVERITY[a.status];
        return (PROTO_RANK[a.proto] === undefined ? 99 : PROTO_RANK[a.proto]) -
               (PROTO_RANK[b.proto] === undefined ? 99 : PROTO_RANK[b.proto]);
      });
      var adminHere = hs.some(function (x) { return x.status === ADMIN; });
      var label = (hs[0].host && hs[0].host !== "-" && hs[0].host !== ip) ? hs[0].host : ip;
      var head = label !== ip ? "  " + ip + " (" + label + ")" : "  " + ip;
      head += "   " + hs.map(function (x) { return x.proto + ":" + GLYPH[x.status]; }).join(", ");
      if (!adminHere) head += "   [no admin proven on this host]";
      blocks.push(head);
      hs.forEach(function (h) {
        commandsFor(h, cred, adminHere).forEach(function (c) { blocks.push("      " + c); });
      });
    });

    if (ldap.length) {
      ldap.sort(function (a, b) {
        if (SEVERITY[a.status] !== SEVERITY[b.status]) return SEVERITY[b.status] - SEVERITY[a.status];
        return byIp(a.ip, b.ip);
      });
      var l = ldap[0];
      blocks.push("  domain-wide (LDAP bind works as " + cred.user + ")");
      blocks.push("      nxc ldap " + l.ip + " -u " + cred.user + " " + secretFlag(cred) +
                  " --bloodhound -c All --dns-server " + l.ip);
      blocks.push("      nxc ldap " + l.ip + " -u " + cred.user + " " + secretFlag(cred) +
                  " --kerberoasting kerb.hashes");
    }
    return blocks;
  }

  function inconclusiveReport(hits, cred) {
    var best = {}, grouped = {};
    hits.forEach(function (h) {
      var k = h.ip + "|" + h.proto;
      if (!best[k] || SEVERITY[h.status] > SEVERITY[best[k].status]) best[k] = h;
    });
    Object.keys(best).forEach(function (k) {
      var h = best[k];
      if (h.status !== UNKNOWN && h.status !== BLOCKED) return;
      var key = cred.user + "|" + h.proto + "|" + h.note;
      (grouped[key] = grouped[key] || {proto: h.proto, note: h.note, ips: []}).ips.push(h.ip);
    });
    var out = [];
    Object.keys(grouped).sort().forEach(function (k) {
      var g = grouped[k];
      out.push("  " + pad(g.proto, 6) + " as " + pad(cred.user, 16) + " " + g.note);
      out.push("         " + g.ips.sort(byIp).join(", "));
    });
    return out;
  }

  /* ══ The command line ════════════════════════════════════════════
     salvo's own argument surface, as far as the estate can answer it.
     Anything it does not know is an error rather than a shrug — a
     wrapper that quietly ignores a flag is the failure this whole tool
     exists to prevent. */

  var VALUE_FLAGS = {
    "-u": "user", "--user": "user", "-p": "password", "--password": "password",
    "-H": "hash", "--hash": "hash", "-d": "domain", "--domain": "domain",
    "-P": "protocols", "--protocols": "protocols", "--parallel": "parallel",
    "--nxc-threads": "threads", "--nxc-timeout": "timeout", "--jitter": "jitter"
  };
  var BARE_FLAGS = {
    "--local-auth": "local", "--dry-run": "dryRun", "--slow": "slow",
    "--stealth": "stealth", "--markdown": "markdown", "--selftest": "selftest",
    "--check-nxc": "checkNxc", "--scope": "scope", "--version": "version",
    "--legend": "legend", "--help": "help", "-h": "help",
    "--no-lockout-guard": "noGuard", "--quiet": "quiet"
  };

  function parseArgs(argv) {
    var a = {targets: [], protocols: null, err: null};
    for (var i = 0; i < argv.length; i++) {
      var t = argv[i];
      if (VALUE_FLAGS.hasOwnProperty(t)) {
        if (i + 1 >= argv.length) { a.err = "argument " + t + ": expected one argument"; return a; }
        a[VALUE_FLAGS[t]] = argv[++i];
      } else if (BARE_FLAGS.hasOwnProperty(t)) {
        a[BARE_FLAGS[t]] = true;
      } else if (t.charAt(0) === "-" && t !== "-") {
        a.err = "unrecognized arguments: " + t;
        return a;
      } else {
        a.targets.push(t);
      }
    }
    return a;
  }

  /* Split a typed line the way a shell would, so a quoted password with a
     space in it survives into the credential rather than becoming a target. */
  function tokenize(line) {
    var out = [], cur = "", quote = null, started = false;
    for (var i = 0; i < line.length; i++) {
      var ch = line.charAt(i);
      if (quote) {
        if (ch === quote) quote = null;
        else cur += ch;
        continue;
      }
      if (ch === "'" || ch === '"') { quote = ch; started = true; continue; }
      if (ch === "\\" && i + 1 < line.length) { cur += line.charAt(++i); started = true; continue; }
      if (/\s/.test(ch)) {
        if (cur || started) { out.push(cur); cur = ""; started = false; }
        continue;
      }
      cur += ch;
      started = true;
    }
    if (quote) return null;                    // unbalanced: the shell would wait
    if (cur || started) out.push(cur);
    return out;
  }

  /* ── Running one salvo invocation ─────────────────────────────────
     Emits [kind, text] lines. `kind` is only ever presentation — it
     decides colour and, for a live result line, how long the terminal
     dwells on it before the next one lands. */

  function runSalvo(argv, emit) {
    var a = parseArgs(argv);
    if (a.err) {
      emit("bang", "usage: salvo [-h] [-u USER] [-p PASSWORD] [-H HASH] [-d DOMAIN] ...");
      emit("bang", "salvo: error: " + a.err);
      return;
    }
    if (a.help) { return helpSalvo(emit); }
    if (a.version) { return emit("plain", "salvo " + ESTATE.salvo_version); }
    if (a.legend) { return legend(emit); }
    if (a.scope) { return scope(emit); }
    if (a.selftest) { return selftest(emit); }
    if (a.checkNxc) { return checkNxc(a, emit); }

    if (!a.targets.length) {
      emit("bang", "[!] no targets given. Try: salvo 10.0.0.0/24 -u jdoe -p 'Password123!' -d corp.local");
      return;
    }
    if (a.password && a.hash) {
      emit("bang", "[!] -p and -H are mutually exclusive - pass one, or list both in a -C file.");
      return;
    }
    if (!a.user) { emit("bang", "[!] no credentials given. Use -u with -p or -H."); return; }
    if (!a.password && !a.hash) { emit("bang", "[!] -u needs -p or -H"); return; }

    var cred = {
      user: a.user,
      secret: a.hash || a.password,
      isHash: !!a.hash,
      domain: a.local ? null : (a.domain || null),
      local: !!a.local
    };
    var shown = cred.secret.length <= 34 ? cred.secret : cred.secret.slice(0, 31) + "...";
    var kind = cred.isHash ? "H" : "P";
    if (cred.local) {
      cred.label = "LOCAL\\" + cred.user + ":" + shown + " [" + kind + "]";
    } else if (cred.domain) {
      cred.label = cred.domain + "\\" + cred.user + ":" + shown + " [" + kind + "]";
    } else {
      /* Printing "DOMAIN\" here would read as though a domain had been applied
         when nxc was in fact left to guess the scope. */
      cred.label = cred.user + ":" + shown + " [" + kind +
                   "]  (no -d given - nxc guessed the scope)";
    }

    var protocols = a.protocols
      ? (a.protocols === "all" ? NXC.protocols.slice() : a.protocols.split(",").map(function (s) { return s.trim(); }))
      : NXC.default_protocols.slice();
    var bad = protocols.filter(function (p) { return !has(NXC.protocols, p); });
    if (bad.length) {
      emit("bang", "[!] unknown protocol(s): " + bad.join(",") + ". valid: " + NXC.protocols.join(","));
      return;
    }

    var tune = {threads: NXC.defaults.threads, timeout: NXC.defaults.timeout,
                parallel: NXC.defaults.parallel, jitter: null};
    if (a.slow) { tune = {threads: 5, timeout: 30, parallel: 3, jitter: null}; }
    if (a.stealth) { tune = {threads: 1, timeout: 30, parallel: 1, jitter: "3-7"}; }
    if (a.threads) tune.threads = +a.threads;
    if (a.timeout) tune.timeout = +a.timeout;
    if (a.parallel) tune.parallel = +a.parallel;
    if (a.jitter) tune.jitter = a.jitter;

    /* ---- what salvo declines to run, and says so ------------------ */
    var overlay = {}, planned = [];
    var hashSkip = [], ldapSkip = false;
    protocols.forEach(function (p) {
      if (cred.isHash && !has(NXC.hash_capable, p)) {
        hashSkip.push(p);
        overlay[p] = [NOTRUN, "nxc defines no -H here, so a hash cannot be tested over this protocol"];
        return;
      }
      if (cred.local && p === "ldap") {
        ldapSkip = true;
        overlay[p] = [NOTRUN, "nxc ldap has no --local-auth - a directory bind is always domain-scoped"];
        return;
      }
      planned.push(p);
    });

    if (a.stealth) {
      emit("info", "[*] --stealth: 1 process(es) at a time, 1 nxc thread(s), jitter 3-7, 5s between jobs.");
      emit("plain", "    This is slow ON PURPOSE. A full 8-protocol sweep of one host will take minutes, not seconds.");
      emit("plain", "");
    }
    if (!a.dryRun) {
      emit("info", "[*] salvo " + ESTATE.salvo_version + "  |  nxc " + ESTATE.nxc_version);
    }
    if (hashSkip.length) {
      emit("info", "[*] hash credentials cannot pass-the-hash over: " + hashSkip.join(", ") +
                   " - skipping those jobs");
    }
    if (ldapSkip) {
      emit("info", "[*] ldap has no --local-auth in nxc (a bind is always domain-scoped) - " +
                   "skipping the local-auth ldap job rather than spending a logon on it");
    }
    if (has(protocols, "vnc")) {
      emit("info", "[*] note: nxc vnc authenticates with a password only, the username is ignored");
    }

    var dropped = [];

    /* ---- dry run: build the commands and stop -------------------- */
    if (a.dryRun) {
      emit("plain", "");
      emit("plain", "[commands that would run - " + planned.length + " of them]");
      emit("plain", "");
      planned.forEach(function (p) {
        emit("plain", "  " + buildCmd(cred, p, a.targets, tune, dropped));
      });
      emit("plain", "");
      return;
    }

    /* ---- the arithmetic, before a single logon ------------------- */
    var ips = expand(a.targets);
    var hostCount = ips.length;
    var worst = planned.length * hostCount;
    if (worst > 3) {
      emit("warn", "[!] LOCKOUT MATH - each protocol against each host is a separate logon,");
      emit("plain", "    and a domain account's counter lives on the DC, so every host counts.");
      emit("plain", "      " + pad(cred.user, 24) + " up to " + worst + " logons (" +
                    planned.length + " protocol-jobs x " + hostCount + " hosts)");
      emit("plain", "    Default AD lockout threshold is often 5. Check it first:");
      emit("plain", "        nxc smb <DC_IP> -u '' -p '' --pass-pol");
      emit("plain", "    Narrow with -P smb,winrm, or spread it out with --stealth.");
      emit("plain", "");
    }

    emit("info", "[*] " + planned.length + " nxc process(es), " + tune.parallel + " at a time");
    emit("plain", "");

    /* ---- go ------------------------------------------------------ */
    var hosts = hostMap();
    var hits = [], attempts = 0, lockedAt = null, sawDomain = false;

    for (var pi = 0; pi < planned.length && !lockedAt; pi++) {
      var proto = planned[pi];
      buildCmd(cred, proto, a.targets, tune, dropped);      // records -d drops
      for (var ii = 0; ii < ips.length; ii++) {
        var ip = ips[ii];
        var h = hosts[ip];
        if (h && h.os) sawDomain = true;                    // the banner names a domain
        var oc = outcomeFor(cred.user, cred.secret, ip, proto);
        if (oc === null || oc === "quiet") continue;        // no line: renders '-'
        var v = classify(proto, oc);
        attempts += 1;
        var hit = {ip: ip, proto: proto, host: h ? h.name : "-", status: v[0], note: v[1]};
        hits.push(hit);
        emit("hit", liveLine(hit, cred));
        /* One nxc process carries every host for this protocol, so the lockout
           ends the RUN, not the job already reading that output: salvo kills
           what has not started, and does not un-see what has. The banner lands
           the moment it is seen, mid-job, which is the whole point of it. */
        if (hit.status === LOCKED && !a.noGuard && !lockedAt) {
          lockedAt = hit;
          emit("plain", "");
          emit("bang", new Array(71).join("!"));
          emit("bang", "  LOCKOUT DETECTED on " + hit.ip + " (" + hit.proto + ") as " + cred.user);
          emit("bang", "  Every remaining job has been killed.");
          emit("bang", "  Check the policy before you touch this domain again:");
          emit("bang", "      nxc smb <DC_IP> -u '' -p '' --pass-pol");
          emit("bang", "  Re-run with --no-lockout-guard only if you know what you are doing.");
          emit("bang", new Array(71).join("!"));
          emit("plain", "");
        }
      }
    }

    emit("plain", "");
    emit("info", "[*] finished in 0s");

    renderMatrix(emit, hits, protocols, cred, overlay);

    if (attempts) {
      emit("plain", "AUTHENTICATION ATTEMPTS ACTUALLY MADE (a '-' never reached auth):");
      emit("plain", "  " + pad(cred.user, 24) + " " + attempts);
      emit("plain", "");
    }

    var incon = inconclusiveReport(hits, cred);
    if (incon.length) {
      emit("plain", "NOT A VERDICT - these did not fail, they were blocked or unreadable:");
      incon.forEach(function (l) { emit("plain", l); });
      emit("plain", "  A credential in this list is still live. Take it to another protocol.");
      emit("plain", "");
    }

    var moves = nextMoves(hits, cred);
    if (moves.length) {
      emit("plain", "NEXT:");
      moves.forEach(function (l) { emit("plain", l); });
      emit("plain", "");
    }

    /* An impacket target parses domain/user:password@host positionally, so a
       password carrying one of those separators makes a pasted command mean
       something else. Cheaper to say than to debug at 2am. */
    if (!cred.isHash && /[@:\/]/.test(cred.secret)) {
      emit("warn", "[!] the password for " + cred.user + " contains @, : or / - impacket parses " +
        "domain/user:password@target positionally, so the commands above need care rather " +
        "than a straight paste.");
      emit("plain", "");
    }

    var notes = [];
    if (dropped.length) {
      dropped.sort();
      notes.push("-d was NOT sent to " + dropped.join(", ") + " - those protocols have no " +
        "domain argument, so nxc authenticated the bare username with no '" + cred.domain +
        "\\' prefix. Those cells answer a different question from the domain columns; on a " +
        "Windows host they usually resolve to the LOCAL account of the same name.");
    }
    /* The hosts announced a domain in their SMB banner that was never passed
       with -d. ldap and anything Kerberos-backed is unreliable without it. */
    if (sawDomain && !cred.local && !cred.domain) {
      notes.push("The targets advertise the domain '" + ESTATE.domain + "'. You did not pass " +
        "-d. Re-run with -d " + ESTATE.domain + " before trusting ldap, or any " +
        "Kerberos-backed result.");
    }
    notes.forEach(function (n) { emit("warn", "[!] " + n); });
    if (notes.length) emit("plain", "");
  }

  function liveLine(hit, cred) {
    var tags = {};
    tags[ADMIN] = "[ADMIN]"; tags[EXEC] = "[EXEC ]"; tags[VALID] = "[  +  ]";
    tags[BLOCKED] = "[VALID*]"; tags[UNKNOWN] = "[  ?  ]"; tags[LOCKED] = "[LOCK!]";
    tags[INVALID] = "[  -  ]"; tags[NOSVC] = "[ nosvc]"; tags[NOTRUN] = "[ n/a ]";
    return pad(tags[hit.status] || "[     ]", 8) + " " + pad(hit.proto, 6) + " " +
           pad(hit.ip, 16) + " " + pad(hit.host.slice(0, 16), 16) + " " + cred.user;
  }

  /* ── The commands that are not a run ──────────────────────────── */

  function legend(emit) {
    emit("plain", "");
    LEGEND.forEach(function (l) { emit("plain", l); });
    emit("plain", "");
    DATA.verdicts.forEach(function (v) {
      emit("plain", "  " + pad(v.key, 7) + " " + v.name);
      emit("plain", "          nxc printed:  " + v.line);
      wrap(v.means, 64).forEach(function (l) { emit("plain", "          " + l); });
      emit("plain", "          so do this:   " + v.do);
      emit("plain", "");
    });
  }

  function scope(emit) {
    emit("plain", "");
    emit("plain", "salvo " + ESTATE.salvo_version + " - authentication only");
    emit("plain", "");
    emit("plain", "  Every nxc command salvo builds is checked against an allowlist");
    emit("plain", "  immediately before it is executed. Anything unrecognised aborts");
    emit("plain", "  the run rather than being sent.");
    emit("plain", "");
    emit("plain", "  flags salvo will never send:");
    ["--am", "--asreproast", "--kerberoasting", "--lsa", "-M", "--ntds", "--put-file",
     "--sam", "-X", "-x"].forEach(function (f) { emit("plain", "      " + f); });
    emit("plain", "");
    emit("plain", "  salvo does not exploit, execute commands, dump credentials,");
    emit("plain", "  spoof, poison, relay, or scan for vulnerabilities. It authenticates,");
    emit("plain", "  reads the answer, and prints a matrix.");
    emit("plain", "");
  }

  var SELFTEST = [
    ["smb", null, "SMB         10.0.0.25  445    WEB01            [*] Windows 10.0 Build 19045 x64"],
    ["smb", ADMIN, "SMB         10.0.0.25  445    WEB01            [+] corp.local\\jdoe:Password123! (Pwn3d!)"],
    ["smb", VALID, "SMB         10.0.0.25  445    WEB01            [+] corp.local\\jdoe:Password123!"],
    ["smb", INVALID, "SMB         10.0.0.25  445    WEB01            [-] ... STATUS_LOGON_FAILURE"],
    ["smb", LOCKED, "SMB         10.0.0.25  445    WEB01            [-] ... STATUS_ACCOUNT_LOCKED_OUT"],
    ["smb", BLOCKED, "SMB         10.0.0.25  445    WEB01            [-] ... STATUS_LOGON_TYPE_NOT_GRANTED"],
    ["winrm", EXEC, "WINRM       10.0.0.25  5985   WEB01            [+] corp.local\\jdoe:Password123! (Pwn3d!)"],
    ["winrm", UNKNOWN, "WINRM       10.0.0.25  5985   WEB01            [-] corp.local\\jdoe:Password123!"],
    ["ssh", EXEC, "SSH         10.0.0.42  22     LNX01            [+] root:toor (Pwn3d!)"],
    ["ssh", INVALID, "SSH         10.0.0.42  22     LNX01            [-] root:toor"],
    ["mssql", ADMIN, "MSSQL       10.0.0.26  1433   SQL01            [+] corp.local\\svc_sql:Winter2026! (Pwn3d!)"],
    ["ldap", UNKNOWN, "LDAP        10.0.0.10  389    DC01             [-] ... STATUS_ACCESS_DENIED"]
  ];

  function selftest(emit) {
    emit("plain", "");
    emit("info", "[*] salvo parser self-test");
    emit("plain", "");
    SELFTEST.forEach(function (row) {
      emit("plain", "  ok    " + pad(row[0], 6) + " " + pad(String(row[1]), 9) + " " +
                    row[2].slice(0, 52));
    });
    emit("plain", "");
    emit("info", "[*] all " + SELFTEST.length + " parser checks passed.");
    emit("plain", "");
  }

  function checkNxc(a, emit) {
    var protos = a.protocols
      ? (a.protocols === "all" ? NXC.protocols.slice() : a.protocols.split(","))
      : NXC.default_protocols.slice();
    emit("plain", "");
    emit("plain", "  protocol   -d     --local-auth  -H     cont   timeout flag");
    emit("rule", "  " + new Array(69).join("-"));
    protos.forEach(function (p) {
      var t = NXC.timeout_flag[p];
      emit("plain", "  " + pad(p, 10) + " " +
        pad(has(NXC.domain_capable, p) ? "yes" : "no", 6) + " " +
        pad(has(NXC.local_auth_capable, p) ? "yes" : "no", 13) + " " +
        pad(has(NXC.hash_capable, p) ? "yes" : "no", 6) + " " +
        pad("yes", 6) + " " + (t ? t + " ok" : "none"));
    });
    emit("plain", "");
    emit("info", "[*] capability tables match the installed NetExec.");
    emit("plain", "");
  }

  function helpSalvo(emit) {
    emit("plain", "");
    emit("plain", "usage: salvo <targets> -u USER (-p PASS | -H HASH) [-d DOMAIN] [options]");
    emit("plain", "");
    emit("plain", "  <targets>          IPs, ranges (10.0.0.20-40) or CIDR");
    emit("plain", "  -u, --user         username");
    emit("plain", "  -p, --password     password          -H, --hash    NT hash");
    emit("plain", "  -d, --domain       domain            --local-auth  authenticate locally");
    emit("plain", "  -P, --protocols    comma list, or 'all'  (default: " +
                  NXC.default_protocols.join(",") + ")");
    emit("plain", "  --dry-run          print the nxc commands, run nothing");
    emit("plain", "  --slow / --stealth tunnel and low-and-slow presets");
    emit("plain", "  --parallel N       concurrent nxc processes (default 6)");
    emit("plain", "  --selftest         parser vs known nxc output formats");
    emit("plain", "  --check-nxc        capability tables vs the installed nxc");
    emit("plain", "  --scope            the flags salvo may and may never send");
    emit("plain", "  --legend           what every glyph in the matrix means");
    emit("plain", "");
  }

  function wrap(text, width) {
    var words = text.split(/\s+/), lines = [], cur = "";
    words.forEach(function (w) {
      if (cur && (cur + " " + w).length > width) { lines.push(cur); cur = w; }
      else cur = cur ? cur + " " + w : w;
    });
    if (cur) lines.push(cur);
    return lines;
  }

  /* ══ The shell ═══════════════════════════════════════════════════
     A prompt, a scrollback, history on the arrow keys and completion
     on Tab. The transcript already in the page is the opening run; the
     prompt appears underneath it once this is wired up. */

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var screen = host.querySelector("[data-screen]");
  var out = host.querySelector("[data-out]");
  var promptEl = host.querySelector("[data-prompt]");
  var typedEl = host.querySelector("[data-typed]");
  var input = host.querySelector("[data-input]");
  var ctl = host.querySelector("[data-ctl]");

  var history = [], hpos = 0, busy = false, queue = null;

  /* Same token rules as the server-side filter in app.py, so a line the
     engine prints and a line the server rendered look identical. */
  var TOKENS = new RegExp(
    "(LOCK!|STATUS_ACCOUNT_LOCKED_OUT)" +
    "|(STATUS_[A-Z_]+)" +
    "|(VALID\\*)" +
    "|(\\bADMIN\\b|Pwn3d!)" +
    "|(!CMD|\\bn\\/a\\b|\\berr\\b)" +
    "|(\\bexec\\b)" +
    "|(\\bok\\b)" +
    "|(\\s\\?(?=\\s|$))" +
    "|((?:^|\\s)--?[A-Za-z][\\w-]*)" +
    "|(\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b)" +
    "|(<$)", "g");
  var TOKEN_CLASS = ["lock", "status", "blocked", "admin", "salvo", "exec", "ok",
                     "unk", "flag", "addr", "mark"];

  /* Built as nodes, never as markup: whatever gets typed at the prompt
     ends up on this screen, and a password is not going to become HTML. */
  function lineEl(kind, text) {
    var el = document.createElement("span");
    el.className = "tl k-" + kind;
    var last = 0;
    text.replace(TOKENS, function (match) {
      var at = arguments[arguments.length - 2];
      if (at > last) el.appendChild(document.createTextNode(text.slice(last, at)));
      var b = document.createElement("b");
      for (var g = 1; g <= TOKEN_CLASS.length; g++) {
        if (arguments[g] !== undefined) { b.className = "t-" + TOKEN_CLASS[g - 1]; break; }
      }
      b.textContent = match;
      el.appendChild(b);
      last = at + match.length;
      return match;
    });
    if (last < text.length) el.appendChild(document.createTextNode(text.slice(last)));
    return el;
  }

  function print(kind, text) {
    out.appendChild(lineEl(kind, text == null ? "" : text));
  }

  function echo(cmd) {
    var el = document.createElement("span");
    el.className = "tl k-cmd";
    var ps = document.createElement("b");
    ps.className = "t-ps1";
    ps.textContent = PS1;
    el.appendChild(ps);
    el.appendChild(document.createTextNode(cmd));
    out.appendChild(el);
  }

  /* Dwell per line kind. A live result line is one nxc process coming
     back and should land like one; a table rule is instant. */
  var DWELL = {hit: 90, info: 60, warn: 55, bang: 40, rule: 12, cmd: 0, plain: 10};

  function play(lines, done) {
    if (reduced) {
      lines.forEach(function (l) { print(l[0], l[1]); });
      done();
      return;
    }
    busy = true;
    var i = 0;
    (function step() {
      if (i >= lines.length) { busy = false; done(); return; }
      var l = lines[i++];
      print(l[0], l[1]);
      var ms = (l[1] ? (DWELL[l[0]] || 10) : 18);
      if (l[0] === "hit") ms += Math.random() * 70;
      window.setTimeout(step, ms);
    })();
  }

  /* ── Non-salvo commands ───────────────────────────────────────── */

  function cmdHelp(emit) {
    emit("plain", "");
    emit("plain", "  This is a working salvo against a fixed six-host estate.");
    emit("plain", "  Every line below runs. Click one, or type it.");
    emit("plain", "");
    DATA.examples.forEach(function (e) {
      emit("run", e[0]);
      emit("dim", "      " + e[1]);
    });
    emit("plain", "");
    emit("plain", "  Also: clear, help, salvo --help. Arrow keys walk your history,");
    emit("plain", "  Tab completes a command.");
    emit("plain", "");
  }

  function cmdHosts(emit) {
    emit("plain", "");
    emit("plain", "  " + pad("address", 12) + pad("name", 8) + pad("listening", 34) + "os");
    emit("rule", "  " + new Array(79).join("-"));
    ESTATE.hosts.forEach(function (h) {
      emit("plain", "  " + pad(h[0], 12) + pad(h[1], 8) +
        pad(h[3].length ? h[3].join(",") : "(nothing)", 34) + (h[2] || "-"));
    });
    emit("plain", "");
    emit("dim", "  Everything else in 10.0.0.0/24 is dark, which is what makes the");
    emit("dim", "  lockout arithmetic worth reading: salvo counts the whole scope.");
    emit("plain", "");
  }

  function cmdCreds(emit) {
    emit("plain", "");
    Object.keys(ESTATE.creds).forEach(function (u) {
      var c = ESTATE.creds[u];
      emit("plain", "  " + pad(u, 16) + pad(c.kind === "H" ? "NT hash" : "password", 10) +
                    pad(c.scope, 8) + c.secret);
      emit("dim", "  " + pad("", 16) + c.blurb);
    });
    emit("plain", "");
    emit("dim", "  Any other username, or the wrong secret, authenticates nowhere -");
    emit("dim", "  which is what makes '.' mean something different from '-'.");
    emit("plain", "");
  }

  /* ── Dispatch ─────────────────────────────────────────────────── */

  function submit(text) {
    var cmd = text.trim();
    echo(cmd);
    if (cmd) { history.push(cmd); }
    hpos = history.length;

    if (!cmd) { ready(); return; }

    var argv = tokenize(cmd);
    if (argv === null) {
      print("bang", "salvo: unbalanced quote");
      ready();
      return;
    }

    var lines = [];
    var emit = function (k, t) { lines.push([k, t]); };
    var name = argv[0];

    if (name === "clear") { out.textContent = ""; ready(); return; }
    else if (name === "help" || name === "?") cmdHelp(emit);
    else if (name === "hosts") cmdHosts(emit);
    else if (name === "creds") cmdCreds(emit);
    else if (name === "salvo") runSalvo(argv.slice(1), emit);
    else if (name === "nxc") {
      emit("plain", "");
      emit("dim", "  nxc runs one protocol per invocation - that is the whole reason");
      emit("dim", "  salvo exists. Try the salvo line instead:");
      emit("run", "salvo 10.0.0.0/24 -u jdoe -p 'Password123!' -d corp.local");
      emit("plain", "");
    } else {
      emit("bang", name + ": command not found. Type help.");
    }

    play(lines, ready);
  }

  function ready() {
    promptEl.hidden = false;
    typedEl.textContent = "";
    input.value = "";
    /* Keep the prompt reachable when a long command has just pushed it past
       the fold — but never yank the page while a reader is mid-transcript. */
    var r = promptEl.getBoundingClientRect();
    if (r.bottom > window.innerHeight) {
      promptEl.scrollIntoView({block: "end", behavior: reduced ? "auto" : "smooth"});
    }
  }

  /* ── Input ────────────────────────────────────────────────────── */

  var COMPLETIONS = ["salvo", "help", "hosts", "creds", "clear",
    "salvo --help", "salvo --legend", "salvo --selftest", "salvo --check-nxc -P all",
    "salvo --scope", "salvo --version"];

  function complete(prefix) {
    var pool = COMPLETIONS.concat(DATA.examples.map(function (e) { return e[0]; }));
    var hit = pool.filter(function (c) { return c.indexOf(prefix) === 0 && c !== prefix; });
    if (!hit.length) return null;
    if (hit.length === 1) return hit[0];
    /* longest common prefix, like a real shell */
    var lcp = hit[0];
    hit.forEach(function (h) {
      var i = 0;
      while (i < lcp.length && i < h.length && lcp.charAt(i) === h.charAt(i)) i++;
      lcp = lcp.slice(0, i);
    });
    return lcp.length > prefix.length ? lcp : null;
  }

  input.addEventListener("input", function () { typedEl.textContent = input.value; });

  input.addEventListener("keydown", function (e) {
    if (busy) { e.preventDefault(); return; }
    if (e.key === "Enter") {
      e.preventDefault();
      promptEl.hidden = true;
      submit(input.value);
      input.value = "";
      typedEl.textContent = "";
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      if (hpos > 0) { hpos -= 1; input.value = history[hpos]; typedEl.textContent = input.value; }
    } else if (e.key === "ArrowDown") {
      e.preventDefault();
      if (hpos < history.length - 1) { hpos += 1; input.value = history[hpos]; }
      else { hpos = history.length; input.value = ""; }
      typedEl.textContent = input.value;
    } else if (e.key === "Tab") {
      e.preventDefault();
      var c = complete(input.value);
      if (c) { input.value = c; typedEl.textContent = c; }
    } else if (e.key === "l" && e.ctrlKey) {
      e.preventDefault();
      out.textContent = "";
    } else if (e.key === "c" && e.ctrlKey) {
      e.preventDefault();
      echo(input.value + "^C");
      input.value = "";
      typedEl.textContent = "";
    }
  });

  /* Clicking anywhere on the screen focuses the prompt, and clicking a
     printed command runs it — the only affordance the terminal needs. */
  screen.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest(".k-run") : null;
    if (t && !busy) {
      var cmd = t.textContent.trim();
      promptEl.hidden = true;
      submit(cmd);
      return;
    }
    if (window.getSelection && String(window.getSelection())) return;   // let them copy
    input.focus({preventScroll: true});
  });

  /* ── Boot ─────────────────────────────────────────────────────── */

  function boot() {
    input.hidden = false;
    if (ctl) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "sh-btn";
      b.textContent = "clear";
      b.addEventListener("click", function () { out.textContent = ""; input.focus({preventScroll: true}); });
      ctl.appendChild(b);
      var h = document.createElement("button");
      h.type = "button";
      h.className = "sh-btn";
      h.textContent = "help";
      h.addEventListener("click", function () {
        if (busy) return;
        promptEl.hidden = true;
        submit("help");
      });
      ctl.appendChild(h);
    }

    /* The recorded run is already on screen and is the same command. Reserve
       the height it occupies before clearing, so replaying it live fills a
       box that was already the right size instead of collapsing the page and
       growing it back a line at a time. */
    var opening = OPENING;
    var lines = [];
    runSalvo(tokenize(opening).slice(1), function (k, t) { lines.push([k, t]); });
    out.style.minHeight = out.offsetHeight + "px";
    out.textContent = "";
    echo(opening);
    play(lines, function () {
      var tip = [];
      tip.push(["plain", ""]);
      tip.push(["dim", "  That was live - not a recording. Type help to see what else runs."]);
      tip.push(["plain", ""]);
      play(tip, function () {
        out.style.minHeight = "";      // from here it just grows
        ready();
      });
    });
  }

  try {
    if (reduced) {
      /* No playback: leave the recorded transcript exactly as rendered and
         put a working prompt under it. */
      input.hidden = false;
      ready();
      if (ctl) {
        var cb = document.createElement("button");
        cb.type = "button";
        cb.className = "sh-btn";
        cb.textContent = "help";
        cb.addEventListener("click", function () { promptEl.hidden = true; submit("help"); });
        ctl.appendChild(cb);
      }
    } else if ("IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          obs.disconnect();
          boot();
        });
      }, {threshold: 0.2});
      io.observe(host);
    } else {
      boot();
    }
  } catch (err) {
    /* Leave the recorded run on screen; it was readable before we started. */
    if (window.console && window.console.error) window.console.error(err);
  }
})();
