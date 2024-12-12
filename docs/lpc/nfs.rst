Network File System and Redundancy 
==================================

.. note::
    - NFS is a protocol to share filesystems across hosts
    - Store important data on the NFS so you’re not tied to any one host. We share the home directory of Yubaba: if you’re on another host you can access this at ``/nfs/home``.
    - Absolutely mission-critical data (I absolutely cannot lose access to this data for even 24 hours) should also be backed up to one additional host. Automatic backup snapshots are taken daily. Contact Nick Richardson for help recovering data.

Network File System Protocol
----------------------------

Commonly known as NFS, the protocol enables the sharing of filesystems amount computers. NFS is nearly transparent to users, and no information is lost when an NFS server (Yubaba, in our case) crashes. Clients can simply wait until the server returns and then continue as if nothing happened. 

**Server Side**

Yubaba is said to “export” its home directory: meaning it makes the directory available for use by the other hosts. Exports are present to NFSv4 clients as a single filesystem hierarchy through a psuedo-filesystem. We don’t maintain the access-control database directly, but instead use configuration management and ``/etc/exports`` to enumerate and configure exported directories and their access settings. 

**Client Side**

NFS filesystems end up getting mounted basically the same way the local filesystems are. The mount maps the remote directory on the remote host (Yubaba) into a directory within the local file tree. After mounting you can access an NFS filesystem exactly like you would a local filesystem. In LPC we mount to ``/nfs/home`` on Zeneba and Kamaji. 

Recommended Use
---------------

The ``/home`` directory of ``yubaba`` is mounted (via a network file share system) to the ``/nfs/home`` directories of the other hosts. You’ll generally want to maintain your data at that location then, so that you have the ability to work on any of the individual hosts (in case another host is in use or down). To automate this, you can modify your ``HOME`` environment variable from your shell launch script, for example. 

**What if the NFS server goes down?**

In the case that ``yubaba`` goes down, data that exists only on network file system will be temporarily unavailable. We’ve not yet had an outage longer than 24 hours or so, but for mission-critical data one should always be using version control to maintain development environment build scripts (e.g., Dockerfile). That way, if ``yubaba`` were to go down you could rebuild your development environment on another host. 

On my list is to automate this behind the scenes, backing up snapshots of ``yubaba`` and artificially (and temporarily) restoring the artifice of the NFS on the other hosts, but for now some care should be taken to ensure your data and development environment are not tied to any one host.
