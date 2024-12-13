Profiling, Optimization, and Debugging
==========================================

Motivation
----------

I'm very often asked a number of common questions relating to debugging or optimizing the performance of someone's research code: out of memory 
exceptions, NaN derivatives, etc. 
This document details some of the concepts, methods, and philosophy around debugging and optimization, with a full walkthrough of how I collect 
data using GPU tooling. 
I don't intend to cover tools in any specific detail, as the tools themselves are well documented elsewhere (links provided at the end of this document). 
Instead, I think what's more useful is to outline the debugging/optimization methodology, which is far more valuable, in my opinion, and surprisingly lacking for
many researchers. 

Philosophy
----------

Debugging and optimization are a balance of a systematic, rigorous, and unbiased engineering attitude, with the "art" of intuition and educated guesses. 
This is one feature of the exercise that makes it very difficult. 
Very often one finds themselves making assumptions about what's going on that are not valid, which can slow or even be fatal to a debugging/optimization exercise. 
When I'm struggling to find an error or improve the performance of some code, I always try to back up and question every assumption I'm making, no matter my degree of confidence. 
At this point I think the major mindset shift that has happened in gaining experience in this domain is I'm far *less* confident in my initial assumptions/guesses than what I observe in my peers who might 
have less experience. 
This is a strange skill to develop, because on the one hand, as you gain experience, your hypotheses do become more accurate on average, but you also need to develop an extreme 
objectivity in parallel to avoid being lulled down rabbit holes by trusting your intuition too much. 

Improvement in this area is ultimately driven by building knowledge and experience. 
You do need *some* understanding of how the computer works and what limits its performance in various settings. 
You do need *some* understanding of your programming tools and what your code does at a low level. 
It is possible to extract very good results, though, with relatively simply mental models of both the hardware and the programs, provided you apply the right 
methods and techniques. 
These systems are very, very complicated. 
As a final word of warning, it is a common mistake to demean these activities as "pedestrian" or "un-intellectual". 
Engineering is different from, say, mathematics, in an aesthetic sense. 
It is much messier and less cohesive, which can be frustrating for the theoretician to accept. 
But there is much to learn here, and you will gain the best results in the long term if you engage these areas (computer engineering and architecture, operating systems, programming languages, 
software systems and user level tooling) with the same effort as you would any other complicated subject. 

Concepts
--------

I generally consider debugging to be the activity of reducing some observed deviation between my mental model/intended behavior or the code, and the actual/observed 
behavior of the code. 
Optimization is the exercise of improving some measured performance metric of the code, for example the wall-clock execution time or the memory footprint. 
Generally though, these often blur into one another. 
As you become more performance-atuned and sharpen your mental expectations of the capabilities of the hardware and the inherent algorithmic complexity of your application, you 
often find yourself thinking something like "this should be much faster" or "there's no way we should be out of memory here". 

Methods
-------

Debugging 
~~~~~~~~~

The gold standard for debugging starts far before you notice any particular issue. 
Version control (i.e., git) is the main addition to someone's workflow which is helpful for debugging. 
On a typical research project, the proper use of branching/merging, healthy commit hygiene, unit tests, and 
familiarity with tools like ``git bisect`` are your foundation, and will be covered in a separate document. 

For on the ground work, I always run the offending code in a debugger. 
For Python, the tool of choice is the `Python Debugger (PDB) <https://docs.python.org/3/library/pdb.html>`_, which you
should familiarize yourself with. 
Being able to use the Python debugger fluently means you're never coupled to the debugger in your IDE, for instance, and liberates you to debug 
code anywhere that Python is installed. 
Make sure to read through the documentation to understand what the stack frame is and how it works to orient yourself in the code base, how to monitor 
data changes as you step through the code, and basic execution commands to step into and through the code. 

Below I illustrate my concrete setup with the debugger. 


A Barebones EveryDay Setup 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

What I use essentially anytime I'm debugging code or starting an optimization exercise is a three pane split in my terminal emulator (I use Iterm2 on MacOS). 

NICK TODO add image 

On the left hand pane I'm running the code from the Python debugger (I use ipdb specifically with vim motions). 
On the right hand panes, I reserve the top for `NVTOP <https://github.com/Syllo/nvtop>`_ to monitor GPU activity in real time with a nice interface, and on the bottom 
I have some kind of data describing CPU activity, this could be `btop <https://github.com/aristocratos/btop>`_ or even something simple like `htop <https://htop.dev/>`_, or in an 
application specific scenario, I might have something else running. 

For instance, below I'm debugging a Jax application, so I'm using `jax-smi <https://github.com/ayaka14732/jax-smi>`_ to monitor the outstanding data buffers and compilation cache 
buffers. 
What I'm doing is: 

	1. Developing some expectations/hypotheses as to what's going on. In debugging, this might mean guesses as to what components of the code I can ignore/assume to be working. In optimization, this might mean guesses as to where in the code the hotspots exist. 
	2. Gather data/evidence to refine these expectations. For instance, I might step to the next line of code, and watch what buffers are allocated (do those match my estimates?) and what the CPU/GPU activity looks like. I'm also estimating how long I think each line of code will take to run (roughly), and verifying that. This is where I adjudicate my hypotheses and correct errors in my mental model. 
  	3. Make a change. This is driven by experience and knowledge. I cannot say anything generic here, unfortunately, except that I try to make as minimal and isolated a change as possible, and I make sure the original version is tracked under version control with a helpful commit message, e.g., ``bug: NaN gradient at example.py:171 on GPU``. I'm tracking my environment by tracking my Docker build file (see :doc:`docker`) under version control. I have an educated guess about what my change will do. 
  	4. Repeat. 

