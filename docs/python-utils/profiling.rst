Profiling Tools
===============

Quickly timing some portion of an application to get a sense for optimization opportunities is ubiquitous. I found myself re-writing variants of the utilites below 
on projects, so I ended up factoring them out into modules under version control to quickly use in my projects. 

A Barebones Python Context Manager
----------------------------------

.. code-block:: python

   from lipsutils.profiling import PythonProfiler

   with PythonProfiler("matmul"): 
       _ = A @ B 
