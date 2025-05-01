#!/usr/bin/env python3
"""
start_services.py

This script starts the Supabase stack first, waits for it to initialize, and then starts
the core services (n8n, Caddy, Redis, Evolution API).
"""

import os
import subprocess
import shutil
import time
import argparse
import sys

def run_command(cmd, cwd=None):
    """Run a shell command and print it."""
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)

def clone_supabase_repo():
    """Clone the Supabase repository using sparse checkout if not already present."""
    if not os.path.exists("supabase"):
        print("Cloning the Supabase repository...")
        run_command([
            "git", "clone", "--filter=blob:none", "--no-checkout",
            "https://github.com/supabase/supabase.git"
        ])
        os.chdir("supabase")
        run_command(["git", "sparse-checkout", "init", "--cone"])
        run_command(["git", "sparse-checkout", "set", "docker"])
        run_command(["git", "checkout", "master"])
        os.chdir("..")
    else:
        print("Supabase repository already exists, updating...")
        os.chdir("supabase")
        run_command(["git", "pull"])
        os.chdir("..")

def prepare_supabase_env():
    """Copy .env to .env in supabase/docker."""
    env_path = os.path.join("supabase", "docker", ".env")
    env_example_path = os.path.join(".env")
    print("Copying .env in root to .env in supabase/docker...")
    shutil.copyfile(env_example_path, env_path)

def stop_existing_containers():
    """Stop and remove existing containers for our unified project ('localai')."""
    print("Stopping and removing existing containers for the unified project 'localai'...")
    run_command([
        "docker", "compose",
        "-p", "localai",
        "-f", "docker-compose.yml",
        "-f", "supabase/docker/docker-compose.yml",
        "down"
    ])

def start_supabase():
    """Start the Supabase services (using its compose file)."""
    print("Starting Supabase services...")
    run_command([
        "docker", "compose", "-p", "localai", "-f", "supabase/docker/docker-compose.yml", "up", "-d"
    ])

def start_core_services():
    """Start the core services (n8n, Caddy, Redis, Evolution API)."""
    print("Starting core services...")
    cmd = ["docker", "compose", "-p", "localai", "-f", "docker-compose.yml", "up", "-d"]
    run_command(cmd)

def check_evolution_api_directories():
    """Create necessary directories for Evolution API if they don't exist."""
    print("Checking Evolution API directories...")
    shared_dir = os.path.join(os.getcwd(), "shared")
    if not os.path.exists(shared_dir):
        print(f"Creating shared directory at {shared_dir}")
        os.makedirs(shared_dir)

def update_caddyfile():
    """Update Caddyfile to include only the necessary services."""
    caddyfile_path = os.path.join(os.getcwd(), "Caddyfile")
    if not os.path.exists(caddyfile_path):
        print("Creating Caddyfile template...")
        with open(caddyfile_path, 'w') as f:
            f.write("""# Global options
{
	email {$LETSENCRYPT_EMAIL}
}

# n8n
{$N8N_HOSTNAME} {
	reverse_proxy localhost:5678
}

# Supabase
{$SUPABASE_HOSTNAME} {
	reverse_proxy localhost:3000
}

# Evolution API
{$EVOLUTION_API_HOSTNAME} {
	reverse_proxy localhost:8080
}
""")
        print(f"Created Caddyfile at {caddyfile_path}")
    else:
        print(f"Caddyfile already exists at {caddyfile_path}")

def main():
    parser = argparse.ArgumentParser(description='Start Supabase and core services.')
    args = parser.parse_args()

    clone_supabase_repo()
    prepare_supabase_env()
    
    # Check and create necessary directories
    check_evolution_api_directories()
    
    # Update Caddyfile
    update_caddyfile()
    
    stop_existing_containers()
    
    # Start Supabase first
    start_supabase()
    
    # Give Supabase some time to initialize
    print("Waiting for Supabase to initialize...")
    time.sleep(10)
    
    # Then start the core services
    start_core_services()
    
    print("\nServices started successfully!")
    print("Access points:")
    print("- n8n: http://localhost:5678")
    print("- Supabase: http://localhost:3000")
    print("- Evolution API: http://localhost:8080")
    print("\nFor HTTPS access, configure your .env file with proper hostnames and restart.")

if __name__ == "__main__":
    main()