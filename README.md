Elastica is an implementation of:  [The Phi Accrual Failure Detector] and [Amazons paper on Gossip]

[The Phi Accrual Failure Detector]: http://ddg.jaist.ac.jp/pub/HDY+04.pdf 
[Amazons paper on Gossip]: http://www.cs.cornell.edu/home/rvr/papers/flowgossip.pdf


Limitations:
  * All nodes in the cluster must listen on the same port.
  * One node per ip.
  * Concern: (theoretically) could end up with two connections to a single node.
    (hint: interleaved incoming/outcoming connections)