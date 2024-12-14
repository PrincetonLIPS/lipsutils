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
    memory: Optional[str] = "32G"
    gpus: Optional[int] = 0
    account: Optional[str] = "lips"
    reservation: Optional[str] = "lips-interactive"


def validate_args(config: CLIArgs):
    if (config.cpus >= 64) or (config.cpus < 1):
        raise ValueError(
            f"Must request a number of cpus between 1 and 64 inclusive, but asked for {config.cpus}"
        )
    if (config.gpus > 8) or (config.gpus < 0):
        raise ValueError(
            f"Must request a number of gpus between 0 and 8 inclusive, but asked for {config.gpus}"
        )


def main(config: CLIArgs):
    """Basic driver for a call to salloc to request an interactive reservation on our lips-interactive daily
    flex reservation.

    Parameters
    ----------
    config.node : str
        The node identifier (see `lipsutils.ionic_info.main`)
    config.cpus : int
        Number of cpus to request for the reservation (default, 1).
    config.memory : str
        String memory request (default: "32G")
    config.gpus : int
        Non-negative number of gpus to request for the reservation (default, 0).

    Example
    -------
    >>> python3 -m lipsutils.ionic_launch node=node010, cpus=32, gpus=8
    salloc: Granted job allocation 22918747
    salloc: Waiting for resource configuration
    salloc: Nodes node010 are ready for job
    """
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
        "-l",
    ]
    subprocess.run(args)


if __name__ == "__main__":
    config = tyro.cli(CLIArgs)
    main(config)
