import time

from lipsutils.utils import human_seconds_str, setup_logger


class PythonProfiler:
    """A barebones Python profiling context manager."""

    def __init__(self, identifier: str, **kwargs):
        self.identifier: str = identifier
        self.log = kwargs["log"] if kwargs.get("log", False) else setup_logger(__name__)

    def __enter__(self):
        self.start_time: float = time.perf_counter()

    def __exit__(self, type, value, traceback):
        run_time: float = time.perf_counter() - self.start_time
        report_str: str = f"Region \[{self.identifier}]: {human_seconds_str(run_time)}"
        self.log.info(report_str)
