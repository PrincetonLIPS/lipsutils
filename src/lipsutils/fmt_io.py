"""String formatting and basic I/O utilities."""

import datetime
from pathlib import Path
import pickle
from typing import Any


def serialize(payload: Any, location: Path) -> None:
    """Use pickle to serialize a generic object `payload` to a provided `location`. 

    Parameters 
    ----------
    payload: Any 
        Object to be serialized. 
    location: Path 
        Location to serialize to. 

    Example
    -----
    >>> save_path: Path = Path("obj.pkl")
    >>> obj: Any = (3, 4)
    >>> serialize(obj, save_path)
    """
    location: Path = Path(location) if (not isinstance(location, Path)) else location
    if location.stem != ".pkl":
        location = location.with_suffix(".pkl")

    with open(location, "wb") as handle:
        pickle.dump(payload, handle, protocol=pickle.HIGHEST_PROTOCOL)


def deserialize(location: Path) -> Any:
    """Use pickle to deserialize a generic object from a provided `location`. 

    Parameters 
    ----------
    location: Path 
        Location to serialize to. 

    Returns 
    -------
    result: Any 
        Object deserialized from `location`.

    Example
    -----
    >>> save_path: Path = Path("obj.pkl")
    >>> obj: Any = deserialize(save_path)
    """
    with open(location, "rb") as handle:
        result = pickle.load(handle)
    return result


def get_now_str() -> str:
    """Convenience method to return a formatted string with second-level resolution, 
    useful for creating logfiles, for instance. 

    Returns 
    -------
    str : 
        Formatted datestring. 

    Example
    -----
    >>> print(get_now_str())
    2024_12_13_3_52_15
    """
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def human_length_str(meters: float) -> str:
    """Formatted string respecting SI length units from meters to picometers. 

    Parameters 
    ----------
    meters: float 
        non-negative float number of meters. 

    Returns 
    -------
    str : 
        string representation of the provided lengthscale. 

    Example 
    -----
    >>> human_length_str(0.000_002_500)    
    2.5 microns
    """
    units: tuple[str] = ("meters", "millimeters", "microns", "nanometers", "picometers")
    power: int = 1

    for unit in units:
        if meters > power:
            return f"{meters:.1f} {unit}"

        meters *= 1000

    return f"{int(meters)} femtometers"


def human_bytes_str(num_bytes: int) -> str:
    """Formatted string respecting byte units from bytes to gigabytes. 

    Parameters 
    ----------
    num_bytes: int 
        non-negative int number of bytes. 

    Returns 
    -------
    str : 
        string representation of the provided number of bytes. 

    Example 
    -----
    >>> human_bytes_str(20498181)    
    19.5 MB
    """
    units: tuple[str] = ("B", "KB", "MB", "GB")
    power: int = 2**10

    for unit in units:
        if num_bytes < power:
            return f"{num_bytes:.1f} {unit}"

        num_bytes /= power

    return f"{int(num_bytes)} TB"


def human_flops_str(num_flops: int) -> str:
    """Formatted string for number of flops with units from flops to teraflops. 

    Parameters 
    ----------
    num_flops: int 
        non-negative int number of flops. 

    Returns 
    -------
    str : 
        string representation of the provided number of flops. 

    Example 
    -----
    >>> human_flops_str(49593815888)    
    46.2 GFLOP
    """
    units: tuple[str] = ("FLOP", "KFLOP", "MFLOP", "GFLOP", "TFLOP")
    power: int = 2**10

    for unit in units:
        if num_flops < power:
            return f"{num_flops:.1f} {unit}"

        num_flops /= power

    return f"{int(num_flops)} PFLOP"


def human_seconds_str(seconds: float) -> str:
    """Formatted string respecting SI time units with units from seconds to picoseconds. 

    Parameters 
    ----------
    seconds: float
        non-negative float number of seconds

    Returns 
    -------
    str : 
        string representation of the provided number of seconds. 

    Example 
    -----
    >>> import time 
    >>> start = time.perf_counter(); [lambda x: x**2 for x in range(1_000)]; runtime = time.perf_counter() - start
    >>> human_seconds_str(runtime)
    367.2 microseconds
    """
    if 60 < seconds:
        return f"{(seconds / 60):.1f} minutes"

    units: tuple[str] = (
        "seconds",
        "milliseconds",
        "microseconds",
        "nanoseconds",
        "picoseconds",
    )
    power: int = 1

    for unit in units:
        if seconds > power:
            return f"{seconds:.1f} {unit}"

        seconds *= 1000

    return f"{int(seconds)} femto"


__all__ = [
    "human_bytes_str",
    "human_flops_str",
    "human_seconds_str",
    "human_length_str",
]
