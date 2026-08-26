"""Single source of truth for every piece of content on the site.

Templates read from RESUME only, so updating the portfolio means editing this
file — no HTML changes required.
"""

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
                "Wraps NetExec across eight protocols with concurrency control, "
                "per-protocol timeout tuning, and resumable job state — plus the "
                "operational security controls the wrapper exists for: request jitter, "
                "process spacing, and a low-and-slow mode for environments where the "
                "lockout policy is the real constraint."
            ),
            "findings_intro": (
                "Three argument-handling defects root-caused by reading NetExec upstream "
                "source, rather than by trial:"
            ),
            "findings": [
                {
                    "flag": "--domain",
                    "text": "Undefined on non-domain protocols, which caused live hosts to be reported as dead.",
                },
                {
                    "flag": "--local-auth",
                    "text": "Invalid on LDAP, and consumed logon attempts against account lockout policy.",
                },
                {
                    "flag": "global timeout",
                    "text": "Deprecated and silently ignored in favour of two-second per-protocol defaults.",
                },
            ],
            "footer": (
                "Ships with a self-test harness and a capability audit that revalidates "
                "the tool against whatever NetExec build is installed."
            ),
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
    "writeups": {
        "project": "salvo",
        "url": "https://github.com/aashiqoffortune-hash/salvo",
        "intro": (
            "salvo builds NetExec command lines, so it has to know exactly which "
            "flags each protocol defines. Getting that wrong throws no error — it "
            "produces a blank cell that reads as \u201cnothing listening there.\u201d "
            "Three of these were root-caused by reading NetExec\u2019s source rather "
            "than by trial."
        ),
        "entries": [
            {
                "id": "domain-flag",
                "title": "A blank cell that reads as a closed port",
                "claim": (
                    "A wrapper that fans one credential across every protocol can "
                    "report a live host as dead — with no error to notice — the moment "
                    "it passes a flag the target protocol\u2019s parser never defined."
                ),
                "evidence": (
                    "ssh, ftp, nfs and vnc have no domain concept and no <code>-d</code> "
                    "argument. Pass one and NetExec\u2019s argparse exits with a usage "
                    "error before a single packet leaves the host. The job produces "
                    "nothing parseable, and the cell renders <code>-</code> — which any "
                    "operator reads as \u201cport closed,\u201d not \u201cthe wrapper "
                    "built a broken command.\u201d The wrong conclusion is silent."
                ),
                "artifact": (
                    "<code>DOMAIN_CAPABLE = {smb, winrm, wmi, mssql, ldap, rdp}</code>. "
                    "salvo withholds <code>-d</code> for the four domainless protocols and "
                    "says so beneath the matrix, because a bare username is a different "
                    "test from a domain one."
                ),
                "verify": "salvo --check-nxc -P all",
                "verify_note": "diffs the table against nxc &lt;proto&gt; --help on the installed build",
            },
            {
                "id": "local-auth",
                "title": "A flag that spends a logon it was never going to use",
                "claim": (
                    "<code>--local-auth</code> on LDAP does not merely fail. It burns an "
                    "authentication attempt against the account lockout counter — the one "
                    "resource an engagement cannot get back."
                ),
                "evidence": (
                    "LDAP accepts <code>-d</code> but not <code>--local-auth</code>, "
                    "because a directory bind is inherently domain-scoped. It sat in the "
                    "local-auth set and should not have. Each wasted attempt counts against "
                    "a threshold that is often five, tracked on the domain controller "
                    "regardless of which member server the request touched."
                ),
                "artifact": (
                    "<code>LOCAL_AUTH_CAPABLE = {smb, winrm, wmi, mssql, rdp}</code> — LDAP "
                    "removed. salvo prints the lockout arithmetic before the run and the "
                    "attempts actually made after it, since a <code>-</code> cell never "
                    "reached authentication."
                ),
                "verify": "salvo <targets> -C creds.txt -d corp.local  # lockout math printed first",
                "verify_note": "",
            },
            {
                "id": "timeout",
                "title": "A timeout the tool accepts and silently ignores",
                "claim": (
                    "NetExec\u2019s global <code>--timeout</code> is deprecated and does "
                    "nothing. A wrapper that keeps passing it inherits two-second defaults "
                    "that report live hosts as dead over any real latency."
                ),
                "evidence": (
                    "NetExec\u2019s own help says the flag is \u201cno longer used, "
                    "replaced by per-protocol timeouts.\u201d The replacements default hard: "
                    "SMB and RPC at 2s, LDAP at 3s — short enough to time out on tunnel "
                    "latency and render a reachable host as a dead one."
                ),
                "artifact": (
                    "A <code>TIMEOUT_FLAG</code> map emits the per-protocol flag instead — "
                    "<code>--smb-timeout</code>, <code>--http-timeout</code>, "
                    "<code>--rpc-timeout</code>, and the rest. ftp, vnc and ldap expose no "
                    "timeout flag at all, and salvo encodes that gap rather than guessing."
                ),
                "verify": "salvo --slow 10.10.100.0/24 -C creds.txt -d corp.local",
                "verify_note": "tunnel preset that raises every per-protocol timeout at once",
            },
            {
                "id": "pwn3d",
                "title": "One word, several unrelated meanings",
                "claim": (
                    "NetExec prints <code>Pwn3d!</code> for conditions that are not the "
                    "same thing. Collapsing them into one verdict is how a standard-user "
                    "shell gets mistaken for domain admin."
                ),
                "evidence": (
                    "On smb, <code>Pwn3d!</code> proves write access to ADMIN$ — real local "
                    "admin. On winrm it proves only that the account is in Remote Management "
                    "Users, which grants execution with no admin rights whatsoever. Reading "
                    "those as equal writes a false privilege level into the notes."
                ),
                "artifact": (
                    "A per-protocol meaning table renders smb and mssql admin as "
                    "<code>ADMIN</code>, and winrm/ssh/wmi execution as <code>exec</code>. "
                    "When no protocol proved admin on a host, the follow-up line says so in "
                    "words rather than leaving it to be assumed."
                ),
                "verify": "",
                "verify_note": "",
            },
            {
                "id": "three-buckets",
                "title": "The credential two-state logic throws away",
                "claim": (
                    "Most tooling records worked or failed. Everything else collapses into "
                    "failed — which is how a provably correct password gets discarded."
                ),
                "evidence": (
                    "A password can be correct while the access path is closed: "
                    "STATUS_LOGON_TYPE_NOT_GRANTED, account disabled, password expired, "
                    "logon-hour and workstation restrictions all mean the credential checked "
                    "out. A WinRM refusal is byte-identical whether the account is valid but "
                    "unprivileged or the password is simply wrong."
                ),
                "artifact": (
                    "Three verdict buckets — valid, blocked (<code>VALID*</code>), unknown "
                    "(<code>?</code>). A NOT A VERDICT block under the matrix lists every "
                    "blocked and unknown result with its reason; a credential in that list "
                    "is still live and named as such."
                ),
                "verify": "",
                "verify_note": "",
            },
        ],
        "close": (
            "Both audit paths — <code>--selftest</code> for the output parser, "
            "<code>--check-nxc</code> for the capability tables — are meant to run "
            "after any NetExec upgrade, so drift surfaces as a failed check rather "
            "than a wrong cell in the field."
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
        {"id": "writeups", "label": "Writeups"},
        {"id": "background", "label": "Background"},
        {"id": "arsenal", "label": "Arsenal"},
        {"id": "verify", "label": "Verify"},
        {"id": "contact", "label": "Contact"},
    ],
}
