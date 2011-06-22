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
    * Simple rpc/messaging mechanism
    * Inconsistent implementation of 'cumulative distribution function' for Exponential Distribution  
       (see https://issues.apache.org/jira/browse/CASSANDRA-2597)
    * A generic Partitioner (keyspace=[0,10], A=[0,3], B=[4,7], C=[8,10]) (too key value specific?)
       (proposal: - consistent way to map a host into a key range and vice versa (get_range(host), get_node(range)). 
                  - auto adjust if node goes up/down. 
                  - auto bootstrap (half the range of the range with most load)     
                  - redundancy/replication?
                  - $1
       )
    * Reed–Solomon error correction (alternative to replication?): http://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction (proposed by github.com/williame)
    * Distinguish between "address I tell people about" and "address I bind to (think ec2, nat)
      currently "solved" by binding to ip 0.0.0.0 and tell about "external" ip

    Dependencies:
    * Tornado 1.2.1 (http://www.tornadoweb.org/)
    * psutil (http://code.google.com/p/psutil/)

Licensed under Apache version 2