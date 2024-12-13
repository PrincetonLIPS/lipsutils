Ionic 
=====

The department maintains and administrates a Beowulf cluster called Ionic. 
Although we also have access to additional Princeton Research computing (guides on Della and Neuronic to come), Ionic stands out since we have a 
daily flex reservation in the cluster scheduler of one full node worth of resources; this is called ``lips-interactive``. 
Practically speaking, we have access to 8 total nodes, each configured with 8 GPUs, meaning Ionic is an attractive candidate for sessions which are 
both interactive and multi-GPU (a relatively harder configuration to be granted on other clusters). 

So, Ionic is a great playground for interactively verifying/debugging multi-GPU projects (which are commonplace) so that you can avoid wasted time if you only 
learn that your multi-GPU configuration fails after waiting for your job to be scheduled on another cluster. 

Getting Information on Our Partition 
------------------------------------
Our Python utilities contain a thinly wrapped module which can be used to query information about nodes on our partition. There is nothing fancy going on here; it is in truth 
a convoluted way to gain this information, but lowers the barrier of entry for those not familiar with Slurm. 

Below I show an example of the usage of this utility and its output. 

.. code-block:: console 

   $ python3 -m lipsutils.ionic_info 
    ┏━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┓
    ┃ Hostname ┃ Status ┃ Free Memory ┃ CPUs ┃ Cores ┃ GPUs                 ┃ CPU Status         ┃
    ┡━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━┩
    │ node012  │ mixed  │ 252.8 GB    │ 64   │ 16    │ In use: 1 (rtx_2080) │ 32 of 64 allocated │
    │ node015  │ mixed  │ 45.9 GB     │ 64   │ 16    │ In use: 8 (rtx_2080) │ 32 of 64 allocated │
    │ node016  │ mixed  │ 28.4 GB     │ 64   │ 16    │ In use: 2 (rtx_2080) │ 4 of 64 allocated  │
    │ node009  │ idle   │ 333.4 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node010  │ idle   │ 324.3 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node011  │ idle   │ 349.1 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node013  │ idle   │ 372.2 GB    │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    │ node014  │ idle   │ 98.9 GB     │ 64   │ 16    │ In use: 0 (rtx_2080) │ 0 of 64 allocated  │
    └──────────┴────────┴─────────────┴──────┴───────┴──────────────────────┴────────────────────┘

Or in color: 

.. image:: ../media/images/ionic_info.png
   :width: 700 
   :align: center
   :alt: Ionic info screenshot.

At a glance, I'm seeing that I could grab an instance with, say 32 cpus and 8 gpus, on ``node010``, which is idle. The far right hand column is partitioned into A: Allocated, I: idle, O: other, and T: total. 
The values under ``GPUs`` can be interpreted as follows, the integer after the second colon indicates the number of GPUs already in use. 

A natural thing to do here would be to alias this call into something a bit quicker to use, so that you can pull down this information at a glance each time you login. 

.. code-block:: console 

   $ echo "alias lips-info=python3 -m lipsutils.ionic_info" >> ~/.zshrc # replace with ~/.bashrc or your appropriate shell rc

Now, simply use the following after reloading your shell. 

.. code-block:: console 

   $ lips-info 


Acquiring an Interactive Session 
--------------------------------

As I allude to above, probably the best feature of Ionic is the availability of multi-GPU interactive reservations. We also provide a simple CLI tool in our utilities package, which has the same 
status as the info tool above (contrived in a technical sense, but hopefully less scary than reading the SLURM documentation). 

Following the example from above, where I see that ``node010`` is available, I can use the following to request an interactive reservation on that node. 

.. code-block:: console

   $ python3 -m lipsutils.ionic_launch node=node010 cpus=32 gpus=8 

   salloc: Granted job allocation 22918747
   salloc: Waiting for resource configuration
   salloc: Nodes node010 are ready for job

Again, it's a bit more convenient to use an alias, so that you can use this tool like: 

.. code-block:: console

   $ launch node=node010 cpus=32 gpus=8 


Other Resources
---------------
The department maintains `documentation <https://csguide.cs.princeton.edu/resources/clusters>`_ on the cluster, and I (Nick Richardson) endorse both Chris Miller and 
Asya Dvorkin as great people to fire off an email to. The other admins may also be helpful, but I have firsthand experience with Chris and Asya. 
