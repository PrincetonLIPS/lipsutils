import dataclasses
import os 
from pathlib import Path
import subprocess
from typing import Optional

import tyro 

@dataclasses.dataclass
class CLIArgs: 
    node: str 
    cpus: Optional[int] = 1 
    memory: Optional[str]="32G"
    gpus: Optional[int] = 0 
    account: Optional[str] = "lips" 
    reservation: Optional[str] = "lips-interactive" 

def validate_args(config: CLIArgs): 
    if (config.cpus >= 64) or (config.cpus < 1): 
        raise ValueError(f"Must request a number of cpus between 1 and 64 inclusive, but asked for {config.cpus}")
    if (config.gpus >= 8) or (config.gpus < 0): 
        raise ValueError(f"Must request a number of gpus between 0 and 8 inclusive, but asked for {config.gpus}")

def main(config: CLIArgs): 
    validate_args(config)
    args = [
        "salloc", 
        f"--gres=gpu:{config.gpus}", 
        "-c", 
        f"{config.cpus}", 
        "-A",
        f"{config.account}", 
        f"--reservation={config.reservation}", 
        f"--nodelist={config.node}", 
        f"--mem={config.memory}", 
        "srun", 
        "--pty", 
        f"{os.environ['SHELL']}", 
        "-l"
    ]
    subprocess.run(args)

if __name__=="__main__": 
    config = tyro.cli(CLIArgs)
    main(config)
