Working with Containers
=======================

Background
----------

Consider the minimal requirements to run some generic application for research in machine learning or scientific computing: 

- The code for the application and its (correct) configuration
- Libraries and other dependencies (potentially dozens), each pinned to a specific version that is known to be compatible with the application and the other dependencies
- An interpreter (e.g., CPython) or runtime to execute the code, also version pinned
- Localizations like user accounts, environment settings, and services provided by the operating system

Container images simplify this workflow drastically by packaging an application and its requirements into a standardized, portable file. The image is the static-time construct, and a container engine (e.g., Docker, Singularity) enables one to instantiate the container, the run-time construct, as a pseudo-isolated process tree sharing the kernel of the host. Tens or hundreds of containers can run simultaneously on the same host without conflicts thanks to kernel namespaces and Linux cgroups features. 

With images typically being a few hundred megabytes in size, it’s practical to copy them between hosts. In machine learning research, images often contain one or more deep learning frameworks (each of which might be several hundred megabytes alone) as well as version pinned GPU libraries. A full-fledged image for a research project (with ML tools, visualization libraries, developer tooling, etc) can result in bloated images to several gigabytes or more. The reason containers are still used widely in industry ML applications is that **reproducibility** and ease of use is unmatched by Python package management (pip, conda, mamba), and disk is extremely cheap. 

Concepts
--------

Virtual Machines vs. Containers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As a reaction to the chaos of software engineering in the 90s, a small stealth startup called VMware succesfully virtualized the x86 architecture, ushering in a new era of stability for professional 
software development. 
At a high level, you can think of a VM as a program which serves to emulate a physical computer. 
Traditional VMs fully emulate a computer, and are motivated by the ability to execute programs written for another architecture (e.g., running an Arm binary on an x86 processor). 

The challenge with the VM model is that they are slow to boot, and portability was traditionally poor. 
A container is analagous to the virtual machine, but crucially: **containers do not require a full-featured operating system**. 
In fact, a single host might run dozens or hundreds of distinct containers, each of which share a single underlying operating system. 
This has huge implications for efficiently using hardware resources; from a user's point of view containers boot almost instantly and are 
extremely portable. 

Container vs. Image 
~~~~~~~~~~~~~~~~~~~

A Docker image is essentially a collection of files which encapsulates a filesystem, libraries, and an application. 
The image contains a subset of a full operating system. 
It is the "build-time" construct that we build with ``docker build``. 
From the programmer's perspective, you can think of the image as a class and the associated container(s) as instance(s) of that class. 

.. code-block:: python 

   # an analogy 
   class DockerImage: 
      os_dependencies: Sequence[Package] = (git, curl, python3.11)
      python_dependencies: Sequence[Package] = (numpy, scipy)
      fs: FileSystem 
      metadata: Other 


   container = DockerImage() 
   another_container = DockerImage()

Images are comprised of a collection of layers. 
Different images can and do share layers, for efficiency. 

The container is the "runtime" instance of an image that we start with ``docker run``. 
With this command we ask the Docker engine to start a new container, which you can think of as an isolated process-tree of sorts (or, something analagous 
to a lightweight VM). 

So our terminology would be that we *build* an image and then launch/run a container *from* that image. 
Our task will be to build an image with all of the libraries/dependencies that our application needs, and then to actually run our application in a container which 
is running from that image. 
With this in mind, the central aspect of good engineering in this context is having a reproducible and maintainable way for some collaborator to reconstruct the 
same image that you have, which is the central focus of the complete project example later. 

Docker vs. Apptainer 
~~~~~~~~~~~~~~~~~~~~

Roughly speaking, you can think of Docker as the industry-preferred containerization platform, and Apptainer as the academic-preferred containerization platform. 
Both offer much of the same functionality (and are based on very similar underlying technologies), but Apptainer uses a different model which trades convenience for 
additional security (which is often rational in more open cluster models like on an academic campus). 

A reasonable way to think about the distinction is that the filesystem associated with your Docker container is mutable, whereas with Apptainer you would need to rebuild 
the image to mutate the underlying container. 
I detail an example of this below, but just to be concrete, suppose I'm developing an application and suddenly realize I need an additional Python dependency (say ``scipy``) 
in my container runtime. 
In Docker, I can mutate the container-associated filesystem on the fly and introduce that new dependency. 
With Apptainer on one of our Princeton clusters, I would have to stop the container, re-build the image, and restart it again to introduce that new dependency. 
Given a complicated image for a large application, it could take 30 minutes to complete the re-build, so you can imagine that for quick development (and the process of 
containerizing an application), Docker is much preferred. 


