"""Recorded terminal sessions and the data behind the salvo page's demos.

Every transcript here is real output from `salvo 1.0.0`, captured by running the
tool against `tests/fake_nxc.py` — the harness in salvo's own repository that
emits genuine NetExec line shapes for a fixed cast of hosts. Nothing is
hand-written to look like a terminal, and nothing was captured against a live
estate. The environment switches that harness exposes (lockout, a rejected
command, capability drift) are what make the failure paths reproducible here.

Re-record with NetExec on PATH and the transcripts are the same shape, against
real hosts.

The capability tables at the bottom are a transcription of the ones at the top
of `salvo.py`, so the in-browser command builder builds the same command lines
salvo would. They are what `salvo --check-nxc` verifies against the installed
NetExec.
"""

from textwrap import dedent


def _d(text):
    """Dedent a transcript and trim the leading newline.

    Column alignment is load-bearing in every one of these — the matrix is a
    fixed-width table — so they are stored indented for readability here and
    straightened on import rather than by hand.
    """
    return dedent(text).strip("\n")


# ── Recorded sessions ────────────────────────────────────────────────
# One per failure mode the tool exists to handle. Played back on the page
# in order; readable as plain text with no JavaScript at all.

DEMOS = [
    {
        "id": "sweep",
        "label": "The sweep",
        "cmd": "salvo 10.0.0.10 10.0.0.11 -u jdoe -p 'Password123!' -d corp.local",
        "note": (
            "Eight protocols fired at once. Live lines land as each nxc process "
            "answers, then the matrix, then what is still live and what to run next."
        ),
        "transcript": _d("""
        [*] salvo 1.0.0  |  nxc 1.5.0-fake
        [!] LOCKOUT MATH - each protocol against each host is a separate logon,
            and a domain account's counter lives on the DC, so every host counts.
              jdoe                     up to 16 logons (8 protocol-jobs x 2 hosts)
            Default AD lockout threshold is often 5. Check it first:
                nxc smb <DC_IP> -u '' -p '' --pass-pol
            Narrow with -P smb,winrm, or spread it out with --stealth.

        [*] 8 nxc process(es), 6 at a time

        [ADMIN]  smb    10.0.0.10        DC01             jdoe
        [VALID*] smb    10.0.0.11        WEB01            jdoe
        [  ?  ]  winrm  10.0.0.10        DC01             jdoe
        [  ?  ]  winrm  10.0.0.11        WEB01            jdoe
        [  +  ]  ldap   10.0.0.10        DC01             jdoe

        [*] finished in 0s

        ==============================================================================
         corp.local\\jdoe:Password123! [P]
        ==============================================================================
        host                  smb   winrm     wmi   mssql    ldap     rdp     ssh     ftp
        ---------------------------------------------------------------------------------
        10.0.0.10 (DC01)    ADMIN       ?       -       -      ok       -       -       - <
        10.0.0.11 (WEB01)  VALID*       ?       -       -       -       -       -       - <

          ADMIN  = provably administrative (smb admin-share write, mssql sysadmin)
          exec   = code execution, NOT admin - check the smb column before assuming
          ok     = authenticated    VALID* = password correct, this access path blocked
          ?      = cannot tell, retest elsewhere    . = refused    - = no service / no answer
          !CMD   = nxc REJECTED the command salvo built - this cell was never tested
          n/a    = salvo ran NO job here - a fact about salvo, not about the host
          err    = salvo could not run this job - also not a verdict
          <      = this host answered on at least one protocol


        AUTHENTICATION ATTEMPTS ACTUALLY MADE (a '-' never reached auth):
          jdoe                     5
        """),
    },
    {
        "id": "lockout",
        "label": "Lockout guard",
        "cmd": "salvo 10.0.0.10 10.0.0.11 -u jdoe -p 'Password123!' -d corp.local",
        "note": (
            "The same command against an account that locks. The arithmetic is "
            "printed before the first logon, and the first "
            "<code>STATUS_ACCOUNT_LOCKED_OUT</code> kills every remaining job "
            "instead of finishing the sweep."
        ),
        "transcript": _d("""
        [*] salvo 1.0.0  |  nxc 1.5.0-fake
        [!] LOCKOUT MATH - each protocol against each host is a separate logon,
            and a domain account's counter lives on the DC, so every host counts.
              jdoe                     up to 16 logons (8 protocol-jobs x 2 hosts)
            Default AD lockout threshold is often 5. Check it first:
                nxc smb <DC_IP> -u '' -p '' --pass-pol
            Narrow with -P smb,winrm, or spread it out with --stealth.

        [*] 8 nxc process(es), 6 at a time
        """),
    },
    {
        "id": "dry",
        "label": "Dry run",
        "cmd": "salvo 10.0.0.0/29 -u jdoe -p 'Password123!' -d corp.local --dry-run",
        "note": (
            "Every nxc command line it would build, and not one packet sent. Read "
            "the ssh and ftp lines: no <code>-d</code>, because those two nxc "
            "parsers define none."
        ),
        "transcript": _d("""
        [commands that would run - 8 of them]

          nxc -t 25 --no-progress smb 10.0.0.0/29 --smb-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress winrm 10.0.0.0/29 --http-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress wmi 10.0.0.0/29 --rpc-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress mssql 10.0.0.0/29 --mssql-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress ldap 10.0.0.0/29 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress rdp 10.0.0.0/29 --rdp-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress ssh 10.0.0.0/29 --ssh-timeout 15 -u jdoe -p 'Password123!' --continue-on-success
          nxc -t 25 --no-progress ftp 10.0.0.0/29 -u jdoe -p 'Password123!' --continue-on-success
        """),
    },
    {
        "id": "hash",
        "label": "A cell never tested",
        "cmd": "salvo 10.0.0.10 10.0.0.11 -u Administrator -H 31d6cfe0... --local-auth -P smb,winrm,ssh,ftp",
        "note": (
            "You cannot pass-the-hash over ssh or ftp. Those cells read "
            "<code>n/a</code> with the reason printed under the table — never the "
            "<code>-</code> that the legend defines as no service."
        ),
        "transcript": _d("""
        [*] salvo 1.0.0  |  nxc 1.5.0-fake
        [*] hash credentials cannot pass-the-hash over: ssh, ftp - skipping those jobs
        [!] LOCKOUT MATH - each protocol against each host is a separate logon,
            and a domain account's counter lives on the DC, so every host counts.
              Administrator            up to 4 logons (2 protocol-jobs x 2 hosts)
            Default AD lockout threshold is often 5. Check it first:
                nxc smb <DC_IP> -u '' -p '' --pass-pol
            Narrow with -P smb,winrm, or spread it out with --stealth.

        [*] 2 nxc process(es), 6 at a time
        """),
    },
    {
        "id": "cmdfail",
        "label": "A command nxc rejected",
        "cmd": "salvo 10.0.0.10 -u jdoe -p 'Password123!' -d corp.local -P smb,winrm",
        "note": (
            "The failure this tool exists to prevent, forced on purpose. nxc refuses "
            "the command; salvo marks those cells <code>!CMD</code> and asks nxc "
            "which flag it objected to, rather than letting a broken command look "
            "like a closed port."
        ),
        "transcript": _d("""
        [*] salvo 1.0.0  |  nxc 1.5.0-fake
        [*] 2 nxc process(es), 6 at a time


        [*] finished in 0s

        No host produced a result. Nothing here is a verdict:
          !CMD  smb, winrm           nxc exited 2 without producing a single result line - this protocol was never tested

        !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
          2 job(s) never ran - nxc rejected the command salvo built.
          Those cells are marked !CMD. They are NOT a statement about the target.
            smb    jdoe                 exit 2  usage: nxc [-h] ... | nxc: error: unrecognized arguments: -d
            winrm  jdoe                 exit 2  usage: nxc [-h] ... | nxc: error: unrecognized arguments: -d

          asking nxc which flag it objected to:
        """),
    },
    {
        "id": "drift",
        "label": "Drift after an upgrade",
        "cmd": "salvo --check-nxc -P smb,winrm,ldap,ssh",
        "note": (
            "Run this after any NetExec upgrade. salvo reads the installed nxc's own "
            "help and reports where its capability tables no longer agree with it — "
            "so drift surfaces as a failed check instead of a wrong cell in the field."
        ),
        "transcript": _d("""
          protocol   -d     --local-auth  -H     cont   timeout flag
          --------------------------------------------------------------------
          smb        yes    no            yes    yes    --smb-timeout ok
          winrm      yes    yes           yes    yes    --http-timeout ok
          ldap       yes    no            yes    yes    none
          ssh        no     no            no     yes    --ssh-timeout ok

        [!] salvo's tables disagree with your nxc:
              LOCAL_AUTH_CAPABLE is wrong for smb
            Fix the sets at the top of salvo.py before your next run.
        """),
    },
]


