import argparse
from slurmjob import create_interactive, run_interactive, set_config, list_files, cancel_job

def main():
    parser = argparse.ArgumentParser(description="Manage Slurm jobs.")
    subparsers = parser.add_subparsers(dest="command")

    parser_config = subparsers.add_parser("config", help="Configure Slurm settings.")
    
    parser_create = subparsers.add_parser("create", help="Create a new interactive Slurm job.")
    
    parser_ls = subparsers.add_parser("ls", help="List available Slurm jobs.")
    
    parser_run = subparsers.add_parser("run", help="Run a Slurm job.")
    parser_run.add_argument("name", type=str, help="Name of the job to run.")
    parser_run.add_argument('sbatch_args', nargs=argparse.REMAINDER, 
                            help="Additional SBATCH arguments")

    parser_cancel = subparsers.add_parser("cancel", help="Cancel a Slurm job.")
    parser_cancel.add_argument("job_id", type=str, help="ID of the job to cancel.")

    args = parser.parse_args()

    if args.command == "config":
        set_config.main()
    elif args.command == "create":
        create_interactive.main()
    elif args.command == "run":
        sbatch_args = ' '.join(args.sbatch_args)
        run_interactive.main(args.name, sbatch_args)
    elif args.command == "ls":
        list_files.main()
    elif args.command == "cancel":
        cancel_job.main(args.job_id)