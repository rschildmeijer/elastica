from tornado import ioloop
import socket
import functools
import fcntl
import tornado.web
import ast
import time
from tornado.iostream import IOStream
from tornado.options import define, options

from afd import AccrualFailureDetector
from gossip import Gossiper

#define("port", type=int, help="Internal messaging",default=14922)
define("address", type=str, help="Internal messaging", default="85.235.31.253:14923")
define("seed", type=str, help="For bootstrapping", default="85.235.31.253:14922")


class MessagingService:

    def __init__(self):
        self._fd = AccrualFailureDetector()
        self._gossiper = Gossiper(self._fd, self)
        self._gossiper.register_application_state_publisher(DummyPublisher()) #remove this line
        self._streams = {}
        self._seed=(options.seed.split(':'))
        self._verb_handlers = {} #Lookup table for registering message handlers based on the verb
        self._bind()

    def _bind(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        flags = fcntl.fcntl(self._socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self._socket.fileno(), fcntl.F_SETFD, flags)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(0) #equivalent to s.settimeout(0.0);
        host, port = options.address.split(":")
        self._socket.bind(("0.0.0.0", int(port)))
        self._socket.listen(128)    #backlog
        ioloop.IOLoop.instance().add_handler(self._socket.fileno(), self._handle_accept, ioloop.IOLoop.READ)

    def _handle_accept(self, fd, events):
        connection, address = self._socket.accept()
        stream = IOStream(connection)
        host = "%s:%d" % address #host = ":".join(str(i) for i in address)
        self._streams[host] = stream

        ccb = functools.partial(self._handle_close, host) #same as: cb =  lambda : self._handle_close(host)
        stream.set_close_callback(ccb)
        stream.read_until("\r\n", functools.partial(self._handle_read, host))

    def _handle_close(self, host):
        print "handle close"
        self._streams.pop(host)

    def _handle_read(self, host, data):
        self._gossiper.new_gossip(ast.literal_eval(data.rstrip()), host)
        self._streams[host].read_until("\r\n", functools.partial(self._handle_read, host))

    """
    def _connect_to_node(self, host, data=None):
        def on_connect():
            self._streams[host].read_until("\r\n", functools.partial(self._handle_read, host))
            if data:
                stream.write(data)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            stream = IOStream(sock)
            print "connect to: %s" % host
            address = host.split(':')
            stream.connect(tuple((address[0], int(address[1]))), on_connect)
            self._streams[host] = stream
            stream.set_close_callback(functools.partial(self._handle_close, host))
        except socket.error, e:
            print "could not connect"
    """
    def _connect_to_node(self, host, data=None):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            address = host.split(':')
            sock.connect(tuple((address[0], int(address[1]))))
            stream = IOStream(sock, io_loop=ioloop.IOLoop.instance())
            self._streams[host] = stream
            stream.set_close_callback(functools.partial(self._handle_close, host))
            self._streams[host].read_until("\r\n", functools.partial(self._handle_read, host))
            if data:
                stream.write(data)
        except socket.error, e:
            a = 5

    def register_verb_handler(self, verb, verb_handler):
        self._verb_handlers[verb] = verb_handler

    def send_one_way(self, to, gossip):
        # if to == options.address:
        #    handle local delivery
        if self._streams.has_key(to):
            self._streams[to].write(gossip)
        else:
            self._connect_to_node(to, gossip)

class DummyPublisher:

    def name(self):
        return "load-information"

    def value(self):
        #return ("load", 1492)
        return ("load", int(time.time()))

def main():
    tornado.options.parse_command_line()
    print "start"
    MessagingService()
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()


