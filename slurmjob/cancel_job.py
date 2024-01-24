#!/usr/bin/env python3

import argparse
import paramiko
from pathlib import Path
import yaml

def load_config():
    package_root = Path(__file__).parent
    config_path = package_root / 'config.yml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Config not found, please run 'slurmjob config' first.")
        exit(1)
        
def cancel_slurm_job(ssh, job_id):
    # Function to cancel the job using the scancel command
    command = f"scancel {job_id}"
    stdin, stdout, stderr = ssh.exec_command(command)
    err = stderr.read().decode("utf-8")
    if err.strip() != "":
        print(f"Error cancelling job: {err}")
    else:
        print(f"Job {job_id} cancelled successfully")

def setup_ssh_and_cancel_job(settings, job_id):
    # Setup SSH connection and cancel the job
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(settings['hostname'], username=settings['username'], key_filename=settings['key_location'])
    
    cancel_slurm_job(ssh, job_id)
    ssh.close()

def main(job_id):
    settings = load_config()
    setup_ssh_and_cancel_job(settings, job_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cancel a Slurm job.")
    parser.add_argument("job_id", help="ID of the job to cancel")
    args = parser.parse_args()
    main(args.job_id)
