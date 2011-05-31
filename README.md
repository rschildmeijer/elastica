Elastica is an implementation of:  [The Phi Accrual Failure Detector] and [Amazons paper on Gossip]

[The Phi Accrual Failure Detector]: http://ddg.jaist.ac.jp/pub/HDY+04.pdf 
[Amazons paper on Gossip]: http://www.cs.cornell.edu/home/rvr/papers/flowgossip.pdf

    Suitable for you if you are building a system that is...
    * Elastic  -- Add new machines in runtime (with no downtime)
    * Decentralized  -- Every node in the cluster is identical.  
    * Fault tolerant  -- Replace failed nodes with no downtime. 

    Limitations:
    
    * No way to explicitly decomission a node

    * Only support for one seed


    TODO

    * Deduce a sane cluster state when a new node joins the cluster (dead nodes > 0)
        solution: only gossip alive_nodes
        reproduce: A alive, B dead and starting C. A sends gossip to C. C thinks A and B are alive.
    * Use protobuf (http://code.google.com/apis/protocolbuffers/docs/pythontutorial.html) for messaging
    * Inconsistent implementation of 'cumulative distribution function' for Exponential Distribution  
        (see https://issues.apache.org/jira/browse/CASSANDRA-2597)


Licensed under Apache version 2