# ── Lab 1 · reading the matrix ───────────────────────────────────────
# The grid is the one printed by the recorded sweep above, cell for cell.
# Every glyph carries the nxc line that produced it, what it actually
# proves, and the next command it earns — so the claim that these are four
# different states can be checked rather than believed.

MATRIX_LAB = {
    "cred": "corp.local\\jdoe:Password123!",
    "protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp"],
    # glyph -> slug, so a cell in the grid can address its own explanation
    # without the template having to sanitise "!CMD" or "n/a" into an id.
    "slugs": {
        "ADMIN": "admin", "exec": "exec", "ok": "ok", "VALID*": "blocked",
        "?": "unknown", "-": "none", "n/a": "na", "!CMD": "cmd",
        "LOCK!": "lock", "err": "err",
    },
    # The bucket each verdict falls in, said in words. "valid" is the CSS
    # hook; printing it beside VALID* would read as the same thing, and the
    # whole point of the panel is that they are not.
    "kinds": {
        "valid": "the credential worked",
        "blocked": "correct, and blocked",
        "unknown": "cannot be told apart",
        "none": "about the host",
        "salvo": "about salvo",
    },
    "rows": [
        {"host": "10.0.0.10", "name": "DC01",
         "cells": ["ADMIN", "?", "-", "-", "ok", "-", "-", "-"]},
        {"host": "10.0.0.11", "name": "WEB01",
         "cells": ["VALID*", "?", "-", "-", "-", "-", "-", "-"]},
    ],
    "verdicts": [
        {
            "key": "ADMIN",
            "slug": "admin",
            "kind": "valid",
            "name": "Provably administrative",
            "line": "SMB  10.0.0.10  445  DC01  [+] corp.local\\jdoe:Password123! (Pwn3d!)",
            "means": "On smb, <code>Pwn3d!</code> means nxc wrote to ADMIN$ — real local "
                     "administrator on this host. On mssql it means the sysadmin role. "
                     "Those are the only two cells salvo will call ADMIN.",
            "do": "<code>impacket-psexec  corp.local/jdoe:'Password123!'@10.0.0.10</code>",
        },
        {
            "key": "exec",
            "slug": "exec",
            "kind": "valid",
            "name": "Code execution, not admin",
            "line": "WINRM  10.0.0.25  5985  WEB01  [+] corp.local\\jdoe:Password123! (Pwn3d!)",
            "means": "The same <code>Pwn3d!</code> word, a different fact. On winrm it means "
                     "membership of Remote Management Users, which grants a shell with no "
                     "administrative rights at all. Rendering it as ADMIN puts a false "
                     "privilege level in the report.",
            "do": "<code>evil-winrm -i 10.0.0.25 -u jdoe -p 'Password123!'</code> — and salvo appends <em>NOT local admin here</em> to that very line, because finding it out by watching a privileged read fail is an expensive way to learn it.",
        },
        {
            "key": "ok",
            "slug": "ok",
            "kind": "valid",
            "name": "Authenticated",
            "line": "LDAP  10.0.0.10  389  DC01  [+] corp.local\\jdoe:Password123!",
            "means": "The credential authenticated and nothing further was proven. On ldap "
                     "that is a working directory bind — enough to collect the domain.",
            "do": "<code>nxc ldap 10.0.0.10 -u jdoe -p 'Password123!' --bloodhound -c All --dns-server 10.0.0.10</code>",
        },
        {
            "key": "VALID*",
            "slug": "blocked",
            "kind": "blocked",
            "name": "Password correct, this path closed",
            "line": "SMB  10.0.0.11  445  WEB01  [-] corp.local\\jdoe:Password123! "
                    "STATUS_LOGON_TYPE_NOT_GRANTED",
            "means": "A <code>[-]</code> line, and the password is provably right. This one, "
                     "plus ACCOUNT_DISABLED, PASSWORD_EXPIRED, PASSWORD_MUST_CHANGE and "
                     "logon-hour or workstation restrictions. Two-state tooling files every "
                     "one of them as a failure and throws away access you already hold.",
            "do": "Take it somewhere else. It is listed again by name under the run's <em>NOT A VERDICT</em> block, which exists so a blocked credential cannot be skimmed past as a failure.",
        },
        {
            "key": "?",
            "slug": "unknown",
            "kind": "unknown",
            "name": "Cannot be told apart",
            "line": "WINRM  10.0.0.10  5985  DC01  [-] corp.local\\jdoe:Password123!",
            "means": "winrm refused with no status code. A correct password for an account "
                     "that simply is not in Remote Management Users is byte-identical to a "
                     "wrong one. Calling this failed is a guess printed as a fact.",
            "do": "Retest the credential where the answer is readable — smb, or an ldap bind. Never write it off on this cell alone.",
        },
        {
            "key": "-",
            "slug": "none",
            "kind": "none",
            "name": "No service, no answer",
            "line": "(no line — nxc produced no result for this host and protocol)",
            "means": "The only glyph on this page that is a statement about the target. "
                     "Nothing was listening, or nothing answered in time. Every other "
                     "empty cell is a statement about salvo, and each prints its reason "
                     "under the table.",
            "do": "Nothing to chase — but check <code>--nxc-timeout</code> before believing it over a tunnel. nxc's own default is 2s for smb.",
        },
        {
            "key": "n/a",
            "slug": "na",
            "kind": "salvo",
            "name": "salvo ran no job here",
            "line": "n/a   ssh, ftp   nxc defines no -H here, so a hash cannot be tested "
                    "over this protocol",
            "means": "A fact about salvo, not about the host. Nothing was sent, so no logon "
                     "was spent — and the cell says so instead of leaving a blank that "
                     "renders as <code>-</code>.",
            "do": "Nothing to retest. <code>--json</code> carries the same distinction in a <code>not_run</code> array, so a consumer of the file is not left to infer it from an absence.",
        },
        {
            "key": "!CMD",
            "slug": "cmd",
            "kind": "salvo",
            "name": "nxc rejected the command",
            "line": "smb   jdoe   exit 2   usage: nxc [-h] ... | nxc: error: unrecognized "
                    "arguments: -d",
            "means": "The cell was never tested. A wrapper that builds a wrong command does "
                     "not error visibly — it produces an empty result that reads as a closed "
                     "port. salvo marks it, then asks nxc which flag it objected to.",
            "do": "<code>salvo --check-nxc -P all</code>",
        },
        {
            "key": "LOCK!",
            "slug": "lock",
            "kind": "blocked",
            "name": "Account locked out",
            "line": "SMB  10.0.0.10  445  DC01  [-] corp.local\\jdoe:Password123! "
                    "STATUS_ACCOUNT_LOCKED_OUT",
            "means": "The one result that ends the run. Every remaining nxc process is killed "
                     "immediately rather than finishing the sweep against an account that is "
                     "already locked.",
            "do": "<code>nxc smb &lt;DC_IP&gt; -u '' -p '' --pass-pol</code> — and check it before you point anything at that domain again.",
        },
        {
            "key": "err",
            "slug": "err",
            "kind": "salvo",
            "name": "salvo could not run the job",
            "line": "err   smb   jdoe   <the reason, printed under the table>",
            "means": "A job that died for salvo's own reasons. Also not a verdict, and also "
                     "given its own glyph rather than an empty cell.",
            "do": "Re-run that job. <code>--logdir</code> keeps the raw nxc text either way.",
        },
    ],
}


