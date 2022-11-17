import socket
import select
import sys
import json
import settingsManager

#remove this import if removing debug code
import time

#lightweight server, for the most part just statelessly bounces messages between players
#the state it does handle, is number of players online and what frame they can progress to

class GameServer(object):
  #TODO: replace hard-coded ports/addresses with configurable ones
  def __init__(self, port=9009):
    self.settings = settingsManager.getSetting().setting
    port =self.settings['networkServerPort']
    self.MESSAGE_SIZE = 96
    self.SOCKET_MODE_UDP = "udp"
    self.SOCKET_MODE_TCP = "tcp"#not implemented yet
    self.connect_mode = self.settings['networkProtocol']
    if(self.connect_mode == self.SOCKET_MODE_UDP):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.conn.bind(("", port))#bind to everything.
    if(self.connect_mode == self.SOCKET_MODE_TCP):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setblocking(0)
        self.conn.bind(('', port))
        self.conn.listen(5)
        self.message_queues = {}
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
      if(self.connect_mode == self.SOCKET_MODE_TCP):
        if len(msg)<self.MESSAGE_SIZE:#fixed-width messages, could be made better by proper buffering 
          msg='{message: <{fill}}'.format(message=msg, fill=self.MESSAGE_SIZE)
        else:
          print(("message too long: "+str(len(msg))+" "+msg))
        for s in self.read_list:
          if s is not self.conn and s.getpeername() == target:
            self.message_queues[s].append(msg)
            if s not in self.write_list:
                self.write_list.append(s)

  def handleMessage(self,msg,addr):
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
            self.send(onlineMsg, player)
      elif cmd == "u" or cmd == "f":#update keyboard or update fighter, passthrough message
        if len(msg) >= 2 and addr in self.players:
          for player in self.players:
            if(addr != player):
              self.send(msg, player)
        else:
          print("Unknown message: {0},{1}".format(msg,addr))
      elif cmd == "p":#client is progressing to frame X
        evtSplit = msg.split("_")
        self.status = evtSplit[0]
        self.tick = int(evtSplit[1])
        if addr in self.players:
          self.players[addr]['nextframe'] = self.tick
        else:
          print(("progress message from unknown player: " + str(addr)))
        allClientsHaveSameFrame = True
        for player in list(self.players.values()):
          if player['nextframe']!=self.tick:
            allClientsHaveSameFrame = False
        if allClientsHaveSameFrame:
          for playeraddr in self.players:
              self.send(msg, playeraddr)#send to players that they can all progress to frame X
      elif cmd == "d":#player disconnected (unused)
        if addr in self.players:
          del self.players[addr]
          #TODO: if len(self.players==0), exit server
          #TODO: close TCP connections
      else:
        print("Unexpected: {0}".format(msg))
  
  def process(self):
    readable, writable, exceptional = (
      select.select(self.read_list, self.write_list, [])
    )
    if self.connect_mode == self.SOCKET_MODE_UDP:
      for f in readable:
        if f is self.conn:
          msg, addr = f.recvfrom(self.MESSAGE_SIZE)
          self.handleMessage(msg,addr)
    if self.connect_mode == self.SOCKET_MODE_TCP:
      for s in readable:
        if s is self.conn:
            connection, client_address = s.accept()
            connection.setblocking(0)
            self.read_list.append(connection)
            self.message_queues[connection] = []
        else:
            data = s.recv(self.MESSAGE_SIZE)
            if data:
                data = data.strip()
                self.handleMessage(data,s.getpeername())
            else:
                if s in self.write_list:
                    self.write_list.remove(s)
                self.read_list.remove(s)
                s.close()
                del self.message_queues[s]

    for s in writable:
        if(len(self.message_queues[s])>0):
            for next_msg in self.message_queues[s]:
              s.sendall(next_msg)
            self.message_queues[s] = []
        self.write_list.remove(s)

    for s in exceptional:
        self.read_list.remove(s)
        if s in self.write_list:
            self.write_list.remove(s)
        s.close()
        del self.message_queues[s]
    
  
  def run(self):
    print("Staring Server")
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