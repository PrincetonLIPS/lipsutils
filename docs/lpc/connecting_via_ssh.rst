Connecting via SSH 
==================


.. note::

   **TLDR**

   - Our hosts aren’t accessible over the public network, use:
       - ``ssh -J ${PRINCETON_NETID}@cycles.cs.princeton.edu ${LPC_USER}@${LPC_HOST}``  from the command line (substitute the variables).
       - Add ``ProxyJump ${PRINCETON_NETID}@cycles.cs.princeton.edu`` to your ssh configuration for the LPC hosts.
   - LPC Static IPs:
       - Yubaba: 172.17.0.102
       - Zeneba: 172.17.0.112
       - Kamaji: 172.17.0.115

Background
----------

To avoid exposing our machines to the public internet, we use Princeton CS servers as jump proxies with the standard secure shell (SSH) protocol. That way our machines have private IPs within the Princeton wired network and are not exposed publicly, but we can still access the machines remotely (that is, over the campus wireless network, or off campus entirely). 

Note: I use “client” here to refer to your local machine: the one you’re trying to use to connect remotely to one of the LPC hosts. I use “host” or “server” to refer to the machine you’re attempting to SSH into. 

Instructions
------------

On the client, open your SSH configuration in a text editor: usually this resides at ``~/.ssh/config`` on GNU/Linux or MacOS machines. 

Paste the following configuration for any of the hosts you intend to use regularly: replacing the IP as necessary with the IP of the host. Here’s a concrete example for a configuration with **yubaba**. 


.. code-block:: console

      Host yubaba
              HostName 172.17.0.102
              User ${LPC_USER}
              Port 22
              ProxyJump ${PRINCETON_NETID}@cycles.cs.princeton.edu 

Passwordless Authentication
---------------------------

To bypass entering your password every time you connect over SSH, you can instead use a key pair to authenticate. On the client-side, you’ll need to generate a key pair (if you don’t already have one). On the server side, you’ll need to add the client’s public key to your ``~/.ssh/authorized_keys`` file. 

**Client-side** 

We’ll use the ``ssh-keygen`` utility to generate an RSA key pair. 

1. Use ``ssh-keygen -t rsa``
2. Accept the default location or add a custom location (you probably can just accept the default). 
3. Enter a passcode or simply hit enter when asked for a passcode for passwordless authentication. 
4. Navigate to the location where the keys were saved (probably ``~/.ssh``) and copy your public key onto the server. 

**Server-side** 

Wherever you copied over your public key (say, ``~/id_rsa.pub``), add it to ``~/.ssh/authorized_keys`` using ``cat ~/id_rsa.pub >> ~/.ssh/authorized_keys``.
