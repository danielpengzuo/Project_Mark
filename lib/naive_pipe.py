from   queue import Queue
from   threading import Thread

class NaivePipe:
    """
    Just a Queue with a listener function, running in a background
    thread.
    """
    def __init__(self, on_item, thread_name=None):
        """
        :param listener:
          Function to be called on the listener end for each item.
        """
        self._queue = Queue()
        self.on = True
        def _listen():
            while self.on:
                item = self._queue.get()
                on_item(item)
        self._thread = Thread(target=_listen, name=thread_name)
        self._thread.start()


    def put(self, item):
        self._queue.put(item)


    def close(self):
        self.on = False
        self._thread.join()
