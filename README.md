# SlurmJob: Quick Interactive Job Setup and Monitoring

## Overview

SlurmJob is a Python package designed to simplify the process of setting up and monitoring interactive jobs on a Slurm cluster. It provides an CLI that abstracts away complex `srun` and `sbatch` commands, allows you to directly connect to your job via a VScode hyperlink, and keeps track of your job's status. The package also automatically constructs the `sbatch` command based on your requirements and stores it on the cluster via SSH.

## 🎉 v0.3.0: Flexible SBATCH Command Parameters

You can now pass additional SBATCH command parameters directly when running a job. This feature enhances the flexibility of job submission, allowing you to tailor job specifications dynamically, rather then creating new job templates for this.

### Example Usage:

```bash
slurmjob run <job_name> --<SBATCH_option1>=<value1> --<SBATCH_option2>=<value2>
```

This command will submit your job with the specified SBATCH options, such as `--qos=idle` or `--cpus-per-task=1-2`.

See here the list of all [SBATCH options](https://slurm.schedmd.com/sbatch.html).
## Behind the Scenes

### How it Works with SSH

When you use SlurmJob, it establishes an SSH connection to the Slurm cluster using the `paramiko` library. Through this SSH connection, it executes various Slurm commands and other shell commands:

- It creates necessary folders and files (like the logs folder and interactive sbatch jobs).
- It submits jobs using the `sbatch` command, now with additional parameters if provided.
- It monitors the job by tailing the Slurm log file with `tail`.

### Manual Equivalent in Slurm Commands

SlurmJob automates a series of steps that you'd otherwise perform manually. The typical manual steps would be:

1. SSH into the cluster.
2. Create a Slurm batch script (`*.sh`) file for your interactive job.
3. Submit this batch file using `sbatch`, now optionally with additional parameters.
4. Monitor job status with `squeue` and logs using `tail -f`.
5. Enter the ssh credentials of your interactive job into VScode.

### Understanding Job Monitoring

SlurmJob continually polls the last line of the Slurm job's log file, looking for a specific pattern to determine when the interactive job is ready. When the pattern is found, it generates a VScode URL which you can use to directly connect to your job.

## Installation

To install SlurmJob, you can use pip:

```bash
pip install git+https://github.com/daangeijs/deepops-slurmjob.git
```

Or to install it locally, you can clone the repository and run:

```bash
pip install .
```

## Commands

### 1. `slurmjob config`

Run this command to set up your initial configuration. You'll be prompted for your `hostname`, `username`, and `key_location`. Advanced settings are optional.

### 2. `slurmjob create`

This command will generate the `sbatch` script for your interactive job. It will prompt you for various job settings and then upload the script to the cluster.

### 3. `slurmjob run <name> [<SBATCH_options>]`

Use this command to run the interactive job that you've created. It will submit the job with any specified SBATCH options, monitor its status, and provide a VScode hyperlink for direct connection.

### 4. `slurmjob ls`

Lists all the existing job files you have in the job folder on your Slurm cluster.

## Configuration Settings

### Basic Config Settings

- **hostname**: The hostname of your Slurm cluster.
- **username**: Your username on the cluster.
- **key_location**: Location of your SSH private key.

### Advanced Config Settings

- **home_folder**: Your home folder on the cluster, default is "home/{username}".
- **log_location**: Where to store log files, default is "/home/{username}/logs".
- **job_location**: Where to store job files, default is "/home/{username}/jobs".
- **machine_prefix**: Prefix for the cluster machine, default is "dlc-".
- **sbatch_command**: The `sbatch` command to run, default is "sbatch {job_location}/{job_name}.sh".

## Interactive Job Setup Variables

When running `slurmjob create`, you'll be prompted for the following:

- **ntasks**: The number of tasks to be allocated for the job.
- **gpus-per-task**: The number of GPUs per task (default is 0).
- **cpus-per-task**: The number of CPUs per task (default is 4).
- **mem**: The amount of memory required for the job (default is 8G).
- **time**: The time limit for the job (default is 4:00:00).
- **container-mounts**: Paths to mount into the job's container.
- **container-image**: The container image to use for the job.
- **output**: The location for output logs (This is set automatically from your config).
- **SSH port**: The port to be used for SSH within the job.

## Security Note

### SSH Keypair Setup

To securely connect to your Slurm host, you'll need to set up an SSH keypair. Follow these steps:

1. On your local machine, generate an SSH keypair:

    ```bash
    ssh-keygen -t rsa -f ~/.ssh/id_rsa
    ```

2. Add your public key (`~/.ssh/id_rsa.pub`) to the `~/.ssh/authorized_keys` file on your Slurm host. You can do this manually or use `ssh-copy-id`:

    ```bash
    ssh-copy-id -i ~/.ssh/id_rsa user@host
    ```
    Replace `username` and `hostname` with your Slurm host username and hostname.

### Update Local SSH Config

Add an entry for your Slurm host in your local `~/.ssh/config` file. Here's a sample configuration:

    ```
    Host my-slurm-host
      HostName your.slurm.hostname
      User your-username
      IdentityFile ~/.ssh/id_rsa
    ```

Replace `your.slurm.hostname` with your Slurm host's hostname and `your-username` with your username on that host. This configuration will let you SSH into your Slurm host using the keypair.