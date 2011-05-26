from tornado import ioloop
import socket
import functools
import fcntl
import tornado.web
import ast
from tornado.iostream import IOStream
from tornado.options import define, options

from afd import AccrualFailureDetector
from gossip import Gossiper

#define("port", type=int, help="Internal messaging",default=14922)
define("address", type=str, help="Internal messaging", default="192.168.0.199:14922")
define("seed", type=str, help="For bootstrapping", default="192.168.0.199:14922")

class MessagingService:

    def __init__(self):
        self._fd = AccrualFailureDetector()
        self._gossiper = Gossiper(self._fd, self)
        self._streams = {}
        self._seed=(options.seed.split(':'))
        self._bind()

    def _bind(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        flags = fcntl.fcntl(self._socket.fileno(), fcntl.F_GETFD)
        flags |= fcntl.FD_CLOEXEC
        fcntl.fcntl(self._socket.fileno(), fcntl.F_SETFD, flags)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.setblocking(0) #equivalent to s.settimeout(0.0);
        address = options.address.split(":")    #feels clumsy
        self._socket.bind(tuple((address[0], int(address[1]))))
        self._socket.listen(128)    #backlog
        ioloop.IOLoop.instance().add_handler(self._socket.fileno(), self._handle_accept, ioloop.IOLoop.READ)
      
    def _handle_accept(self, fd, events):
        connection, address = self._socket.accept()
        stream = IOStream(connection)
        host = ":".join(str(i) for i in address)
        self._streams[host] = stream

        ccb = functools.partial(self._handle_close, host) #same as: cb =  lambda : self._handle_close(host)
        stream.set_close_callback(ccb)
        stream.read_until("\r\n", functools.partial(self._handle_read, host))

    def _handle_close(self, host):
        self._streams.pop(host)

    def _handle_read(self, host, data):
        self._gossiper.new_gossip(ast.literal_eval(data.rstrip()), host)
        self._streams[host].read_until("\r\n", functools.partial(self._handle_read, host))

    def _connect_to_node(self, host, data=None):
        def on_connect(self):
            self._streams[host].read_until("\r\n", functools.partial(self._handle_read, host))
            if data:
                stream.write(data)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            stream = IOStream(sock)
            print "connect to: %s" % host
            stream.connect(tuple(host.split(':')), on_connect)
            self._streams[host] = stream
            stream.set_close_callback(functools.partial(self._handle_close, host))
        except socket.error, e:
            print "could not connect"



    def send_one_way(self, to, gossip):
        if self._streams.has_key(to):
            self._streams[to].write(gossip)
        else:
            self._connect_to_node(to, gossip)

def main():
    tornado.options.parse_command_line()
    print "start"
    MessagingService()
    ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()


