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
        print("Config not found, please run 'runjob config' first.")
        exit(1)

def list_jobs(hostname, username, key_location, job_location):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(hostname, username=username, key_filename=key_location)

    # List the files in the jobs folder
    command = f"ls {job_location}"
    stdin, stdout, stderr = ssh.exec_command(command)
    files = stdout.read().decode("utf-8").strip().split("\n")

    # Strip off the file extensions
    job_names = [Path(file).stem for file in files]
    return job_names

def main():
    config = load_config()
    job_names = list_jobs(config['hostname'], config['username'], config['key_location'], config['job_location'])
    print("Jobs available:")
    for job_name in job_names:
        print(f"  {job_name}")
        
        
if __name__ == '__main__':
    main()