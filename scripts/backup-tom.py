#!/usr/bin/env python3
"""backup-tom.py - faz o backup para GitHub. Chamado por backup-tom.sh ou cron."""
import os, sys, subprocess, re, shutil, tempfile, datetime

HERMES_HOME = os.environ.get('HERMES_HOME', '/opt/data')
REPO_SLUG = 'rodrigolimasl/tom-hermes'
BACKUP_DIR = os.path.join(HERMES_HOME, 'backups')
WORKDIR = os.path.join(BACKUP_DIR, 'tom-hermes')
LOG = os.path.join(BACKUP_DIR, 'backup-tom.log')
AGENT = 'Tom'

def log(msg):
    ts = datetime.datetime.now().strftime('%F %T')
    with open(LOG, 'a') as f:
        f.write(f'{ts} {msg}\n')

def run(cmd, **kw):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)

def extract_token(env_path):
    if not os.path.exists(env_path):
        return None
    token_key = "GITHUB_TOKEN"
    with open(env_path) as f:
        for line in f:
            if line.startswith(token_key + '='):
                val = line.split('=', 1)[1]
                return val.strip().strip('"').strip("'").strip()
    return None

def sanitize_yaml(yaml_path, out_path):
    keys = ['api_key', 'token', 'secret', 'password', 'credential', 'auth']
    pattern = '(' + '|'.join(keys) + '):\\s*\\S+'
    with open(yaml_path) as f:
        content = f.read()
    def replacer(m):
        full = m.group(0)
        return full.rsplit(':', 1)[0] + ': ""'
    cleaned = re.sub(pattern, replacer, content, flags=re.I)
    with open(out_path, 'w') as f:
        f.write(cleaned)

def main():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    token = extract_token(os.path.join(HERMES_HOME, '.env'))
    if not token:
        print(f'[{AGENT}] ERRO: GITHUB_TOKEN ausente')
        log('ERRO: token ausente')
        return 1
    
    # Configure Git credentials via environment
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    env['GIT_ASKPASS_URL'] = token
    
    # Create askpass helper
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as askpass:
        askpass.write('#!/usr/bin/env bash\n')
        askpass.write('case "$1" in\n')
        askpass.write('  *Username*) echo "x-access-token" ;;\n')
        askpass.write('  *Password*) echo "$GIT_ASKPASS_URL" ;;\n')
        askpass.write('esac\n')
        askpass_path = askpass.name
    os.chmod(askpass_path, 0o700)
    env['GIT_ASKPASS'] = askpass_path
    
    try:
        # Safe directory
        run(f'git config --global --add safe.directory {WORKDIR}', env=env)
        
        # Clone if needed
        needs_clone = not os.path.isdir(os.path.join(WORKDIR, '.git'))
        if needs_clone:
            clone = run(f'git clone -q https://github.com/{REPO_SLUG}.git {WORKDIR}', env=env)
            if clone.returncode == 0:
                pass  # clone já traz tudo
            else:
                # First backup - init empty repo
                run(f'git -C {WORKDIR} init -q', env=env)
                run(f'git -C {WORKDIR} remote add origin https://github.com/{REPO_SLUG}.git', env=env)
        
        # Always sync with remote before we work (handles init-without-clone case)
        run(f'git -C {WORKDIR} fetch -q origin', env=env)
        run(f'git -C {WORKDIR} checkout -q -B main origin/main', env=env)
        
        # Clean worktree
        for item in os.listdir(WORKDIR):
            if item == '.git':
                continue
            path = os.path.join(WORKDIR, item)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        
        # Copy config.yaml sanitized
        config_src = os.path.join(HERMES_HOME, 'config.yaml')
        config_dst = os.path.join(WORKDIR, 'config.yaml')
        if os.path.exists(config_src):
            sanitize_yaml(config_src, config_dst)
        
        # Copy SOUL
        for s in ['SOUL', 'SOUL.md', 'soul.md']:
            src = os.path.join(HERMES_HOME, s)
            if os.path.exists(src):
                shutil.copy2(src, WORKDIR)
        
        # Copy directories
        for d in ['skills', 'scripts', 'hooks', 'plans']:
            src = os.path.join(HERMES_HOME, d)
            dst = os.path.join(WORKDIR, d)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
        
        # Copy cron definitions
        cron_src = os.path.join(HERMES_HOME, 'cron')
        if os.path.isdir(cron_src):
            for root, dirs, files in os.walk(cron_src):
                for fn in files:
                    if fn.endswith(('.json', '.yaml', '.yml', '.md')):
                        src_file = os.path.join(root, fn)
                        rel = os.path.relpath(src_file, HERMES_HOME)
                        dst_file = os.path.join(WORKDIR, rel)
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy2(src_file, dst_file)
        
        # Copy memories
        mem_src = os.path.join(HERMES_HOME, 'memories')
        if os.path.isdir(mem_src):
            for root, dirs, files in os.walk(mem_src):
                for fn in files:
                    if fn.endswith('.md'):
                        src_file = os.path.join(root, fn)
                        rel = os.path.relpath(src_file, HERMES_HOME)
                        dst_file = os.path.join(WORKDIR, rel)
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy2(src_file, dst_file)
        
        # README
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M %Z')
        readme = f"""# Backup operacional — Hermes ({AGENT})
Espelho seletivo do estado operacional do Hermes. NÃO é backup do sistema inteiro.
- Último backup: {now}
- Incluído: config.yaml (sanitizado), SOUL, skills/, scripts/, hooks/, plans/, cron/ (defs), memories/**/*.md
- Excluído: .env, tokens, credenciais, sessões, logs, caches, locks, state DB, temporários
"""
        with open(os.path.join(WORKDIR, 'README.md'), 'w') as f:
            f.write(readme)
        
        # Git commit and push
        os.chdir(WORKDIR)
        run('git add -A', env=env)
        diff = run('git diff --cached --quiet', env=env)
        if diff.returncode == 0:
            log('sem mudanças')
            return 0
        
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        run(f'git -c user.name="hermes-backup" -c user.email="backup@tom" commit -qm "backup: Hermes {AGENT} {now_str} Manaus"', env=env)
        
        # Rebase on latest to avoid non-fast-forward; force push (backup unilateral)
        run('git pull --rebase -q origin main', env=env)
        res = run('git push -f -q origin main', env=env)
        if res.returncode != 0:
            print(f'[{AGENT}] PUSH FAILED: {res.stderr.strip()}')
            log(f'PUSH FAILED: {res.stderr.strip()}')
            return 1
        
        log(f'backup enviado para {REPO_SLUG}')
        return 0
    finally:
        try:
            os.unlink(askpass_path)
        except:
            pass

if __name__ == '__main__':
    sys.exit(main())