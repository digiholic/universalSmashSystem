import socket
import select
import sys
import json

#remove this import if removing debug code
import time

#lightweight server, for the most part just statelessly bounces messages between players
#the state it does handle, is number of players online and what frame they can progress to

class GameServer(object):
  #TODO: replace hard-coded ports/addresses with configurable ones
  def __init__(self, port=9009):
    self.SOCKET_MODE_UDP = "UDP"
    self.connect_mode = self.SOCKET_MODE_UDP
    if(self.connect_mode == self.SOCKET_MODE_UDP):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.conn.bind(("", port))#bind to everything. 
    self.read_list = [self.conn]
    self.write_list = []
    self.players = {}
    
    self.DEBUG_ENABLED = False
    #quick and dirty way of testing artificial latency
    #cycles through this list and sleeps for that amount of time (in seconds)
    self.sleep_intervals = [0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    
    
  def send(self,msg,target):
      if(self.connect_mode == self.SOCKET_MODE_UDP):
          self.conn.sendto(msg, target)
  def receive(self,sock):
      if(self.connect_mode == self.SOCKET_MODE_UDP):
          msg,addr = sock.recvfrom(128)
          return msg,addr
        
  def process(self):
    readable, writable, exceptional = (
      select.select(self.read_list, self.write_list, [])
    )
    for f in readable:
      if f is self.conn:
        #msg, addr = f.recvfrom(128)
        msg,addr = self.receive(f)
        if len(msg) >= 1:
          cmd = msg[0]
          if cmd == "c":#player connected
            self.players[addr] = {'nextframe':0}
            #TODO: what happens when there is more than 2 players? (game will start at 2)
            if(len(self.players)>1):#game is ready to start, send connect message to all
              playerno = 1#give each player a unique number
              for player in self.players:
                onlineMsg = """t_0_{"playerno":"""+str(playerno)+"""}"""
                playerno+=1
                print("online {0}".format(onlineMsg))
                self.send(onlineMsg, player)
          elif cmd == "u" or cmd == "f":#update keyboard or update fighter, passthrough message
            if len(msg) >= 2 and addr in self.players:
              for player in self.players:
                if(addr != player):
                  print("sending {0}".format(msg))
                  self.send(msg, player)
            else:
              print "Unknown message: {0},{1}".format(msg,addr)
          elif cmd == "p":#client is progressing to frame X
            evtSplit = msg.split("_")
            self.status = evtSplit[0]
            self.tick = int(evtSplit[1])
            if addr in self.players:
              self.players[addr]['nextframe'] = self.tick
            else:
              print("progress message from unknown player")
            allClientsHaveSameFrame = True
            for player in self.players.values():
              if player['nextframe']!=self.tick:
                allClientsHaveSameFrame = False
            if allClientsHaveSameFrame:
              for playeraddr in self.players:
                  self.send(msg, playeraddr)#send to players that they can all progress to frame X
                  print("progress {0}".format(msg))
          elif cmd == "d":#player disconnected (unused)
            if addr in self.players:
              del self.players[addr]
              #TODO: if len(self.players==0), exit server
          else:
            print "Unexpected: {0}".format(msg)
  def run(self):
    print "Staring Server"
    while True:
      self.process()
      if(self.DEBUG_ENABLED):
        top = self.sleep_intervals.pop()#dequeue the frame that's persisted the length of the queue
        time.sleep(top)
        self.sleep_intervals.insert(0,top)#enqueue event onto start of queue

#TODO: integrate this into tussle. Make it a menu option or something.
if __name__ == "__main__":
  g = GameServer()
  g.run()