Formatting and IO Tools 
=======================

String Formatting
-----------------

For temporal outputs from microbenchmarks, integer byte outputs from methods like ``array.nbytes``, etc., I like 
to have some ways to clean up the output. 

.. code-block:: python 

   import time 

   import numpy as np

   from lipsutils.utils import * 

   X: np.ndarray = np.zeros((100, 100))

   def microbenchmark(): 
       for _ in range(100): 
           _ = X @ X 

   start = time.perf_counter()
   microbenchmark()
   runtime = time.perf_counter() - start

   print(f"X size: {human_bytes_str(X.nbytes)}")
   print(f"Microbenchmark runtime: {human_seconds_str(runtime)}")

With output: 

.. code-block:: console 

   $ python3 example.py 

   X size: 78.1 KB
   Microbenchmark runtime: 920 microseconds

Logging 
-------

I prefer to keep my logging as clean as possible, often writing out more verbose logs to a file but keeping ``stdout`` fairly terse. 
I also commonly encounter the use case that I want to quickly setup a logger in different parts of an application, and make sure all the output goes to the same place. 
The ``log_utils`` module offers a single simple API function which handles all of these cases. 

.. code-block:: python 

   import logging

   from lipsutils.log_utils import setup_logger 

   log = setup_logger(
            __file__, 
            stream_level=logging.WARNING, # reduce noise on stdout 
            file_level=logging.INFO,      # but capture everything just in case! 
            custom_handle="mylog.out",    # where the output should be written
            ) 

   log.info("Hi file") 
   log.warn("Hi stdout!") 

De/Serialization
----------------

We should always prefer custom binary formats by using ``np.save`` for numeric data, for instance. 
But sometimes I want a quick-and-dirty way to serialize some arbitrary Python object, and again, I find myself 
writing the same code over and over again. 

.. code-block:: python 

   from lipsutils.utils import serialize, deserialize 

   class RandomObject: 
       pass

   instance = RandomObject()
   save_path = "random.pkl"
   serialize(instance, save_path)
   reloaded = deserialze(save_path)

