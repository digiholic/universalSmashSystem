import socket 
import json 
import select 
import random
import pygame

import time

class NetworkEvt(object):
    pass#empty, for deserialising, attributes are added from json

class NetworkUpdateMessage(object):
    def __init__(self):
        self.status = "u"
        self.json = "{}"
        self.type = 0
        self.frame = 0
    def toString(self):
        return self.status+"_"+str(self.type)+"_"+str(self.frame)+"_"+self.json
    def isValid(self,msg):
        return (len(msg)>1 and msg[0] == "u" and msg.count("_")==3)
    def isBlank(self):
        return self.type == 0
    def fromString(self,msg):
        evt = NetworkEvt()
        evtSplit = msg.split("_")
        self.status = evtSplit[0]
        self.type = int(evtSplit[1])
        self.frame = int(evtSplit[2])
        self.json = evtSplit[3]
        evt.type = self.type
        jsondict = json.loads(self.json).items()
        for attr,val in jsondict:
            setattr(evt,attr,val)
        return evt
    def update(self,_type,_json,_frame):
        self.json = _json
        self.type = _type
        self.frame = _frame

class NetworkTickMessage(object):
    def __init__(self):
        self.status = "t"
        self.json = ""
        self.tick = 0
    def isValid(self,msg):
        return (len(msg)>1 and msg[0] == "t" and msg.count("_")==2)
    def fromString(self,msg):
        evtSplit = msg.split("_")
        self.status = evtSplit[0]
        self.tick = int(evtSplit[1])
        self.json = evtSplit[2]
        return self

class NetworkFighterMessage(object):
    def __init__(self):
        self.status = "f"
        self.frame = 0
        self.json = ""
    def setFighter(self,_frame,_fighterAttrs):
        self.frame = _frame
        self.json = json.dumps(_fighterAttrs)
    def isValid(self,msg):
        return (len(msg)>1 and msg[0] == "f" and msg.count("|")==2)
    def toString(self):
        return self.status+"|"+str(self.frame)+"|"+self.json
    def fromString(self,msg):
        evtSplit = msg.split("|")
        self.status = evtSplit[0]
        self.frame = int(evtSplit[1])
        self.json = evtSplit[2]
        return self

class NetworkProgressMessage(object):
    def __init__(self):
        self.status = "p"
        self.frame = 0
    def isValid(self,msg):
        return (len(msg)>1 and msg[0] == "p" and msg.count("_")==1)
    def toString(self):
        return self.status+"_"+str(self.frame)
    def fromString(self,msg):
        evtSplit = msg.split("_")
        self.status = evtSplit[0]
        self.frame = int(evtSplit[1])
        return self
        
class NetworkBufferEntry(object):
    def __init__(self):
        self.eventList = []
        self.receivedFrom = {}
    def getEvents(self):
        self.eventList = []
        for k,v in self.receivedFrom.items():
            for e in v:
                self.eventList.append(e)
        return self.eventList
        
