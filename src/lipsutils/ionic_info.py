import dataclasses
from pathlib import Path
import subprocess
from typing import Optional

from rich.console import Console
from rich.table import Table
import tyro

# Valid on Ionic as of 12/12/2024
SINFO_BIN = Path("/usr/bin/sinfo")
LIPS_FLEX_NODESPEC: str = "node009,node01[0-6]"
FMT_SPEC: str = "NodeHost:10,StateLong:10,Partition:10,FreeMem,Memory,Cpus,Cores,AllocMem,Available,GresUsed:30,CPUsState"


@dataclasses.dataclass
class CLIArgs:
    partition: Optional[str] = "lips"
    nodespec: Optional[str] = LIPS_FLEX_NODESPEC
    verbose: Optional[bool] = False


def main(config: CLIArgs):
    if not SINFO_BIN.exists():
        raise FileNotFoundError(f"Did not find sinfo binary at {str(SINFO_BIN)}...")

    subprocess.run(
        [
            str(SINFO_BIN),
            f"--partition={config.partition}",
            f"--nodes={config.nodespec}",
            "--exact",
            f"--Format={FMT_SPEC}",
        ]
    )


if __name__ == "__main__":
    config = tyro.cli(CLIArgs)
    main(config)
