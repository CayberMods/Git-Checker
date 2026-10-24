import os
import re
import sys
import json
import time
import argparse
import concurrent.futures
from urllib.parse import urlparse

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from rich.align import Align
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich.padding import Padding
from rich import box

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

console = Console()

MASCOT = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣠⠀⢀⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣤⣴⣄⠀⢾⣷⠛⠂⠘⠻⠿⠿⣷⣆⢰⡀⢢⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⡄⠃⣼⡿⣦⢿⠋⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣦⡙⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⣀⣙⣿⣿⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⢿⣿⣦⣭⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣆⣐⣿⣿⣿⣿⣿⠍⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣿⣿⣻⣿⠟⠀⠀⠀⠀⠀⠀⠐⠶⠀⠀⠆⠀⠀⠀⠀⠐⠂⠀⠀⠩⣿⣿⣾⣿⣿⣿⣂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢠⣶⣿⣿⣿⣿⣙⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢋⣿⣿⣾⣿⣏⡛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⡻⠿⣌⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣛⣿⣿⣿⣿⣿⣾⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠛⣿⣿⣿⣭⣿⣿⣿⣿⡂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣉⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢡⣤⡌⠹⣸⣥⣿⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣗⣛⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠛⢧⡀⠙⣿⣿⣿⣷⣞⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣘⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⢦⣈⠻⢿⣿⣿⣿⣿⣿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⢰⣾⣿⣿⣿⣿⣿⠿⠿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠳⠤⣉⠛⠿⣿⣿⣿⣿⣿⣦⣤⣀⣀⣀⣀⣀⣀⣤⣾⣿⣿⢿⡟⠛⠛⠛⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠂⠝⠤⡉⠛⠛⢫⣯⣭⡍⠙⠛⠛⠿⠦⠈⠃⠘⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
"""

TITLE_LINE = "GIT - CHECKER"

SUBTITLE = "Git Exposure Scanner  •  .git Leak Detection  •  Risk Assessment"

AUTHOR_LINE = "Developer : CayberMods     Version : non-versi"

TAGLINE = "Pentesting  |  Ethical Hacking  |  Security Research"

SENSITIVE_PATTERNS = {
    "env_file": [r"\.env", r"\.env\.", r"env\.php", r"\.env\.local"],
    "config": [r"config\.php", r"config\.json", r"wp-config\.php", r"configuration\.php", r"settings\.py", r"\.yml", r"\.yaml"],
    "backup": [r"\.bak", r"\.backup", r"\.old", r"\.orig", r"\.save", r"\.swp", r"\.sql", r"\.dump", r"\.zip", r"\.tar", r"\.gz", r"\.rar"],
    "credentials": [r"password", r"passwd", r"credential", r"secret", r"token", r"apikey", r"api_key", r"auth", r"\.pem", r"\.key", r"\.p12", r"\.pfx", r"id_rsa", r"id_dsa", r"htpasswd", r"netrc", r"\.git-credentials"],
    "log": [r"\.log", r"access\.log", r"error\.log", r"debug\.log", r"\.log\.", r"logs/"],
    "source": [r"\.php", r"\.py", r"\.js", r"\.rb", r"\.java", r"\.sh", r"\.bash", r"\.env", r"\.ini"],
    "database": [r"\.sqlite", r"\.db", r"\.mdb", r"database", r"\.sql"],
    "docker": [r"Dockerfile", r"docker-compose", r"\.dockerignore"],
    "ci_cd": [r"\.gitlab-ci", r"\.travis", r"jenkinsfile", r"\.github", r"\.circleci"],
}

LOG_PATTERNS = {
    "log_file": r"\.log",
    "access_log": r"access\.log",
    "error_log": r"error\.log",
    "debug_log": r"debug\.log",
    "app_log": r"(application|app|server)\.log",
    "syslog": r"syslog",
    "auth_log": r"(auth|secure)\.log",
    "sql_log": r"\.sql",
    "dump_file": r"(dump|backup|\.bak|\.old|\.orig)",
    "env_file": r"\.env",
    "cred_file": r"(credential|password|secret|token|\.pem|\.key|id_rsa)",
    "config_file": r"(config|settings|wp-config|\.ini|\.conf)",
}

CREDENTIAL_PATTERNS = {
    "password": r"(?i)(password|passwd|pass)\s*[:=]\s*['\"]?([^\s'\"]{3,})",
    "username": r"(?i)(username|user|login|db_user)\s*[:=]\s*['\"]?([^\s'\"]{2,})",
    "api_key": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{10,})",
    "secret": r"(?i)(secret|secret_key)\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{8,})",
    "token": r"(?i)(token|access_token|auth_token)\s*[:=]\s*['\"]?([A-Za-z0-9_\-\.]{10,})",
    "aws_key": r"(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}",
    "private_key": r"-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----",
    "jwt": r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}",
    "github_token": r"gh[pousr]_[A-Za-z0-9]{36,}",
    "slack_token": r"xox[baprs]-[A-Za-z0-9\-]{10,}",
    "google_api": r"AIza[0-9A-Za-z\-_]{35}",
    "stripe_key": r"sk_live_[0-9a-zA-Z]{24,}",
    "db_url": r"(?i)(mysql|postgres|mongodb|redis|ftp|smtp)://([^\s'\"]+)",
    "email": r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}",
    "ssh_remote": r"git@[\w\.\-]+:[\w\.\-/]+",
}

CRITICAL_RISK = [
    r"\.env", r"\.git-credentials", r"id_rsa", r"\.pem", r"\.key",
    r"wp-config\.php", r"\.sql", r"config\.php", r"\.htpasswd",
]

MEDIUM_RISK = [
    r"\.log", r"\.bak", r"\.old", r"\.zip", r"\.tar", r"\.gz",
    r"\.sqlite", r"database", r"password", r"secret", r"token",
]

GIT_PATHS = [
    "/.git/", "/.git", "/.git/HEAD", "/.git/config", "/.git/index",
    "/.git/COMMIT_EDITMSG", "/.git/logs/HEAD", "/.git/packed-refs",
    "/.git/refs/heads/main", "/.git/refs/heads/master",
    "/.git/objects/info/packs", "/.git/info/refs", "/.git/description",
    "/.git/hooks/applypatch-msg.sample",
]

GIT_HEADER_SIGNS = [
    "ref: refs/", "[core]", "repositoryformatversion",
    "DIRC", "PACK", "commit ", "tree ", "parent ", "author ",
]

DUMP_PATHS = [
    "/.git/HEAD", "/.git/config", "/.git/index", "/.git/COMMIT_EDITMSG",
    "/.git/description", "/.git/packed-refs", "/.git/logs/HEAD",
    "/.git/info/refs", "/.git/objects/info/packs",
    "/.git/refs/heads/main", "/.git/refs/heads/master",
    "/.git/ORIG_HEAD", "/.git/FETCH_HEAD", "/.git/hooks/applypatch-msg.sample",
    "/.git/info/exclude", "/.git/logs/refs/heads/main", "/.git/logs/refs/heads/master",
]


def center_panel(renderable, **kwargs):
    return Align.center(renderable, vertical="middle")


def normalize_url(target):
    target = target.strip()
    if not target:
        return None
    if not re.match(r"^https?://", target, re.IGNORECASE):
        target = "http://" + target
    return target.rstrip("/")


def detect_protocol(target):
    target = target.strip()
    if re.match(r"^https://", target, re.IGNORECASE):
        return "https", target.rstrip("/")
    if re.match(r"^http://", target, re.IGNORECASE):
        return "http", target.rstrip("/")
    base = target.rstrip("/")
    for scheme in ["https", "http"]:
        try:
            url = f"{scheme}://{base}/"
            r = requests.get(url, timeout=8, verify=False, allow_redirects=True)
            if r.status_code < 500:
                return scheme, f"{scheme}://{base}"
        except requests.exceptions.RequestException:
            continue
    return "http", f"http://{base}"


def safe_request(url, method="GET", timeout=10):
    try:
        return requests.request(
            method, url, timeout=timeout, verify=False, allow_redirects=True,
            headers={"User-Agent": "Mozilla/5.0 (Git-Checker Security Scanner)"}
        )
    except requests.exceptions.RequestException:
        return None


def human_size(n):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if n < 1024.0:
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} PB"


def check_git_exposure(domain):
    domain = normalize_url(domain)
    if not domain:
        return None
    scheme, base = detect_protocol(domain)
    results = {
        "domain": base, "protocol": scheme, "git_found": False, "git_url": None,
        "status_code": None, "size": 0, "size_human": "0 B",
        "estimated_folders": [], "sensitive_files": [], "log_files": [],
        "risk_level": "LOW", "risk_score": 0, "risk_details": [],
        "exposed_paths": [],
    }
    found_git = False
    for path in GIT_PATHS:
        url = base + path
        r = safe_request(url)
        if r is None:
            continue
        if r.status_code == 200 and any(sig in r.text for sig in GIT_HEADER_SIGNS):
            found_git = True
            results["git_found"] = True
            results["git_url"] = base + "/.git/"
            results["status_code"] = r.status_code
            results["exposed_paths"].append({"path": path, "code": r.status_code, "length": len(r.text)})
            break
    if not found_git:
        r = safe_request(base + "/.git/HEAD")
        if r is not None and r.status_code == 200 and "ref:" in r.text:
            found_git = True
            results["git_found"] = True
            results["git_url"] = base + "/.git/"
            results["status_code"] = 200
    if not found_git:
        return results
    total_size = 0
    folders = set()
    sensitive_found = []
    log_found = []
    for fpath in DUMP_PATHS:
        url = base + fpath
        r = safe_request(url, timeout=8)
        if r is None:
            continue
        if r.status_code == 200 and len(r.content) > 0:
            total_size += len(r.content)
            results["exposed_paths"].append({"path": fpath, "code": r.status_code, "length": len(r.content)})
            parts = fpath.strip("/").split("/")
            if len(parts) > 1:
                folders.add("/".join(parts[:-1]))
            fname = parts[-1].lower()
            for cat, patterns in SENSITIVE_PATTERNS.items():
                for pat in patterns:
                    if re.search(pat, fname, re.IGNORECASE):
                        sensitive_found.append({"file": fpath, "category": cat, "url": url})
                        break
            for lname, lpat in LOG_PATTERNS.items():
                if re.search(lpat, fname, re.IGNORECASE):
                    log_found.append({"file": fpath, "type": lname, "url": url})
                    break
    try:
        r = safe_request(base + "/.git/config")
        if r is not None and r.status_code == 200:
            urls = re.findall(r"url\s*=\s*(\S+)", r.text)
            for u in urls:
                folders.add(f"remote:{u}")
    except Exception:
        pass
    results["size"] = total_size
    results["size_human"] = human_size(total_size)
    results["estimated_folders"] = sorted(folders)[:50]
    results["sensitive_files"] = sensitive_found
    results["log_files"] = log_found
    risk_score = 0
    risk_details = []
    if sensitive_found:
        critical_count = 0
        for sf in sensitive_found:
            for pat in CRITICAL_RISK:
                if re.search(pat, sf["file"], re.IGNORECASE):
                    critical_count += 1
                    break
        if critical_count > 0:
            risk_score += 50 + (critical_count * 5)
            risk_details.append(f"{critical_count} critical files exposed (credentials/config)")
        medium_count = 0
        for sf in sensitive_found:
            for pat in MEDIUM_RISK:
                if re.search(pat, sf["file"], re.IGNORECASE):
                    medium_count += 1
                    break
        if medium_count > 0:
            risk_score += 20 + (medium_count * 2)
            risk_details.append(f"{medium_count} medium-risk files (backup/log/db)")
    if log_found:
        risk_score += 15 + len(log_found) * 3
        risk_details.append(f"{len(log_found)} log files found")
    if total_size > 1024 * 100:
        risk_score += 10
    if total_size > 1024 * 1024:
        risk_score += 15
    if len(results["exposed_paths"]) > 5:
        risk_score += 10
        risk_details.append(f"{len(results['exposed_paths'])} exposed paths")
    results["risk_score"] = min(risk_score, 100)
    if risk_score >= 70:
        results["risk_level"] = "CRITICAL"
    elif risk_score >= 40:
        results["risk_level"] = "HIGH"
    elif risk_score >= 20:
        results["risk_level"] = "MEDIUM"
    results["risk_details"] = risk_details
    return results


def dump_git_files(result, out_dir="dumps"):
    if not result or not result.get("git_found"):
        console.print(center_panel(Panel("[red]Target has no exposed .git[/red]", border_style="red", box=box.ROUNDED)))
        return None
    base = result["domain"]
    host = re.sub(r"^https?://", "", base).replace("/", "_").replace(":", "_")
    target_dir = os.path.join(out_dir, host)
    os.makedirs(target_dir, exist_ok=True)
    saved = []
    dumped_data = {}
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                  TimeElapsedColumn()) as prog:
        task = prog.add_task("Dumping .git files...", total=len(DUMP_PATHS))
        for path in DUMP_PATHS:
            url = base + path
            r = safe_request(url, timeout=10)
            if r is not None and r.status_code == 200 and len(r.content) > 0:
                safe_name = path.strip("/").replace("/", "_")
                fpath = os.path.join(target_dir, safe_name)
                try:
                    with open(fpath, "wb") as f:
                        f.write(r.content)
                    saved.append(fpath)
                    dumped_data[path] = r.content
                except Exception:
                    pass
            prog.advance(task)
    t = Table(box=box.ROUNDED, border_style="green", header_style="bold green", title="Dump Result")
    t.add_column("Property", style="green")
    t.add_column("Value", style="white")
    t.add_row("Files Dumped", str(len(saved)))
    t.add_row("Output Directory", target_dir)
    console.print(Align.center(t))
    return {"dir": target_dir, "files": saved, "data": dumped_data}


def search_credentials(result, dumped_data=None):
    if not result or not result.get("git_found"):
        console.print(center_panel(Panel("[red]No exposed .git to search[/red]", border_style="red", box=box.ROUNDED)))
        return []
    base = result["domain"]
    findings = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%")) as prog:
        task = prog.add_task("Scanning for credentials...", total=len(DUMP_PATHS))
        for path in DUMP_PATHS:
            content = None
            source = "remote"
            if dumped_data and path in dumped_data:
                content = dumped_data[path].decode("utf-8", errors="ignore")
                source = "dumped"
            else:
                r = safe_request(base + path, timeout=10)
                if r is not None and r.status_code == 200:
                    content = r.text
            if content:
                for ctype, pat in CREDENTIAL_PATTERNS.items():
                    try:
                        matches = re.findall(pat, content)
                    except re.error:
                        continue
                    for m in matches:
                        val = m if isinstance(m, str) else (m[-1] if isinstance(m, tuple) else str(m))
                        if val and len(str(val)) > 2:
                            findings.append({
                                "type": ctype, "value": str(val)[:200],
                                "file": path, "source": source,
                            })
            prog.advance(task)
    seen = set()
    unique = []
    for f in findings:
        key = (f["type"], f["value"])
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique


def save_report(result, findings, dump_info, path):
    report = {
        "target": result,
        "credentials": findings,
        "dump": {
            "dir": dump_info["dir"] if dump_info else None,
            "files": dump_info["files"] if dump_info else [],
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        console.print(Align.center(Panel(f"[green]Report saved:[/green] {path}", border_style="green", box=box.ROUNDED)))
        return True
    except Exception as e:
        console.print(Align.center(Panel(f"[red]Failed to save: {e}[/red]", border_style="red", box=box.ROUNDED)))
        return False


def print_header():
    console.clear()
    logo_panel = Panel(
        Align.center(Text(MASCOT, style="bold cyan")),
        border_style="cyan", box=box.DOUBLE, padding=(0, 1),
    )
    console.print(logo_panel)
    info = Text.assemble(
        (TITLE_LINE + "\n", "bold cyan"),
        (SUBTITLE + "\n", "dim white"),
        (AUTHOR_LINE + "\n", "bold yellow"),
        (TAGLINE, "italic magenta"),
    )
    console.print(Panel(Align.center(info), border_style="magenta", box=box.ROUNDED))
    console.print()


def display_results(results):
    if not results:
        console.print(Align.center(Panel("[red]No results[/red]", border_style="red", box=box.ROUNDED)))
        return
    table = Table(title="Git Exposure Scan Results", box=box.ROUNDED, border_style="cyan", header_style="bold magenta")
    table.add_column("Domain", style="cyan", justify="center")
    table.add_column("Protocol", style="green", justify="center")
    table.add_column("Git", style="yellow", justify="center")
    table.add_column("Status", style="white", justify="center")
    table.add_column("Size", style="blue", justify="center")
    table.add_column("Risk", style="red", justify="center")
    for r in results:
        if r is None:
            continue
        git_status = "[green]FOUND[/green]" if r["git_found"] else "[red]NOT FOUND[/red]"
        risk_color = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(r["risk_level"], "white")
        table.add_row(
            r["domain"], r["protocol"].upper(), git_status,
            str(r["status_code"]) if r["status_code"] else "-",
            r["size_human"] if r["git_found"] else "-",
            f"[{risk_color}]{r['risk_level']}[/{risk_color}]",
        )
    console.print(Align.center(table))


def display_detail(result):
    if not result or not result["git_found"]:
        return
    info_table = Table(box=box.ROUNDED, border_style="cyan", header_style="bold cyan", show_header=False)
    info_table.add_column("Key", style="cyan", width=18)
    info_table.add_column("Value", style="white")
    info_table.add_row("Domain", result["domain"])
    info_table.add_row("Git URL", result["git_url"])
    info_table.add_row("Status Code", str(result["status_code"]))
    info_table.add_row("Total Size", result["size_human"])
    risk_color = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(result["risk_level"], "white")
    info_table.add_row("Risk Score", f"{result['risk_score']}/100")
    info_table.add_row("Risk Level", f"[{risk_color}]{result['risk_level']}[/{risk_color}]")
    console.print(Align.center(Panel(info_table, title="[bold cyan]Target Details[/bold cyan]", border_style="cyan", box=box.DOUBLE)))

    if result["risk_details"]:
        rt = Table(title="Risk Details", box=box.ROUNDED, border_style="yellow", header_style="bold yellow")
        rt.add_column("#", style="dim", justify="center", width=4)
        rt.add_column("Description", style="yellow")
        for i, d in enumerate(result["risk_details"], 1):
            rt.add_row(str(i), d)
        console.print(Align.center(rt))

    if result["sensitive_files"]:
        st = Table(title="Sensitive Files Found", box=box.ROUNDED, border_style="red", header_style="bold red")
        st.add_column("#", style="dim", justify="center", width=4)
        st.add_column("File", style="red")
        st.add_column("Category", style="yellow")
        for i, sf in enumerate(result["sensitive_files"], 1):
            st.add_row(str(i), sf["file"], sf["category"])
        console.print(Align.center(st))

    if result["log_files"]:
        lt = Table(title="Log Files Found", box=box.ROUNDED, border_style="magenta", header_style="bold magenta")
        lt.add_column("#", style="dim", justify="center", width=4)
        lt.add_column("File", style="magenta")
        lt.add_column("Type", style="yellow")
        for i, lf in enumerate(result["log_files"], 1):
            lt.add_row(str(i), lf["file"], lf["type"])
        console.print(Align.center(lt))

    if result["estimated_folders"]:
        ft = Table(title="Estimated Folders / Paths", box=box.ROUNDED, border_style="blue", header_style="bold blue")
        ft.add_column("#", style="dim", justify="center", width=4)
        ft.add_column("Path", style="blue")
        for i, f in enumerate(result["estimated_folders"][:30], 1):
            ft.add_row(str(i), f)
        console.print(Align.center(ft))


def display_credentials(findings):
    if not findings:
        console.print(Align.center(Panel("[yellow]No credentials found[/yellow]", border_style="yellow", box=box.ROUNDED)))
        return
    table = Table(title="Credential Findings", box=box.ROUNDED, border_style="red", header_style="bold red")
    table.add_column("#", style="dim", justify="center", width=4)
    table.add_column("Type", style="red", justify="center")
    table.add_column("Value", style="yellow")
    table.add_column("File", style="cyan")
    table.add_column("Source", style="magenta", justify="center")
    for i, f in enumerate(findings, 1):
        table.add_row(str(i), f["type"], f["value"], f["file"], f["source"])
    console.print(Align.center(table))


def post_scan_menu(result):
    if not result or not result.get("git_found"):
        console.print(Align.center(Panel("[yellow]Target not vulnerable, no further actions available.[/yellow]",
                                        border_style="yellow", box=box.ROUNDED)))
        return
    dumped = {"data": None, "dir": None, "files": []}
    credentials = []
    while True:
        console.print()
        menu = Table(title=f"Actions for {result['domain']}", box=box.ROUNDED, border_style="cyan", show_header=False)
        menu.add_column("Opt", style="bold cyan", justify="center", width=5)
        menu.add_column("Action", style="white")
        menu.add_row("1", "Dump .git files")
        menu.add_row("2", "Search credentials (remote)")
        menu.add_row("3", "Dump + Search credentials")
        menu.add_row("4", "Show target details")
        menu.add_row("5", "Show credential findings")
        menu.add_row("6", "Save report (JSON auto-name)")
        menu.add_row("7", "Save report to custom path")
        menu.add_row("8", "Re-scan target")
        menu.add_row("0", "Back / Exit menu")
        console.print(Align.center(menu))
        choice = Prompt.ask("[bold cyan]Select option[/bold cyan]",
                            choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"], default="0")
        if choice == "0":
            break
        elif choice == "1":
            d = dump_git_files(result)
            if d:
                dumped = d
        elif choice == "2":
            credentials = search_credentials(result, dumped.get("data"))
            display_credentials(credentials)
        elif choice == "3":
            d = dump_git_files(result)
            if d:
                dumped = d
            credentials = search_credentials(result, dumped.get("data"))
            display_credentials(credentials)
        elif choice == "4":
            display_detail(result)
        elif choice == "5":
            display_credentials(credentials)
        elif choice == "6":
            host = re.sub(r"^https?://", "", result["domain"]).replace("/", "_").replace(":", "_")
            default_path = f"report_{host}_{int(time.time())}.json"
            save_report(result, credentials, dumped if dumped.get("dir") else None, default_path)
        elif choice == "7":
            path = Prompt.ask("[cyan]Report path[/cyan]", default="report.json")
            save_report(result, credentials, dumped if dumped.get("dir") else None, path)
        elif choice == "8":
            console.print(Align.center(Panel("[cyan]Re-scanning...[/cyan]", border_style="cyan", box=box.ROUNDED)))
            result = check_git_exposure(result["domain"])
            display_detail(result)


def scan_single(target):
    console.print(Align.center(Panel(f"[cyan]Scanning:[/cyan] {target}", border_style="cyan", box=box.ROUNDED)))
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as prog:
        task = prog.add_task("Checking .git exposure...", total=None)
        res = check_git_exposure(target)
        prog.update(task, completed=True)
    return res


def scan_bulk(targets, threads=10):
    results = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                  TimeElapsedColumn()) as prog:
        task = prog.add_task("Scanning targets...", total=len(targets))
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
            futures = {ex.submit(check_git_exposure, t): t for t in targets}
            for fut in concurrent.futures.as_completed(futures):
                try:
                    res = fut.result()
                    if res:
                        results.append(res)
                except Exception:
                    pass
                prog.advance(task)
    return results


def load_targets(args):
    targets = []
    if args.single:
        targets.append(args.single)
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        targets.append(line)
        except FileNotFoundError:
            console.print(Align.center(Panel(f"[red]File not found: {args.file}[/red]", border_style="red", box=box.ROUNDED)))
    return targets


def bulk_menu(results):
    vulnerable = [r for r in results if r and r.get("git_found")]
    while True:
        console.print()
        menu = Table(title="Bulk Scan Actions", box=box.ROUNDED, border_style="cyan", show_header=False)
        menu.add_column("Opt", style="bold cyan", justify="center", width=5)
        menu.add_column("Action", style="white")
        menu.add_row("1", f"Show results table ({len(results)} targets, {len(vulnerable)} vulnerable)")
        menu.add_row("2", "Dump all vulnerable targets")
        menu.add_row("3", "Search credentials on all vulnerable targets")
        menu.add_row("4", "Dump + Search all vulnerable targets")
        menu.add_row("5", "Pick a target for detailed interaction")
        menu.add_row("6", "Save full report (JSON)")
        menu.add_row("0", "Exit")
        console.print(Align.center(menu))
        choice = Prompt.ask("[bold cyan]Select option[/bold cyan]",
                            choices=["0", "1", "2", "3", "4", "5", "6"], default="0")
        if choice == "0":
            break
        elif choice == "1":
            display_results(results)
        elif choice == "2":
            for r in vulnerable:
                dump_git_files(r)
        elif choice == "3":
            for r in vulnerable:
                console.print(Align.center(Panel(f"[cyan]Searching credentials for:[/cyan] {r['domain']}",
                                                 border_style="cyan", box=box.ROUNDED)))
                findings = search_credentials(r)
                display_credentials(findings)
        elif choice == "4":
            for r in vulnerable:
                console.print(Align.center(Panel(f"[cyan]Processing:[/cyan] {r['domain']}",
                                                 border_style="cyan", box=box.ROUNDED)))
                dumped = dump_git_files(r)
                findings = search_credentials(r, dumped.get("data") if dumped else None)
                display_credentials(findings)
        elif choice == "5":
            if not vulnerable:
                console.print(Align.center(Panel("[yellow]No vulnerable targets[/yellow]",
                                                 border_style="yellow", box=box.ROUNDED)))
                continue
            ttable = Table(title="Pick a Target", box=box.ROUNDED, border_style="cyan", header_style="bold cyan")
            ttable.add_column("#", style="dim", justify="center")
            ttable.add_column("Domain", style="cyan")
            ttable.add_column("Risk", style="red", justify="center")
            for i, r in enumerate(vulnerable, 1):
                risk_color = {"CRITICAL": "bold red", "HIGH": "red", "MEDIUM": "yellow", "LOW": "green"}.get(r["risk_level"], "white")
                ttable.add_row(str(i), r["domain"], f"[{risk_color}]{r['risk_level']}[/{risk_color}]")
            console.print(Align.center(ttable))
            try:
                idx = int(Prompt.ask(f"[cyan]Pick target (1-{len(vulnerable)})[/cyan]"))
                if 1 <= idx <= len(vulnerable):
                    display_detail(vulnerable[idx - 1])
                    post_scan_menu(vulnerable[idx - 1])
            except ValueError:
                pass
        elif choice == "6":
            path = Prompt.ask("[cyan]Report path[/cyan]", default=f"bulk_report_{int(time.time())}.json")
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                console.print(Align.center(Panel(f"[green]Report saved:[/green] {path}",
                                                 border_style="green", box=box.ROUNDED)))
            except Exception as e:
                console.print(Align.center(Panel(f"[red]Failed: {e}[/red]",
                                                 border_style="red", box=box.ROUNDED)))


def main():
    parser = argparse.ArgumentParser(
        prog="git-checker",
        description="Git-Checker - .git Exposure Scanner for Ethical Hacking & Security Research",
        epilog="Example: python git_checker.py -s example.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-s", "--single", metavar="TARGET", help="Scan a single target domain")
    parser.add_argument("-f", "--file", metavar="FILE", help="Scan multiple targets from a file (one per line)")
    parser.add_argument("-t", "--threads", type=int, default=10, metavar="N", help="Number of concurrent threads (default: 10)")
    parser.add_argument("-o", "--output", metavar="FILE", help="Save scan report to JSON file")
    parser.add_argument("--no-banner", action="store_true", help="Hide the banner")
    args = parser.parse_args()
    if not args.no_banner:
        print_header()
    targets = load_targets(args)
    if not targets:
        console.print(Align.center(Panel("[red]No targets provided. Use -s <domain> or -f <file>.[/red]",
                                         border_style="red", box=box.ROUNDED)))
        parser.print_help()
        return
    summary = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
    summary.add_column("Key", style="cyan")
    summary.add_column("Value", style="white")
    summary.add_row("Total Targets", str(len(targets)))
    summary.add_row("Threads", str(args.threads))
    console.print(Align.center(summary))
    console.print()
    start = time.time()
    if len(targets) == 1:
        results = [scan_single(targets[0])]
    else:
        results = scan_bulk(targets, args.threads)
    elapsed = time.time() - start
    console.print()
    display_results(results)
    console.print(Align.center(Panel(f"[cyan]Elapsed time:[/cyan] {elapsed:.2f}s", border_style="cyan", box=box.ROUNDED)))
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            console.print(Align.center(Panel(f"[green]Report saved:[/green] {args.output}",
                                             border_style="green", box=box.ROUNDED)))
        except Exception as e:
            console.print(Align.center(Panel(f"[red]Failed: {e}[/red]",
                                             border_style="red", box=box.ROUNDED)))
    if len(targets) == 1:
        r = results[0]
        display_detail(r)
        post_scan_menu(r)
    else:
        bulk_menu(results)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print(Align.center(Panel("[red]Cancelled by user[/red]", border_style="red", box=box.ROUNDED)))
        sys.exit(0)
