class Gossiper(object):
    """ This module is responsible for Gossiping cluster information. The abstraction
    maintains the list of live and dead endpoints. Periodically i.e. every 1 second this module
    chooses a random node and initiates a round of Gossip with it. This module as and when it hears a gossip
    updates the Failure Detector with the liveness information.

    Amazon paper on Gossip at http://www.cs.cornell.edu/home/rvr/papers/flowgossip.pdf """


    def __init__(self, fd):
        self._fd = fd
        
