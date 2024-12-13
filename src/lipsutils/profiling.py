import ctypes
import functools
from pathlib import Path
import time
from typing import Optional

from lipsutils.fmt_io import human_seconds_str
from lipsutils.log_utils import setup_logger

# cuda runtime library: change this if neceessary!
# valid for Ionic 12/12/2024
try:
    cuda_runtime_path: Path = Path("/usr/local/cuda-12.1/lib64/libcudart.so.12.1.105")
    cuda_runtime = ctypes.CDLL(str(cuda_runtime_path))
    CUDA_AVAILABLE = True
    import nvtx
except OSError:
    CUDA_AVAILABLE = False


class PythonProfiler:
    """A barebones Python profiling context manager.

    Example
    -------
    >>> with PythonProfiler("f"): 
        _ = f()
    """

    def __init__(self, identifier: str, **kwargs):
        self.identifier: str = identifier
        self.log = kwargs["log"] if kwargs.get("log", False) else setup_logger(__name__)

    def __enter__(self):
        self.start_time: float = time.perf_counter()

    def __exit__(self, type, value, traceback):
        run_time: float = time.perf_counter() - self.start_time
        report_str: str = f"Region \[{self.identifier}]: {human_seconds_str(run_time)}"
        self.log.info(report_str)


def cuda_profiler_start():
    """Launches the CUDA runtime profiler."""
    if not CUDA_AVAILABLE:
        raise RuntimeError("Cuda runtime is not available!")
    return_value: int = cuda_runtime.cudaProfilerStart()
    if return_value != 0:
        raise Exception(f"cudaProfilerStart() returned {return_value}")


def cuda_profiler_stop():
    """Terminates the CUDA runtime profiler."""
    if not CUDA_AVAILABLE:
        raise RuntimeError("Cuda runtime is not available!")
    return_value: int = cuda_runtime.cudaProfilerStop()
    if return_value != 0:
        raise Exception(f"cudaProfilerStop() returned {return_value}")


class CudaProfiler:
    """Cuda profiling context manager, for use under `nsys` and `ncu`. 

    Example
    -------
    >>> with CudaProfiler("gradient fn"): 
        _ = jax.grad(f)(x) 
    """
    def f(): 
        pass 
    def __init__(self, identifier: Optional[str] = None):
        if not CUDA_AVAILABLE:
            raise RuntimeError("Cuda runtime is not available!")
        self.identifier: str = identifier

    def __enter__(self):
        if self.identifier is not None:
            nvtx.mark(message=self.identifier)
        cuda_profiler_start()

    def __exit__(self, type, value, traceback):
        cuda_profiler_stop()


def cuda_profiler(f: callable):
    """Wrapper intended to decorate functions that one wants to run under
    the supervision of the CUDA runtime profiler. Uses functools.wraps to carry over
    method name, docstring, args, etc.

    Parameters
    ----------
    f: callable
        callable to be profiled.

    Returns
    -------
    wrap: callable
        wrapped version of `f` which will run within a CUDA profiling fence and
        otherwise behaves identically.

    Example
    -------
    >>> 
    @cuda_profiler 
    def f(): 
        pass 
    """

    @functools.wraps(f)
    def wrap(*args, **kwargs):
        cuda_profiler_start()
        result = f(*args, **kwargs)
        cuda_profiler_stop()
        return result

    return wrap
