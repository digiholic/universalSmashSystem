import engine.baseActions as baseActions
import pygame
import math

class CPUplayer():
    def __init__(self):
        self.mode = 'duckling'
        self.keysHeld = []
        self.jump_last_frame = 0
    
    def loadGameState(self,fighter,stage,players):
        self.fighter = fighter
        self.gameState = stage
        self.players = players
        
    def getDistanceTo(self,target):
        sx,sy = self.fighter.rect.center
        tx,ty = target.rect.center
        
        return (tx - sx, ty - sy)
    
    def pressButton(self,button):
        if not button in self.keysHeld:
            self.fighter.keyPressed(button)
            self.keysHeld.append(button)
    
    def releaseButton(self,button):
        if button in self.keysHeld:
            self.fighter.keyReleased(button)
            self.keysHeld.remove(button)

    def segmentIntersects(self, startPoint, endPoint, rect):
        if startPoint[0]==endPoint[0] and startPoint[1]==endPoint[1]: #Degenerate
            return rect.collidePoint(startPoint)
        elif startPoint[0]==endPoint[0]: #Vertical
            if rect.left > startPoint[0] or rect.right < startPoint[0]:
                return False
            if (startPoint[1] < rect.top and endPoint[1] < rect.top) or (startPoint[1] > rect.bottom and endPoint[1] > rect.bottom):
                return False
            return True
        elif startPoint[1]==endPoint[1]: #Horizontal
            if rect.top > startPoint[1] or rect.bottom < startPoint[1]:
                return False
            if (startPoint[0] < rect.left and endPoint[0] < rect.left) or (startPoint[0] > rect.right and endPoint[0] > rect.right):
                return False
            return True
        else:
            # We have an implicit equation of the form:
            # x = startPoint[0]+t*(endPoint[0]-startPoint[0])
            # y = startPoint[1]+t*(endPoint[1]-startPoint[1])
            t_left = (rect.left-startPoint[0])/(endPoint[0]-startPoint[0])
            t_right = (rect.right-startPoint[0])/(endPoint[0]-startPoint[0])
            t_top = (rect.top-startPoint[1])/(endPoint[1]-startPoint[1])
            t_bottom = (rect.bottom-startPoint[1])/(endPoint[1]-startPoint[1])
            #There are 3 cases:
            #The line doesn't intersect the rectangle
            #The line intersects the rectangle, but the segment stops before it does
            #The segment intersects the rectangle
            if (t_left < 0 and t_right < 0) or (t_left > 1 and t_right > 1):
                return False
            if (t_top < 0 and t_bottom < 0) or (t_top > 1 and t_bottom > 1):
                return False
            if (t_top > t_left and t_bottom > t_left and t_top > t_right and t_bottom > t_right):
                return False
            if (t_top < t_left and t_bottom < t_left and t_top < t_right and t_bottom < t_right):
                return False
            return True

    def getPathDistance(self, startPoint, endPoint):
        nodes = [startPoint, endPoint]
        solid_list = []
        for platform in self.gameState.platform_list:
            if platform.solid:
                solid_list += [platform.rect]
                nodes += [[platform.rect.right+1, platform.rect.top-1], [platform.rect.right+1, platform.rect.bottom+1], [platform.rect.left-1, platform.rect.top-1], [platform.rect.left-1, platform.rect.bottom+1]]

        closedSet = set()
        openSet = set([0])
        cameFrom = dict()
        dists = {0: 0}
        estimates = {0: math.sqrt((startPoint[0]-endPoint[0])**2+(startPoint[1]-endPoint[1])**2)}

        while (len(openSet) > 0):
            current = min(filter(lambda n: n[0] in openSet, estimates.items()), key=lambda x: x[1])[0] #Current now has the farthest-off point
            if current == 1:
                break

            openSet.remove(current)
            closedSet.add(current)
            for node in range(0,len(nodes)):
                if node in closedSet:
                    continue
                if not any(map(lambda f: self.segmentIntersects(nodes[node], nodes[current], f), solid_list)):
                    tentativeDist = dists[current] + math.sqrt((nodes[current][0]-nodes[node][0])**2+(nodes[current][1]-nodes[node][1])**2)
                    if node not in openSet:
                        openSet.add(node)
                    elif node in dists and tentativeDist >= dists[node]:
                        continue
                    cameFrom[node] = current
                    dists[node] = tentativeDist
                    estimates[node] = dists[node]+math.sqrt((nodes[node][0]-endPoint[0])**2+(nodes[node][1]-endPoint[1])**2)
        print cameFrom
        if 1 not in dists:
            return -1
        else: return dists[1]
    
    def update(self):
        print self.getPathDistance(self.fighter.rect.center, [1000,1500])
        """
        These modes will determine the current state of the player. Right now,
        the only mode is 'duckling' mode, where the AI will follow the player.
        """
        if self.mode == 'duckling':
            dx, dy = self.getDistanceTo(self.players[0])
            if dx < 0 and abs(dx)>abs(dy)//2:
                self.pressButton('left')
            else:
                self.releaseButton('left')
                
            if dx > 0 and abs(dx)>abs(dy)//2:
                self.pressButton('right')
            else:
                self.releaseButton('right')

            if dy < 0 and abs(dy)>abs(dx)//2 and self.jump_last_frame > 8 and self.fighter.change_y>=-1:
                self.pressButton('jump')
                self.jump_last_frame = 0
            else:
                self.releaseButton('jump')
                self.jump_last_frame += 1

            if dy > 0 and abs(dy)>abs(dx)//2 and self.fighter.grounded and not isinstance(self.fighter.current_action, baseActions.Crouch):
                self.pressButton('down')
            else:
                self.releaseButton('down')
