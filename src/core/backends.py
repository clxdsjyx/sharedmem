import os
import multiprocessing
import threading
import Queue as queue

__shmdebug__ = False
__all__ = ['set_debug', 'get_debug', 'cpu_count', 'ThreadBackend', 'ProcessBackend']

def set_debug(flag):
  """ in debug mode (flag==True), no slaves are spawn,
      rather all work are done in serial on the master thread/process.
      so that if the worker throws out exceptions, debugging from the main
      process context is possible. (in iptyhon, with debug magic command, eg)
  """
  global __shmdebug__
  __shmdebug__ = flag

def get_debug():
  global __shmdebug__
  return __shmdebug__

def cpu_count():
  """ The cpu count defaults to the number of physical cpu cores
      but can be set with OMP_NUM_THREADS environment variable.
      OMP_NUM_THREADS is used because if you hybrid sharedmem with
      some openMP extenstions one environment will do it all.

      on some machines the physical number of cores does not equal
      the number of cpus shall be used. PSC Blacklight for example.

      Pool defaults to use cpu_count() slaves. however it can be overridden
      in Pool.
  """
  num = os.getenv("OMP_NUM_THREADS")
  try:
    return int(num)
  except:
    return multiprocessing.cpu_count()

class ThreadBackend:
      QueueFactory = staticmethod(queue.Queue)
      JoinableQueueFactory = staticmethod(queue.Queue)
      EventFactory = staticmethod(threading.Event)
      @staticmethod
      def SlaveFactory(*args, **kwargs):
        slave = threading.Thread(*args, **kwargs)
        slave.daemon = True
        return slave
      LockFactory = staticmethod(threading.Lock)
      StorageFactory = staticmethod(threading.local)

class ProcessBackend:
      QueueFactory = staticmethod(multiprocessing.Queue)
      JoinableQueueFactory = staticmethod(multiprocessing.JoinableQueue)
      EventFactory = staticmethod(multiprocessing.Event)
      LockFactory = staticmethod(multiprocessing.Lock)
      @staticmethod
      def SlaveFactory(*args, **kwargs):
        slave = multiprocessing.Process(*args, **kwargs)
        slave.daemon = True
        return slave
      @staticmethod
      def StorageFactory():
          return lambda:None

