from tornado import ioloop
from time import sleep
import errno
import logging
import os
import socket
import functools
import fcntl
import time
import urlparse
import tornado.web
from tornado.iostream import IOStream
from tornado.options import define, options

from afd import AccrualFailureDetector
from gossip import Gossiper

define("port", type=int, help="Port to bind for internal messaging", default=14922)
define("address", type=str, help="Address to bind for internal messaging", default="localhost")
define("seed", type=str, help="Seed for bootstrapping")

class Messaging:

    def __init__(self):
        self._fd = AccrualFailureDetector()
        self._gossiper = Gossiper(self._fd)
        self._bind()
        self._sockets = []
        self._streams = {}

    def _bind(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        flags = fcntl.fcntl(self._socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self._socket.fileno(), fcntl.F_SETFD, flags)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(0) #equivalent to s.settimeout(0.0);
        self._socket.bind((options.address, options.port))
        self._socket.listen(128)    #backlog
        ioloop.IOLoop.instance().add_handler(self._socket.fileno(), self._handle_accept, ioloop.IOLoop.READ)
        print "bind complete"
        self._connect_to_seed()

    def _handle_accept(self, fd, events):
        print "_handle_accept"
        connection, address = self._socket.accept()
        stream = IOStream(connection)
        self._sockets.append(connection)
        self._streams[connection] = stream

        ccb = functools.partial(self._handle_close, connection) #same as: cb =  lambda : self._handle_close(connection)
        stream.set_close_callback(ccb)

        stream.read_until("\r\n", functools.partial(self._handle_read, connection))

    def _handle_close(self, socket):
        print "_handle_close"
        #TODO cleanup + start reconnect logic

    def _handle_read(self, socket, data):
        print "_handle_read"
        print data
        print socket.getpeername()

    def _connect_to_seed(self):
        print "connecting to seed..."

def main():
    tornado.options.parse_command_line()
    print "start"
    Messaging()
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()