class Network(object):
    def send(self,msg,target):
        if(self.connect_mode == self.SOCKET_MODE_UDP):
            self.conn.sendto(msg, target)
    def receive(self,sock):
        if(self.connect_mode == self.SOCKET_MODE_UDP):
            msg,addr = sock.recvfrom(128)
            return msg,addr
        
    #TODO: replace hard-coded ports/addresses/buffer/etc with configurable ones
    def __init__(self):
        #set to false to disable all networking and just run locally
        self.enabled = False
        if(self.enabled):
            self.SOCKET_MODE_UDP = "UDP"#maybe later add code to support TCP. Might be preferable to avoid dropping packets?
            self.connect_mode = self.SOCKET_MODE_UDP
            self.clientport = random.randrange(8000, 8999)
            self.addr = "192.168.1.1"#change to IP of server to connect to
            self.serverport = 9009
            if(self.connect_mode == self.SOCKET_MODE_UDP):
                self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.conn.bind(("", self.clientport))#bind to everything. 
            self.read_list = [self.conn]
            self.write_list = []
            self.send("c", (self.addr, self.serverport))
            #count each frame with an id so that it can be identified when sent over the wire
            self.tick_count = 0
            self.buffer_size = 6 #number of frames of latency to introduce locally (should be greater than the network latency)
            self.max_frame = self.buffer_size
            self.buffer = [NetworkBufferEntry() for x in range(self.buffer_size)]
            for x in self.buffer:
                x.receivedFrom['local']=[]
            self.fighter_buffer = [[] for x in range(self.buffer_size)]
            
            self.STATE_WAITING_FOR_OPPONENT = 0
            self.STATE_PLAYING = 1
            self.current_state = self.STATE_WAITING_FOR_OPPONENT
            self.playerno = 0
            #TODO: on exit implement disconnect (message status "d" to server)
            
    """
    Creates a fake 'pipe' between the local event source (keyboard) and the network processing
    if networking is disabled, this method does nothing
    if networking is enabled, this method takes the local events and sends them over the network
    it also receives events from the network and appends them to the local queue
    
    Since this sends inputs per frame, if games are out of sync at the frame-level, this will diverge
    
    there is a number of frames as a buffer. Local input is pushed onto the end of the buffer
    at that stage the frame count is recorded and sent over the wire with the count
    when receiving inputs, insert them onto the buffer at the correct frame
    this assumes that latency never exceeds the number of frames in the buffer
    it also assumes the frame rate of each client is very close to being the same
    
    the game will be laggy to local input by the size of the buffer, but will be consistent
    
    ideally, the clients will be in sync as they would have the same frame rate.
    since this is unlikely in practice, each client sends to the server a request to progress to frame X
    where X = buffer_size
    when the server receives this from every player, it sends back an acknowldgeemnt that the client can progress
    if the client doesn't receive this, it stalls
    
    if the latency/frame rates of the clients never differs by more than buffer_size, then the games will play smoothly
    if one begins to get ahead by too much, the game will stutter.
    
    Sample code has been written to sync fighters in the case that the game diverges.
    This needs to be updated/enabled if it's needed.
    In theory syncing fighters would be a safety net to re-sync the state.
    (for example, in the case keyboard packets are lost over the network)
    In practice, this should be avoided if possible because it will cause fighters to jump around
    and it means tracking code changes to fighters in this class (making code slightly harder to maintain).
    Additioanlly it requires possible engine changes to allow state rollback/fast forward
    
    TODO: implement a translation layer between controls?
    player 1 keybindings on computer 1 should translate to player 2 keybindings on computer 2
    """
    def processEvents(self,events):
        if(not self.enabled):
            return events#not turned on, nothing to do
        #enqueue/dequeue from buffer
        bufferObj = NetworkBufferEntry()
        bufferObj.receivedFrom['local']=events
        self.buffer.insert(0,bufferObj)#enqueue event onto start of queue
        nextEventObj = self.buffer.pop()#dequeue the frame that's persisted the length of the queue
        nextEventList = nextEventObj.getEvents()
        
        self.sendBuffer()
        self.readFromNetwork()
        
        MAX_STALL_COUNT = 100#1 second max 
        while(self.tick_count > self.max_frame and MAX_STALL_COUNT>=0):
            print("Stall at frame: "+str(self.tick_count)+" max: "+str(self.max_frame))
            MAX_STALL_COUNT-=1
            self.readFromNetwork()
            time.sleep(0.01)#wait 1/100th of a second before checking again.
        if(MAX_STALL_COUNT<0):
            print("Max stalls exceeded.")
            #TODO: lost connectivity? exit battle?
            
        if(self.current_state == self.STATE_WAITING_FOR_OPPONENT):
            return []#absorb events until players are ready
        #TODO: stop clock (game countdown timer) from progressing while waiting.
        self.tick_count += 1
        return nextEventList
    
    def sendBuffer(self):
        bufferTicks = self.tick_count+(self.buffer_size)
        b = self.buffer[0]
        if('local' in b.receivedFrom):
            events = b.receivedFrom['local']
            for e in events:
                #TODO: make this work for devices other than keyboard
                if e.type == pygame.locals.KEYDOWN or e.type == pygame.locals.KEYUP:
                    #send input to others
                    msgEvt = NetworkUpdateMessage()
                    msgEvt.update(e.type,json.dumps(e.__dict__),bufferTicks)
                    self.send(msgEvt.toString(), (self.addr, self.serverport))
                    #print("sent input for frame: "+str(bufferTicks)+" current frame: "+str(self.tick_count))
        #periodically send "progressing to frame X"
        if(self.tick_count % self.buffer_size == 0):
            msgProgress = NetworkProgressMessage()
            msgProgress.frame = self.tick_count + self.buffer_size
            self.send(msgProgress.toString(),(self.addr, self.serverport))
            #print("send req to progress to frame: "+str(self.tick_count))
    
    def readFromNetwork(self):
        repeat = True
        while(repeat):
            repeat = False
            readable, writable, exceptional = (
                select.select(self.read_list, self.write_list, [], 0)
            )
            for f in readable:
              if f is self.conn:
                #msg, addr = f.recvfrom(128)
                msg,addr = self.receive(f)
                repeat = True#may be more than 1 message waiting to be read, catch up by looping until select returns nothing
                msgEvt = NetworkUpdateMessage()
                msgTick = NetworkTickMessage()
                msgFighter = NetworkFighterMessage()
                msgProgress = NetworkProgressMessage()
                if(msgEvt.isValid(msg)):
                    fromString = msgEvt.fromString(msg)
                    receivedTime = msgEvt.frame
                    #print("received input for frame: "+str(msgEvt.frame)+" current frame: "+str(self.tick_count))
                    frameDiff = self.buffer_size - (receivedTime - self.tick_count)
                    if(frameDiff<self.buffer_size and frameDiff>=0):
                        if(addr not in self.buffer[frameDiff].receivedFrom):#initialise list
                            self.buffer[frameDiff].receivedFrom[addr] = []
                        if(not msgEvt.isBlank()):
                            self.buffer[frameDiff].receivedFrom[addr].append(fromString)#new entry, insert into buffer
                    else:
                        print("frame outside range"+str(msgEvt.frame))
                        if msgEvt.frame>=self.buffer_size:
                            #Note: should never get here, it means frame rates are out of sync by a lot
                            #but if we have hit this, try and re-sync frame count
                            print(str(self.tick_count)+" adjusted to: "+str(msgEvt.frame-self.buffer_size+1))
                            self.tick_count = msgEvt.frame-self.buffer_size+1
                if(msgTick.isValid(msg)):
                    msgTick.fromString(msg)
                    self.tick_count = msgTick.tick
                    self.playerno = json.loads(msgTick.json)['playerno']
                    if(self.current_state == self.STATE_WAITING_FOR_OPPONENT):
                        self.current_state = self.STATE_PLAYING
                    print("starting")
                if(msgFighter.isValid(msg)):
                    fromString = msgFighter.fromString(msg)
                    receivedTime = msgFighter.frame
                    frameDiff = receivedTime - self.tick_count
                    if(frameDiff-1<self.buffer_size and frameDiff-1>-1):
                        self.fighter_buffer[frameDiff-1].append(fromString)#insert into buffer
                if(msgProgress.isValid(msg)):
                    fromString = msgProgress.fromString(msg)
                    self.max_frame = fromString.frame
                    #print("can progress to frame: "+str(self.max_frame))
    def processFighters(self,fighters):
        if(not self.enabled or
           not self.current_state == self.STATE_PLAYING or 
           not self.tick_count%100 == 0):
            return None
        return None #TODO: enable by removing this statement.
        #NOTE: before this can be enabled, some work needs to be done on the frame counts
        #unlike the keyboard which can be predicted due to a local latency buffer
        #the fighter's position is only known at the current frame,
        #therefore by the time the opponent gets it the data is obsolete.
        #in theory the best way of handling this would be to roll state forward/back
        #the engine currently cannot do this
        
        #need to confirm minimal set params are that can capture fighter state
        #e.g. x,y, speed?, angle?, state?, gravity? friction?
        self.fighter_buffer.insert(0,[])#enqueue empty list to keep buffer the same size
        nextFighterList = self.fighter_buffer.pop()#dequeue the frame that's persisted the length of the queue
        if self.playerno == 1:#player 1 is authorotive - it will send, rest will receive
            for f in fighters:
                msg = NetworkFighterMessage()
                msg.setFighter(self.tick_count,{
                    'rectX':f.rect.top,
                    'rectY':f.rect.left
                })
                """
                    #'grounded' : f.grounded,
                    #'back_walled' : f.back_walled,
                    #'front_walled' : f.front_walled,
                    #'ceilinged' : f.ceilinged,
                    #'damage' : f.damage,
                    #'landing_lag' : f.landing_lag,
                    #'platform_phase' : f.platform_phase,
                    #'tech_window' : f.tech_window,
                    #'change_x' : f.change_x,
                    #'change_y' : f.change_y,
                    #'preferred_xspeed' : f.preferred_xspeed,
                    #'preferred_yspeed' : f.preferred_yspeed,
                    #'facing' : f.facing,
                    #'no_flinch_hits' : f.no_flinch_hits,
                    #'flinch_damage_threshold' : f.flinch_damage_threshold,
                    #'flinch_knockback_threshold' : f.flinch_knockback_threshold,
                    #'armor_damage_multiplier' : f.armor_damage_multiplier,
                    #'invulnerable' : f.invulnerable,
                    #'respawn_invulnerable' : f.respawn_invulnerable,
                    #'shield' : f.shield,
                    #'shield_integrity' : f.shield_integrity,
                    #'hitstop' : f.hitstop,
                    #'hitstop_vibration' : f.hitstop_vibration,
                    #'hitstop_pos' : f.hitstop_pos,
                    #'ledge_lock' : f.ledge_lock
                    #jumps = var['jumps']#??
                    #airdodges = 1#??
                    
                    #grabbing = None#??
                    #grabbed_by = None#??
                    #hit_tagged = None#??"""
                self.send(msg.toString(), (self.addr, self.serverport))
        for fighter_message in nextFighterList:
            fighter_data = json.loads(fighter_message.json).items()
            print("updating fighter"+str(fighter_data.frame)+" "+str(self.tick_count))
            for f in fighters:
                for attr,val in fighter_data:
                    if(attr == "rectX"):
                        print("prev x was: "+str(f.rect.top)+" new: "+str(val))
                        f.rect.x = val
                        continue
                    if(attr == "rectY"):
                        print("prev y was: "+str(f.rect.left)+" new: "+str(val))
                        f.rect.x = val
                        continue
                    setattr(f,attr,val)#currently completely broken
                    