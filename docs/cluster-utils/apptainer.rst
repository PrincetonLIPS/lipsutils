Interoperating Docker and Apptainer
===================================

This page assumes you have a ``Dockerfile`` for an associated docker container with which you've been developing on a local machine or LPC. 
If you're unfamiliar with docker or containers in general, check out :doc:`../tutorials/docker` for an introduction.

To use the Princeton Research Clusters, you must also develop at least a basic familiarity with `Apptainer <https://apptainer.org/>`_, another containerization platform which is preferred on academic clusters. 

This page describes how to migrate a ``Dockerfile`` to an analogous Apptainer build file, which is used to derive an Apptainer image to run your code on a Princeton research cluster. 

Example 
-------

We'll use the same project described in :doc:`../tutorials/docker`, so take a look at that material if this seems unfamiliar. 
Our ``Dockerfile`` is shown below: 

.. code-block:: console 

    # syntax=docker/dockerfile:1

    FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
    LABEL maintainer="njkrichardson@princeton.edu" 

    COPY ./build/requirements.txt /requirements.txt

    WORKDIR /docker-practice
    ENV PYTHONPATH=/docker-practice:/docker-practice/src

    # ubuntu dependencies 
    RUN --mount=type=cache,target=/var/cache/apt \
    apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install --yes \
        build-essential \
        python3-pip

    # install python dependencies 
    RUN pip install -r /requirements.txt \
    && rm -f /requirements.txt 

    CMD ["/bin/bash"]

Below I show the translation of this ``Dockerfile`` into an Apptainer ``build.def`` 

.. code-block:: console 

    Bootstrap: docker
    From: nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

    %files
        ./build/requirements.txt /requirements.txt

    %post
        apt-get -y update
        DEBIAN_FRONTEND=noninteractive apt-get install --yes \
            build-essential \
            python3-pip

        # install python dependencies
        pip install -r /requirements.txt \
        && rm -f /requirements.txt

We can see that these are almost identical. 
It's important to use the ``Bootstrap: docker`` directive if you want to use the same base image as the 
Docker image. 

.. code-block:: console 

    Bootstrap: docker
    From: nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04

We then use a ``%files`` block to execute our copy operations, which mirror the Docker ``COPY`` instruction in format (host source, destination).

.. code-block:: console 

    %files
        ./build/requirements.txt /requirements.txt

Finally, our ``%post`` section executes the analagous ``RUN`` instructions as in our Dockerfile. 

.. code-block:: console 

    %post
        apt-get -y update
        DEBIAN_FRONTEND=noninteractive apt-get install --yes \
            build-essential \
            python3-pip

        # install python dependencies
        pip install -r /requirements.txt \
        && rm -f /requirements.txt

I would then save this file as ``build/build.def``, for instance, and execute: 

.. code-block:: console 

    (ionic) $ apptainer build build/dp.sif build/build.def 

Which would then build the image. 

Apptainer Environment 
~~~~~~~~~~~~~~~~~~~~~~~

Unlike Docker, where I explicitly bind environment variables at build time, with Apptainer I use a slightly different approach because of the difference in their 
underlying architecture with respect to filesystem visibility. 

In :doc:`../tutorials/docker` I described explicitly binding our working directory, and the ``PYTHONPATH``, for instance, at build time. 
With Apptainer, containers by default have visibility over host environment variables, so to better isolate my containers from the host, I run all Apptainer commands 
with ``apptainer exec -e --pwd /docker_practice`` which cleans the environment before running the container, and sets our working directory. 

The way I configure binding (analagous to ``docker run -v <host_path>:<container_path>``) and environment variables is maintaining a separate file with this configuration. 
For instance, let's say I have a ``.env`` with the following contents. 

.. code-block:: console 

    (ionic) $ cat .env 

    export APPTAINERENV_PYTHONPATH="/docker_practice:/docker_practice/src"
    export APPTAINER_BINDPATH="$(pwd):/docker_practice"

Then I would simply ``source .env`` before running ``apptainer exec -e --pwd /docker_practice ./build/dp.sif python3 src/example.py`` which is analagous to 
how things worked in Docker. 
See the `documentation <https://apptainer.org/docs/user/main/environment_and_metadata.html>`_ for further details on how environment variables work with Apptainer. 


Apptainer Runtime Usage 
~~~~~~~~~~~~~~~~~~~~~~~

Using an apptainer image at runtime is slightly different, rather than starting the container in detached mode in the background, we typically simply execute single commands using 
``apptainer exec``, for example at the payload of a Slurm batch script (see :doc:`slurm` for details). 
For GPU usage, be sure to provide the ``--nv`` flag. 