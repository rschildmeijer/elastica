Elastica is an implementation of:  [The Phi Accrual Failure Detector] and [Amazons paper on Gossip]

[The Phi Accrual Failure Detector]: http://ddg.jaist.ac.jp/pub/HDY+04.pdf 
[Amazons paper on Gossip]: http://www.cs.cornell.edu/home/rvr/papers/flowgossip.pdf


    Limitations:
    
    * All nodes in the cluster must listen on the same port.

    * One node per ip.

    * Only support for one seed

    * Concern: (theoretically) could end up with two connections to a single node.
      (hint: interleaved incoming/outcoming connections)


    TODO

    * Deduce a sane cluster state when a new node joins the cluster (dead nodes > 0)
        solution: only gossip alive_nodes
        reproduce: A alive, B dead and starting C. A sends gossip to C. C thinks A and B are alive.
    * Use protobuf (http://code.google.com/apis/protocolbuffers/docs/pythontutorial.html) for messaging


Licensed under Apache version 2