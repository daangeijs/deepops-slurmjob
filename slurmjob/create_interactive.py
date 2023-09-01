#!/usr/bin/env python3

from pathlib import Path
import yaml
import paramiko

def load_config():
    package_root = Path(__file__).parent
    config_path = package_root / 'config.yml'
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Config not found, please run 'slurmjob config' first.")
        exit(1)

def create_remote_directory(ftp, directory):
    try:
        ftp.mkdir(directory)
    except IOError:
        pass

def main():
    config = load_config()

    # Set up directories and sbatch template values
    log_directory = config['log_location']
    job_directory = config['job_location']

    ntasks = input("Enter the number of tasks [1]: ") or "1"
    gpus_per_task = input("Enter the number of gpus per task [0]: ") or "0"
    cpus_per_task = input("Enter the number of cpus per task [4]: ") or "4"
    mem = input("Enter the memory [8G]: ") or "8G"
    time = input("Enter the time [4:00:00]: ") or "4:00:00"
    container_mounts = input("Enter the container mounts (e.g., /my/volume:/volume/in_docker): ")
    container_image = input("Enter the container image (e.g., my-registry#name:tag)")
    port = input("Enter the port for SSH: ")
    job_name = input("Enter the name for your interactive job: ")

    script_content = f"""#!/bin/bash
#SBATCH --ntasks={ntasks}
#SBATCH --gpus-per-task={gpus_per_task}
#SBATCH --cpus-per-task={cpus_per_task}
#SBATCH --mem={mem}
#SBATCH --time={time}
#SBATCH --container-mounts={container_mounts}
#SBATCH --container-image="{container_image}"
#SBATCH --output={log_directory}/slurm-%j.out
echo "Started SSH on port {port}"
/usr/sbin/sshd -D -p {port}
"""

    # Connect to the remote host
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(config['hostname'], username=config['username'], key_filename=config['key_location'])

    ftp = ssh.open_sftp()

    # Create necessary directories if they don't exist
    create_remote_directory(ftp, log_directory)
    create_remote_directory(ftp, job_directory)

    # Save the sbatch script
    script_filename = f"{job_name}.sh"
    with ftp.file(f"{job_directory}/{script_filename}", 'w') as f:
        f.write(script_content)

    ftp.close()
    ssh.close()

    print(f"sbatch template generated and saved as '{script_filename}' in the remote {job_directory}.")

if __name__ == '__main__':
    main()
