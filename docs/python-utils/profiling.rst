Profiling Tools
===============

Quickly timing some portion of an application to get a sense for optimization opportunities is ubiquitous. I found myself re-writing variants of the utilites below 
on projects, so I ended up factoring them out into modules under version control to quickly use in my projects. 

A Barebones Python Context Manager
----------------------------------

Intended for use in any generic script. 

.. code-block:: python

   from lipsutils.profiling import PythonProfiler

   with PythonProfiler("matmul"): 
       _ = A @ B 

A CUDA Profiling Delimiting Context Manager
-------------------------------------------

Use with tools like ``nsys`` and ``ncu`` to delimit profiling regions and reduce noise in profiles on a GPU

.. note::

   ``lipsutils.profiling`` needs to know the path to the CUDA runtime library, which is by default (and as of the time of this writing) valid on Ionic. 

See :doc:`../tutorials/gpu_profiling` for additional usage details. 

.. code-block:: python

   from lipsutils.profiling import CudaProfiler, cuda_profiler

   with CudaProfiler("matmul"): 
       _ = A @ B 

   @cuda_profiler
   def f(*args, **kwargs): 
       ... 



