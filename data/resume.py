"""Single source of truth for every piece of content on the site.

Templates read from RESUME only, so updating the portfolio means editing this
file — no HTML changes required.

The one thing that lives elsewhere is `data/demos.py`: the recorded terminal
sessions on the salvo page, the estate its terminal answers for, and the nxc
capability tables transcribed from salvo itself. That is captured output and
transcribed code rather than written copy, so it is kept apart from the prose
and reaches the templates through RESUME["salvo"] like everything else.
"""

from data.demos import BOOT, ESTATE, EXAMPLES, NXC, OPENING, VERDICTS

RESUME = {
    "profile": {
        "name": "Aashiq Shaikh",
        "tagline": "Penetration Tester",
        "discipline": "Active Directory · Linux · Infrastructure",
        "location": "Navi Mumbai, India",
        "email": "aashiqoffortune@gmail.com",
        "github": "https://github.com/aashiqoffortune-hash",
        "github_handle": "aashiqoffortune-hash",
        "meta_description": (
            "Aashiq Shaikh — penetration tester working Active Directory, Linux and "
            "infrastructure. Two years owning the RHEL, HSM and PKI stack behind payment "
            "platforms for 30+ Indian banks, now applied to the offensive side. RHCE."
        ),
        # The single sentence the whole page is built to earn.
        "thesis": (
            "I spent two years as sole owner of the authentication, HSM and PKI "
            "infrastructure behind payment platforms for 30+ Indian banks."
        ),
        "thesis_turn": "Now I break into the same class of systems.",
        "lede": [
            "Offensive security practitioner working Windows, Linux and Active Directory "
            "estates end to end — unauthenticated external position through to domain "
            "compromise, documented to commercial penetration test report standard.",
            "The defensive half is not background colour. I hardened these stacks to CIS "
            "Benchmark under RBI and UIDAI mandate, ran the HSMs that held the keys, and "
            "carried the pager for them. I know how the blue side builds it, which is "
            "usually where it breaks.",
        ],
    },

    # Headline numbers. Every one is drawn from production work or shipped code.
    "stats": [
        {"value": "30+", "label": "Indian banks on infrastructure I owned"},
        {"value": "10+", "label": "Tier-1 deployments, SBI / NPCI / BoB / IPPB"},
        {"value": "0", "label": "Critical incidents in two years on call"},
        {"value": "3", "label": "Upstream defects root-caused in NetExec"},
    ],

    # The engagement, in the order an engagement actually runs. This is the
    # spine of the page: real sequence, not decorative numbering.
    "chain": [
        {
            "phase": "Recon & Initial Access",
            "stage": "EXTERNAL",
            "summary": (
                "From an unauthenticated external position to first shell. Service "
                "enumeration and version fingerprinting to establish what is actually "
                "exposed, then CVE-driven exploitation of the off-the-shelf software "
                "that turns up in the fingerprint."
            ),
            "detail": (
                "Web application footholds are the common path: SQL injection escalated "
                "to remote code execution, local file inclusion chained with log "
                "poisoning, upload filter bypass to webshell, and command injection."
            ),
            "tags": ["Nmap", "ffuf", "gobuster", "Burp Suite", "sqlmap", "CVE triage"],
        },
        {
            "phase": "Privilege Escalation",
            "stage": "LOCAL ROOT",
            "summary": (
                "First shell is rarely the account that matters. Windows: unquoted "
                "service paths, weak service permissions, and token impersonation with "
                "PrintSpoofer where SeImpersonate is present."
            ),
            "detail": (
                "Linux: SUID and PATH hijacking, sudo misconfiguration, cron abuse, and "
                "tar wildcard injection. The escalation is chosen from what enumeration "
                "actually returned, not run down a checklist."
            ),
            "tags": ["PrintSpoofer", "SeImpersonate", "SUID / PATH", "sudo", "cron", "tar wildcard"],
        },
        {
            "phase": "Active Directory",
            "stage": "DOMAIN",
            "summary": (
                "Attack path analysis before attack execution — BloodHound and SharpHound "
                "to find the edge that actually reaches Domain Admin, rather than "
                "grinding every reachable host."
            ),
            "detail": (
                "Kerberos abuse through Kerberoasting and AS-REP roasting; ACL and ACE "
                "exploitation via ForceChangePassword and GenericAll; DCSync once the "
                "replication right is in hand."
            ),
            "tags": ["BloodHound", "Rubeus", "Impacket", "Kerberoasting", "AS-REP", "DCSync", "GenericAll"],
        },
        {
            "phase": "Credential Access",
            "stage": "HARVEST",
            "summary": (
                "Post-exploitation credential harvest: LSA secrets extraction from "
                "registry hives, autologon credential recovery, and pass-the-hash lateral "
                "movement with the material that comes back."
            ),
            "detail": (
                "Spraying is done against the lockout policy, not through it — measured "
                "attempt counts, deliberate spacing, and awareness of what each protocol "
                "charges against the account before it is sent."
            ),
            "tags": ["Mimikatz", "LSA secrets", "Pass-the-hash", "Hashcat", "NetExec"],
        },
        {
            "phase": "Pivoting & Lateral Movement",
            "stage": "INTERNAL",
            "summary": (
                "Segmented networks are the point of the exercise. Ligolo-ng and Chisel "
                "to reach non-routable internal subnets, then authenticated enumeration "
                "and controlled credential spraying through the established tunnel."
            ),
            "detail": (
                "Across SMB, WinRM, LDAP, MSSQL, RDP, SSH and FTP — each protocol tuned "
                "separately, because each one fails differently through a tunnel."
            ),
            "tags": ["Ligolo-ng", "Chisel", "SMB", "WinRM", "LDAP", "MSSQL", "RDP", "SSH", "FTP"],
        },
        {
            "phase": "Reporting",
            "stage": "DELIVERABLE",
            "summary": (
                "The engagement is worth what the report is worth. Full-length reports "
                "authored in self-hosted SysReptor: attack narrative, evidenced "
                "reproduction steps, business impact, prioritised remediation."
            ),
            "detail": (
                "Written for two audiences in one document — an engineer who has to "
                "reproduce the finding, and an executive who has to fund the fix."
            ),
            "tags": ["SysReptor", "Attack narrative", "Business impact", "Remediation"],
        },
    ],

    "projects": [
        {
            "name": "salvo",
            "kind": "Credential-spray orchestrator",
            "lang": "Python",
            "summary": (
                "One credential fanned across every NetExec protocol at once, read "
                "back as a single matrix with an honest verdict in each cell — built "
                "to stop live access being lost to tooling that only knows worked or "
                "failed, and to count every logon against lockout before it spends it."
            ),
            "findings_intro": "",
            "findings": [],
            "footer": "",
            "case": True,
            "tags": ["Python", "NetExec", "OPSEC", "Concurrency"],
        },
        {
            "name": "Offensive Decision Reference",
            "kind": "Working reference",
            "lang": "350,000 characters",
            "summary": (
                "Indexed by observed condition rather than by tool or exploit name. Each "
                "entry maps a concrete signal — a privilege present in a token, a "
                "BloodHound edge, a Kerberos error code, a host presenting two interfaces "
                "in different subnets — to the action it warrants and the failure mode "
                "that most often wastes time on it."
            ),
            "findings_intro": "",
            "findings": [],
            "footer": (
                "Built to compress the gap between enumeration output and attack decision "
                "under a time constraint."
            ),
            "tags": ["Methodology", "Active Directory", "Research"],
        },
        {
            "name": "rsg-kali",
            "kind": "Installer and wrapper",
            "lang": "Shell",
            "summary": "Packaged reverse shell payload generation for Kali Linux.",
            "findings_intro": "",
            "findings": [],
            "footer": "",
            "tags": ["Kali Linux", "Packaging"],
        },
    ],

    # Engineering writeups — claim, then the evidence for it, then the artifact
    # in the code that carries it. Every artifact reference is a real construct
    # in salvo.py, verifiable in the repository.
    # The case for salvo, in the builder's voice — why it exists, what it
    # does, and the evidence behind each claim it makes. Written to be read
    # by someone deciding whether the tool is worth their time.
    "salvo": {
        "name": "salvo",
        "url": "https://github.com/aashiqoffortune-hash/salvo",
        "tagline": "One credential, every NetExec protocol, one honest matrix.",
        "stack": "Python, standard library only. No dependency beyond NetExec itself.",

        # What ships, rather than what it does. A tool other people can install
        # is a different claim from a script in a repository, and the
        # difference is checkable from outside — so it is stated in the
        # numbers that can be checked.
        "ships": {
            "install": "pipx install salvo-nxc",
            "note": (
                "Published as <code>salvo-nxc</code> — <code>salvo</code> on PyPI is an "
                "unrelated HTTP load tester by another author. The installed command is "
                "still <code>salvo</code>."
            ),
            "facts": [
                {"k": "146", "v": "tests, stdlib unittest — no pip, no virtualenv"},
                {"k": "3.8 → 3.14", "v": "Python versions the suite runs on in CI"},
                {"k": "0", "v": "dependencies beyond NetExec, asserted by a test"},
                {"k": "PyPI", "v": "released by tag, published through Trusted Publishing"},
            ],
        },

        # What the page's terminal runs on: the estate it answers for, nxc's
        # capability tables, the legend, the runnable examples `help` offers,
        # and one real recorded run for the no-JavaScript case. See
        # data/demos.py.
        "estate": ESTATE,
        "nxc": NXC,
        "verdicts": VERDICTS,
        "examples": EXAMPLES,
        "boot": BOOT,
        "opening": OPENING,

        # Why it exists — the problem, stated the way it actually bites.
        "problem": [
            "NetExec tests one protocol per invocation. Validating a single "
            "credential properly means running it eight times — SMB, WinRM, WMI, "
            "MSSQL, LDAP, RDP, SSH, FTP — and reading eight separate scrollbacks. "
            "Point that at a subnet with a handful of credentials and it is "
            "hundreds of windows to eyeball, by hand, under a clock.",
            "The thing you are reading back is lossy. A password that is correct "
            "but blocked looks identical to a wrong one, so live access gets filed "
            "as failure and thrown away. And a single word — <code>Pwn3d!</code> — "
            "is printed for conditions as different as write access to a domain "
            "controller and permission to open a shell as a nobody. I built salvo "
            "because credential validation at scale is exactly where real access "
            "goes missing, lost to tooling that only knows two answers.",
        ],

        # What it does — the short version, three moves.
        "does": [
            {
                "head": "Fans one credential across every protocol at once",
                "body": "Runs the eight protocol jobs concurrently and collapses "
                        "eight scrollbacks into a single matrix — one row per host, "
                        "one column per protocol, read top to bottom in one look.",
            },
            {
                "head": "Prints an honest verdict in every cell",
                "body": "Not worked-or-failed. Authenticated, provably "
                        "administrative, blocked-but-valid, and genuinely-unknown are "
                        "four different states, and salvo keeps them apart instead of "
                        "flattening them into a lie.",
            },
            {
                "head": "Counts the cost before it spends it",
                "body": "Every protocol against every host is a logon against a "
                        "lockout counter you cannot see. salvo does the arithmetic up "
                        "front, reports what it actually cost, and stops the moment a "
                        "real lockout appears.",
            },
            {
                "head": "Picks up where it stopped, for free",
                "body": "With <code>--state</code>, a repeat run skips jobs already "
                        "answered and merges their results back in, so the matrix stays "
                        "complete even though no single process ever saw all of it. "
                        "That is not only time saved — every skipped job is an "
                        "authentication attempt not made against a lockout counter.",
            },
        ],

        # The claims salvo makes, each with the evidence that the problem is
        # real and that salvo answers it. This is the heart of the page.
        "claims": [
            {
                "id": "thrown-away",
                "claim_short": "Nothing thrown away",
                "claim": "A provably correct credential should never be filed as a failure.",
                "evidence": (
                    "A login can fail for reasons that mean the password was right: "
                    "<code>STATUS_LOGON_TYPE_NOT_GRANTED</code>, account disabled, "
                    "password expired, logon-hour and workstation restrictions. "
                    "Two-state tooling records all of them as failed, and you lose a "
                    "credential you already own. salvo marks these "
                    "<code>VALID*</code> and lists every one under a NOT A VERDICT "
                    "block — still live, named, retestable from somewhere else."
                ),
            },
            {
                "id": "pwn3d",
                "claim_short": "Pwn3d disambiguated",
                "claim": "\u201cPwn3d!\u201d is not one thing, and treating it as one puts a false privilege level in the report.",
                "evidence": (
                    "On SMB, <code>Pwn3d!</code> means write access to ADMIN$ — real "
                    "local admin. On WinRM it means the account is in Remote "
                    "Management Users, which grants a shell with no admin rights at "
                    "all. salvo renders the first <code>ADMIN</code> and the second "
                    "<code>exec</code>, and when nothing proved admin on a host it "
                    "says so in words rather than leaving it to be assumed."
                ),
            },
            {
                "id": "lockout",
                "claim_short": "Lockout counted",
                "claim": "Every spray is a logon against a counter you can\u2019t see, so the tool should count for you.",
                "evidence": (
                    "Eight protocols across N hosts is up to 8N logons, and a domain "
                    "account\u2019s lockout counter lives on the domain controller "
                    "no matter which member server you touched. The default AD "
                    "threshold is often five. salvo prints the lockout math before it "
                    "starts, reports the attempts actually made after, and kills the "
                    "whole run on the first <code>STATUS_ACCOUNT_LOCKED_OUT</code> "
                    "instead of finishing the sweep."
                ),
            },
            {
                "id": "silent-lie",
                "claim_short": "No silent lies",
                "claim": "A wrapper that builds the wrong command doesn\u2019t error — it lies to you as a closed port.",
                "evidence": (
                    "ssh, ftp, nfs and vnc define no <code>-d</code> flag; pass one "
                    "and NetExec\u2019s parser exits before a packet is sent, and the "
                    "empty result renders as <code>-</code> — indistinguishable from "
                    "\u201cnothing listening.\u201d LDAP takes <code>-d</code> but "
                    "not <code>--local-auth</code>, and passing it burns a logon. The "
                    "global <code>--timeout</code> is deprecated and silently ignored. "
                    "I found each of these by reading NetExec\u2019s source, encoded "
                    "them in capability tables, and made the tool revalidate itself "
                    "against whatever NetExec is installed."
                ),
            },
            {
                "id": "scope",
                "claim_short": "Scope enforced",
                "claim": "“It only authenticates” is worth nothing as a promise. It has to be enforced, and the enforcement has to be testable.",
                "evidence": (
                    "salvo never passes <code>-x</code>, <code>-X</code>, "
                    "<code>-M</code>, <code>--sam</code>, <code>--lsa</code>, "
                    "<code>--ntds</code> or any other execution, dumping or collection "
                    "flag to NetExec. Every command is checked against an exhaustive "
                    "allowlist immediately before it spawns, and an unrecognised flag "
                    "aborts the run rather than being sent. The check reads the whole "
                    "line rather than the positions flags are expected in — a username "
                    "or password beginning with <code>-</code> lands exactly where a "
                    "flag’s value goes, which is where a forbidden one would "
                    "otherwise ride along unseen. The test suite asserts it across "
                    "every protocol and every credential shape, reading salvo’s "
                    "own lists rather than a copy of them, so a flag added later fails "
                    "CI until someone consciously allows it. That matters under "
                    "restricted-tooling rules, where what a tool <em>can</em> do is the "
                    "question being asked."
                ),
            },
        ],

        # Evidence the reader can run themselves — the strongest kind.
        "run": [
            {"cmd": "salvo 192.168.1.0/24 -u jdoe -p 'Password1!' -d corp.local --dry-run",
             "note": "prints every nxc command it would run, and runs nothing"},
            {"cmd": "salvo --check-nxc -P all",
             "note": "diffs salvo\u2019s capability tables against your installed NetExec"},
            {"cmd": "salvo --selftest",
             "note": "proves the output parser still agrees with NetExec\u2019s format"},
            {"cmd": "salvo --scope",
             "note": "prints the flags salvo may and may not send \u2014 from the lists that gate it, not a copy"},
        ],
        "close": (
            "Don\u2019t take the claims on faith. <code>--dry-run</code> shows you "
            "exactly what it would send and <code>--scope</code> prints the lists that "
            "decide it, both read out of the code that enforces them. "
            "<code>--check-nxc</code> and <code>--selftest</code> are meant to run "
            "after any NetExec upgrade, so drift shows up as a failed check rather "
            "than a wrong answer in the field."
        ),
    },

    # ── Sample deliverable ────────────────────────────────────────────
    # A demonstration report against a fictional environment, and labelled
    # as one on the page. Real client work is confidential and lab material
    # belongs to the vendor whose lab it is, so neither gets published —
    # which leaves a written sample as the only honest way to show what the
    # deliverable actually looks like. Every host, address, account and
    # finding below is invented. The addresses are RFC 1918 and the domain
    # uses the reserved .internal suffix, so nothing here resolves anywhere.
    "case_study": {
        "client": "A mid-market general insurer",
        "profile": "~1,200 staff · two data centres · hybrid AD estate",
        "engagement": "Internal network penetration test",
        "window": "10 working days, plus a 2-day retest",
        "standard": "CVSS v3.1 · retest included · authored in SysReptor",
        "lede": (
            "Client reports are confidential and lab material belongs to the vendor "
            "whose lab it is, so neither is published here. What follows is a written "
            "sample against an invented environment — the same structure, severity "
            "reasoning and language a real deliverable carries, with nothing real in it."
        ),

        # The findings table, as it appears on the contents page.
        "findings": [
            {"id": "F-01", "sev": "Critical", "cvss": "9.8",
             "title": "Unauthenticated remote code execution on an internet-facing file transfer appliance",
             "impact": "Full compromise of a DMZ host holding client claim documents.",
             "status": "Resolved"},
            {"id": "F-02", "sev": "High", "cvss": "8.1",
             "title": "Backup share readable by all domain users exposes a service account credential",
             "impact": "Any authenticated user reaches an account with rights across the estate.",
             "status": "Resolved"},
            {"id": "F-03", "sev": "High", "cvss": "7.5",
             "title": "Service account with a Kerberos-requestable ticket and a crackable password",
             "impact": "Offline recovery of a credential holding privileged group membership.",
             "status": "Resolved"},
            {"id": "F-04", "sev": "Medium", "cvss": "6.5",
             "title": "SMB signing not enforced on domain member servers",
             "impact": "Authentication relayable between hosts by an attacker already on the LAN.",
             "status": "Risk accepted"},
            {"id": "F-05", "sev": "Medium", "cvss": "5.3",
             "title": "Password policy permits an eight-character minimum",
             "impact": "Materially shortens offline cracking time for every recovered hash.",
             "status": "Resolved"},
            {"id": "F-06", "sev": "Low", "cvss": "3.7",
             "title": "Deprecated TLS cipher suites on internal management interfaces",
             "impact": "Weakens transport for administrative sessions on the management VLAN.",
             "status": "Open"},
        ],

        # One finding written out in full, so the prose is visible rather
        # than described. F-02 because it is the one that shows a chain:
        # a finding that reads as low severity in isolation and is not.
        "worked": {
            "id": "F-02",
            "sev": "High",
            "cvss": "8.1",
            "vector": "CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N",
            "title": "Backup share readable by all domain users exposes a service account credential",
            "affected": "FS-02.corp.internal (10.40.12.24) · share BACKUP$",
            "sections": [
                {"head": "Summary",
                 "body": "A file share on FS-02 permits read access to the built-in Domain "
                         "Users group. The share holds nightly configuration exports from the "
                         "job scheduling platform, and one of those exports contains the "
                         "plaintext credential the scheduler uses to authenticate to member "
                         "servers. Any account on the domain — including a temporary "
                         "contractor account, or any account recovered by phishing — can read "
                         "it."},
                {"head": "Why this is High and not Medium",
                 "body": "The share permission on its own is an information disclosure. The "
                         "severity comes from what the disclosed credential holds: the "
                         "scheduler account is a member of a group granted local administrator "
                         "on 40 of 58 member servers, so a single unprivileged read moves an "
                         "attacker from one authenticated session to administrative access "
                         "across most of the server estate. The scope metric is set to Changed "
                         "for that reason — the impact lands outside the component that "
                         "carries the weakness."},
                {"head": "Reproduction",
                 "body": "Enumerated readable shares from a standard domain user account, "
                         "identified BACKUP$ as readable, and located the credential in a "
                         "configuration export within it. Authenticating as the disclosed "
                         "account against a sample of three member servers returned "
                         "administrative access on all three. Reproduction steps, the exact "
                         "file path and the evidence captures are in the report body; they are "
                         "not repeated here."},
                {"head": "Business impact",
                 "body": "The claims processing and document management servers are both "
                         "inside the affected set. An attacker with any foothold on the domain "
                         "reaches the systems holding policyholder data without needing a "
                         "second vulnerability, and does so using a valid credential, which "
                         "makes the activity difficult to separate from normal scheduler "
                         "traffic in the logs."},
                {"head": "Remediation",
                 "body": "Restrict the share to the backup operators group and remove Domain "
                         "Users. Rotate the scheduler credential, and move it to a group "
                         "managed service account so it is no longer stored in an exported "
                         "file. Reduce the scheduler's local administrator rights to the "
                         "servers that genuinely require them. The first two are configuration "
                         "changes measured in hours; the third needs a review of which jobs "
                         "touch which hosts."},
                {"head": "Retest",
                 "body": "Re-tested on day 2 of the retest window. Domain Users no longer has "
                         "read access, the credential has been rotated and migrated, and "
                         "authenticating as the previous credential fails on all three sampled "
                         "servers. The rights reduction was in progress and tracked as a "
                         "follow-up item rather than closed."},
            ],
        },

        # What every report carries, whatever the engagement found.
        "carries": [
            ("Executive summary", "Written for the person who signs off the budget, not the "
                                  "person who runs the fix. Risk in business terms, no tool names."),
            ("Attack narrative", "The route through the estate as one continuous story, so a "
                                 "reader can see how three medium findings became a critical one."),
            ("Evidenced reproduction", "Every finding reproducible from the report alone, with "
                                       "captures taken at the point of proof."),
            ("Prioritised remediation", "Ordered by risk reduced per hour of work, not by severity "
                                        "label — the two are not the same list."),
            ("Retest", "A second pass against the fixes, with findings closed, partially closed "
                       "or still open stated plainly."),
        ],
    },

    "professional_experience": [
        {
            "role": "Linux System Administrator / Infrastructure Engineer",
            "company": "Integra Micro Systems Pvt. Ltd.",
            "period": "Feb 2023 — Dec 2024",
            "location": "Mumbai / Bengaluru",
            "lede": (
                "Sole Mumbai-based infrastructure engineer for iMFAST, a financial "
                "inclusion platform serving 30+ Indian banks and PSUs across 10+ Tier-1 "
                "deployments including State Bank of India, NPCI, Bank of Baroda, IPPB "
                "and BPCL."
            ),
            "points": [
                {
                    "head": "Owned what an attacker reaches for first",
                    "body": "Authentication gateways, MFA, eKYC, middleware and API gateways, "
                            "and AePS transaction paths — hardened to CIS Benchmark and operated "
                            "under UIDAI and RBI mandate.",
                },
                {
                    "head": "Ran the cryptographic backbone",
                    "body": "Thales Luna HSM infrastructure — partitioning, HA pairs, key "
                            "lifecycle management, network HSM clients — backing every "
                            "cryptographic operation for MFA, Aadhaar Data Vault encryption, "
                            "eKYC signing and transaction security.",
                },
                {
                    "head": "Hardened the production estate",
                    "body": "RHEL 8/9 running Nginx, RabbitMQ, Node.js, KeyDB and MySQL/MariaDB "
                            "under real-time authentication load, with the observability stack "
                            "(Prometheus, Grafana, ELK, Zabbix) and HA storage and networking "
                            "built to bank audit and uptime requirements.",
                },
                {
                    "head": "Automated the audit",
                    "body": "Bash and Python tooling for security auditing of Linux middleware "
                            "stacks, holding continuous audit readiness against RBI and NPCI "
                            "frameworks.",
                },
                {
                    "head": "Carried it without a critical incident",
                    "body": "Zero critical incidents attributable to configuration or security "
                            "failure across two years of 24/7 on-call ownership of national "
                            "banking infrastructure.",
                },
            ],
        },
    ],

    "skills": [
        {
            "group": "Offensive Tooling",
            "items": [
                "Nmap", "BloodHound / SharpHound", "Impacket", "NetExec", "Mimikatz",
                "Rubeus", "PowerView", "evil-winrm", "PrintSpoofer", "Burp Suite",
                "sqlmap", "ffuf", "gobuster", "Hydra", "Hashcat", "Metasploit",
                "Ligolo-ng", "Chisel", "SysReptor",
            ],
        },
        {
            "group": "Attack Techniques",
            "items": [
                "AD attack path analysis", "Kerberos abuse", "ACL / ACE exploitation",
                "Lateral movement", "Windows privilege escalation",
                "Linux privilege escalation", "Pivoting and tunnelling",
                "Credential harvesting", "Credential spraying",
                "Web application exploitation", "Post-exploitation", "Reporting",
            ],
        },
        {
            "group": "Enterprise Linux",
            "items": [
                "RHEL 8/9", "CentOS", "Ubuntu", "Kernel hardening", "SELinux", "PAM",
                "firewalld / iptables", "LVM / RAID", "systemd", "HA clustering",
            ],
        },
        {
            "group": "Crypto & Compliance",
            "items": [
                "Thales Luna HSM", "PKI", "Key lifecycle management", "CIS Benchmarks",
                "ISO 27001", "PCI DSS", "RBI / UIDAI / NPCI",
            ],
        },
        {
            "group": "Infrastructure",
            "items": [
                "TCP/IP", "DNS", "DHCP", "VPN", "SAN / NFS", "Docker", "VMware",
                "Ansible", "Terraform", "GitLab CI/CD", "AWS (EC2, IAM, S3)", "Azure",
            ],
        },
        {"group": "Scripting", "items": ["Python", "Bash", "PowerShell"]},
        {
            "group": "Platforms",
            "items": ["Kali Linux", "Windows Server 2016 / 2019", "Windows 10 / 11"],
        },
    ],

    # Every entry here is independently verifiable. That is the point of the section.
    "credentials": [
        {
            "name": "Red Hat Certified Engineer",
            "abbr": "RHCE",
            "issuer": "Red Hat",
            "issued": "14 August 2024",
            "cert_id": "220-172-050",
            "verify": "https://www.credly.com/badges/a78c122a-86d8-4848-bbd7-166daabc1835",
            "pdf": "files/RHCE-certificate.pdf",
        },
        {
            "name": "Red Hat Certified System Administrator",
            "abbr": "RHCSA",
            "issuer": "Red Hat",
            "issued": "02 January 2023",
            "cert_id": "220-172-050",
            "verify": "https://www.credly.com/badges/60d9ce86-e4ab-46d8-b235-fa0d14a3ad3a",
            "pdf": "files/RHCSA-certificate.pdf",
        },
    ],

    "awards": [
        {
            "name": "Most Promising Talent",
            "issuer": "Integra Group",
            "issued": "10 February 2024",
            "note": "Certificate of Excellence, signed by the Chairman, within the first year.",
        },
    ],

    "education": [
        {
            "degree": "Bachelor of Commerce",
            "institution": "University of Mumbai",
            "period": "2019 — 2022",
            "detail": "CGPI 7.10 / 10",
        },
    ],

    # ── Engagements ───────────────────────────────────────────────────
    # The commercial page. The portfolio answers "can he do it"; this
    # answers "what does it cost and when can you start", which is the
    # question that actually has money attached to it.
    #
    # Prices are held here as paired strings rather than numbers because
    # they are copy, not arithmetic — nothing on the page computes with
    # them, and the currency switch is a straight substitution.
    "engagements": {
        "lede": (
            "Fixed scope, fixed price, dates agreed before anything starts. No hourly "
            "rate that grows, and no quote that arrives after the work."
        ),

        # Why anyone is reading this page at all. Nobody buys a penetration
        # test because they want one — they buy one because something is
        # blocked, and naming the blockage is what makes the page land.
        "triggers": [
            {
                "tag": "Deadline",
                "head": "An audit or regulator is asking",
                "body": "An RBI, NPCI or UIDAI expectation, an ISO 27001 or PCI DSS cycle, "
                        "or an annual test you have put off. You need a report with "
                        "evidence and a retest, not a scanner export with a tool’s logo "
                        "on the cover.",
            },
            {
                "tag": "Revenue",
                "head": "A customer’s security review is holding a contract",
                "body": "An enterprise buyer sent a questionnaire and asked for your most "
                        "recent penetration test. The deal does not move until you produce "
                        "one. This is the most expensive kind of blocked, and the easiest "
                        "to unblock.",
            },
            {
                "tag": "Exposure",
                "head": "You do not know what is exposed",
                "body": "You shipped fast, the estate grew, staff left with access, and "
                        "nobody has looked from the outside in. You want the honest "
                        "version before somebody else finds it and tells you on their "
                        "own terms.",
            },
        ],

        "packages": [
            {
                "id": "perimeter",
                "flag": "Entry engagement",
                "name": "Perimeter Review",
                "who": "Everything reachable from the internet without credentials — what "
                       "an attacker sees before they have anything at all.",
                "subject": "Perimeter Review",
                "inr": "₹45,000",
                "usd": "$650",
                "meta": "4 working days · report + 1 retest",
                "featured": False,
                "items": [
                    "External attack surface discovery and service fingerprinting",
                    "Exposed panels, forgotten hosts, stale DNS and subdomain takeover checks",
                    "CVE triage against what is <strong>actually running</strong>, verified by hand rather than taken from a scanner’s guess",
                    "TLS posture, authentication exposure and credential-stuffing surface",
                    "Full written report with prioritised remediation",
                    "One retest pass once the fixes are in",
                ],
            },
            {
                "id": "appinfra",
                "flag": "Most engagements land here",
                "name": "Application &amp; Infrastructure",
                "who": "The engagement that satisfies an auditor or an enterprise "
                       "customer’s security review. The application plus the "
                       "infrastructure behind it.",
                "subject": "Application and Infrastructure VAPT",
                "inr": "₹1,45,000",
                "usd": "$1,950",
                "meta": "10 working days · report + retest + readout",
                "featured": True,
                "items": [
                    "Everything in Perimeter Review",
                    "Authenticated <strong>and</strong> unauthenticated application testing — injection, access control, authentication and session handling, business logic",
                    "Privilege escalation and horizontal access testing across user roles",
                    "API testing, including authorisation on every exposed method",
                    "Server and service hardening reviewed against CIS Benchmark",
                    "<strong>Attack narrative</strong> — how findings chain, not only a list of them",
                    "CVSS v3.1 scoring, executive summary, evidenced reproduction",
                    "Retest pass and a live remediation call with your engineers",
                ],
            },
            {
                "id": "internal",
                "flag": "Full estate",
                "name": "Internal &amp; Active Directory",
                "who": "Assumed breach. One foothold inside, and the question of how far "
                       "it reaches — the test that reflects how compromises actually run.",
                "subject": "Internal and Active Directory assessment",
                "inr": "₹2,75,000",
                "usd": "$3,600",
                "meta": "15 working days · report + retest + readout",
                "featured": False,
                "items": [
                    "Assumed-breach assessment from a standard domain user account",
                    "Attack path analysis — the edge that actually reaches Domain Admin, mapped before anything is executed",
                    "Kerberos abuse, ACL and ACE exploitation, delegation review",
                    "Credential hygiene: password policy under real cracking, service account exposure, reused local administrator",
                    "Segmentation validated by <strong>pivoting through it</strong>, not by reading the firewall rules",
                    "Spraying done <strong>against</strong> the lockout policy rather than through it — measured, spaced, and counted before it is spent",
                    "Full report, retest pass, and an executive readout",
                ],
            },
        ],

        # The commercial terms, stated on the page rather than discovered in
        # a contract. Every one of these exists to remove a question that
        # would otherwise cost an email round trip.
        "terms": [
            "Scope larger than these, or somewhere in between? Send the shape of the estate and a fixed quote follows within 24 hours.",
            "Remediation advisory, hardening and follow-up support: ₹18,000 / $240 per day.",
            "40% to book the dates, 60% on delivery of the report.",
            "NDA before scoping. Written authorisation naming the in-scope assets before any testing begins.",
        ],

        "steps": [
            {"head": "Scoping call",
             "body": "Twenty minutes. What you run, what you are worried about, and the "
                     "deadline you are working to. No charge and no obligation.",
             "when": "Day 0 · free"},
            {"head": "Fixed quote and dates",
             "body": "A written scope, a fixed price, and the exact working days it will "
                     "run. If the scope changes later the price is re-agreed before "
                     "anything is done — never billed after.",
             "when": "Within 24 hours"},
            {"head": "Paperwork and authorisation",
             "body": "NDA, rules of engagement, and written authorisation to test, signed "
                     "by someone with the authority to give it. Nothing is touched "
                     "before this exists.",
             "when": "Before start"},
            {"head": "Testing, with the line open",
             "body": "Anything critical reaches you the hour it is found, not in the "
                     "report three weeks later. A short daily note says where the "
                     "engagement is.",
             "when": "The agreed window"},
            {"head": "Report, readout, retest",
             "body": "Full report, a live walkthrough with your engineers, and a retest "
                     "pass once the fixes are in — each finding marked closed, partially "
                     "closed or still open.",
             "when": "+2 days, then retest"},
        ],

        # Objection handling. Each of these is a question that otherwise ends
        # the conversation silently, so each is answered in full and without
        # hedging — including the two that are answered against interest.
        "faq": [
            {
                "q": "You are one person. Why not a firm?",
                "a": "You get the person who does the work, on the call, every time — not "
                     "a sales engineer who scoped it and a junior who ran it. The trade is "
                     "real and worth stating plainly: I cannot field six testers against a "
                     "five-thousand-host estate in a week. If that is your engagement you "
                     "want a firm, and I will say so on the call rather than take the "
                     "booking.",
            },
            {
                "q": "What are your offensive certifications?",
                "a": "My verifiable certifications are RHCE and RHCSA, both linked on the "
                     "portfolio and checkable at Red Hat. I hold no offensive certification "
                     "and I am not going to imply otherwise. What I offer instead is "
                     "checkable in a different way: a complete written finding on this "
                     "site, a tool other people install from PyPI, an upstream defect trail "
                     "in NetExec, and two years of production ownership of the class of "
                     "infrastructure you are asking me to test. Read the sample finding and "
                     "judge the work — if it reads like something you would hand an "
                     "auditor, the question answers itself.",
            },
            {
                "q": "What happens if you do not find anything serious?",
                "a": "You get the full report and it says so plainly. A clean result against "
                     "a stated scope is a legitimate outcome and a legitimate thing to show "
                     "an auditor or a customer; it is only worthless if the scope was too "
                     "narrow to matter, which is a scoping conversation rather than a "
                     "testing one. I would rather write an honest thin report than pad a "
                     "thick one — severity inflation is the fastest way for a report to be "
                     "dismissed by the engineers who have to act on it.",
            },
            {
                "q": "Is testing our systems legal, and how is it authorised?",
                "a": "Testing is lawful only with written authorisation from someone "
                     "empowered to give it for those systems. Before anything begins we "
                     "sign an NDA, agree rules of engagement in writing — scope, excluded "
                     "systems, testing hours, escalation contacts — and I take signed "
                     "authorisation naming the in-scope assets. Some hosting and cloud "
                     "providers require their own notification, and I will tell you which. "
                     "Anything outside the signed list is not touched, however interesting "
                     "it looks.",
            },
            {
                "q": "Will this take production down?",
                "a": "Denial-of-service testing is out of scope unless you ask for it "
                     "separately and in writing. Exploitation is done to prove access, not "
                     "to cause damage, and anything genuinely destructive is demonstrated "
                     "rather than executed. Testing hours are agreed up front. If something "
                     "I do causes an unexpected problem I stop and call you immediately — "
                     "that is what the escalation contact in the rules of engagement is for.",
            },
            {
                "q": "Who owns the report, and how is our data handled?",
                "a": "You own the report outright. Findings, evidence and anything "
                     "recovered during testing stay confidential permanently and are never "
                     "reused as marketing — which is exactly why the sample on this site is "
                     "written against an invented environment rather than a real client. "
                     "Evidence is held encrypted for the retest window and the period your "
                     "NDA specifies, then destroyed on request with written confirmation.",
            },
            {
                "q": "How quickly can you start?",
                "a": "Within five working days of signed paperwork, and often sooner for a "
                     "Perimeter Review. If you are against a fixed audit or customer "
                     "deadline, say the date in your first message and you will get an "
                     "honest answer about whether it is achievable rather than a booking "
                     "and a discovery later.",
            },
            {
                "q": "We are outside India. Does that work?",
                "a": "Yes. The work is remote by nature and invoices in USD. The prices "
                     "above hold. The only thing worth agreeing up front is an overlap "
                     "window for the daily notes and the readout call — I work IST and "
                     "routinely overlap with Europe, the Gulf, and US Eastern mornings.",
            },
        ],

        "close": {
            "head": "Send four lines. Get a fixed quote in 24 hours.",
            "body": "No discovery funnel, no sales sequence. You email what you have, you "
                    "get what it costs and what it will take, and you decide. If your "
                    "engagement is a bad fit for one person, you will be told that too.",
            "brief": [
                "What your company does, in a sentence",
                "What needs testing — an application, an internal network, everything facing the internet",
                "The deadline, and what it is for — auditor, customer review, board, or nothing yet",
                "Rough size: number of applications, hosts, or staff",
            ],
        },
    },

    "nav": [
        {"id": "engagement", "label": "Engagement"},
        {"id": "report", "label": "Case study"},
        # Labelled for what a buyer scans for, not for what the page is
        # titled — "Engagements" would sit one line under "Engagement" in
        # the rail and read as a duplicate.
        {"id": "engagements", "label": "Rates & scope", "route": "engagements", "arrow": True},
        {"id": "tooling", "label": "Tooling"},
        {"id": "salvo", "label": "salvo", "route": "salvo", "arrow": True},
        {"id": "background", "label": "Background"},
        {"id": "arsenal", "label": "Arsenal"},
        {"id": "verify", "label": "Verify"},
        {"id": "contact", "label": "Contact"},
    ],
}
