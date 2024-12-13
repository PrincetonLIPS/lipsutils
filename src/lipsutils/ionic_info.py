import dataclasses
from pathlib import Path
import subprocess
from typing import Optional

from rich.console import Console
from rich.table import Table
import tyro

from lipsutils.fmt_io import human_bytes_str

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
    """Basic driver for a call to the sinfo binary on Ionic. Uses Rich formatting to produce a simplified
    table of the results on the lips partition.

    Example
    -------
    >>> python3 -m lipsutils.ionic_info
    ┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
    ┃ Hostname ┃ Status ┃ Free Memory ┃ CPUs ┃ Cores ┃ GPUs                 ┃ CPU Status         ┃
    ┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
    │ node012  │ mixed  │ 252.8 GB    │ 64   │ 16    │ In use: 1 (rtx_2080) │ 32 of 64 allocated │
    │ node015  │ mixed  │ 45.9 GB     │ 64   │ 16    │ In use: 8 (rtx_2080) │ 32 of 64 allocated │
    │ node016  │ mixed  │ 28.4 GB     │ 64   │ 16    │ In use: 2 (rtx_2080) │ 4 of 64 allocated  │
    │ node009  │ idle   │ 333.4 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node010  │ idle   │ 324.3 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node011  │ idle   │ 349.1 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node013  │ idle   │ 372.2 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node014  │ idle   │ 98.9 GB     │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    └──────────┴────────┴─────────────┴──────┴───────┴──────────────────────┴────────────────────┘

    """
    if not SINFO_BIN.exists():
        raise FileNotFoundError(f"Did not find sinfo binary at {str(SINFO_BIN)}...")

    result = subprocess.run(
        [
            str(SINFO_BIN),
            f"--partition={config.partition}",
            f"--nodes={config.nodespec}",
            "--exact",
            f"--Format={FMT_SPEC}",
        ],
        stdout=subprocess.PIPE,
    )
    result: str = result.stdout.decode("utf-8")

    # rows
    hostnames: list[str] = []
    status: list[str] = []
    free_mem: list[str] = []
    cpus: list[str] = []
    cores: list[str] = []
    gres: list[str] = []
    cpu_status: list[str] = []

    for entry in result.split("\n")[1:-1]:
        fields = entry.split()
        hostnames.append(fields[0])
        status.append(fields[1])
        free_mem.append(fields[3])
        cpus.append(fields[5])
        cores.append(fields[6])
        gres.append(fields[9])
        cpu_status.append(fields[10])

    table = Table(title="LIPS Partition Information")
    table.add_column("Hostname")
    table.add_column("Status")
    table.add_column("Free Memory")
    table.add_column("CPUs")
    table.add_column("Cores")
    table.add_column("GPUs")
    table.add_column("CPU Status")

    for data in zip(hostnames, status, free_mem, cpus, cores, gres, cpu_status):
        hostname, status, free_mem, cpus, cores, gres, cpu_status = data

        if status == "idle":
            status = f"[green]{status}[/green]"
        elif status == "mixed":
            status = f"[orange1]{status}[/orange1]"

        num_gpus_used = int(gres.split(":")[2][0])
        gpu_model: str = gres.split(":")[1]

        if num_gpus_used == 0:
            gres = f"[green]In use: {num_gpus_used} ({gpu_model})[/green]"
        elif num_gpus_used < 8:
            gres = f"[orange1]In use: {num_gpus_used} ({gpu_model})[/orange1]"
        else:
            gres = f"[red]In use: {num_gpus_used} ({gpu_model})[red]"

        free_mem = human_bytes_str(int(free_mem) * int(2**20))

        cpus_allocated: int = int(cpu_status.split("/")[0])
        cpus_total: int = int(cpu_status.split("/")[3])

        cpu_allocation_proportion: float = float(cpus_allocated) / cpus_total

        if cpu_allocation_proportion < 0.25:
            cpu_status = f"[green]{cpus_allocated} of {cpus_total} allocated[/green]"
        elif cpu_allocation_proportion < 0.75:
            cpu_status = (
                f"[orange1]{cpus_allocated} of {cpus_total} allocated[/orange1]"
            )
        else:
            cpu_status = f"[red]{cpus_allocated} of {cpus_total} allocated[/red]"

        data = (hostname, status, free_mem, cpus, cores, gres, cpu_status)

        table.add_row(*data)
    console = Console()
    console.print(table)


if __name__ == "__main__":
    config = tyro.cli(CLIArgs)
    main(config)
