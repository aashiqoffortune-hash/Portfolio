"""Single source of truth for every piece of content on the site.

Templates read from RESUME only, so updating the portfolio means editing this
file — no HTML changes required.

The one thing that lives elsewhere is `data/demos.py`: the recorded terminal
sessions on the salvo page, and the capability tables the page's command builder
works from. Those are captured output and transcribed code rather than written
copy, so they are kept apart from the prose and reach the templates through
RESUME["salvo"] like everything else.
"""

from data.demos import BUILDER, DEMOS, LOCKOUT_LAB, MATRIX_LAB

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

        # Recorded sessions and the three interactive labs. See data/demos.py
        # for how each transcript was captured.
        "demos": DEMOS,
        "matrix": MATRIX_LAB,
        "lockout": LOCKOUT_LAB,
        "builder": BUILDER,

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
        ],

        # Evidence the reader can run themselves — the strongest kind.
        "run": [
            {"cmd": "salvo 192.168.1.0/24 -u jdoe -p 'Password1!' -d corp.local --dry-run",
             "note": "prints every nxc command it would run, and runs nothing"},
            {"cmd": "salvo --check-nxc -P all",
             "note": "diffs salvo\u2019s capability tables against your installed NetExec"},
            {"cmd": "salvo --selftest",
             "note": "proves the output parser still agrees with NetExec\u2019s format"},
        ],
        "close": (
            "Don\u2019t take the claims on faith. <code>--dry-run</code> shows you "
            "exactly what it would send, and <code>--check-nxc</code> and "
            "<code>--selftest</code> are meant to run after any NetExec upgrade, so "
            "drift shows up as a failed check rather than a wrong answer in the field."
        ),
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

    "nav": [
        {"id": "engagement", "label": "Engagement"},
        {"id": "tooling", "label": "Tooling"},
        {"id": "salvo", "label": "salvo", "route": "salvo", "arrow": True},
        {"id": "background", "label": "Background"},
        {"id": "arsenal", "label": "Arsenal"},
        {"id": "verify", "label": "Verify"},
        {"id": "contact", "label": "Contact"},
    ],
}