A Full Example 
--------------

In this complete example I'll walk through many of the common tasks involved in containerizing a project, from pinning dependencies, choosing a base image, writing a Dockerfile, changing things at runtime, and supporting multiple hardware targets. 

Project
~~~~~~~

Our running example will be a very simple application, to keep a focus on the engineering and not the application. Of course, by abstracting many of the details of a real application, we do ignore some of the challenges that arise in the real-world, but this guide should be enough to get you started. 

At the end of this document, I'll catalogue some of the more common issues that arise in more complicated applications. 

Our project structure will look as follows: 

.. code-block:: console 

    docker-practice/ 
        src/
            example.py 

Where ``example.py`` contains: 

.. code-block:: python 

   try: 
       import jax
       print("JAX dependency resolved!")
   except ModuleNotFoundError: 
       print("JAX not available!")
       import sys; sys.exit(0)

   try: 
       _ = jax.devices("cuda")
       print("GPU available!")
   except RuntimeError: 
       print("GPU not available!")

Clearly, the content here is just intended to report whether Jax can be loaded, and if so, whether we can see any 
CUDA capable devices (GPUs). 


Pinning Dependencies
~~~~~~~~~~~~~~~~~~~~

Our first step is pinning our dependencies. 
I typically recommend strict pinning (i.e., exact version equality) to simplify dependency resolution.

.. note:: 

   If you don't already have a working version of the project running on your local environment, you may skip this section.

If you've already been working on the project, and are now trying to containerize it (you've been using a virtual environment, say), then a quick way to do this is to confirm that all tests pass and the application works as you expect, and then running ``pip freeze > requirements.txt`` to populate a file containing the version information. 

.. code-block:: console 

   (.venv) $ pip freeze > requirements.txt 
   (.venv) $ cat requirements.txt 
        absl-py==2.1.0
        altgraph @ file:///AppleInternal/Library/BuildRoots/860631e9-c1c5-11ee-98ee-b6ef2fd8d87b/Library/Caches/com.apple.xbs/Sources/python3/altgraph-0.17.2-py2.py3-none-any.whl
        anyio==4.4.0
        ...
        jax==0.4.30
        jaxlib==0.4.30
        ...
        urllib3==2.2.1
        wcwidth==0.2.13
        webencodings==0.5.1
        websocket-client==1.8.0
        wmctrl==0.5
        zeroconf==0.135.0
        zipp==3.17.0

There's likely a ton of nonsense in here. 
On my local machine running MacOS you can also see an entry that certainly will cause issues (the local file). 
It's good form to prune this list to only the relevant dependencies. 
This is somewhat of an art, but generally anything that is imported in one of your project modules should be pinned. 
In our case, this is just Jax, so our cleaned ``requirements.txt`` looks like: 

.. code-block:: console 

   (.venv) $ cat requirements.txt 
        jax==0.4.30
        jaxlib==0.4.30

Now if I'm being extremely clinical here, I might create a fresh venv, run ``pip install -r requirements.txt``, and then re-run my tests/application to make sure everything is working. 

Choosing a Base Image 
~~~~~~~~~~~~~~~~~~~~~

Now we need to determine our base image (which we will append layers to and serves as our starting point). 
This depends on where you intend to deploy the project, but let's say you've been working on your local machine (a laptop) and are hoping to containerize and port the application to run on GPU, one of 
our LPC hosts. 

There are many possible base image choices here, with tradeoffs like disk usage, pre-built available tools, and whether you need a minimal or full-featured operating system within the container runtime. Generally though, 
there aren't many gotchas here, the choice I make below will work in almost all cases. 

What is a relevant consideration is that we intend to run on GPU, meaning we need an image with the relevant GPU libraries and software. With that in mind, I'll choose an Ubuntu base image with support for CUDA 12 and 
CUDNN, which I know to be compatible with this version of Jax, and supported by our LPC hosts. 

Below, I show how our ``Dockerfile`` will contain this base image identifier, and the rest of the information needed to build our image. 


Writing a Dockerfile 
~~~~~~~~~~~~~~~~~~~~

The Dockerfile is our build construct that codifies the properties of our image (and therefore the behavior of our container at runtime). 
A Dockerfile looks something like a shell script with some Docker-specific commands, and this file (*not* your image) is what should be always tracked under 
version control. 
When working on a project (especially with collaborators), it's critical in my opinion that after cloning a repository and building the image from a Dockerfile, things 
just work. 
I typically configure a continuous integration strategy using GitHub actions to assert that this is the case for any push to or merge into my ``main`` branch (once the project has 
reached some level of stability, of course). 

