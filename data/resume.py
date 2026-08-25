"""Single source of truth for every piece of content on the site.

Templates read from RESUME only, so updating the portfolio means editing this
file — no HTML changes required.
"""

RESUME = {
    "profile": {
        "name": "Aashiq Shaikh",
        "legal_name": "Aashiq Sadik Basha Shaikh",
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
            "pdf": "files/RHCE-Aashiq-Sadik-Basha-Shaikh.pdf",
        },
        {
            "name": "Red Hat Certified System Administrator",
            "abbr": "RHCSA",
            "issuer": "Red Hat",
            "issued": "02 January 2023",
            "cert_id": "220-172-050",
            "verify": "https://www.credly.com/badges/60d9ce86-e4ab-46d8-b235-fa0d14a3ad3a",
            "pdf": "files/RHCSA-Aashiq-Sadik-Basha-Shaikh.pdf",
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
        {"id": "background", "label": "Background"},
        {"id": "arsenal", "label": "Arsenal"},
        {"id": "verify", "label": "Verify"},
        {"id": "contact", "label": "Contact"},
    ],
}
