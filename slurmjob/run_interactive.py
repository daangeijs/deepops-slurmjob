#!/usr/bin/env python3

import argparse
import paramiko
import time
import re
import threading
import yaml
import signal
from pathlib import Path, PurePosixPath

from scancel import cancel_slurm_job


def load_config():
    package_root = Path(__file__).parent
    config_path = package_root / 'config.yml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Config not found, please run 'runjob config' first.")
        exit(1)
        
def signal_handler(signum, frame, ssh, job_id):
    # This function will be called when Ctrl+C is pressed
    cancel_slurm_job(ssh, job_id)
    exit(0)    
        
def poll_log_for_pattern(ssh, log_file, pattern, found_event):
    seen_lines = set()
    while not found_event.is_set():
        current_last_line = get_last_line(ssh, log_file)
        if current_last_line not in seen_lines:
            print(current_last_line)
            seen_lines.add(current_last_line)
            if pattern.search(current_last_line):
                found_event.set()
                return
        time.sleep(1)

def get_last_line(ssh, log_file):
    log_file = PurePosixPath(log_file)
    command = f"tail -n 1 {log_file}"
    stdin, stdout, stderr = ssh.exec_command(command)
    return stdout.read().decode("utf-8").strip()

def get_machine_attached_to_job(ssh, job_id, machine_prefix):
    while True:
        stdin, stdout, stderr = ssh.exec_command(f"squeue -h -j {job_id}")
        output = stdout.read().decode("utf-8")
        if output.strip() != "":
            machine_name = output.split()[-1]
            if machine_name.startswith(machine_prefix):
                return machine_name
        time.sleep(5)

def create_log_folder(ssh, log_location):
    stdin, stdout, stderr = ssh.exec_command(f"mkdir -p {log_location}")

def submit_slurm_job(ssh, sbatch_command):
    stdin, stdout, stderr = ssh.exec_command(sbatch_command)
    err = stderr.read().decode("utf-8")
    print(err)
    if err.strip() != "":
        raise Exception(f"Error submitting job: {err}")
    else:
        job_submission_output = stdout.read().decode("utf-8")
        job_id = job_submission_output.split()[-1]
        print(f"Submitted batch job {job_id}")
        return job_id

def setup_ssh_and_submit_job(settings, job_name, sbatch_args):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(settings['hostname'], username=settings['username'], key_filename=settings['key_location'])
    create_log_folder(ssh, settings['log_location'])
    sbatch_command = f"sbatch {sbatch_args} {settings['job_location']}/{job_name}.sh"
    job_id = submit_slurm_job(ssh, sbatch_command)
    
    # Setup Ctrl+C handler
    signal.signal(signal.SIGINT, lambda signum, frame: signal_handler(signum, frame, ssh, job_id))
    
    machine_name = get_machine_attached_to_job(ssh, job_id, settings['machine_prefix'])
    print(f"Job {job_id} is running on {machine_name}")

    log_file = PurePosixPath(settings['log_location']) / Path(f"slurm-{job_id}.out")
    ssh_config_pattern = re.compile(r"Started SSH on port (\d+)")

    pattern_found_event = threading.Event()
    poll_thread = threading.Thread(
        target=poll_log_for_pattern,
        args=(ssh, log_file, ssh_config_pattern, pattern_found_event),
    )
    poll_thread.start()

    while not pattern_found_event.is_set():
        time.sleep(1)

    last_line = get_last_line(ssh, log_file)
    match = ssh_config_pattern.search(last_line)
    if match:
        port_number = match.group(1)
        print("Interactive session started")
        vscode_link = f"vscode://vscode-remote/ssh-remote+{settings['username']}@{machine_name}:{port_number}{settings['home_folder']}?ssh={settings['key_location']}"        
        # Write the VSCode link to the log file
        stdin, stdout, stderr = ssh.exec_command(f"echo '{vscode_link}' >> {log_file}")
        print(vscode_link)

    ssh.close()
    
def main(args, sbatch_args):
    settings = load_config()
    setup_ssh_and_submit_job(settings, args, sbatch_args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a job.")
    parser.add_argument("--job_name", help="Name of the job to run")
    parser.add_argument('sbatch_args', nargs=argparse.REMAINDER, 
                        help="Additional SBATCH arguments")
    args = parser.parse_args()
    main(args.job_name, ' '.join(args.sbatch_args))
