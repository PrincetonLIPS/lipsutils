Using Containers 
================

.. note::

    - You can’t install system-wide packages: instead use container images and build files to manage development environments.
    - All users are members of the **docker** group: you don’t need to run docker commands using **sudo**.
    - A collection of default images are installed and maintained on every host (please do not clobber these images)
        - Alpine Linux (latest)
        - Ubuntu Linux (latest)
        - PyTorch 2.0.1
        - Tensorflow (latest)
    - See :doc:`gpu` for information on containers with support for GPUs.

Background
----------

For sanity of user experience and administration alike, general users are not able to download packages globally to any host (for example, using the advanced package tool **apt** on Debian-based Linux). The rationale here is that users will in the usual case not be aware of packages that have been/will be downloaded by others. By inadvertently downloading, upgrading, or removing packages, users can easily create an incompatible collection of packages and bring the whole system down or break other users’ applications. 

That said, users clearly need the ability to download packages and create custom environments to run all but the simplest applications. Consider the minimal requirements to run some generic application for research in scientific computing: 

- The code for the application and its (correct) configuration
- Libraries and other dependencies (potentially dozens), each pinned to a specific version that is known to be compatible with the application and the other dependencies
- An interpreter (e.g., CPython) or runtime to execute the code, also version pinned
- Localizations like user accounts, environment settings, and services provided by the operating system

Container images simplify this workflow drastically by packaging an application and its requirements into a standardized, portable file. The image is the static-time construct, and a container engine (e.g., Docker, Singularity) enables one to instantiate the container, the run-time construct, as a pseudo-isolated process tree sharing the kernel of the host. Tens or hundreds of containers can run simultaneously on the same host without conflicts thanks to kernel namespaces and Linux cgroups features. 

With images typically being a few hundred megabytes in size, it’s practical to copy them between hosts. In machine learning research, images often contain one or more deep learning frameworks (each of which might be several hundred megabytes alone) as well as version pinned GPU libraries. A full-fledged image for a research project (with ML tools, visualization libraries, developer tooling, etc) can result in bloated images to several gigabytes or more. The reason containers are still used widely in industry ML applications is that **reproducibility** and ease of use is unmatched by Python package management (pip, conda, mamba), and disk is extremely cheap. 

Workflows
---------

.. note::

    This section is undergoing some maintenance, check back soon!



Resources
---------

Docker is a fairly mature system with a lot of infrastructure built out for more complex use cases. They have great online documentation, and I can highly recommend the following resources for getting familiar with Docker.

**Resources** 

- `Using Docker: Developing and Deploying Software with Containers <https://www.amazon.ca/Using-Docker-Developing-Deploying-Containers/dp/1491915765>`_
- `Docker Deep Dive <https://www.amazon.ca/Docker-Deep-Dive-Nigel-Poulton/dp/1916585256/ref=sr_1_1?crid=2PAOR0LL6SP63&keywords=docker+deep+dive&qid=1691099116&s=books&sprefix=docker+deep+div%2Cstripbooks%2C160&sr=1-1>`_
- `Docker Documentation <https://docs.docker.com/>`_
- `Dockerfile Best Practices <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/>`_

*modulo some unimportant technical details 

.. note::
    It’s worth distinguishing between **root** and **sudo**. The **root** user is defined as the user with UID 0: this user is (for all intents and purposes) able to execute arbitrary instructions at the operating system level. Relatedly, **sudo** is a program (not a user) currently maintained by Tom Miller, running on nearly all Linux systems. The program takes as its argument a command to be executed as root, and then consults configuration files to determine whether the request is actually permitted. Unlike commands run as **root**, using **sudo** keeps a log of the commands executed, the hosts on which they were run, the people who ran them, the directories from which they were run, and the times invoked: this simplifies administration and enhances security significantly.
