import os
import logging
from invoke import task, Context
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# SSH Tunnel settings
TUNNEL_PORT = os.getenv("PGPORT", "5433")
REMOTE_PORT = os.getenv("REMOTE_PORT", "5432")
SSH_USER = os.getenv("SSH_USER")
SSH_HOST = os.getenv("SSH_HOST")

# DBT project path
DBT_PROJECT_DIR = "concert_analytics_dbt"

# DBT environment variables
DBT_ENV = {
    "DBT_HOST": os.getenv("PGHOST", "localhost"),
    "DBT_PORT": os.getenv("PGPORT", TUNNEL_PORT),
    "DBT_USER": os.getenv("PGUSER"),
    "DBT_PASSWORD": os.getenv("PGPASSWORD"),
    "DBT_DB": os.getenv("DBT_DB"),
    "DBT_SCHEMA": os.getenv("DBT_SCHEMA"),
}

@task
def tunnel(c: Context):
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Start SSH tunnel if in local environment"""
    environment = os.getenv("ENVIRONMENT", "local")
    if environment == "server":
        log.info("🏗️ Running on server — skipping SSH tunnel")
        return

    result = c.run(f"lsof -i TCP:{TUNNEL_PORT} | grep ssh", warn=True, hide=True)
    if result.ok:
        log.info(f"🔌 Tunnel already running on port {TUNNEL_PORT}")
    else:
        log.info(f"🚀 Starting SSH tunnel to {SSH_USER}@{SSH_HOST}...")
        c.run(f"ssh -f -N -L {TUNNEL_PORT}:localhost:{REMOTE_PORT} {SSH_USER}@{SSH_HOST}")
        log.info(f"🔐 Tunnel established at localhost:{TUNNEL_PORT}")

def run_dbt_command(c: Context, command: str):
    """Run a dbt command inside the dbt project folder"""
    home = os.path.expanduser("~")
    target_profile = os.path.join(home, ".dbt", "profiles.yml")

    # Only call setup_profile if the symlink is missing or broken
    result = c.run(f"test -L {target_profile} && test -e {target_profile}", warn=True, hide=True)
    if not result.ok:
        log.info("🧪 DBT profile symlink missing or broken — running setup...")
        setup_profile(c)

    log.info(f"🏃 Running dbt {command}")
    with c.cd(DBT_PROJECT_DIR):
        c.run(f"dbt {command}", env=DBT_ENV)

@task(pre=[tunnel])
def run(c: Context, selector=""):
    """
    Run `dbt run`, optionally with a --select selector (e.g. tag:analytics_project)
    Usage: inv run --selector=tag:analytics_project
    """
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    select_arg = f"--select {selector}" if selector else ""
    run_dbt_command(c, f"run {select_arg}")

@task(pre=[tunnel])
def build(c: Context):
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Run dbt build"""
    run_dbt_command(c, "build")

@task(pre=[tunnel])
def test(c: Context):
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Run dbt test"""
    run_dbt_command(c, "test")

@task(pre=[tunnel])
def deps(c: Context):
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Run dbt deps"""
    run_dbt_command(c, "deps")

@task(pre=[tunnel])
def bootstrap(c: Context):
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Create required schemas and database functions for a rebuild."""
    run_dbt_command(c, "run-operation bootstrap_database")

@task(pre=[tunnel])
def dbt(c: Context, command="run"):
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Run arbitrary dbt command (e.g. --select my_model)"""
    run_dbt_command(c, command)

@task(name="close")
def kill_tunnel(c: Context):
    """Kill the SSH tunnel on the local machine"""
    port = os.getenv("TUNNEL_PORT", "5433")
    log.info(f"🔍 Checking for SSH tunnel on port {port}...")
    result = c.run(f"lsof -ti tcp:{port}", warn=True, hide=True)
    if result.ok:
        log.info("🛑 Killing tunnel...")
        c.run(f"lsof -ti tcp:{port} | xargs kill", warn=True)
        log.info("✅ Tunnel closed.")
    else:
        log.info("💤 No tunnel process found. Nothing to kill.")

@task
def setup_profile(c: Context):
    """Ensure ~/.dbt/profiles.yml points to the version-controlled config"""
    log.info("🔧 Setting up dbt profile symlink")
    home = os.path.expanduser("~")
    dbt_dir = os.path.join(home, ".dbt")
    target_profile = os.path.join(dbt_dir, "profiles.yml")
    source_profile = os.path.join(os.getcwd(), "concert_analytics_dbt", "config", "profiles.yml")

    c.run(f"mkdir -p {dbt_dir}")

    # If the file exists and is not a symlink, back it up
    result = c.run(f"test -f {target_profile} && [ ! -L {target_profile} ]", warn=True, hide=True)
    if result.ok:
        backup_path = f"{target_profile}.backup"
        log.info(f"🗂️ Backing up existing profiles.yml to {backup_path}")
        c.run(f"mv {target_profile} {backup_path}")

    # Create or replace the symlink
    c.run(f"ln -sf {source_profile} {target_profile}")
    log.info(f"✅ Symlink created: {target_profile} → {source_profile}")