Below I'm showing the Dockerfile, which I created with the name ``Dockerfile`` in my project directory as follows: 

.. code-block:: console 

    docker-practice/
        src/
        Dockerfile 

This is the name expected by the docker commandline tools. Here are the contents of that file: 

.. code-block:: console 

    # syntax=docker/dockerfile:1

    FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
    LABEL maintainer="njkrichardson@princeton.edu" 

    COPY ./requirements.txt /requirements.txt

    WORKDIR /docker_practice
    ENV PYTHONPATH=/docker_practice:/docker_practice/src

    # ubuntu dependencies 
    RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
        build-essential \
        python3-pip

    # install python dependencies 
    RUN pip install -r /requirements.txt \
    && rm -f /requirements.txt 

    CMD ["/bin/bash"]

Let's step through this. The first line of the file specifies the Dockerfile syntax version. 

.. code-block:: console 

    # syntax=docker/dockerfile:1

The next block of two lines specifies the base image with the ``FROM`` directive and a maintainer email. 
The text after the ``FROM`` directive shows that we're using an Ubuntu 22.04 base image. 

.. code-block:: console 

    FROM ubuntu:22.04
    LABEL maintainer="njkrichardson@princeton.edu" 


In many cases in ML research, the choice of base image is primarily driven by the framework being used (PyTorch, Tensorflow, Jax, etc.). 
These are such common cases that there exists images which come ready out of the box with these frameworks installed. 
`DockerHub <https://hub.docker.com/>`_ is the place to go to find images. 
If I search for PyTorch and then click tags, I can start scrolling through all of the provided PyTorch images and choose one that meets my needs. 
Then I would simply copy-paste the tag (e.g., ``pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel``) and use that as my base image (after ``FROM``). 

The next line uses the ``COPY`` instruction to copy the requirements file from our local project directory (on the host) to the filesystem of the image at the path ``/requirements.txt``. 
We need this so that we can "see" the requirements within the build process. 

.. code-block:: console 

    COPY ./requirements.txt /requirements.txt

The next block configures the ``WORKDIR`` and configures the ``PYTHONPATH``. 
The ``WORKDIR`` instruction sets the working directory for any later ``RUN`` instructions that follow, and by 
setting the ``PYTHONPATH`` here with the ``ENV`` instruction, we save time running commands in the container runtime later. 

.. code-block:: console 

    WORKDIR /docker_practice
    ENV PYTHONPATH=/docker_practice:/docker_practice/src

The subsequent block configures the base operating system (Ubuntu, in this case) dependencies. At minimum we need Python3, but in other cases we might need other 
libraries like ``curl``, for instance. 
The reason we use ``--mount-type=cache,target=/var/cache/apt`` is to cache this data for future re-builds (since usually this is stable even if we're still updating our 
Python dependencies or something else). 
The reason to use ``DEBIAN_FRONTEND=noninteractive`` is that some ``apt-get install`` invocations wait for commandline input, which we can't provide during the build process. 

.. code-block:: console 

    # ubuntu dependencies 
    RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
        build-essential \
        python3-pip

.. code-block:: console 

    # install python dependencies 
    RUN pip install -r /requirements.txt \
    && rm -f /requirements.txt 

Finally, we install our Python dependencies. 
I know that ``pip`` is valid to use here since I installed python3 with the ``pip`` extra before. 
Then, we cleanup by removing the requirements file from the image (this does not affect our copy on the host). 

From here, we have a working Dockerfile. 
I choose a name for the image, say ``docker_practice``, a "tag" which is something like a version specifier (often ``latest``), and use the following command to build the image. 

.. code-block:: console 

   $ docker build --tag docker_practice:latest . 

Which looks in our current working directory for a file with name ``Dockerfile`` to build. 
After this command completes (if running for the first time, it will take a while to pull down the base image from DockerHub), we are ready to proceed. 

We can confirm that the image was built by running: 

.. code-block:: console 

   $ docker images

   REPOSITORY           TAG       IMAGE ID       CREATED        SIZE
   docker_practice      latest    0b41b87b6d2e   1 minute ago    4.93GB


Starting the Container and Executing Commands
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To start the container, run the following command (we are still on our local machines here): 

.. code-block:: console 

   $ docker run -dt -v "$(pwd)":"/docker_practice" --name dp docker_practice:latest /bin/bash 

Using ``-dt`` runs it in detached mode to keep it up in the background to respond to commands. 

