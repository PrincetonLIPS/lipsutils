Interoperating Docker and Apptainer
===================================

This page assumes you have a ``Dockerfile`` for an associated docker container which with you've been developing on a local machine or LPC. 
If you're unfamiliar with docker or containers in general, check out :doc:`../tutorials/docker` for an introduction.

To use the Princeton Research Clusters, you must also develop at least a basic familiarity with `Apptainer <https://apptainer.org/>`_, another containerization platform which is preferred on academic clusters. 

This page describes how to migrate a ``Dockerfile`` to an analagous Apptainer build file, which is used to derive an Apptainer image to run your code on a Princeton research cluster. 

Example 
-------

We'll use the same project described in :doc:`../tutorials/docker`, so take a look at that material if this seems unfamiliar. 
Our ``Dockerfile`` is shown below: 

.. code-block:: console 

    # syntax=docker/dockerfile:1

    FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
    LABEL maintainer="njkrichardson@princeton.edu" 

    COPY ./requirements.txt /requirements.txt

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

    # syntax=docker/dockerfile:1

    FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
    LABEL maintainer="njkrichardson@princeton.edu" 

    COPY ./requirements.txt /requirements.txt

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


