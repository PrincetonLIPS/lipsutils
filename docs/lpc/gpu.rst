Using GPUs
==========


.. note::
    - CPUs are optimized for single-thread latency, GPUs are optimized for throughput. Consider using GPUs for workloads with minimal control flow and lots of data parallelism.
    - Launch GPU-compatible container runtimes using ``--gpus all``  with ``docker run`` for GPU support in a container.  A collection of default images with GPU support are installed and maintained on every host (please do not clobber these images):
        - PyTorch 2.0.1
        - Tensorflow (latest)
    - LPC currently maintains CUDA 12.2, we maintain an update schedule below in this document.
    - Profile GPU workloads using ``nsys`` and/or ``ncu``, adding capture range delimiters and annotations (see instructions below).

Background
----------

**GPUs vs. CPUs**

Generally speaking, modern CPUs and GPUs are architected and implemented with distinct design motivations, as described below. Keep in mind this is a massively simplified view of the world, but it captures the primary distinction between these systems. 

**CPU**

CPUs are motivated by the problem of executing a single computational thread (a sequence of instructions) as quickly as possible. The latency associated with executing a single thread in general is limited by uncertainty around what needs to be done next (i.e., the control flow of the program) and what data it will require. 

Because of this, modern CPU implementations include advanced techniques in hardware like branch prediction, cache prefetching, and other predictive mechanisms to mitigate uncertainty and extract instruction level parallelism. A modern CPU fetches a large batch of instructions (on the order of a few hundred), predicts how branches will be resolved, and then analyzes the resulting (speculative) dependency graph and partitions the graph into micro-graphs which are executed in parallel using a collection of 10-20 independent processing elements. 

These features for prediction and extracting parallelism at the instruction level require substantial resources. As a result, CPUs can typically support a small number of threads (typically between 10-20, or maybe a few hundred on the very extreme end). 

A good basic treatment of CPUs is given in David Harris’ Digital Design and Computer Architecture (in particular, chapters 6-8). More advanced microarchitecture is covered in David Patterson and John Hennessy’s Computer Architecture: A Quantitative Approach. 

**GPU**

GPUs are motivated by the problem of executing a large number of threads, with throughput as the objective. A common adage is that GPUs “hide” or “mask” the imbalance between logic and communication using throughput. At any point in the executing the program, many hundreds or thousands of threads may be stalled waiting for operands to arrive from the memory system. But, unlike a CPU (in which a hundred stalled threads essentially means zero forward logical progress), many tens of thousands of other threads continue to execute. 

The tradeoffs are that each thread is physically backed by relatively limited hardware, and all threads must share a common memory system. From the programmer’s perspective, the interpretation might be: 

1. Branches (``if`` statements) that can’t be resolved at compile time hurt more because GPUs lack branch prediction and other features to mitigate this. 
2. Each thread must be at a high enough arithmetic intensity to have any hope of utilizing the GPU well. Arithmetic intensity, for our purposes, can be defined as the number of floating point operations per byte requested from memory. For a machine learning example, consider the arithmetic intensity of linear layer matrix-matrix multiplication (linear in the matrix dimension) versus an elementwise nonlinearity (constant arithmetic intensity of 1, which is low). 

These tradeoffs should be somewhat intuitive. You get more threads, but they are more limited and need to share the (common) memory system well to get performance. 

Historically GPUs evolved from video graphics arrays (VGAs) and accelerators from the graphics community, in which the threads contained relatively straightforward control flow (few conditional branches/jumps) and significant data locality (e.g., threads could be grouped according to spatially local pixels, likely using the same texture map). In the early 2000s GPU designs became motivated by the broader array of computing applications which contained these problem characteristics: the execution of a large number of mostly-independent threads running the same program on localized data (a single-instruction multiple-thread (SIMT) programming model). 

