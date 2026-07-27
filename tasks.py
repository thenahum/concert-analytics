import os
import logging
import shlex
from pathlib import Path
from invoke import task, Context
from dotenv import load_dotenv

# Configure logger
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

# DBT project path
DBT_PROJECT_DIR = "concert_analytics_dbt"
DEFAULT_NOTEBOOK_PATH = "projects/0003-Taylor-Swift-Eras-Tour/notebooks/eras_tour_analysis.ipynb"


def load_repo_env() -> None:
    """Load the repository .env only when a task needs runtime configuration."""
    load_dotenv(dotenv_path=Path(__file__).with_name(".env"))


def dbt_env() -> dict[str, str]:
    """Build dbt's environment from current process settings."""
    load_repo_env()
    pg_port = os.getenv("PGPORT", "5433")
    env = {
        "DBT_HOST": os.getenv("PGHOST", "localhost"),
        "DBT_PORT": pg_port,
        "DBT_USER": os.getenv("PGUSER"),
        "DBT_PASSWORD": os.getenv("PGPASSWORD"),
        "DBT_DB": os.getenv("DBT_DB") or os.getenv("PGDATABASE"),
        "DBT_SCHEMA": os.getenv("DBT_SCHEMA", "public"),
    }
    return {key: value for key, value in env.items() if value is not None}


def require_env_vars(names: list[str]) -> None:
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        rendered = ", ".join(missing)
        raise RuntimeError(f"Missing required environment variable(s): {rendered}")


def dbt_executable() -> str:
    local_dbt = Path(__file__).parent / ".venv" / "bin" / "dbt"
    if local_dbt.exists():
        return quote_path(local_dbt)
    return "dbt"


def python_executable() -> str:
    local_python = Path(__file__).parent / ".venv" / "bin" / "python"
    if local_python.exists():
        return quote_path(local_python)
    return "python"


def quote_path(path: str | Path) -> str:
    return shlex.quote(str(path))

@task
def tunnel(c: Context):
    load_repo_env()
    tunnel_port = os.getenv("PGPORT", "5433")
    remote_port = os.getenv("REMOTE_PORT", "5432")
    ssh_user = os.getenv("SSH_USER")
    ssh_host = os.getenv("SSH_HOST")

    log.info(f"🌍 Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    """Start SSH tunnel if in local environment"""
    environment = os.getenv("ENVIRONMENT", "local")
    if environment == "server":
        log.info("🏗️ Running on server — skipping SSH tunnel")
        return

    require_env_vars(["SSH_USER", "SSH_HOST"])

    result = c.run(f"lsof -i TCP:{shlex.quote(tunnel_port)} | grep ssh", warn=True, hide=True)
    if result.ok:
        log.info(f"🔌 Tunnel already running on port {tunnel_port}")
    else:
        log.info(f"🚀 Starting SSH tunnel to {ssh_user}@{ssh_host}...")
        c.run(
            "ssh -f -N "
            f"-L {shlex.quote(tunnel_port)}:localhost:{shlex.quote(remote_port)} "
            f"{shlex.quote(ssh_user)}@{shlex.quote(ssh_host)}"
        )
        log.info(f"🔐 Tunnel established at localhost:{tunnel_port}")

def run_dbt_command(c: Context, command: str, *, setup_profiles: bool = True):
    """Run a dbt command inside the dbt project folder"""
    home = os.path.expanduser("~")
    target_profile = os.path.join(home, ".dbt", "profiles.yml")

    # Only call setup_profile if the symlink is missing or broken
    result = c.run(f"test -L {quote_path(target_profile)} && test -e {quote_path(target_profile)}", warn=True, hide=True)
    if setup_profiles and not result.ok:
        log.info("🧪 DBT profile symlink missing or broken — running setup...")
        setup_profile(c)

    log.info(f"🏃 Running dbt {command}")
    with c.cd(DBT_PROJECT_DIR):
        c.run(f"{dbt_executable()} {command}", env=dbt_env())

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

@task(name="dbt-parse")
def dbt_parse(c: Context):
    """Parse dbt project files without starting a tunnel or changing ~/.dbt."""
    run_dbt_command(c, "parse", setup_profiles=False)

@task(name="dbt-ls")
def dbt_ls(c: Context, selector=""):
    """List dbt nodes without starting a tunnel or changing ~/.dbt."""
    select_arg = f"--select {selector}" if selector else ""
    run_dbt_command(c, f"ls {select_arg}", setup_profiles=False)


@task(name="notebook-sync")
def notebook_sync(c: Context, path=DEFAULT_NOTEBOOK_PATH):
    """Sync a paired Jupytext notebook and py:percent file."""
    notebook_path = Path(path)
    if not notebook_path.exists():
        raise RuntimeError(f"Notebook path does not exist: {notebook_path}")

    log.info(f"📓 Syncing Jupytext pair for {notebook_path}")
    c.run(f"{python_executable()} -m jupytext --sync {quote_path(notebook_path)}")


@task(name="close")
def kill_tunnel(c: Context):
    """Kill the SSH tunnel on the local machine"""
    load_repo_env()
    port = os.getenv("TUNNEL_PORT") or os.getenv("PGPORT", "5433")
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
    load_repo_env()
    log.info("🔧 Setting up dbt profile symlink")
    home = os.path.expanduser("~")
    dbt_dir = os.path.join(home, ".dbt")
    target_profile = os.path.join(dbt_dir, "profiles.yml")
    source_profile = os.path.join(os.getcwd(), "concert_analytics_dbt", "config", "profiles.yml")

    c.run(f"mkdir -p {quote_path(dbt_dir)}")

    # If the file exists and is not a symlink, back it up
    result = c.run(f"test -f {quote_path(target_profile)} && [ ! -L {quote_path(target_profile)} ]", warn=True, hide=True)
    if result.ok:
        backup_path = f"{target_profile}.backup"
        log.info(f"🗂️ Backing up existing profiles.yml to {backup_path}")
        c.run(f"mv {quote_path(target_profile)} {quote_path(backup_path)}")

    # Create or replace the symlink
    c.run(f"ln -sf {quote_path(source_profile)} {quote_path(target_profile)}")
    log.info(f"✅ Symlink created: {target_profile} → {source_profile}")
