FAQ
===

Account Management
------------------

**Do I have an account?**

If you haven’t requested an account explicitly, no, you don’t have one. 

**How do I obtain a user account?**

Fill out the `LPC Account Request Form <https://forms.gle/fq7YqgGU3r91aSCi7>`_ or reach out to Nick Richardson. 

**Do I need a separate account for each machine?**

LPC uses OpenLDAP, a distributed directory service, for authentication, meaning one set of credentials is sufficient to access any of the machines.

**How do I change my password?**

https://man7.org/linux/man-pages/man1/passwd.1.html

General
-------

**What is the LIPS Private Compute for?**

The idea here is to have our own private systems for bootstrapping small scale experiments. That is, instead of thinking of these hosts as a “second” or “private” cluster, instead they’re just machines where we have elevated privileges relative to the Princeton cluster, meaning we are able to do things like build containerized environments for our applications. A core use case would be getting your experiment set up inside of a containerized environment, and then porting it over to a Princeton CS cluster for the actual compute. Importantly, our machines also contain GPUs, so you can ensure your application runs on GPU as well before moving it over to a Princeton cluster. 

**Is (insert host here) down?**

Our hosts are configured with a monitoring system: if they do not push a message to the monitoring system each hour, a loud alert message is sent via the Slack integration to our Slack organization in the channel #lpc. Moreover, GPU availability is tested each hour (which essentially ensures that drivers are configured correctly). 

Alternatively, simply check the `LPC Administration <https://github.com/PrincetonLIPS/lpc_admin>`_ repository, which has regularly updated badges showing which machines are up. 

Feel free to submit a ticket or reach out to Nick Richardson for resolving client-side connection issues. 


SSH and Remote Connections
--------------------------

**I just got an account, and changed my password as instructed, but now I’m being prompted to change my password every time I attempt to log on, and the connection is closed as soon as I do.**

This can happen when the client is maintaining multiple connections to the host while the password change occurs (ssh can and often does multiplex connections behind the scenes). The solution in that case is to close all ssh connections to the server and then log back in. 

Installing Software
-------------------

**How can I install my own software if apt and other package management tools have to be run as root?**

The recommended approach is to use a containerized environment (see :doc:`containers`) in which tools like ``apt`` will work as you expect, and you can configure an environment to your liking. If you feel that a package is needed system-wide, submit a ticket `here <https://forms.gle/EKom4nC4PTYWwqKw6>`_ or reach out to Nick Richardson. 

File Access and Storage
-----------------------

**How do I access files between different hosts?**

LPC supports a network file system. The ``/home`` directory associated with **yubaba** is privileged in that it is mounted (over the network) on the other hosts on the ``/nfs`` directory. So there general idea is: 

- If you’re on **yubaba**, it’s business as usual
- If you’re on any other host, probably you want to set ``HOME=/nfs/home/yourusername`` in your startup script, and then it’s also business as usual.

This also helps avoid getting stuck if (1) someone else is using your usual host or (2) your usual host is down. We’ve had generally strong uptime metrics but outages do happen, especially since we depend on Princeton CS networks. 

**I accidentally deleted some crucial data, am I screwed?**

LPC maintains weekly backup snapshots, so as long as you created the data longer than one week ago, you are not screwed. If you created the data more recently than one week ago, there are still ways to potentially recover the data, but it is less likely. Please submit a ticket or reach out to Nick Richardson for help recovering data.
