from tornado import ioloop
import socket
import functools
import fcntl
import tornado.web
from tornado.iostream import IOStream
from tornado.options import define, options

from afd import AccrualFailureDetector
from gossip import Gossiper

define("port", type=int, help="Port to bind for internal messaging", default=14922)
define("address", type=str, help="Address to bind for internal messaging", default="127.0.0.1")
define("seed", type=str, help="Seed for bootstrapping", default="127.0.0.1")

class MessagingService:

    def __init__(self):
        self._fd = AccrualFailureDetector()
        self._gossiper = Gossiper(self._fd)
        self._streams = {}
        self._bind()

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
        if options.address != options.seed:
            self._connect_to_node(options.seed)

    def _handle_accept(self, fd, events):
        print "_handle_accept"
        connection, address = self._socket.accept()
        host = address[0]
        stream = IOStream(connection)
        self._streams[host] = stream

        ccb = functools.partial(self._handle_close, host) #same as: cb =  lambda : self._handle_close(host)
        stream.set_close_callback(ccb)

        #self._gossiper.add_node(host)
        stream.read_until("\r\n", functools.partial(self._handle_read, host))

    def _handle_close(self, host):
        print "_handle_close"
        self._streams.pop(host)
        #self._gossiper.remove_node(host)

    def _handle_read(self, host, data):
        print "_handle_read"
        self._gossiper.new_gossip(data, host)

    def _connect_to_node(self, host, data=None):
        print "connecting to seed..."
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
            #socket.settimeout(self.timeout)
            sock.connect((host, options.port)) #TODO how to connect async?
            stream = IOStream(sock, io_loop=ioloop.IOLoop.instance())
            self._streams[host] = stream
            stream.set_close_callback(functools.partial(self._handle_close, host))
            if data:
                stream.write(data)
        except socket.error, e:
            print "socket.error"

    def send_gossip(self, to, gossip):
        print "sending gossip: %, to: %s" % (gossip, to)
        if self._streams[to]:
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


