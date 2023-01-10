# coding=utf-8
import random
import time
import os
import socket
import threading
import json
import traceback
import sys
####

# from flaskapp import FlaskApp

class Node():

    def __init__(self):
        self.currentTerm = 0
        self.status="FOLLOWER"
        self.voteCount=0
        self.log = []
        self.state = 'ACTIVE'
        self.leader=None
        self.timeout = None
        self.lock = threading.Lock()
        self.heartBeat = None
        self.minVote=3
        self.udpPort=5555
        self.timeout_thread = None
        self.currentNode = os.getenv('name')
        self.serverList=["Node1","Node2","Node3","Node4","Node5"]
        self.count=0
        self.nodeActiveDict = {
            "Node1":"ACTIVE",
            "Node2":"ACTIVE",
            "Node3":"ACTIVE",
            "Node4":"ACTIVE",
            "Node5":"ACTIVE"
        }
        self.hb_time = 100
        self.termDetails={
        "votedFor": None,
        "request": None,
        "term": 0,
        "key": None,
        "value": None
        }
        self.nextIndex = {}
        self.logIndex=0
        self.commitIndex = 0
        self.lastApplied = 0
        self.matchIndex={}
        self.commitEligible=0
        self.lastcommit=-1

    def start_timer(self):
        self.get_timer()
        if self.timeout_thread and self.timeout_thread.isAlive():
            return
        self.startTimerNew = threading.Thread(target=self.startTimer)
        self.startTimerNew.start()
    
    def init_socket(self):
        SERVER = os.getenv('name')
        ADDR = (SERVER,self.udpPort)
        UDP_Socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        UDP_Socket.bind((ADDR))
        return UDP_Socket

    def get_timer(self):
        self.timeout = (random.randrange(150, 300) / 1000) + time.time()

    def startTimer(self):
        while self.status != 'LEADER' and self.state=='ACTIVE':
            delta = self.timeout - time.time()
            if delta < 0 :
                self.init_election()
            else:
                time.sleep(delta)

    def sender(self,target,message):
        try:
            msg_bytes = json.dumps(message).encode('utf-8')
            self.sock.sendto(msg_bytes, (target,self.udpPort))
        except KeyboardInterrupt:
            self.print('Shutting down server...')
            self.sock.close()


    def init_listener(self):        
        threading.Thread(target=self.listener).start()

    
    def listener(self):
        #print(f"Starting Listener ",file=sys.stderr)
        while True:
            try:
                msg, addr = self.sock.recvfrom(1024)
                decoded_msg = json.loads(msg.decode('utf-8'))
                threading.Thread(target=self.listener_thread_handler, args=[msg,decoded_msg]).start()
            except:
                print(f"ERROR while fetching from socket : {traceback.print_exc()}")

    def listener_thread_handler(self,msg,decoded_msg):


        if decoded_msg['request'] == 'VOTE_REQUEST' and self.state=='ACTIVE':
            self.voting_init(decoded_msg)
        elif decoded_msg['request'] == 'APPEND_RPC' and self.state=='ACTIVE':
            self.heartbeat_handler(decoded_msg)
        elif decoded_msg['request'] == 'CONVERT_FOLLOWER' and self.state=='ACTIVE':
            self.convert_follower()
        elif decoded_msg['request'] == 'LEADER_INFO' and self.state=='ACTIVE':
            self.getLeaderInfo()
        elif decoded_msg['request'] == 'SHUTDOWN' and self.state=='ACTIVE':
            self.init_shutdown()
        elif decoded_msg['request'] == 'TIMEOUT' and self.state=='ACTIVE':
            self.call_timeout()
        elif decoded_msg['request'] == 'VOTE_ACK' and decoded_msg['sender_name'] != self.currentNode:
            self.vote_verify(decoded_msg)
        elif decoded_msg['request']=='UPDATELEADERELIGIBLE':
            self.minVote=decoded_msg['value']
        elif decoded_msg['request']=='STORE':
            self.store_handle(decoded_msg)
        elif decoded_msg['request']=='APPEND_REPLY':
            self.append_rply(decoded_msg)
        elif decoded_msg['request']=='COMMIT_REQUEST':
            self.init_commit(decoded_msg)
        elif decoded_msg['request']=='RETRIEVE':
            self.init_retrieve(decoded_msg)
   
   
   
   
    def init_election(self):
        self.currentTerm=self.currentTerm+1
        self.status="CANDIDATE"
        self.voteCount=0
        self.start_timer()
        self.vote_counter()
        self.req_vote()
        

    def vote_verify(self,msg):
        if msg['value'] == 'SUCCESS':
            self.vote_counter()
        else:
            self.status == 'FOLLOWER'


    def vote_counter(self):
        if self.status == 'CANDIDATE' or self.status == 'LEADER':
            self.voteCount+=1
            if self.voteCount >= self.minVote:
                with self.lock:
                    self.status="LEADER"
                    self.leader=self.currentNode
                    for servers in self.serverList:
                        self.nextIndex[servers] =  len(self.log) + 1
                        self.matchIndex[servers] = 0
                    print("Leader Selected",self.leader,flush=True)
                self.startHeartbeat()

    
    def startHeartbeat(self):

        while self.status == 'LEADER' and self.state=='ACTIVE':
            start_time = time.time()
            for i in self.serverList:
                if i!=self.currentNode:
                    with self.lock:
                        nextIndex = self.nextIndex[i]
                        prevLogIndex = nextIndex - 1
                        prevLogTerm = -1
                        if prevLogIndex-1 >= 0 :
                            prevLogTerm = self.log[prevLogIndex-1]['term']
                        entries = self.log[prevLogIndex:]                     
                        
                        appendRpc ={
                        "term": self.currentTerm,
                        "leaderId":self.currentNode,
                        "entries":entries,
                        "prevLogIndex":prevLogIndex,
                        "prevLogTerm":prevLogTerm,
                        "l_commit_index":self.commitIndex
                        }

                        message={
                            "sender_name": self.currentNode,
                            "request": "APPEND_RPC",
                            "term": self.currentTerm,
                            "key": 'Append_rpc_msg',
                            "value": appendRpc
                            }
                    threading.Thread(target=self.sender, args=[i,message]).start()
            delta = time.time() - start_time
            time.sleep((self.hb_time - delta) / 1000)


    def req_vote(self):
        for i in self.serverList:
            if i!=self.currentNode :
                    lli = len(self.log)
                    if lli > 0:
                        llt = self.log[lli-1]['term']
                    else :
                        llt = 1

                    mess={
                        "term": self.currentTerm,
                        "voteCount": self.voteCount,
                        "candidateId":self.currentNode,
                        "lastLogIndex":lli,
                        "lastLogTerm":llt
                    }
                    message={
                        "sender_name": self.currentNode,
                        "request": "VOTE_REQUEST",
                        "term": self.currentTerm,
                        "key": 'key',
                        "value": mess
                        }
                    threading.Thread(target=self.sender, args=[i,message]).start()
        

   


   


    def init_retrieve(self,decoded_msg):
        

        if self.status == "LEADER":

            reply = {
                "sender_name": self.currentNode,
                "request": "RETRIEVE",
                "term": self.currentTerm,
                "key": 'COMMITTED_LOGS',
                "value": self.log
            }

            replyEnc = json.dumps(reply).encode('utf-8')
            threading.Thread(target=self.init_reply,args=[decoded_msg['sender_name'],replyEnc]).start()
        else :
            store_reply = {
                "sender_name": self.currentNode,
                "request": "LEADER_INFO",
                "term": self.currentTerm,
                "key": 'LEADER',
                "value": self.leader,
                "action":"RETRIEVE"
            }

            reply = json.dumps(store_reply).encode('utf-8')
            threading.Thread(target=self.init_reply,args=[decoded_msg['sender_name'],reply]).start()


    def writeLog(self):
        json_string = json.dumps(self.log)
        with open('json_data_new.json', 'w') as outfile:
            json.dump(json_string, outfile)


    def init_commit(self,data):
        print(self.log)
        threading.Thread(target=self.writeLog).start()

    def append_rply(self,data):
        with self.lock:
            if data['value'] == 'FAIL':
                if data['sender_name'] in self.nextIndex:
                    self.nextIndex[data['sender_name']] -= 1
            elif data['value'] == 'SUCCESS':
                if data['sender_name'] in self.nextIndex: 
                    self.nextIndex[data['sender_name']] = 1 + len(self.log)
                    self.matchIndex[data['sender_name']] = self.nextIndex[data['sender_name']] - 1
                self.commitEligible+=1
                temp=0
                for i in  self.nodeActiveDict:
                    if self.nodeActiveDict[i]=='ACTIVE':
                        temp+=1

                if(self.commitEligible > (temp/2) + 1):
                    self.commitEligible=0
                    for i in self.matchIndex:
                        if(self.commitIndex < self.matchIndex[i] and data['term']==self.currentTerm):
                            self.commitIndex=max(self.matchIndex[i],self.commitIndex)
                    self.matchIndex[self.leader] += 1
                    message={
                    "sender_name": self.currentNode,
                    "request": "COMMIT_REQUEST",
                    "term": self.currentTerm,
                    "key": 'key',
                    "value": 'COMMIT'
                    }
                    reply=json.dumps(message).encode('utf-8')
                    for i in self.serverList:
                        threading.Thread(target=self.init_reply,args=[i,reply]).start()
                
    
    def store_handle(self,data):
        with self.lock:
            if self.status == "LEADER":
                self.checkBool = True
                single_log = {
                    "term":self.currentTerm,
                    "key" : data['key'],
                    "value" : data['value']
                }
                self.log.append(single_log)
            else :
                store_reply = {
                    "sender_name": self.currentNode,
                    "request": "LEADER_INFO",
                    "term": self.currentTerm,
                    "key": 'LEADER',
                    "value": self.leader,
                    "action":"STORE"
                }

                reply = json.dumps(store_reply).encode('utf-8')
                threading.Thread(target=self.init_reply,args=[data['sender_name'],reply]).start()


    def call_timeout(self):
        msg={
            "sender_name":self.currentNode,
            "request":"CONVERT_FOLLOWER",
            "term": self.currentTerm
        }
        self.sock.sendto(json.dumps(msg).encode('utf-8'), (self.leader, self.udpPort))
        print(self.currentNode," ", self.leader)
        self.init_election()



    def init_shutdown(self):
        if self.state == 'ACTIVE':
            eligible = 0
            if(self.minVote%2==0):
                eligible=self.minVote
            else:
                eligible=self.minVote+1

            totalcount=2*(eligible-1)
            val=(totalcount-1)/2+1
            message={
            "sender_name": self.currentNode,
            "request": "UPDATELEADERELIGIBLE",
            "term": self.currentTerm,
            "key": 'minVote',
            "value": val
            }
            threading.Thread(target=self.sender,args=[self.currentNode,message]).start()
            print("Shutdown::")
            self.state = 'INACTIVE'


    def getLeaderInfo(self):
        message={
                "sender_name": self.currentNode,
                "request": "LEADER_INFO",
                "term": self.currentTerm,
                "key": 'LEADER',
                "value": self.leader
                }
        print(message,flush=True)

    
    def convert_follower(self):
        if self.status == 'LEADER':
            self.status = 'FOLLOWER'           
            self.start_timer()
    

    def heartbeat_handler(self,message):
        if message['term'] >= self.currentTerm :
            self.get_timer()
            leader = message['value']['leaderId']
            self.leader = leader
            if self.status == 'CANDIDATE':
                self.status == 'FOLLOWER'
            elif self.status == 'LEADER':
                self.status == 'FOLLOWER'
                self.start_timer()
            self.voteCount = 0
            
            
            
            
            with self.lock:
                if message['term'] > self.currentTerm :
                    self.currentTerm = message['term']
            val = message['value']
            if len(val['entries']) != 0:
                self.create_Reply(message,val)
        else:
            current_message={
                "sender_name": self.currentNode,
                "request": "APPEND_REPLY",
                "term": self.currentTerm,
                "key": 'key',
                "value": 'FAIL'
                }
            reply=json.dumps(current_message).encode('utf-8')
            threading.Thread(target=self.init_reply,args=[message['sender_name'],reply]).start()


    def create_Reply(self,message,msg):        
        prev_log = msg['prevLogTerm']
        prev_index = msg['prevLogIndex'] - 1

        if prev_log != -1:

            if  len(self.log) > 0 and 'term' in self.log[prev_index] and self.log[prev_index]['term'] != prev_log:
                current_message={
                "sender_name": self.currentNode,
                "request": "APPEND_REPLY",
                "term": self.currentTerm,
                "key": 'key',
                "value": 'FAIL'
                }
                reply=json.dumps(current_message).encode('utf-8')
                threading.Thread(target=self.init_reply,args=[message['sender_name'],reply]).start()

            else:

                self.log.extend(msg['entries'])
                current_message={
                "sender_name": self.currentNode,
                "request": "APPEND_REPLY",
                "term": self.currentTerm,
                "key": 'key',
                "value": 'SUCCESS',
                "logEntry": len(self.log)-1
                }
                reply=json.dumps(current_message).encode('utf-8')
                threading.Thread(target=self.init_reply,args=[message['sender_name'],reply]).start()
                
                if(message['value']['l_commit_index']> self.commitIndex):
                    self.commitIndex=min(message['value']['l_commit_index'],len(self.log)-1)
        else:
            self.log.extend(msg['entries'])
            current_message={
            "sender_name": self.currentNode,
            "request": "APPEND_REPLY",
            "term": self.currentTerm,
            "key": 'key',
            "value": 'SUCCESS',
            "logEntry": len(self.log)-1
            }
            reply=json.dumps(current_message).encode('utf-8')
            threading.Thread(target=self.init_reply,args=[message['sender_name'],reply]).start()
            
            if(message['value']['l_commit_index']> self.commitIndex):
                self.commitIndex=min(message['value']['l_commit_index'],len(self.log)-1)


        


    def voting_init(self,decoded_msg):
        if decoded_msg['term'] > self.currentTerm:



            voteData = decoded_msg['value']
            lastLogIndexCandidate = voteData['lastLogIndex']
            lastLogTermCandidate = voteData['lastLogTerm']

            lastLogIndexCurrent = len(self.log) - 1
            if self.currentTerm > lastLogTermCandidate or (self.currentTerm == lastLogTermCandidate and lastLogIndexCurrent > lastLogIndexCandidate):
                message={
                "sender_name": self.currentNode,
                "request": "VOTE_ACK",
                "term": self.currentTerm,
                "key": 'key',
                "value": 'FAIL'
                }
                reply=json.dumps(message).encode('utf-8')
                threading.Thread(target=self.init_reply,args=[decoded_msg['sender_name'],reply]).start()
                
            else:
                self.currentTerm=decoded_msg['term']
                self.termDetails['votedFor']= decoded_msg['sender_name']
                self.voteCount = 0
                self.get_timer()
                message={
                "sender_name": self.currentNode,
                "request": "VOTE_ACK",
                "term": self.currentTerm,
                "key": 'key',
                "value": 'SUCCESS'
                }

                currentTermDetails = {
                    'votedFor':decoded_msg['sender_name'],
                    'term':decoded_msg['term'],
                    'log':self.log,
                    'hb_time':100,
                    'timeoutInterval':self.timeout
                }

                reply=json.dumps(message).encode('utf-8')
                threading.Thread(target=self.init_reply,args=[decoded_msg['sender_name'],reply]).start()


    def init_reply(self,server_name,ack):
        self.sock.sendto(ack,(server_name,self.udpPort))


      
if __name__ == "__main__":
    n = Node()

    n.get_timer()  
    n.start_timer()
    n.sock = n.init_socket()
    n.init_listener()
    