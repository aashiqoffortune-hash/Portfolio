/* salvo case page — the recorded terminal player and the three labs.

   Progressive enhancement, same rule as main.js: every transcript, every
   verdict card and both computed panels are already rendered by the server.
   Nothing here reveals content that was not readable before it ran, and the
   first thing an unexpected failure does is put everything back on screen. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function all(sel, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(sel));
  }

  /* If anything below throws, undo every hide this file performs. A broken
     enhancement must leave the page where it found it, not empty. */
  function bail() {
    all(".tl[hidden], .term-pane[hidden], .vcard[hidden]").forEach(function (el) {
      el.hidden = false;
    });
  }

  /* ── Painting generated output ───────────────────────────────────
     The recorded transcripts are coloured on the server. The two labs
     print lines that did not exist until you moved a control, so they
     need the same rules here. Kept deliberately in step with _TOKENS
     in app.py. */

  var TOKENS = new RegExp(
    "(LOCK!|STATUS_ACCOUNT_LOCKED_OUT)" +
    "|(STATUS_[A-Z_]+)" +
    "|(VALID\\*)" +
    "|(\\bADMIN\\b|Pwn3d!)" +
    "|(!CMD|\\bn\\/a\\b|\\berr\\b)" +
    "|(\\bexec\\b)" +
    "|(\\bok\\b)" +
    "|((?:^|\\s)--?[A-Za-z][\\w-]*)" +
    "|(\\b(?:\\d{1,3}\\.){3}\\d{1,3}\\b)",
    "g"
  );
  var TOKEN_CLASS = ["lock", "status", "blocked", "admin", "salvo", "exec", "ok", "flag", "addr"];

  /* Built as DOM rather than markup, so a password typed into the builder
     can never be read back as HTML. */
  function line(kind, text) {
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

  function paint(pre, lines) {
    pre.textContent = "";
    lines.forEach(function (l) {
      pre.appendChild(line(l[0], l[1]));
    });
  }

  function pad(s, n) {
    s = String(s);
    while (s.length < n) s += " ";
    return s;
  }

  /* ── Copy ────────────────────────────────────────────────────── */

  function button(label, act, title) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "term-btn";
    b.textContent = label;
    if (act) b.setAttribute("data-act", act);
    if (title) b.title = title;
    return b;
  }

  function copyable(btn, getText) {
    btn.addEventListener("click", function () {
      var text = getText();
      var done = function () {
        var was = btn.textContent;
        btn.textContent = "copied";
        window.setTimeout(function () { btn.textContent = was; }, 1400);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
        return;
      }
      /* No clipboard API (or no secure context): select it so ⌘C still works. */
      var ta = document.createElement("textarea");
      ta.value = text;
      ta.setAttribute("readonly", "");
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      try { document.execCommand("copy"); done(); } catch (e) { /* leave it */ }
      document.body.removeChild(ta);
    });
  }

  /* ══ 1 · The recorded sessions ═══════════════════════════════════
     A transcript is a list of lines that already know what kind they
     are, and the kind is what decides the dwell: a live result line is
     one nxc process finishing and should land like one, where a table
     rule is instant. That is the whole illusion — no frame timing, no
     canvas, just honest per-line pacing. */

  var DWELL = { hit: 400, info: 115, warn: 115, bang: 70, rule: 26, plain: 24 };

  function Player(pane) {
    this.pane = pane;
    this.body = pane.querySelector("[data-body]");
    this.cmdEl = pane.querySelector("[data-cmd]");
    this.caret = pane.querySelector("[data-caret]");
    this.out = pane.querySelector("[data-out]");
    this.lines = all(".tl", this.out);
    this.command = this.cmdEl.textContent;
    this.speed = 1;
    this.timer = null;
    this.typed = 0;
    this.shown = 0;
    this.running = false;
    this.played = false;
  }

  Player.prototype.dwell = function (el) {
    var kind = (el.className.match(/k-([a-z]+)/) || [0, "plain"])[1];
    var ms = el.textContent ? (DWELL[kind] || 24) : 44;
    if (kind === "hit") ms += Math.random() * 360;   // processes finish unevenly
    return ms / this.speed;
  };

  Player.prototype.at = function (fn, ms) {
    var self = this;
    this.timer = window.setTimeout(function () { self.timer = null; fn(); }, ms);
  };

  Player.prototype.rewind = function () {
    window.clearTimeout(this.timer);
    this.timer = null;
    this.running = false;
    this.typed = 0;
    this.shown = 0;
    this.cmdEl.textContent = "";
    this.caret.hidden = false;
    this.lines.forEach(function (el) { el.hidden = true; });
    this.body.scrollTop = 0;
  };

  Player.prototype.finish = function () {
    window.clearTimeout(this.timer);
    this.timer = null;
    this.running = false;
    this.played = true;
    this.typed = this.command.length;
    this.shown = this.lines.length;
    this.cmdEl.textContent = this.command;
    this.caret.hidden = true;
    this.lines.forEach(function (el) { el.hidden = false; });
    this.sync();
  };

  Player.prototype.pause = function () {
    window.clearTimeout(this.timer);
    this.timer = null;
    this.running = false;
    this.sync();
  };

  Player.prototype.play = function () {
    if (this.running) return;
    if (this.shown >= this.lines.length && this.typed >= this.command.length) this.rewind();
    this.running = true;
    this.played = true;
    this.caret.hidden = false;
    this.sync();
    this.step();
  };

  Player.prototype.step = function () {
    var self = this;
    if (!this.running) return;

    if (this.typed < this.command.length) {
      this.typed += 1;
      this.cmdEl.textContent = this.command.slice(0, this.typed);
      this.at(function () { self.step(); },
              (this.typed === this.command.length ? 420 : 22 + Math.random() * 34) / this.speed);
      return;
    }

    if (this.shown < this.lines.length) {
      var el = this.lines[this.shown++];
      el.hidden = false;
      this.body.scrollTop = this.body.scrollHeight;
      this.at(function () { self.step(); }, this.dwell(el));
      return;
    }

    this.running = false;
    this.caret.hidden = true;
    this.sync();
  };

  Player.prototype.sync = function () {
    if (!this.playBtn) return;
    this.playBtn.textContent = this.running ? "pause" : "play";
    this.playBtn.title = this.running ? "Pause playback" : "Play this session";
  };

  Player.prototype.controls = function () {
    var self = this;
    var host = this.pane.querySelector("[data-ctl]");
    if (!host) return;

    this.playBtn = button("play", "play");
    this.playBtn.addEventListener("click", function () {
      if (self.running) self.pause(); else self.play();
    });

    var replay = button("↺", null, "Play from the top");
    replay.addEventListener("click", function () { self.rewind(); self.play(); });

    var end = button("end", null, "Show the whole transcript now");
    end.addEventListener("click", function () { self.finish(); });

    var rate = button("1×", null, "Playback speed");
    rate.addEventListener("click", function () {
      self.speed = self.speed === 1 ? 2 : (self.speed === 2 ? 4 : 1);
      rate.textContent = self.speed + "×";
    });

    var copy = button("copy", null, "Copy the whole session");
    copyable(copy, function () {
      return "$ " + self.command + "\n" +
             self.lines.map(function (l) { return l.textContent; }).join("\n") + "\n";
    });

    host.appendChild(this.playBtn);
    host.appendChild(replay);
    host.appendChild(end);
    host.appendChild(rate);
    host.appendChild(copy);
    this.sync();
  };

  function terminal(root) {
    var panes = all(".term-pane", root);
    var tabs = all(".term-tab", root);
    if (!panes.length) return;

    var players = {};
    panes.forEach(function (pane) {
      var p = new Player(pane);
      players[pane.getAttribute("data-pane")] = p;
      if (!reduced) {
        p.controls();
        p.rewind();
      } else {
        /* Reduced motion: no playback at all. The transcripts stay exactly as
           the server rendered them, and the only control is copy. */
        var host = pane.querySelector("[data-ctl]");
        if (host) {
          var copy = button("copy", null, "Copy the whole session");
          copyable(copy, function () {
            return "$ " + p.command + "\n" +
                   p.lines.map(function (l) { return l.textContent; }).join("\n") + "\n";
          });
          host.appendChild(copy);
        }
      }
    });

    var current = panes[0].getAttribute("data-pane");

    function show(id, andPlay) {
      current = id;
      panes.forEach(function (pane) {
        pane.hidden = pane.getAttribute("data-pane") !== id;
      });
      tabs.forEach(function (t) {
        t.classList.toggle("on", t.getAttribute("data-pane") === id);
      });
      var p = players[id];
      if (p && andPlay && !reduced) { p.rewind(); p.play(); }
    }

    tabs.forEach(function (tab) {
      tab.addEventListener("click", function (e) {
        e.preventDefault();
        show(tab.getAttribute("data-pane"), true);
      });
    });

    show(current, false);

    /* Start the first session when it comes into view, once — the point of
       recording them was that they play without being asked. */
    if (!reduced && "IntersectionObserver" in window) {
      var io = new IntersectionObserver(function (entries, obs) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          obs.disconnect();
          var p = players[current];
          if (p && !p.played) p.play();
        });
      }, { threshold: 0.25 });
      io.observe(root);
    } else if (!reduced) {
      var first = players[current];
      if (first) first.play();
    }
  }

  /* ══ 2 · Reading the matrix ══════════════════════════════════════
     Every cell is already an anchor to its own explanation, so without
     this the grid is a table of contents over a stack of cards. With
     it, one card at a time, in place. */

  function matrix(lab) {
    var cards = all(".vcard", lab);
    var cells = all("a.cell[data-v]", lab);
    if (!cards.length || !cells.length) return;

    function select(slug) {
      cards.forEach(function (c) { c.hidden = c.getAttribute("data-v") !== slug; });
      cells.forEach(function (c) { c.classList.toggle("on", c.getAttribute("data-v") === slug); });
    }

    cells.forEach(function (cell) {
      cell.addEventListener("click", function (e) {
        e.preventDefault();
        select(cell.getAttribute("data-v"));
      });
    });

    select(cards[0].getAttribute("data-v"));
  }

  /* ══ 3 · The lockout arithmetic ══════════════════════════════════
     salvo's own multiplication, with the inputs left open. It warns
     for every account above three logons, not just the worst one, so
     this does too. */

  function lockout(lab, accounts) {
    var pre = lab.querySelector('[data-out="lockout"]');
    var verdict = lab.querySelector('[data-out="verdict"]');
    if (!pre || !verdict) return;

    var hosts = lab.querySelector('[data-in="hosts"]');
    var creds = lab.querySelector('[data-in="creds"]');
    var thr = lab.querySelector('[data-in="thr"]');
    var protos = all('[data-in="proto"]', lab);
    var read = {
      hosts: lab.querySelector('[data-out="hosts"]'),
      creds: lab.querySelector('[data-out="creds"]'),
      thr: lab.querySelector('[data-out="thr"]'),
      nproto: lab.querySelector('[data-out="nproto"]')
    };

    function render() {
      var nHosts = parseInt(hosts.value, 10);
      var nCreds = parseInt(creds.value, 10);
      var nThr = parseInt(thr.value, 10);
      var jobs = protos.filter(function (p) { return p.checked; }).length;
      var worst = jobs * nHosts;

      read.hosts.textContent = nHosts;
      read.creds.textContent = nCreds;
      read.thr.textContent = nThr;
      read.nproto.textContent = jobs;

      if (!jobs) {
        paint(pre, [["info", "[*] no protocols selected - salvo would have nothing to run."]]);
        verdict.className = "lab-verdict";
        verdict.textContent = "No jobs, no logons. Also no answers.";
        return;
      }

      var out = [];
      /* salvo stays quiet below four logons for an account, and a warning
         that fires for everything is a warning nobody reads. */
      if (worst > 3) {
        out.push(["warn", "[!] LOCKOUT MATH - each protocol against each host is a separate logon,"]);
        out.push(["plain", "    and a domain account's counter lives on the DC, so every host counts."]);
        for (var i = 0; i < nCreds; i++) {
          out.push(["plain", "      " + pad(accounts[i % accounts.length], 24) +
                             " up to " + worst + " logons (" + jobs +
                             " protocol-jobs x " + nHosts + " hosts)"]);
        }
        out.push(["plain", "    Default AD lockout threshold is often 5. Check it first:"]);
        out.push(["plain", "        nxc smb <DC_IP> -u '' -p '' --pass-pol"]);
        out.push(["plain", "    Narrow with -P smb,winrm, or spread it out with --stealth."]);
      } else {
        out.push(["info", "[*] " + worst + " logons for the account - salvo prints no lockout"]);
        out.push(["info", "    warning below four, because a warning that fires for"]);
        out.push(["info", "    everything is a warning nobody reads."]);
      }
      paint(pre, out);

      var over = worst >= nThr;
      verdict.className = "lab-verdict" + (over ? " over" : "");
      if (over) {
        verdict.textContent = worst + " logons against a threshold of " + nThr + ". " +
          (nCreds > 1 ? nCreds + " accounts lock" : "That account locks") + " " +
          Math.floor(worst / nThr) + "× over — and the counter is on the DC, " +
          "so spreading the sweep across member servers does not help.";
      } else {
        verdict.textContent = worst + " logons against a threshold of " + nThr +
          ". Inside it — on the threshold you were told. Confirm the real one first: " +
          "nxc smb <DC_IP> -u '' -p '' --pass-pol";
      }
    }

    [hosts, creds, thr].concat(protos).forEach(function (el) {
      el.addEventListener("input", render);
      el.addEventListener("change", render);
    });
    render();
  }

  /* ══ 4 · The command builder ═════════════════════════════════════
     A faithful --dry-run. The capability tables come from the page's
     JSON block, which is a transcription of the ones at the top of
     salvo.py — the same tables `salvo --check-nxc` verifies against
     the installed NetExec. Getting these wrong is the failure the tool
     exists to prevent, so the builder gets them from one place. */

  var SAFE = /^[A-Za-z0-9_@%+=:,.\/-]+$/;   /* shlex.quote's own safe set */

  function q(s) {
    if (s === "" || s == null) return "''";
    if (SAFE.test(s)) return s;
    return "'" + String(s).replace(/'/g, "'\"'\"'") + "'";
  }

  function builder(lab, cfg) {
    var pre = lab.querySelector('[data-out="build"]');
    var cmdOut = lab.querySelector('[data-out="salvocmd"]');
    var note = lab.querySelector('[data-out="buildnote"]');
    if (!pre || !cmdOut) return;

    var f = {
      targets: lab.querySelector('[data-in="targets"]'),
      user: lab.querySelector('[data-in="user"]'),
      kind: lab.querySelector('[data-in="kind"]'),
      secret: lab.querySelector('[data-in="secret"]'),
      domain: lab.querySelector('[data-in="domain"]'),
      local: lab.querySelector('[data-in="local"]'),
      preset: lab.querySelector('[data-in="preset"]')
    };
    var protos = all('[data-in="bproto"]', lab);
    var count = lab.querySelector('[data-out="bproto"]');
    var defaults = cfg.defaults;
    var DEFAULT_SET = "smb,winrm,wmi,mssql,ldap,rdp,ssh,ftp";

    function has(list, p) { return list.indexOf(p) >= 0; }

    function render() {
      var chosen = protos.filter(function (p) { return p.checked; })
                         .map(function (p) { return p.value; });
      var isHash = f.kind.value === "H";
      var local = f.local.checked;
      var domain = local ? "" : f.domain.value.trim();
      var user = f.user.value.trim() || "jdoe";
      var secret = f.secret.value;
      var targets = f.targets.value.trim().split(/\s+/).filter(Boolean);
      if (!targets.length) targets = ["10.0.0.0/29"];
      var tune = cfg.presets[f.preset.value] || {};
      var threads = tune.threads || defaults.threads;
      var timeout = tune.timeout || defaults.timeout;

      count.textContent = chosen.length;

      var skipHash = [], skipLdap = false, dropped = [], cmds = [];

      chosen.forEach(function (p) {
        if (isHash && !has(cfg.hash_capable, p)) { skipHash.push(p); return; }
        if (local && p === "ldap") { skipLdap = true; return; }

        /* nxc's generic options come before the protocol and the protocol's
           own after it. Getting that order wrong is the commonest nxc
           mistake, so the order here is salvo's, exactly. */
        var c = ["nxc", "-t", String(threads)];
        if (tune.jitter) c.push("--jitter", tune.jitter);
        c.push("--no-progress", p);
        targets.forEach(function (t) { c.push(q(t)); });
        if (cfg.timeout_flag[p]) c.push(cfg.timeout_flag[p], String(timeout));
        c.push("-u", q(user), isHash ? "-H" : "-p", q(secret));
        if (local) {
          if (has(cfg.local_auth_capable, p)) c.push("--local-auth");
        } else if (domain) {
          if (has(cfg.domain_capable, p)) c.push("-d", q(domain));
          else dropped.push(p);
        }
        c.push("--continue-on-success");
        cmds.push("  " + c.join(" "));
      });

      var out = [];
      if (f.preset.value === "stealth") {
        out.push(["info", cfg.notes.stealth]);
        out.push(["plain", "    This is slow ON PURPOSE. A full 8-protocol sweep of one host " +
                           "will take minutes, not seconds."]);
      }
      if (skipHash.length) {
        out.push(["info", cfg.notes.hash_skip.replace("{}", skipHash.join(", "))]);
      }
      if (skipLdap) out.push(["info", cfg.notes.ldap_local]);
      if (has(chosen, "vnc")) out.push(["info", cfg.notes.vnc]);
      if (out.length) out.push(["plain", ""]);
      out.push(["plain", "[commands that would run - " + cmds.length + " of them]"]);
      out.push(["plain", ""]);
      cmds.forEach(function (c) { out.push(["plain", c]); });
      paint(pre, out);

      /* The salvo invocation itself, as you would type it. */
      var line = ["salvo"].concat(targets.map(q));
      line.push("-u", q(user), isHash ? "-H" : "-p", q(secret));
      if (local) line.push("--local-auth");
      else if (domain) line.push("-d", q(domain));
      if (chosen.join(",") !== DEFAULT_SET) {
        line.push("-P", chosen.length ? chosen.join(",") : "none");
      }
      if (f.preset.value) line.push("--" + f.preset.value);
      line.push("--dry-run");
      cmdOut.textContent = line.join(" ");

      if (note) {
        var said = [];
        if (dropped.length) {
          said.push("<code>-d</code> is withheld from <code>" + dropped.join("</code>, <code>") +
                    "</code> — those nxc parsers define no domain argument, and passing it " +
                    "would make argparse exit before a packet was sent. Those columns test " +
                    "the bare username, which is a different question.");
        }
        if (skipHash.length) {
          said.push("<code>" + skipHash.join("</code>, <code>") + "</code> take no " +
                    "<code>-H</code>, so a hash cannot be tested there. salvo runs no job " +
                    "at all and renders those cells <code>n/a</code> — never the " +
                    "<code>-</code> that reads as a closed port.");
        }
        if (skipLdap) {
          said.push("<code>ldap</code> takes <code>-d</code> but not " +
                    "<code>--local-auth</code>, because a directory bind is always " +
                    "domain-scoped. salvo drops the job rather than spending a logon on it.");
        }
        if (!chosen.length) said.push("Nothing selected, so there is nothing to send.");
        if (!said.length) {
          said.push("Every selected protocol accepts every flag in these command lines. " +
                    "Take the domain off <code>ssh</code>, or ask for a hash over " +
                    "<code>ftp</code>, and salvo says what it withheld instead of " +
                    "building a command nxc would reject.");
        }
        note.innerHTML = said.join(" ");
      }
    }

    Object.keys(f).forEach(function (k) {
      f[k].addEventListener("input", render);
      f[k].addEventListener("change", render);
    });
    protos.forEach(function (p) { p.addEventListener("change", render); });
    render();
  }

  /* ══ Snippet copy ════════════════════════════════════════════════ */

  function snippets() {
    all(".run").forEach(function (run) {
      var code = run.querySelector("code");
      if (!code) return;
      var btn = button("copy");
      btn.className = "term-btn run-copy";
      copyable(btn, function () { return code.textContent; });
      run.appendChild(btn);
    });
  }

  /* ══ Boot ════════════════════════════════════════════════════════ */

  try {
    var term = document.querySelector("[data-term]");
    if (term) terminal(term);

    var mx = document.querySelector('[data-lab="matrix"]');
    if (mx) matrix(mx);

    var raw = document.getElementById("salvo-data");
    var cfg = raw ? JSON.parse(raw.textContent) : null;

    if (cfg) {
      var lk = document.querySelector('[data-lab="lockout"]');
      if (lk) lockout(lk, cfg.accounts);

      var bl = document.querySelector('[data-lab="build"]');
      if (bl) builder(bl, cfg);
    }

    snippets();
  } catch (err) {
    bail();
    if (window.console && window.console.error) window.console.error(err);
  }
})();
