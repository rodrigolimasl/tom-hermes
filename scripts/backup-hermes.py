import os
import shutil
import subprocess
import re
from datetime import datetime

# --- CONFIGURATION ---
AGENT_NAME = "tom"
HERMES_HOME = os.path.expanduser("~/.hermes") # Or the actual home directory
BACKUP_DIR = "/tmp/hermes-backup"
LOG_FILE = f"/tmp/backup-{AGENT_NAME}.log"
LOCK_DIR = f"/tmp/backup-{AGENT_NAME}.lock"

# GitHub Config (To be filled/read from .env via the shell wrapper)
# GITHUB_TOKEN and REPO_URL will be passed via environment variables

# Scope definitions
INCLUDE_DIRS = ["skills", "scripts", "hooks", "plans", "memories", "cron"]
INCLUDE_FILES = ["config.yaml", "SOUL.md"]
EXCLUDE_PATTERNS = [".env", "state.db", "kanban.db", ".cache", "audio_cache", "image_cache"]

def log(message):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def sanitize_config(src, dst):
    with open(src, "r") as f:
        content = f.read()
    # Regex to find sensitive keys and replace their values with ""
    pattern = r'^([ \t]*[^:#]*(api_key|token|secret|password|credential|auth)[^:]*:[ \t]*).+$'
    sanitized = re.sub(pattern, r'\1""', content, flags=re.MULTILINE | re.IGNORECASE)
    with open(dst, "w") as f:
        f.write(sanitized)

def run_cmd(cmd, env=None):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, env=env)
    if result.returncode != 0:
        raise Exception(f"Command failed: {cmd}\nError: {result.stderr}")
    return result.stdout

def main():
    if os.path.exists(LOCK_DIR):
        log("Backup already running. Skipping.")
        return

    try:
        os.makedirs(LOCK_DIR)
        log("Starting backup process...")

        # 1. Setup Workdir
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR)
        os.makedirs(BACKUP_DIR)

        # 2. Collect Data
        # Files
        for file in INCLUDE_FILES:
            src = os.path.join(HERMES_HOME, file)
            if os.path.exists(src):
                dst = os.path.join(BACKUP_DIR, file)
                if file == "config.yaml":
                    sanitize_config(src, dst)
                else:
                    shutil.copy2(src, dst)

        # Directories
        for d in INCLUDE_DIRS:
            src = os.path.join(HERMES_HOME, d)
            if os.path.exists(src):
                dst = os.path.join(BACKUP_DIR, d)
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS))

        # 3. Git Operations
        token = os.getenv("GITHUB_TOKEN")
        repo_url = os.getenv("GITHUB_REPO") # e.g. github.com/user/repo.git

        if not token or not repo_url:
            raise Exception("GITHUB_TOKEN or GITHUB_REPO not found in environment")

        # Clone or Update
        auth_url = f"https://x-access-token:{token}@{repo_url.replace('https://', '')}"
        
        # We use a separate temp folder for the git repo to avoid cluttering the WORKDIR
        git_dir = "/tmp/hermes-backup-git"
        if os.path.exists(git_dir):
            shutil.rmtree(git_dir)
        
        run_cmd(f"git clone -q {auth_url} {git_dir}")
        
        # Sync content from BACKUP_DIR to git_dir
        for item in os.listdir(BACKUP_DIR):
            s = os.path.join(BACKUP_DIR, item)
            d = os.path.join(git_dir, item)
            if os.path.isdir(s):
                if os.path.exists(d): shutil.rmtree(d)
                shutil.copytree(s, d)
            else:
                shutil.copy2(s, d)

        # Commit and Push
        os.chdir(git_dir)
        run_cmd(f"git checkout -B main")
        run_cmd("git add .")
        
        # Only commit if there are changes
        diff = run_cmd("git diff --cached --quiet")
        if subprocess.run("git diff --cached --quiet", shell=True).returncode != 0:
            run_cmd(f"git commit -m 'backup: Hermes {AGENT_NAME} {datetime.now().strftime('%Y-%m-%d %H:%M')}'")
            run_cmd("git push -f origin main")
            log("Backup pushed to GitHub successfully.")
        else:
            log("No changes detected. Nothing to push.")

    except Exception as e:
        log(f"CRITICAL ERROR: {str(e)}")
        print(f"Backup failed: {str(e)}") # Print to stdout so cron notifies user
        raise e
    finally:
        shutil.rmtree(LOCK_DIR, ignore_errors=True)
        if os.path.exists(BACKUP_DIR):
            shutil.rmtree(BACKUP_DIR, ignore_errors=True)

if __name__ == "__main__":
    main()
