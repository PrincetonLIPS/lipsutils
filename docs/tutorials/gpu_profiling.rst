GPU Profiling, Optimization, and Debugging
==========================================

As of June 20, 2023, Nvidia is currently in the process of migrating the profiling and telemetry systems from the previous generation (using primarily ``nvprof`` and ``nvvp``) to the `Nsight Compute <https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html>`_ (``ncu``) and `Nsight Systems <https://docs.nvidia.com/nsight-systems/UserGuide/index.html>`_ (``nsys``) tools. 

Users familiar with using the previous generation tools should read the `transition guide <https://docs.nvidia.com/nsight-compute/NsightComputeCli/index.html#nvprof-guide>`_. You might want to consider learning about and integrating the telemetry tools in your application if you’re interested in: 

- debugging execution
- debugging memory issues
- performance optimization

Capturing Telemetry
-------------------

It is straightforward to capture profiling telemetry from the command line. For quick-and-dirty sanity checks, you can print to the command line, but more involved scenarios generally require that you maintain outputs in report files (usually in a directory where you track a baseline and comparison runs as you modify the application). 

`Nsight Systems <https://developer.nvidia.com/nsight-systems>`_ is the more commonly used tool: it provides a higher-level view of the execution of the profiled application. This is (almost always) the tool to use, with the exception of kernel debugging, for which Nsight Compute is more appropriate. The remainder of this section covers Nsight Systems. 

Basic Usage
~~~~~~~~~~~


For basic use cases, you’ll use the ``profile`` command switch and provide ``nsys`` with an output report filename and the application. 

I’ll use the following Python application, which computes a sequence of matrix-matrix multiplication operations: 

.. code-block:: python 


	import jax.numpy as np 
		 
	for size in [2**i for i in range(1, 10)]: 
	    A: np.ndarray = np.arange(size**2).reshape(size, size) 
	    B: np.ndarray = np.arange(size**2).reshape(size, size) 
	    C: np.ndarray = A @ B

To profile the entire application and save the output, I’ll use: 


.. code-block:: console

		$ nsys --output=baseline.out python3 demo.py

After ``rsync``-ing the report back to my local host, I can open it up using the local Nsight Systems tool to interrogate the application. 


TODO Nick add image

Notice the bottom partition is displaying the Stats System View, which contains aggregate statistics like API calls, kernel launches, and memory system interactions. This is similar to what you’d get on the command-line using ``nvprof``. 

In the upper partition by default we see the Timeline view, which shows time series of the execution behavior of the various “Processes” shown on the lefthand side. For example, we can see the CPython interpreter system calls as it handles module import and setup for its overhead. 

The CUDA HW row shows a speckling of small kernel executions in the right half of the time series. We can zoom in on one of these operations (note the difference in timescale between the first image and this one) and look at an individual kernel execution, for example this ``dot3`` kernel executed in about 2 us, and we can see information like its launch configuration (in terms of grids, blocks, and threads per block), and stream identity (to name a few). 


TODO Nick add image

Restricting Capture Range
-------------------------

Notice in the previous case about half of the capture telemetry was useless since the program hadn’t started executing our matrix-matrix multiplication operations. It’s convenient to delimit the profiling regions so that you only capture relevant portions of the execution. For example, a full machine learning application might include file I/O to deserialize a dataset and load it into memory, preprocessing overhead, logging and diagnostics, plotting, and other peripheral operations that are typically not relevant to the profiling exercise. 

In this case, you can use the (TODO Nick add ref) module which contains a few utilities for specifying a capture range (make sure to modify ``cuda_runtime_path`` depending on your host). I’ll just modify the application to use the ``CudaProfiler`` context manager which will handle the delimiting. 

.. code-block:: python

	import jax.numpy as np 
	from cuda_utils import CudaProfiler

	with CudaProfiler():
	    for size in [2**i for i in range(1, 10)]: 
	        A: np.ndarray = np.arange(size**2).reshape(size, size) 
	        B: np.ndarray = np.arange(size**2).reshape(size, size) 
	        C: np.ndarray = A @ B

I’ll now call ``nsys`` with the ``--capture-range`` flag to indicate that it should look for these delimiter directives. ``nsys profile --output=delimited.out --capture-range cudaProfilerApi python3 demo.py``. 


TODO Nick add image 

You can see above our captured trace only contains the loop executions. In this case the improvement is marginal (we reclaim maybe half of the trace that was wasted before) but in more complicated applications this is crucial. 

Specifying API Capture
----------------------

If your application utilizes a number of different APIs (e.g., cuBLAS, cuFFT, cuDNN, etc.) it can be useful to specify the information you’re interested in. 


.. code-block:: console

		$ nsys profile --output=apis.out --trace cuda,osrt,nvtx,cublas,cudnn python3 demo.py

In this case I’m not actually using any of these libraries so the profiling output is not different. 

Annotating Regions with NVTX
----------------------------

A very useful tool is the Nvidia Tools Extension Library (NVTX). NVTX provides cross-platform features to add marks and annotations to the profiling telemetry that it compatible with Nsight Systems. After installing the library (using ``mamba``, ``conda``, or ``pip`` for example), you can use it as follows: 

.. code-block:: python

	import jax.numpy as np 
	import nvtx 
	from cuda_utils import CudaProfiler
		 
	with CudaProfiler():
	    nvtx.mark(message="About to start the loop!") 
	    for size in [2**i for i in range(1, 10)]: 
	        A: np.ndarray = np.arange(size**2).reshape(size, size) 
	        B: np.ndarray = np.arange(size**2).reshape(size, size)
	        with nvtx.annotate(message=f"Matrix size {size}", color="green"): 
	            C: np.ndarray = A @ B

TODO Nick add image

This adds helpful annotations as you can see above. 

You can also use ``nvtx.annotate`` as a decorator, like this: 

.. code-block:: python

	@nvtx.annotate(message="matmul", color="blue")
	def matmul(A: np.ndarray, B: np.ndarray) -> np.ndarray: 
	    return A @ B

There are also more sophisticated capabilities like domains and categories that you can explore in the documentation. 

Memory Usage
~~~~~~~~~~~~

To capture memory usage just add the ``--cuda-memory-usage true`` option, which adds a memory usage process to look at GPU memory usage. 

.. note::

		Google’s XLA compiler infrastructure uses a rather aggressive memory allocator, which by default allocates around 90% of the available GPU memory. Even if you disable this with ``XLA_PYTHON_CLIENT_ALLOCATOR=platform``, the allocator will request double its current allocation each time it grows near the limit of its current allocation. This is important to understand when debugging applications using XLA.

