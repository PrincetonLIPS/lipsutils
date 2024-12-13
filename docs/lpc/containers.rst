Using Containers 
================

.. note::

    **TLDR**

    - You can’t install system-wide packages: instead use container images and build files to manage development environments.
    - All users are members of the **docker** group: you don’t need to run docker commands using **sudo**.
    - A collection of default images are installed and maintained on every host (please do not clobber these images)
        - Alpine Linux (latest)
        - Ubuntu Linux (latest)
        - PyTorch 2.0.1
        - Tensorflow (latest)
    - See :doc:`gpu` for information on containers with support for GPUs.

For sanity of user experience and administration alike, general users are not able to download packages globally to any host (for example, using the advanced package tool **apt** on Debian-based Linux). The rationale here is that users will in the usual case not be aware of packages that have been/will be downloaded by others. By inadvertently downloading, upgrading, or removing packages, users can easily create an incompatible collection of packages and bring the whole system down or break other users’ applications. 

That said, users clearly need the ability to download packages and create custom environments to run all but the simplest applications. 
So, develop your projects and applications within a Docker container!

If you're not familiar with Docker, I recommend reading :doc:`../tutorials/docker` as an overview. 