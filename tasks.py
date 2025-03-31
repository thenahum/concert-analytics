# tasks.py
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
    log.info(f"🏃 Running dbt {command}")
    with c.cd(DBT_PROJECT_DIR):
        c.run(f"dbt {command}", env=DBT_ENV)

@task(pre=[tunnel])
def run(c: Context):
    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Run dbt run"""
    run_dbt_command(c, "run")

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