On running the container, we need to `*bind* <https://docs.docker.com/engine/storage/bind-mounts/>`_  our project directory into the container runtime so that our container 
sees the same files we are looking at on the host. 
The ``-v <host-path>:<container-path>`` binds our local project directory to the directory ``/docker_practice`` in the container. 
Remember in the ``Dockerfile`` we set ``WORKDIR /docker_practice`` so all of our commands in the container will have this mounted directory as their working directory. 
This keeps things sensible because relative paths below our project directory behave in the same way. 

The ``--name dp`` sets the name of our *container* to ``dp``, and the final non-optional arguments specify the image to use and a start command (which can be left as this shell invokation). 

After running the container, we should be able to see it using: 

.. code-block:: console 

   $ docker ps 
   CONTAINER ID   IMAGE                    COMMAND       CREATED        STATUS          PORTS     NAMES
   0c4c95909fd0   docker_practice:latest   "/bin/bash"   2 minutes ago  Up 1 minute               dp 

To actually run a command in the container, we can use the following: 

.. code-block:: console 

   $ docker exec dp python3 -c "import jax.numpy as np; print(np.ones(3).devices())"
   {CpuDevice(id=0)}

As we can see, we are indeed running in our container, where ``python3`` is installed. 
Since we're still working locally, the ``jax.Array`` we instantiate has a buffer allocated on 
CPU. 

We can also check that our bind mount is working correctly, by running

.. code-block:: console 

   $ docker exec dp python3 src/example.py

   JAX dependency resolved!
   GPU not available! 

Already we've handled the basic systems to be managed in a collaborative workflow. 
We could now simply push up our ``Dockerfile``, and our collaborator can build the image and will be able to run the same code we can. 


Runtime Changes 
~~~~~~~~~~~~~~~ 

Suppose I'm developing and realize I'd like to use `Equinox <https://docs.kidger.site/equinox/>`_ to simplify a neural network implementation in raw Jax. 
Do I need to rebuild the container with this new dependency?
No (or at least, not immediately). 
As mentioned before, an advantage of Docker is the ability to mutate the image even while the container is running. I can simply use: 

.. code-block:: console 

   $ docker exec dp pip install equinox
   ... 

And now ``equinox`` is installed within the container. 
What I would usually do at this point is verify that I've chosen a version compatible with everything else, and 
then I would run:

.. code-block:: console 

   $ docker exec dp pip freeze | grep equinox >> requirements.txt 

to add equinox (version pinned) to our requirements. 
Then next time I rebuild the container (or the next person who builds the container from the version tracked ``requirements.txt``), it will already have equinox installed. 

Using GPUs 
~~~~~~~~~~

At this point let's suppose we are on a machine with a GPU (I'm using zeneba), and we've cloned our repository with the project source code and the ``Dockerfile`` and dependencies. 

Our base image already supports GPU, but we do need to change the Jax dependency to install jaxlib with cuda support. 
The way I typically do this is I create a ``build/`` directory.
I create a copy of our original Dockerfile at ``build/Dockerfile.cpu`` and put our requirements in there as well. 
After these operations my project directory looks like this: 

.. code-block:: console 

   docker-practice/ 
      build/
         requirements.txt
         Dockerfile.cpu
      src/
      Dockerfile

Finally, we need to change the Jax version to be that which enables CUDA usage. 
Since I like to maintain a separate CPU build, I again typically make a copy of our requirements at ``build/requirements_gpu.txt`` with the dependencies updated. 

.. code-block:: console 

   (zeneba) $ cat ./build/requirements_gpu.txt 

        jax[cuda12]==0.4.37

This means I also update the requirements file we load in ``docker-practice/Dockerfile`` as follows: 

.. code-block:: console 

   COPY ./build/requirements_gpu.txt /requirements.txt

Note that ``Dockerfile.cpu`` would also need to be updated as 

.. code-block:: console 

   COPY ./build/requirements.txt /requirements.txt

since we changed the location of the original requirements file. 
Those are all of the changes needed on the build side. 

Now we need to rebuild the image on this machine 

.. code-block:: console 

   (zeneba) $ docker build --tag docker_practice:latest . 
   ... 

After the build completes, we need to augment our earlier ``run`` command with the ``--gpus all`` flag, to load the required configuration so that the container can see the GPUs on the host. 

.. code-block:: console 

   (zeneba) $ docker run --gpus all -dt -v "($pwd)":"/docker_practice" --name dp docker_practice:latest /bin/bash

From here we should verify that the container can see the GPUs: 

