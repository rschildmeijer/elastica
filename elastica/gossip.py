import random
import math
import tornado.web
from tornado import ioloop
from tornado.options import options
from tornado.ioloop import PeriodicCallback

class Gossiper(object):
    """ This module is responsible for Gossiping cluster information. The abstraction
    maintains the list of live and dead nodes. Periodically i.e. every 1 second this module
    chooses a random node and initiates a round of Gossip with it. This module as and when it hears a gossip
    updates the Failure Detector with the liveness information.

    Amazon paper on Gossip at http://www.cs.cornell.edu/home/rvr/papers/flowgossip.pdf

    Gossip timer task runs every second.
    During each of these runs the node initiates gossip exchange according to following rules:
      1, Gossip to random live node (if any)
      2, Gossip to random unreachable node with certain probability depending on number of unreachable and live nodes
      3, If the node gossiped to at (1) was not seed, or the number of live nodes is less than number of seeds,
         gossip to random seed with certain probability depending on number of unreachable, seed and live nodes."""


    def __init__(self, fd):
        self._fd = fd
        self._node_states = {}
        self._alive_nodes = [] #maybe a set() would be more appropriate?
        self._dead_nodes = []
        self._node_state_change_listeners = []  #on_join(host), on_alive(host), on_dead(host)
        self._generation = random.randint(1, math.pow(2, 32))
        self._version = 1
        self._local_node = options.address

        PeriodicCallback(self._initiate_gossip_exchange, 1000, ioloop.IOLoop.instance()).start()
        PeriodicCallback(self._scrutinize_cluster, 1000, ioloop.IOLoop.instance()).start()

    def _initiate_gossip_exchange(self):
        print "sending gossip"

    def _scrutinize_cluster(self):
        print "scrutinize cluster"

#    def add_node(self, host):
#        """ Invoked by the MessagingService when a new node has connected to me """
#        if host not in self._alive_nodes:
#            self._alive_nodes.append(host)
#        if host in self._dead_nodes:
#            self._dead_nodes.remove(host)
#            self._notify_on_alive(host)
#        else:
#            self._notify_on_join(host)
#        self._fd.heartbeat(host)

#    def remove_node(self, host):
#        """ Invoked by the MessagingService when we lose the connection to a node """
#        if host in self._alive_nodes:
#            print "node %s: alive -> dead" % host
#            self._alive_nodes.remove(host)
#            self._dead_nodes.append(host)
#            self._notify_on_dead(host)
#        else:
#            print "trying to remove a node that has already been marked as dead, glitch?"


    def new_gossip(self, gossip, sender):
        """ Invoked by the MessagingService when we receive gossip from another node in the cluster """
        print "%s sent gossip: %s" % (sender, gossip)

    def _notify_on_join(self, host):
        print "notifying node state change listeners, on_join(%s)" % host
        [listener.on_join(host) for listener in self._node_state_change_listeners]
        #for listener in self._node_state_change_listeners #better style?
        #    listener.on_join(host)

    def _notify_on_alive(self, host):
        print "notifying node state change listeners, on_alive(%s)" % host
        [listener.on_alive(host) for listener in self._node_state_change_listeners]

    def _notify_on_dead(self, host):
        print "notifying node state change listeners, on_dead(%s)" % host
        [listener.on_dead(host) for listener in self._node_state_change_listeners]

#    def _notify_on_restart(self, host):
#        print "notifying node state change listeners, on_restart(%s)" % host
#        [listener.on_restart(host) for listener in self._node_state_change_listeners]