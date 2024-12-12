import datetime


def get_now_str() -> str:
    return datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


def human_length_str(meters: float) -> str:
    units: tuple[str] = ("meters", "millimeters", "microns", "nanometers", "picometers")
    power: int = 1

    for unit in units:
        if meters > power:
            return f"{meters:.1f} {unit}"

        meters *= 1000

    return f"{int(meters)} femtometers"


def human_bytes_str(num_bytes: int) -> str:
    units: tuple[str] = ("B", "KB", "MB", "GB")
    power: int = 2**10

    for unit in units:
        if num_bytes < power:
            return f"{num_bytes:.1f} {unit}"

        num_bytes /= power

    return f"{int(num_bytes)} TB"


def human_flops_str(num_flops: int) -> str:
    units: tuple[str] = ("FLOP", "KFLOP", "MFLOP", "GFLOP", "TFLOP")
    power: int = 2**10

    for unit in units:
        if num_flops < power:
            return f"{num_flops:.1f} {unit}"

        num_flops /= power

    return f"{int(num_flops)} PFLOP"


def human_seconds_str(seconds: int) -> str:
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