Modern GPUs represent the realization of a two-decade long design effort to rethink GPU architecture, implementation, and programming models. A modern GPU often consumes less than 20pJ per instruction (orders of magnitude lower than a CPU), and amortizes that instruction overhead with many-times more useful work. To first order, by using less energy the system can execute more threads at once while maintaining a reasonable power limit and respecting the thermal limits of the packages. Our consumer GPUs in the lab, purchased for under $1000 can support over 100K threads.  

TODO Nick: add image

The image above is a high-level illustration of a GPU architecture (this depicts the A100). The GPU is partitioned into 8 Graphics Processing Clusters (GPCs) each containing 16 thread engines (called “Streaming Multiprocessors” or SMs by Nvidia). Each thread engine supports 2048 threads, so the A100 supports more than 250K threads. On the left and right sides of the die, memory controllers interface to 6 stacks of high-bandwidth memory (HBM), an advanced memory technology that supports nearly a TB/s of bandwidth per stack. The center blue stripe of the GPU is a cache shared by all threads, and within each SM (you may need to zoom in to see this) is a local L1 cache and large register files. 

TODO Nick: add image

Within the SM is an array of processing elements for various supported data types, load-store units for interfacing with global memory (DRAM/HBM, that is), and in recent generations, small ASIC-like elements designed specifically for matrix-matrix multiplication variants (these significantly improve performance for deep learning applications). A small special function unit (SFU) lies in the bottom right-hand corner to support special operations like trigonometric functions (sine, cosine, etc.), square root, etc. 

When to Consider Using a GPU
----------------------------

As can be understood from the short discussion above, GPUs excel at executing applications which contain significant data parallelism and minimal control flow. That is, you want to run (relatively) simple programs over a large collection of data items. At the operational level of abstraction, common candidates here are parallel-friendly numerical linear algebra algorithms like those found in scientific computing, graphics, and deep learning. 

If this advice seems overly abstract, here’s a concrete suggestion. For those of you who are members of the Church of Jax, imagine that the vectorizing maps (e.g, `jax.vmap`) are your “cues” to start thinking about porting your application to a GPU. Of course, there are patterns (e.g., sparse and conditional operations) that will be better suited for a CPU, but to zeroth order this is a reasonable heuristic. 

**Nvidia RTX 3080Ti**

Our lab owns 4 Nvidia RTX 3080Ti GPUs. This system runs Nvidia’s Ampere GA102 architecture, with 12GB of memory, 80 streaming multiprocessors (SMs), and dedicated hardware for ray tracing and matrix multiplication. It’s a standard mid-tier GPGPU module, pulling up to 350W across roughly 30B transistors, with around 1TB/s memory bandwidth and around 30TFLOPS of single precision floating point performance. It’s built on Samsung’s 8nm node. 

LPC Systems
-----------


**Nvidia Container Runtime**

Using the GPUs inside a Docker container runtime is straightforward. LPC maintains the `Nvidia Container Runtime <https://developer.nvidia.com/nvidia-container-runtime>`_, an OCI-specification compatible runtime that is GPU-aware. There are also a variety of Nvidia created images `available freely on Dockerhub <https://hub.docker.com/r/nvidia/cuda/tags>`_. These containers are preconfigured with the CUDA binaries and tools, in case you need to run a different version than the defaults (this is not completely flexible, as the systems/architectures are not fully backward compatible). 

Assuming you’ve obtained an image, starting a container runtime with GPU access is simple. For example, 

.. code-block:: console

    $ docker run -dt --gpus all --name gpu_container 12.0.0-cudnn8-devel-ubuntu20.04


would get me started with a container running CUDA 12.0.0 and CUDNN 8 with developer tools on Ubuntu 20.04.

.. note::

   Containers with pre-configured deep learning frameworks like PyTorch and TensorFlow are also available, and typically more convenient than building the framework as a separate step in setting up your container runtime.

**Current System Status**

The current status of the Nvidia/CUDA tools and drivers are maintained below, along with an update schedule. 

TODO Nick add this
