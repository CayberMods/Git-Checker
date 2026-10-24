# Git-Checker

A fast and clean CLI tool to detect exposed `.git` directories on web servers, assess security risk, dump `.git` files, and search for leaked credentials. Built with [Rich](https://github.com/Textualize/rich) for a modern terminal UI.

> **Disclaimer:** This tool is intended for **authorized security testing, ethical hacking, and security research only**. Only use it against systems you own or have explicit written permission to test. The author is not responsible for any misuse or damage caused by this tool.

---

## Features

- **Automatic `.git` Exposure Detection** – Identifies publicly accessible `.git` directories and files
- **Auto Protocol Detection** – Automatically resolves `http` or `https` for each target
- **Git Size & Folder Estimation** – Calculates exposed `.git` size and estimates folder structure
- **Security Risk Assessment** – Scores each target (`LOW` / `MEDIUM` / `HIGH` / `CRITICAL`)
- **Sensitive File Detection** – Flags exposed config, backup, database, and credential files
- **Log File Detection** – Detects exposed access, error, debug, and SQL logs
- **Auto Log Credential Search** – Scans dumps and remote files for passwords, API keys, tokens, JWTs, private keys, AWS keys, DB URLs, emails, and more
- **Auto Git Dumper** – Downloads reachable `.git` files to a local directory
- **Single Target Scan** – Scan one domain at a time
- **Bulk Scan** – Scan many targets from a file with multithreading
- **Interactive Post-Scan Menu** – Dump, search credentials, save reports, or re-scan after the initial scan
- **JSON Report Export** – Save full scan results, credentials, and dump info
- **Clean Rich UI** – Centered panels, tables, and progress bars for a polished experience

---

## Installation

```bash
git clone https://github.com/CayberMods/Git-Checker.git
cd Git-Checker
pip install -r requirements.txt
```

Requirements

· Python 3.8+
· requests
· rich

Install manually if needed:

```bash
pip install requests rich
```

---

Usage

```bash
python git_checker.py -s <target>
python git_checker.py -f <targets.txt>
```

Arguments

Flag Description
-s, --single Scan a single target domain
-f, --file Scan multiple targets from a file (one per line)
-t, --threads Number of concurrent threads (default: 10)
-o, --output Save scan report to a JSON file
--no-banner Hide the banner
-h, --help Show help message

Examples

Scan a single domain:

```bash
python git_checker.py -s example.com
```

Bulk scan with 20 threads:

```bash
python git_checker.py -f targets.txt -t 20
```

Save report:

```bash
python git_checker.py -s example.com -o report.json
```

Targets file format (targets.txt):

```
example.com
https://site2.com
http://site3.org
# comments are ignored
```

---

Interactive Menu

After a scan finishes, an interactive menu lets you:

```
1  Dump .git files
2  Search credentials (remote)
3  Dump + Search credentials
4  Show target details
5  Show credential findings
6  Save report (JSON auto-name)
7  Save report to custom path
8  Re-scan target
0  Back / Exit menu
```

Bulk mode also has its own menu to dump, search credentials, or pick a specific target for detailed interaction.

---

What It Detects

Exposed Files

- · .git/HEAD, .git/config, .git/index, .git/COMMIT_EDITMSG
- · .git/logs/HEAD, .git/logs/refs/heads/*
- · .git/packed-refs, .git/info/refs, .git/refs/heads/*
- · .git/objects/info/packs, .git/description, .git/ORIG_HEAD, 
- .git/FETCH_HEAD

Credential Patterns

- · Passwords, usernames
- · API keys, secrets, tokens
- · AWS keys, GitHub tokens, Slack tokens, Google API keys, Stripe keys
- · Private keys (RSA, DSA, EC, OpenSSH, PGP)
- · JWT tokens
- · Database/connection URLs (MySQL, PostgreSQL, MongoDB, Redis, FTP, SMTP)
- · SSH remotes and email addresses

Risk Scoring

- Level Score Description
-LOW 0–19 Minimal exposure
- MEDIUM 20–39 Backup/log/db files found
- HIGH 40–69 Sensitive files exposed
- CRITICAL 70–100 Credentials, keys, or config files exposed

---

Output Example

```
╭─────────── Git Exposure Scan Results ────────────────╮
│ Domain           │ Protocol  │ Git          │ Risk       │
├───────────────┼──────────┼───────────┼───────────┤
│ http://site.com  │ HTTP      │ FOUND        │ HIGH       │
╰───────────────┴──────────┴───────────┴───────────╯
```

---

Legal Notice

This project is provided as-is for educational and authorized security testing purposes only. By using this tool, you agree to:

- · Only test systems you own or have explicit permission to test
- · Follow all applicable laws in your jurisdiction
- · Not use this tool for unauthorized access, data theft, or any illegal activity

Unauthorized access to computer systems is illegal and punishable by law. The developer assumes no liability for misuse.

---

Credits

- Category: Pentesting · Ethical Hacking · Security Research
- Version: non-versi

If you find this tool useful, consider giving it a ⭐ on GitHub.
