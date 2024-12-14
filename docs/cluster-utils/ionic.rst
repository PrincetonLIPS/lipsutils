Ionic 
=====

The computer science department maintains and administrates a Beowulf cluster called Ionic. 
Although our group also has access to several other Princeton Research computing clusters (guides on Della and Neuronic to come), Ionic stands out since we have a 
daily flex reservation in the cluster scheduler of one full node worth of resources; this is called ``lips-interactive``. 
In practice, we have access to 8 total nodes, each configured with 8 RTX 2080Ti GPUs, making Ionic an attractive candidate for sessions which are 
both interactive and multi-GPU (a relatively harder configuration to be granted on other clusters). 

An Ionic interactive session should be in your workflow for interactively verifying and debugging multi-GPU projects. 
It's painful to waste time in the queue of a job scheduler only to find out that your multi-GPU configuration fails, when you could have quickly 
verified it on with interactive session.  

Getting Information on Our Partition 
------------------------------------
Our :doc:`Python utilites <../python-utils/api>` contain a script which can be used to query information about nodes on our partition. There is nothing fancy going on here; it is in truth 
a convoluted way to gain this information, but lowers the barrier of entry for those not familiar with Slurm. 

Below I show an example of the usage of this utility and its output, assuming you've installed the Python package and are on one of the Ionic login nodes. 
To connect to Ionic, check out the `connection guide <https://researchcomputing.princeton.edu/support/knowledge-base/connect-ssh>`_. 

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


At a glance, I'm seeing that I could grab an instance with 32 cpus and 8 gpus on ``node010``, which is idle. 
The colors help me quickly sort visually nodes/resources that are completely free (green), partially allocated (orange), or nearly/completely allocated (red). 

I create an `alias <https://www.gnu.org/software/bash/manual/html_node/Aliases.html>`_ so that I can pull down this information at a glance each time I login. 

.. code-block:: console 

   $ echo "alias lips-info=\"python3 -m lipsutils.ionic_info\"" >> ~/.zshrc # replace with ~/.bashrc or your appropriate shell rc

Now, I can use the following after reloading my shell. 

.. code-block:: console 

   $ lips-info 


Acquiring an Interactive Session 
--------------------------------

As I allude to above, probably the best feature of Ionic is the opportunity to be granted interactive multi-GPU reservations. 
We also provide a simple CLI tool in our utilities package, which has the same status as the tool above; which is to say contrived in a technical sense, 
but less scary than reading the SLURM documentation. 

Following the example from above, where I see that ``node010`` is available, I can use the following to request an interactive reservation on that node. 

.. code-block:: console

   $ python3 -m lipsutils.ionic_launch --node=node010 --cpus=32 --gpus=8 

   salloc: Granted job allocation 22918747
   salloc: Waiting for resource configuration
   salloc: Nodes node010 are ready for job

Again, it's a bit more convenient to use an alias, so that you can use this tool like: 

.. code-block:: console

   $ launch --node=node010 --cpus=32 --gpus=8 


Other Resources
---------------

  - Ionic hardware, storage, and software is detailed in `this document <https://csguide.cs.princeton.edu/resources/clusters>`_. 
  - The `SLURM resource scheduler <https://slurm.schedmd.com/documentation.html>`_ is widely used, and worth gaining familiarity with. 
  - The department maintains some `documentation <https://csguide.cs.princeton.edu/resources/clusters>`_ on the cluster, and I (Nick Richardson) endorse both Chris Miller and Asya Dvorkin as great people to fire off an email to for questions that are not covered in the docs. The other admins may also be helpful, but I have firsthand experience working with Chris and Asya to resolve strange issues, explain many aspects of the cluster design/operation, and handle special requests for particular jobs.
  

.. note::

   Other clusters like Neuronic and Della offer different tradeoffs and will be covered in a separate document. 
   For instance, Neuronic contains a number of L40 GPUs, which offer significantly higher GPU memory and FP32/FP64 performance. 