Measurement Discipline
~~~~~~~~~~~~~~~~~~~~~~

The chief crime committed in both debugging and optimization exercises is moving forward with a false assumption. 
This often takes the form of assuming you know which section of the code deserves optimization effort, with function is causing the issue, etc. 
In both cases, it's crucial to *gather evidence* to support your assumptions. 
The more stuck you find yourself, the stronger your standard for this evidence ought to be. 
I always remind myself that if things empirically don't behave as I expect, there must be some discrepancy in my mental model.
Then the temporary game is to find that discrepancy: try to treat this as an integral part of the process, not something to get frustrated at. 


Full Example: GPU Profiling
-------------------------------------

It is straightforward to capture profiling telemetry on the GPU from the command line. For quick-and-dirty sanity checks, you can print to the command line, but more involved scenarios generally require that you maintain outputs in report files (usually in a directory where you track a baseline and comparison runs as you modify the application). 

`Nsight Systems <https://developer.nvidia.com/nsight-systems>`_ is the tool I use most often if I need to do anything complicated: it provides a higher-level view of the execution of the profiled application. This is (almost always) the tool to use, with the exception of kernel debugging, for which Nsight Compute is more appropriate. The remainder of this section covers Nsight Systems. 
You can follow the link above to download the host-side (e.g., on your laptop) application which is what you'll use to interpret the data the tool produces. 

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

This generates a report file ``baseline.out``, which I ``rsync`` back to my local host, I can open it up using the local Nsight Systems tool to interrogate the application. 


TODO Nick add image

Notice the bottom partition is displaying the Stats System View, which contains aggregate statistics like API calls, kernel launches, and memory system interactions. This is similar to what you’d get on the command-line using ``nvprof``. 

In the upper partition by default we see the Timeline view, which shows time series of the execution behavior of the various “Processes” shown on the lefthand side. For example, we can see the CPython interpreter system calls as it handles module import and setup for its overhead. 

The CUDA HW row shows a speckling of small kernel executions in the right half of the time series. We can zoom in on one of these operations (note the difference in timescale between the first image and this one) and look at an individual kernel execution, for example this ``dot3`` kernel executed in about 2 us, and we can see information like its launch configuration (in terms of grids, blocks, and threads per block), and stream identity (to name a few). 


TODO Nick add image

Restricting Capture Range
~~~~~~~~~~~~~~~~~~~~~~~~~

Notice in the previous case about half of the capture telemetry was useless since the program hadn’t started executing our matrix-matrix multiplication operations. It’s convenient to delimit the profiling regions so that you only capture relevant portions of the execution. For example, a full machine learning application might include file I/O to deserialize a dataset and load it into memory, preprocessing overhead, logging and diagnostics, plotting, and other peripheral operations that are typically not relevant to the profiling exercise. 

In this case, you can use the ``liputils.profiling`` module which contains a few utilities for specifying a capture range (make sure to modify ``cuda_runtime_path`` depending on your host). I’ll just modify the application to use the ``CudaProfiler`` context manager which will handle the delimiting. 

.. code-block:: python

	import jax.numpy as np 
	from lipsutils.profiling import CudaProfiler

	with CudaProfiler():
	    for size in [2**i for i in range(1, 10)]: 
	        A: np.ndarray = np.arange(size**2).reshape(size, size) 
	        B: np.ndarray = np.arange(size**2).reshape(size, size) 
	        C: np.ndarray = A @ B

I’ll now call ``nsys`` with the ``--capture-range`` flag to indicate that it should look for these delimiter directives. ``nsys profile --output=delimited.out --capture-range cudaProfilerApi python3 demo.py``. 

TODO Nick add image 

You can see above our captured trace only contains the loop executions. In this case the improvement is marginal (we reclaim maybe half of the trace that was wasted before) but in more complicated applications this is crucial. 
You want to reduce noise to simplify the problem. 

Specifying API Capture
~~~~~~~~~~~~~~~~~~~~~~

If your application utilizes a number of different APIs (e.g., cuBLAS, cuFFT, cuDNN, etc.) it can be useful to specify the information you’re interested in. 


.. code-block:: console

		$ nsys profile --output=apis.out --trace cuda,osrt,nvtx,cublas,cudnn python3 demo.py

In this case I’m not actually using any of these libraries so the profiling output is not different. 

Annotating Regions with NVTX
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A very useful tool is the Nvidia Tools Extension Library (NVTX). NVTX provides cross-platform features to add marks and annotations to the profiling telemetry that it compatible with Nsight Systems. After installing the library (using ``mamba``, ``conda``, or ``pip`` for example), you can use it as follows: 

.. code-block:: python

	import jax.numpy as np 
	import nvtx 
	from lipsutils.profiling import CudaProfiler
		 
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