.. code-block:: console 

   (zeneba) $ docker exec dp nvidia-smi 

       Thu Dec 12 19:27:47 2024
       +-----------------------------------------------------------------------------------------+
       | NVIDIA-SMI 560.35.03              Driver Version: 560.35.03      CUDA Version: 12.2     |
       |-----------------------------------------+------------------------+----------------------+
       | GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
       | Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
       |                                         |                        |               MIG M. |
       |=========================================+========================+======================|
       |   0  NVIDIA GeForce RTX 3080 Ti     On  |   00000000:3D:00.0 Off |                  N/A |
       |  0%   35C    P8             33W /  260W |       1MiB /  12264MiB |      0%      Default |
       |                                         |                        |                  N/A |
       +-----------------------------------------+------------------------+----------------------+

       +-----------------------------------------------------------------------------------------+
       | Processes:                                                                              |
       |  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
       |        ID   ID                                                               Usage      |
       |=========================================================================================|
       |  No running processes found                                                             |
       +-----------------------------------------------------------------------------------------+

And finally, I would confirm that Jax is installed with GPU support: 

.. code-block:: console 

   (zeneba) $ docker exec dp python3 src/example.py
   JAX dependency resolved!
   GPU available!


Supporting Multiple Targets
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now that we have two distinct Dockerfiles and sets of dependencies (one for CPU, and the other for GPU), it can be annoying to keep track of how each command is different. 
At this point in a project I typically give up and write paste this quick ``Makefile`` for the project. 

.. code-block:: console 

   .PHONY: docker-build, docker-build-cpu, docker-run, docker-run-cpu

   IMAGE_NAME := docker_practice

   docker-build : 
       docker build --tag ${IMAGE_NAME}:latest . 

   docker-build-cpu : 
       docker build --tag ${IMAGE_NAME}_cpu:latest --file ./build/Dockerfile.cpu . 

   docker-run : 
       docker run --gpus all -dt -v "$(shell pwd)":"/${IMAGE_NAME}" --name ${IMAGE_NAME} ${IMAGE_NAME}:latest /bin/bash

   docker-run-cpu : 
       docker run  -dt -v "$(shell pwd)":"/${IMAGE_NAME}" --name ${IMAGE_NAME}_cpu ${IMAGE_NAME}_cpu:latest /bin/bash

I typically add additional convenience features, but this is a quick way to support multiple targets. 
When instructing a collaborator, I would tell them to run the following on GPU: 

.. code-block:: console 

   $ make docker-build 
   $ make docker-run 

And this on CPU: 

.. code-block:: console 

   $ make docker-build-cpu
   $ make docker-run-cpu

Then they are off to the races. 


Advanced Use Cases
------------------

Using Tensorboard by Binding Ports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   This secion is under construction! Check back soon. 

Cleaning up Bloated Images
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::

   This secion is under construction! Check back soon. 

Building from Wheels
~~~~~~~~~~~~~~~~~~~~

.. note::

   This secion is under construction! Check back soon. 


Debugging within the Container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To use the Python debugger in the container runtime, we need to use the ``-it`` flag for an interative invocation of ``docker exec``: 

.. code-block:: console 

   $ docker exec -it dp python3 -m pdb src/example.py

   [2] > /docker_practice/src/example.py(1)<module>()
    -> import jax

Personally I prefer to use `ipdb <https://pypi.org/project/ipdb/>`_ and configure things so that ``breakpoint()`` in my modules defers to it. 


Resources
---------

Docker is a fairly mature system with a lot of infrastructure built out for more complex use cases. They have great online documentation, and I can highly recommend the following resources for getting familiar with Docker.

**Resources** 

- `Using Docker: Developing and Deploying Software with Containers <https://www.amazon.ca/Using-Docker-Developing-Deploying-Containers/dp/1491915765>`_
- `Docker Deep Dive <https://www.amazon.ca/Docker-Deep-Dive-Nigel-Poulton/dp/1916585256/ref=sr_1_1?crid=2PAOR0LL6SP63&keywords=docker+deep+dive&qid=1691099116&s=books&sprefix=docker+deep+div%2Cstripbooks%2C160&sr=1-1>`_
- `Docker Documentation <https://docs.docker.com/>`_
- `Dockerfile Best Practices <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/>`_

.. note::
    It’s worth distinguishing between **root** and **sudo**. The **root** user is defined as the user with UID 0: this user is (for all intents and purposes) able to execute arbitrary instructions at the operating system level. Relatedly, **sudo** is a program (not a user) currently maintained by Tom Miller, running on nearly all Linux systems. The program takes as its argument a command to be executed as root, and then consults configuration files to determine whether the request is actually permitted. Unlike commands run as **root**, using **sudo** keeps a log of the commands executed, the hosts on which they were run, the people who ran them, the directories from which they were run, and the times invoked: this simplifies administration and enhances security significantly.