# ── Lab 2 · the lockout arithmetic ───────────────────────────────────
# The same multiplication salvo prints before it spends a single logon,
# with the inputs left open. Protocol order matches salvo's own.

LOCKOUT_LAB = {
    "protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp"],
    "default_protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp"],
    "hosts": 8,
    "creds": 1,
    # salvo warns for every account over the threshold, not just the worst
    # one, so the lab needs more than one name to put in the column.
    "accounts": ["jdoe", "svc_sql", "backupadm", "helpdesk", "svc_iis", "wsus_svc"],
    "threshold": 5,
    "note": "The default Active Directory lockout threshold is often 5, and a domain "
            "account's counter lives on the domain controller no matter which member "
            "server you touched. salvo prints this before the run, reports what the run "
            "actually cost after it, and kills every remaining job on the first real "
            "lockout.",
}


# ── Lab 3 · the command builder ──────────────────────────────────────
# A transcription of the capability tables at the top of salvo.py, so the
# page builds the same nxc command lines `salvo --dry-run` would print.
# These are the tables `salvo --check-nxc` verifies against the installed
# NetExec after an upgrade.

BUILDER = {
    "protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp", "nfs", "vnc"],
    "default_protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp"],

    # nxc sub-parsers that define -d/--domain. ssh, ftp, nfs and vnc have no
    # domain concept at all; passing -d makes argparse exit before a packet.
    "domain_capable": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp"],

    # ldap is the trap: it takes -d but not --local-auth, because a directory
    # bind is inherently domain-scoped.
    "local_auth_capable": ["smb", "winrm", "wmi", "mssql", "rdp"],

    # -H / pass-the-hash. You cannot pass-the-hash over ssh, ftp, nfs or vnc.
    "hash_capable": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp"],

    # nxc's global --timeout is deprecated upstream and silently ignored, so
    # salvo emits the per-protocol flag. ldap, ftp and vnc define none, and
    # run at nxc's own default.
    "timeout_flag": {
        "smb": "--smb-timeout",
        "winrm": "--http-timeout",
        "wmi": "--rpc-timeout",
        "mssql": "--mssql-timeout",
        "rdp": "--rdp-timeout",
        "ssh": "--ssh-timeout",
        "nfs": "--nfs-timeout",
    },

    "defaults": {"threads": 25, "timeout": 15, "parallel": 6},

    # The builder opens on exactly these inputs, and the output below is the
    # real `salvo --dry-run` for them — the same eight lines the recorded dry
    # run above prints. So the page starts from verified output rather than
    # from its own reimplementation, and only diverges once you change
    # something.
    "seed": {
        "targets": "10.0.0.0/29",
        "user": "jdoe",
        "secret": "Password123!",
        "is_hash": False,
        "domain": "corp.local",
        "local_auth": False,
        "protocols": ["smb", "winrm", "wmi", "mssql", "ldap", "rdp", "ssh", "ftp"],
        "preset": "",
    },
    "seed_output": _d("""
        [commands that would run - 8 of them]

          nxc -t 25 --no-progress smb 10.0.0.0/29 --smb-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress winrm 10.0.0.0/29 --http-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress wmi 10.0.0.0/29 --rpc-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress mssql 10.0.0.0/29 --mssql-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress ldap 10.0.0.0/29 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress rdp 10.0.0.0/29 --rdp-timeout 15 -u jdoe -p 'Password123!' -d corp.local --continue-on-success
          nxc -t 25 --no-progress ssh 10.0.0.0/29 --ssh-timeout 15 -u jdoe -p 'Password123!' --continue-on-success
          nxc -t 25 --no-progress ftp 10.0.0.0/29 -u jdoe -p 'Password123!' --continue-on-success
    """),

    # The advisory lines salvo prints when a protocol cannot take the
    # credential it was handed. Reproduced verbatim so the builder says what
    # the tool says.
    "notes": {
        "hash_skip": "[*] hash credentials cannot pass-the-hash over: {} - skipping those jobs",
        "ldap_local": "[*] ldap has no --local-auth in nxc (a bind is always domain-scoped) - "
                      "skipping the local-auth ldap job rather than spending a logon on it",
        "vnc": "[*] note: nxc vnc authenticates with a password only, the username is ignored",
        "stealth": "[*] --stealth: 1 process(es) at a time, 1 nxc thread(s), jitter 3-7, "
                   "5s between jobs.",
        "domain_drop": "[!] -d will NOT be sent to {} - those nxc parsers define no domain "
                       "argument, so the bare username is tested there. A different question "
                       "from the domain columns.",
    },
    "presets": {
        "slow": {"parallel": 3, "threads": 5, "timeout": 30},
        "stealth": {"parallel": 1, "threads": 1, "timeout": 30, "jitter": "3-7", "job_delay": 5},
    },
}
