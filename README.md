##RAFT

Raft is a consensus algorithm that is designed to be easy to understand. It’s
equivalent to Paxos in fault-tolerance and performance. The difference is that
it’s decomposed into relatively independent subproblems, and it cleanly addresses
all major pieces needed for practical systems

###Consensus and State machine

Consensus is the process by which a collection of computers works together as a
coherent group to ensure overall system-reliability in the face of malfunctioning
nodes. This is often accomplished by having nodes coordinate with each other.
In our project, we utilize distributed replicated log with consensus to ensure
that all state machines get the same log.


State machine is a program that takes in inputs and outputs a result, A log
is a collection of operations (client requests) that are to be executed on the state
machines, Consensus ensures that the logs are replicated across all nodes as long
as all the logs are identical, the state machine will produce the same sequence
of results. As long as majority of servers are up, the consensus mechanism can
ensure log replication


###Controller Requests

#####1.2.1 Store
The controller will be used to send out STORE requests to the RAFT cluster.
This is similar to the client making a request to the RAFT cluster where the
request gets appended to the log’s of the leader and eventually gets appended to
the follower’s logs. You will be using the STORE cmd to make client requests

![alt text](https://github.com/rnair56/RAFT/blob/main/store.png)
