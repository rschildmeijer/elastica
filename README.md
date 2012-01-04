Elastica is an implementation of:  [The Phi Accrual Failure Detector] and [Amazons paper on Gossip] with inspiration from
[Lookup data in p2p system] (A tweaked Chord implementation where |finger table| = |cluster|)

[The Phi Accrual Failure Detector]: http://ddg.jaist.ac.jp/pub/HDY+04.pdf 
[Amazons paper on Gossip]: http://www.cs.cornell.edu/home/rvr/papers/flowgossip.pdf
[Lookup data in p2p system] http://www.google.se/url?sa=t&rct=j&q=lookup%20in%20p2p%20system%20&source=web&cd=3&ved=0CDkQFjAC&url=http%3A%2F%2Fwww.cs.berkeley.edu%2F~istoica%2Fpapers%2F2003%2Fcacm03.pdf&ei=PcUET4GgJY6K4gSnlcSNCA&usg=AFQjCNFD1N8Y7VrxHhwDoKFaTNfO32wG9A&cad=rja

    Suitable if you are building a system that is...
    * Elastic  -- Add new machines in runtime (with no downtime)
    * Decentralized  -- Every node in the cluster is identical.  
    * Fault tolerant  -- Replace failed nodes with no downtime. 
    * Self-stabilizing  -- The system will end up in a correct state no matter what state it is initialized with.
    
    Limitations:
    
    * No way to explicitly decomission a node

    * Only support for one seed
    
    * Two tcp connections between each pair of nodes


    Miscellaneous
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
    * Distinguish between "address I tell people about" and "address I bind to (think ec2, nat)
      currently "solved" by binding to ip 0.0.0.0 and tell about "external" ip

    Dependencies:
    * Tornado 1.2.1 (http://www.tornadoweb.org/)
    * psutil (http://code.google.com/p/psutil/)

Licensed under Apache version 2