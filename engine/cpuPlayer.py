import engine.controller as controller
import pygame
import math
import pprint

class CPUplayer(controller.Controller):
    def __init__(self,bindings):
        controller.Controller.__init__(self,bindings)
        self.mode = 'duckling'
        self.jump_last_frame = 0
        self.type = 'CPU'
        
    def getDistanceTo(self,target):
        sx,sy = self.fighter.rect.center
        tx,ty = target.rect.center
        return (tx - sx, ty - sy)

    def passInputs(self):
        self.update()
        controller.Controller.passInputs(self)

    def getPathDistance(self, start_point, end_point):
        import engine.abstractFighter as abstractFighter
        nodes = [start_point, end_point]
        solid_list = []
        for platform in self.fighter.gameState.platform_list:
            if platform.solid:
                solid_list += [platform.rect]
                nodes += [[platform.rect.right+self.fighter.sprite.boundingRect.width/2.0, platform.rect.top-self.fighter.sprite.boundingRect.height/2.0], 
                          [platform.rect.right+self.fighter.sprite.boundingRect.width/2.0, platform.rect.bottom+self.fighter.sprite.boundingRect.height/2.0], 
                          [platform.rect.left-self.fighter.sprite.boundingRect.width/2.0, platform.rect.top-self.fighter.sprite.boundingRect.height/2.0], 
                          [platform.rect.left-self.fighter.sprite.boundingRect.width/2.0, platform.rect.bottom+self.fighter.sprite.boundingRect.height/2.0]]

        closed_set = set()
        open_set = set([0])
        came_from = dict()
        dists = {0: 0}
        estimates = {0: math.sqrt((start_point[0]-end_point[0])**2+(start_point[1]-end_point[1])**2)}

        while (len(open_set) > 0):
            current = min(filter(lambda n: n[0] in open_set, estimates.items()), key=lambda x: x[1])[0] #Current now has the farthest-off point
            if current == 1:
                break

            open_set.remove(current)
            closed_set.add(current)
            for node in range(0,len(nodes)):
                if node in closed_set:
                    continue
                current_ecb = pygame.Rect(nodes[current][0]-self.fighter.ecb.current_ecb.rect.width//2, nodes[current][1]-self.fighter.ecb.current_ecb.rect.height//2, self.fighter.ecb.current_ecb.rect.width, self.fighter.ecb.current_ecb.rect.height)
                next_ecb = pygame.Rect(nodes[node][0]-self.fighter.ecb.current_ecb.rect.width//2, nodes[node][1]-self.fighter.ecb.current_ecb.rect.height//2, self.fighter.ecb.current_ecb.rect.width, self.fighter.ecb.current_ecb.rect.height)

                if not any(map(lambda f: abstractFighter.pathRectIntersects(current_ecb, next_ecb, f) <= 1, solid_list)):
                    tentativeDist = dists[current] + math.sqrt((nodes[current][0]-nodes[node][0])**2+(nodes[current][1]-nodes[node][1])**2)
                    if node not in open_set:
                        open_set.add(node)
                    elif node in dists and tentativeDist >= dists[node]:
                        continue
                    came_from[node] = current
                    dists[node] = tentativeDist
                    estimates[node] = dists[node]+math.sqrt((nodes[node][0]-end_point[0])**2+(nodes[node][1]-end_point[1])**2)
        if 1 not in dists:
            return 99999
        else: return dists[1]

    def ducklingTargeting(self):
        opposing_players = filter(lambda k: k != self.fighter, self.fighter.players)
        opposing_dists = map(lambda x: self.getPathDistance(self.fighter.rect.center, x.rect.center), opposing_players)
        return opposing_players[opposing_dists.index(min(opposing_dists))].rect.center

    def ledgeTargeting(self):
        ledge_points = map(lambda x: [x.rect.left-self.fighter.sprite.boundingRect.width/2.0 if x.side == 'left' else x.rect.right+self.fighter.sprite.boundingRect.width/2.0, x.rect.bottom+self.fighter.sprite.boundingRect.height/2.0], self.fighter.gameState.platform_ledges)
        ledge_distances = map(lambda x: self.getPathDistance(self.fighter.sprite.boundingRect.center, x), ledge_points)
        return ledge_points[ledge_distances.index(min(ledge_distances))]

    def platformTargeting(self):
        target_points = map(lambda x: [x.rect.left-self.fighter.sprite.boundingRect.width/2.0, x.rect.top-self.fighter.sprite.boundingRect.height/2.0], self.fighter.gameState.platform_list)+map(lambda x: [x.rect.right+self.fighter.sprite.boundingRect.width/2.0, x.rect.top-self.fighter.sprite.boundingRect.height/2.0], self.fighter.gameState.platform_list)
        target_distances = map(lambda x: self.getPathDistance(self.fighter.sprite.boundingRect.center, x), target_points)
        return target_points[target_distances.index(min(target_distances))]

    def update(self):
        construct_list = []
        import engine.baseActions as baseActions
        if self.fighter is None or not hasattr(self.fighter, 'players') or self.fighter.players is None:
            print("Can't find!")
            return
        if self.mode == 'duckling': #Follow the player
            distance = self.getPathDistance(self.fighter.rect.center, self.ducklingTargeting())
            prev_distance = self.getPathDistance(self.fighter.ecb.current_ecb.rect.center, self.fighter.players[0].sprite.boundingRect.center)
            #We offset by one so that simply running away doesn't trigger catchup behavior
            (dx, dy) = self.getDistanceTo(self.fighter.players[0])
            if dx < 0:
                if not isinstance(self.fighter.current_action, baseActions.LedgeGrab):
                    construct_list += ['left']
            if dx > 0:
                if not isinstance(self.fighter.current_action, baseActions.LedgeGrab):
                    construct_list += ['right']
            if dy < 0 and self.jump_last_frame > 8 and distance-prev_distance>0:
                construct_list += ['jump']
                self.jump_last_frame = 0
            else:
                self.jump_last_frame += 1
            if dy > 0 and self.fighter.grounded and not isinstance(self.fighter.current_action, baseActions.Crouch):
                construct_list += ['down']
        for key in filter(lambda x: x not in construct_list, self.keys_held):
            self.keys_to_release += [key]
        for key in filter(lambda x: x not in self.keys_held, construct_list):
            self.keys_to_pass += [key]
