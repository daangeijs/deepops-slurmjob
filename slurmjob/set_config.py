#!/usr/bin/env python3

import os
import yaml

def save_config(settings):
    package_root = os.path.dirname(__file__)
    config_path = os.path.join(package_root, 'config.yml')
    with open(config_path, 'w') as f:
        yaml.dump(settings, f)

def load_config():
    if os.path.exists('config.yml'):
        with open('config.yml', 'r') as f:
            return yaml.safe_load(f)
    return {}

def main():
    existing_config = load_config()

    hostname = input(f"Enter the hostname [{existing_config.get('hostname', '')}]: ") or existing_config.get('hostname', '')
    username = input(f"Enter the username [{existing_config.get('username', '')}]: ") or existing_config.get('username', '')
    key_location = input(f"Enter the location of SSH private key [{existing_config.get('key_location', '')}]: ") or existing_config.get('key_location', '')

    settings = {
        'hostname': hostname,
        'username': username,
        'key_location': key_location
    }

    advanced = input("Setup advanced config? (yes/no) [no]: ")

    if advanced.lower() == 'yes':
        default_home_folder = f"/home/{username}"
        home_folder = input(f"Enter the home folder [{existing_config.get('home_folder', default_home_folder)}]: ") or existing_config.get('home_folder', default_home_folder)

        default_log_location = f"{home_folder}/logs"
        log_location = input(f"Enter the log location [{existing_config.get('log_location', default_log_location)}]: ") or existing_config.get('log_location', default_log_location)

        default_job_location = f"{home_folder}/jobs"
        job_location = input(f"Enter the job location [{existing_config.get('job_location', default_job_location)}]: ") or existing_config.get('job_location', default_job_location)

        default_machine_prefix = "dlc-"
        machine_prefix = input(f"Enter the machine prefix [{existing_config.get('machine_prefix', default_machine_prefix)}]: ") or existing_config.get('machine_prefix', default_machine_prefix)

        default_sbatch_command = f"sbatch {job_location}/{{job_name}}.sh"
        sbatch_command = input(f"Enter the sbatch command [{existing_config.get('sbatch_command', default_sbatch_command)}]: ") or existing_config.get('sbatch_command', default_sbatch_command)

        settings.update({
            'home_folder': home_folder,
            'log_location': log_location,
            'job_location': job_location,
            'machine_prefix': machine_prefix,
            'sbatch_command': sbatch_command
        })

    else:
        # Use default settings
        default_home_folder = f"/home/{username}"
        default_log_location = f"{default_home_folder}/logs"
        default_job_location = f"{default_home_folder}/jobs"
        default_machine_prefix = "dlc-"
        default_sbatch_command = f"sbatch {default_job_location}/{{job_name}}.sh"

        settings.update({
            'home_folder': default_home_folder,
            'log_location': default_log_location,
            'job_location': default_job_location,
            'machine_prefix': default_machine_prefix,
            'sbatch_command': default_sbatch_command
        })

    save_config(settings)
    print("Config saved.")

if __name__ == '__main__':
    main()
