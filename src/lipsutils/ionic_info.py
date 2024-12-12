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

    result = subprocess.run(
        [
            str(SINFO_BIN),
            f"--partition={config.partition}",
            f"--nodes={config.nodespec}",
            "--exact",
            f"--Format={FMT_SPEC}",
        ], stdout=subprocess.PIPE
    )
    result: str = result.stdout.decode('utf-8')

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
        if num_gpus_used == 0: 
            gres = f"[green]{gres}[/green]"
        elif num_gpus_used < 8: 
            gres = f"[orange1]{gres}[/orange1]"
        else: 
            gres = f"[red]{gres}[/red]"

        data = (hostname, status, free_mem, cpus, cores, gres, cpu_status) 

        table.add_row(*data)

    console = Console()
    console.print(table)




if __name__ == "__main__":
    config = tyro.cli(CLIArgs)
    main(config)
