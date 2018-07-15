from threading import Thread
from websocket import (
    create_connection,
    WebSocketConnectionClosedException,
    WebSocketAddressException
)
import json
import logging


# TODO: Configurable
MAX_RETRY = 5

class BaseWebSocket:
    def __init__(self, base_url, thread_name=None):
        self.base_url = base_url
        self.ws = None
        self._thread_name = thread_name
        self._retry = 0


    def start(self):
        """
        :param params:
          A dictionary of http query parameters to send.
          See https://docs.gemini.com/websocket-api/#market-data
          for details.

          The default is because this keeps idle connection from
          being closed.
        """
        def _go():
            self.stop = False
            self.on_open()
            self._connect()
            self._listen()
            self._disconnect()
            self.on_close()
        self.thread = Thread(target=_go, name=self._thread_name)
        self.thread.start()


    def _new_socket(self):
        return create_connection(self.base_url)


    def _connect(self):
        if self.stop:
            return
        self._retry += 1
        if self._retry > MAX_RETRY:
            # Hard failure
            raise RuntimeError(
                f"max retry ({MAX_RETRY}) exceeded for socket connection"
            )
        try:
            self.ws = self._new_socket()
        except Exception as e:
            logging.error("Failed to make new socket", exc_info=e)
            # Retry
            self._connect()
        else:
            self.on_connection()


    def _listen(self):
        while not self.stop:
            try:
                data = self.ws.recv()
            except (WebSocketConnectionClosedException, WebSocketAddressException):
                self.on_disconnection()
                self._connect()
            except Exception as e:
                # TODO: more thinking here
                self.on_error(e)
            else:
                try:
                    self.on_message(json.loads(data))
                except Exception as e:
                    self.on_error(e)


    def _disconnect(self):
        try:
            if self.ws:
                self.ws.close()
                self.on_disconnection()
        except WebSocketConnectionClosedException as e:
            pass


    def close(self):
        self.stop = True
        self.thread.join()


    def on_open(self):
        """
        Callback on the start of the entire persistent client.
        """
        logging.info('Starting client')


    def on_message(self, msg):
        raise NotImplementedError()


    def on_error(self, e):
        logging.error(repr(e))


    def on_close(self):
        """
        Callback on the closing of the entire persistent client.
        """
        logging.info('Client closed')


    def on_connection(self):
        """
        Callback on single web socket connection.
        """
        self._retry = 0
        logging.info(f'Connected to {self.base_url}')


    def on_disconnection(self):
        """
        Callback on single web socket disconnection.
        """
        logging.info(f"Web socket {self.base_url} disconnected")
