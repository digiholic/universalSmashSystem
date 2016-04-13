import engine.controller as controller
import pygame
import math
import pprint

class CPUplayer(controller.Controller):
    def __init__(self,bindings):
        controller.Controller.__init__(self,bindings)
        self.mode = 'duckling'
        self.jump_last_frame = 0
        
    def getDistanceTo(self,target):
        sx,sy = self.fighter.rect.center
        tx,ty = target.rect.center
        return (tx - sx, ty - sy)

    def passInputs(self):
        self.update()
        controller.Controller.passInputs(self)

    def segmentIntersects(self, startPoint, endPoint, rect):
        if startPoint[0]==endPoint[0] and startPoint[1]==endPoint[1]: #Degenerate
            return rect.collidepoint(startPoint)
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
            t_left = (rect.left-startPoint[0])/(endPoint[0]-startPoint[0])
            t_right = (rect.right-startPoint[0])/(endPoint[0]-startPoint[0])
            t_top = (rect.top-startPoint[1])/(endPoint[1]-startPoint[1])
            t_bottom = (rect.bottom-startPoint[1])/(endPoint[1]-startPoint[1])
            if (t_left < 0 and t_right < 0) or (t_left > 1 and t_right > 1):
                return False
            if (t_top < 0 and t_bottom < 0) or (t_top > 1 and t_bottom > 1):
                return False
            if (t_top > t_left and t_bottom > t_left and t_top > t_right and t_bottom > t_right):
                return False
            if (t_top < t_left and t_bottom < t_left and t_top < t_right and t_bottom < t_right):
                return False
            return True

    def pathRectIntersects(self, startPoint, endPoint, solid_list, width, height):
        startRect = pygame.Rect(startPoint[0]-width/2.0+2, startPoint[1]-height/2.0, width-4, height-1)
        endRect = pygame.Rect(endPoint[0]-width/2.0+2, endPoint[1]-height/2.0, width-4, height-1)
        if any(map(lambda f: self.segmentIntersects(startRect.topleft, endRect.topleft, f), solid_list)): return True
        if any(map(lambda f: self.segmentIntersects(startRect.topright, endRect.topright, f), solid_list)): return True
        if any(map(lambda f: self.segmentIntersects(startRect.bottomleft, endRect.bottomleft, f), solid_list)): return True
        if any(map(lambda f: self.segmentIntersects(startRect.bottomright, endRect.bottomright, f), solid_list)): return True
        return False

    def getPathDistance(self, startPoint, endPoint):
        nodes = [startPoint, endPoint]
        solid_list = []
        for platform in self.fighter.gameState.platform_list:
            if platform.solid:
                solid_list += [platform.rect]
                nodes += [[platform.rect.right+self.fighter.sprite.boundingRect.width/2.0, platform.rect.top-self.fighter.sprite.boundingRect.height/2.0], 
                          [platform.rect.right+self.fighter.sprite.boundingRect.width/2.0, platform.rect.bottom+self.fighter.sprite.boundingRect.height/2.0], 
                          [platform.rect.left-self.fighter.sprite.boundingRect.width/2.0, platform.rect.top-self.fighter.sprite.boundingRect.height/2.0], 
                          [platform.rect.left-self.fighter.sprite.boundingRect.width/2.0, platform.rect.bottom+self.fighter.sprite.boundingRect.height/2.0]]

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
                if not self.pathRectIntersects(nodes[current], nodes[node], solid_list, self.fighter.sprite.boundingRect.width, self.fighter.sprite.boundingRect.height):
                    tentativeDist = dists[current] + math.sqrt((nodes[current][0]-nodes[node][0])**2+(nodes[current][1]-nodes[node][1])**2)
                    if node not in openSet:
                        openSet.add(node)
                    elif node in dists and tentativeDist >= dists[node]:
                        continue
                    cameFrom[node] = current
                    dists[node] = tentativeDist
                    estimates[node] = dists[node]+math.sqrt((nodes[node][0]-endPoint[0])**2+(nodes[node][1]-endPoint[1])**2)
        if 1 not in dists:
            return 99999
        else: return dists[1]

    def ducklingTargeting(self):
        opposingPlayers = filter(lambda k: k != self.fighter, self.fighter.players)
        opposingDists = map(lambda x: self.getPathDistance(self.fighter.rect.center, x.rect.center), opposingPlayers)
        return opposingPlayers[opposingDists.index(min(opposingDists))].rect.center

    def ledgeTargeting(self):
        ledgePoints = map(lambda x: [x.rect.left-self.fighter.sprite.boundingRect.width/2.0 if x.side == 'left' else x.rect.right+self.fighter.sprite.boundingRect.width/2.0, x.rect.bottom+self.fighter.sprite.boundingRect.height/2.0], self.fighter.gameState.platform_ledges)
        ledgeDistances = map(lambda x: self.getPathDistance(self.fighter.sprite.boundingRect.center, x), ledgePoints)
        return ledgePoints[ledgeDistances.index(min(ledgeDistances))]

    def platformTargeting(self):
        targetPoints = map(lambda x: [x.rect.left-self.fighter.sprite.boundingRect.width/2.0, x.rect.top-self.fighter.sprite.boundingRect.height/2.0], self.fighter.gameState.platform_list)+map(lambda x: [x.rect.right+self.fighter.sprite.boundingRect.width/2.0, x.rect.top-self.fighter.sprite.boundingRect.height/2.0], self.fighter.gameState.platform_list)
        targetDistances = map(lambda x: self.getPathDistance(self.fighter.sprite.boundingRect.center, x), targetPoints)
        return targetPoints[targetDistances.index(min(targetDistances))]

    def update(self):
        constructList = []
        import engine.baseActions as baseActions
        if self.fighter is None or not hasattr(self.fighter, 'players') or self.fighter.players is None:
            print("Can't find!")
            return
        if self.mode == 'duckling': #Follow the player
            distance = self.getPathDistance(self.fighter.rect.center, self.ducklingTargeting())
            prevDistance = self.getPathDistance(self.fighter.ecb.yBar.rect.center, self.fighter.players[0].sprite.boundingRect.center)
            #We offset by one so that simply running away doesn't trigger catchup behavior
            (dx, dy) = self.getDistanceTo(self.fighter.players[0])
            if dx < 0:
                if not isinstance(self.fighter.current_action, baseActions.LedgeGrab):
                    constructList += ['left']
            if dx > 0:
                if not isinstance(self.fighter.current_action, baseActions.LedgeGrab):
                    constructList += ['right']
            if dy < 0 and self.jump_last_frame > 8 and distance-prevDistance>0:
                constructList += ['jump']
                self.jump_last_frame = 0
            else:
                self.jump_last_frame += 1
            if dy > 0 and self.fighter.grounded and not isinstance(self.fighter.current_action, baseActions.Crouch):
                constructList += ['down']
        for key in filter(lambda x: x not in constructList, self.keysHeld):
            self.keysToRelease += [key]
        for key in filter(lambda x: x not in self.keysHeld, constructList):
            self.keysToPass += [key]
