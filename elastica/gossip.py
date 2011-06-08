import time
import random
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


    def __init__(self, fd, ms):
        self._fd = fd
        self._ms = ms
        self._node_states = {}  #does not contain gossip digest about the local node
        self._alive_nodes = []
        self._dead_nodes = []
        self._node_state_change_listeners = []  #on_join(host), on_alive(host), on_dead(host)
        self._generation = int(time.time())
        self._version = 0

        PeriodicCallback(self._initiate_gossip_exchange, 1000, ioloop.IOLoop.instance()).start()
        PeriodicCallback(self._scrutinize_cluster, 1000, ioloop.IOLoop.instance()).start()

    def _initiate_gossip_exchange(self):
        self._version += 1
        gossiped_to_seed = False
        if len(self._alive_nodes) > 0:
            gossiped_to_seed = self._send_gossip(self._alive_nodes)

        if len(self._dead_nodes) > 0:
            probability = float(len(self._dead_nodes)) / (len(self._alive_nodes) + 1)
            if random.random() < probability:
                self._send_gossip(self._dead_nodes)

        if not gossiped_to_seed or len(self._alive_nodes) < 1:    #1 = len(self._seeds)
            # gossip to a seed for facilitating partition healing
            if options.seed == options.address: #size == 1 && seeds.contains(FBUtilities.getLocalAddress()
                return
            if len(self._alive_nodes) == 0:
                self._send_gossip([options.seed])
            else:
                probability = 1.0 / (len(self._alive_nodes) + len(self._dead_nodes))
                if random.random() <= probability:
                    self._send_gossip([options.seed])

    def _send_gossip(self, nodes):
        """ Returns true if the chosen target was also a seed. False otherwise"""
        node = random.choice(nodes)
        gossip = self._node_states.copy()
        gossip[options.address] = {"generation": self._generation, "version": self._version}
        self._ms.send_one_way(node, str(gossip) + "\r\n")
        return node == options.seed

    def _scrutinize_cluster(self):
        dead = [host for host in self._alive_nodes if self._fd.isDead(host)]
        if len(dead) > 0:
            [self._dead_nodes.append(node) for node in dead]
            [self._alive_nodes.remove(node) for node in dead]
            [self._notify_on_dead(node) for node in dead]

    def new_gossip(self, gossip, sender):
        """ Invoked by the MessagingService when we receive gossip from another node in the cluster """
        #gossip will contain info about me
        if options.address in gossip:
            del gossip[options.address]
        for host in gossip.keys():
            digest = gossip[host]
            if host in self._node_states:
                #has digest about host, maybe update
                if digest["generation"] > self._node_states[host]["generation"]:
                    self._update_node_state(host, digest)
                elif digest["version"] > self._node_states[host]["version"]: #should probably make sure that generations are eq
                    self._update_node_state(host, digest)
            else:
                #had no previous info about host
                self._node_states[host] = digest
                self._fd.heartbeat(host)
                self._alive_nodes.append(host)
                self._notify_on_join(host)

    def _update_node_state(self, host, digest):
        self._fd.heartbeat(host)
        self._node_states[host] = digest
        if host in self._dead_nodes:
            self._dead_nodes.remove(host)
            self._alive_nodes.append(host)
            self._notify_on_alive(host)

    def _notify_on_join(self, host):
        print "on_join(%s)" % host
        [listener.on_join(host) for listener in self._node_state_change_listeners]

    def _notify_on_alive(self, host):
        print "on_alive(%s)" % host
        [listener.on_alive(host) for listener in self._node_state_change_listeners]

    def _notify_on_dead(self, host):
        print "on_dead(%s)" % host
        [listener.on_dead(host) for listener in self._node_state_change_listeners]