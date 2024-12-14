SLURM Resources and Templates 
=============================

A Minimal Example 
-----------------

A minimal batch script looks something like this: 

.. code-block:: console

   #!/usr/bin/env bash
   #
   # --- admin
   #SBATCH --account=lips
   #SBATCH --job-name="Minimal Job Example" 
   #SBATCH --mail-user=lipsmember@princeton.edu
   #SBATCH --mail-type=end
   #SBATCH --time=01:00:00
   #
   # --- resources
   #SBATCH --nodes=1
   #SBATCH --ntasks=1
   #SBATCH --cpus-per-task=1
   #SBATCH --gres=gpu:2
   #SBATCH --mem=64gb
   #SBATCH --output=project_space.out

   set -x 
   apptainer exec --nv -e --pwd /project container_image.sif python3 workload.py
   exit 0

I would save this in a file like ``launch.slurm`` (the extension is not required). 


Walking through the batch file, in the first block we: 

 - set the account
 - set a name for the job
 - set an email to send on the jobs completion 
 - set a time limit for the job (in this case 1 hour)

In the second block, we set resource requirements: 

 - launch the job on 1 node
 - configure 1 task (this is analagous to the number of processes launched using MPI)
 - configure 1 cpu per task 
 - configure 2 gpus per task 
 - configure 64GB of memory 
 - configure the slurm output file 

Finally, the "payload" of the job executes a script ``workload.py`` via a container runtime using ``apptainer``. 
In a setting like this, I probably sourced an environment file with variables to bind my source code directory (so that the apptainer 
container can see ``workload.py``). 
For more detail on how this works check out :doc:`apptainer`. 

I would run this job using the following command: 

.. code-block:: console 

   (ionic) $ sbatch ./launch.slurm 


Array Jobs
----------

For multiprocess jobs or workloads using MPI, one can simply configure ``ntasks`` and ``cpus-per-task`` appropriately. But a common simpler use case 
in ML involves a large collection (array) of jobs, each of which differ in some minor way, but you don't want to pull out MPI or setup a full-featured distributed 
application. 
Examples here might be: 

 - Fit a deep network varying a hyperparameter
 - Run a simpe data processing script on different partitions of an aggregate dataset 
 - Map a training run against several datasets

In this case, `slurm array jobs <https://slurm.schedmd.com/job_array.html>`_ are extremely handy. The idea here is that the batch script will launch a collection of jobs, 
each of which has a distinct local variable ``SLURM_ARRAY_TASK_ID``. 
Usually one wants to pass this variable to the target workload script, which parses this argument in some way. 
For instance, suppose the workload script looks like: 

.. code-block:: python 

   import argparse 

   import numpy as np

   parser = argparse.ArgumentParser()
   parser.add_argument("--task-id", required=True, type=int, default=0, help="Slurm Array task identifier.")
   parser.add_argument("--num-tasks", required=True, type=int, default=1, help="Number of slurm array tasks.")

   def train_net(step_size: float) -> None: 
       # training code 

   def main(args):
       if args.task_id >= args.num_tasks: 
           raise ValueError(f"Got {args.task_id=} but {args.num_tasks=}")

       step_sizes: np.ndarray = np.logspace(-6, -2, num=args.num_tasks)
       train_net(step_sizes[args.task_id])

   if __name__=="__main__": 
      args = parser.parse_args()
      main(args)

We use the provided task id determine which step size to train the network with, and have resolution that 
depends on how many tasks we are able to launch in total. 
The launch script could look as follows: 

.. code-block:: console 

   #!/usr/bin/env bash
   #
   # --- admin
   #SBATCH --account=lips
   #SBATCH --job-name="Minimal ArrayJob Example" 
   #SBATCH --mail-user=lipsmember@princeton.edu
   #SBATCH --mail-type=end
   #SBATCH --time=01:00:00
   #
   # --- resources
   #SBATCH --nodes=1
   #SBATCH --ntasks=1
   #SBATCH --cpus-per-task=1
   #SBATCH --mem=64gb
   #SBATCH --array=0-49%50
   #SBATCH --output=train_job_%A_%a.out

   set -x 
   apptainer exec -e --pwd /project container_image.sif python3 train.py --task-id=${SLURM_ARRAY_TASK_ID} --num-tasks=${SLURM_ARRAY_TASK_COUNT}
   exit 0

Monitoring Jobs 
---------------

After submitting a job to the scheduler, you can check the status of your jobs using the following:

.. code-block:: console 

   $ squeue -u ${USER}

Once the job begins, you should depend on your logging to track progress, which highlights the importance of informative logs so that you have a sense 
for what's going on. 
You could also use a tool like `Tensorboard <https://www.tensorflow.org/tensorboard>`_ or `wandb <https://wandb.ai/site/>`_. 