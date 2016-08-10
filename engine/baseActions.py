import engine.action as action
import engine.hitbox as hitbox
import engine.article as article
import pygame
import math
import settingsManager

class Move(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self,length) 
        
    def setUp(self,actor):
        if self.sprite_name=="": self.sprite_name = "move"
        action.Action.setUp(self, actor)
        self.accel = True
        self.direction = actor.facing
        
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_xspeed = 0
        
    def update(self, actor):
        action.Action.update(self, actor)
        actor.preferred_xspeed = actor.var['max_ground_speed']*self.direction
        actor.accel(actor.var['static_grip'])

        (key,invkey) = actor.getForwardBackwardKeys()
        if self.direction == actor.facing:
            if actor.keysContain(invkey):
                actor.flip()
        else:
            if not actor.keysContain(key):
                actor.flip()
        
        
        self.frame += 1
        
        if self.frame > self.last_frame: self.frame = 0
        
    def stateTransitions(self,actor):
        moveState(actor,self.direction)
        if actor.grounded is False:
            actor.doAction('Fall')
        (key,invkey) = actor.getForwardBackwardKeys()
        if self.frame > 0 and actor.keyBuffered(invkey, 0, state = 1):
            actor.doDash(-1*actor.getFacingDirection())
        elif self.frame > 0 and actor.keyBuffered(key, 0, state = 1):
            actor.doDash(actor.getFacingDirection())

class Dash(action.Action):
    def __init__(self,length=1,runStartFrame=0): 
        action.Action.__init__(self,length)
        self.runStartFrame = runStartFrame
        
    def setUp(self,actor):
        if self.sprite_name=="": self.sprite_name = "dash"
        action.Action.setUp(self, actor)
        self.pivoted = False
        if actor.facing == 1: self.direction = 1
        else: self.direction = -1

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_xspeed = 0

    def update(self, actor):
        action.Action.update(self, actor)
        if self.frame == 0:
            actor.preferred_xspeed = actor.var['run_speed']*self.direction
        (key,invkey) = actor.getForwardBackwardKeys()
        if actor.grounded is False:
            actor.doAction('Fall')
        if not self.pivoted:
            if actor.keysContain(invkey) and actor.change_x != actor.var['run_speed']*self.direction:
                actor.flip() #Do the moonwalk!
                self.pivoted = True
        actor.accel(actor.var['static_grip'])

        self.frame += 1
        
        if self.frame > self.last_frame: 
            self.frame = self.runStartFrame
            
    def stateTransitions(self,actor):
        dashState(actor,self.direction)
        
class Pivot(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name = "pivot"
        action.Action.setUp(self, actor)
        
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        if isinstance(nextAction, Move):
            nextAction.accel = False
        #actor.flip()

    def stateTransitions(self, actor):
        if actor.keyHeld('jump', self.frame):
            actor.doAction('Jump')
        (key, invkey) = actor.getForwardBackwardKeys()
        if actor.keysContain(invkey):
            print("pivot pivot")
            actor.doAction('Pivot')

        
    def update(self,actor):
        action.Action.update(self, actor)
        if actor.grounded is False:
            actor.doAction('Fall')
        actor.accel(actor.var['pivot_grip'])
        if self.frame == 0:
            actor.flip()
        if self.frame != self.last_frame:
            self.frame += 1
            actor.preferred_xspeed = 0
        if self.frame == self.last_frame:
            (key, _) = actor.getForwardBackwardKeys()
            if actor.keysContain(key):
                if actor.checkSmash(key):
                    if actor.facing == 1:
                        actor.doDash(0)
                    else:
                        actor.doDash(180)
                else:
                    if actor.facing == 1:
                        actor.doGroundMove(0)
                    else:
                        actor.doGroundMove(180)
            else:
                actor.doAction('NeutralAction')
          
class Stop(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name = "stop"
        action.Action.setUp(self, actor)
        
    def update(self, actor):
        action.Action.update(self, actor)
        #print(self.frame,actor.sprite.index)
        actor.preferred_xspeed = 0
        self.frame += 1
        
    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        actor.accel(actor.var['static_grip'])
        (key,invkey) = actor.getForwardBackwardKeys()
        if actor.keyHeld(key,self.frame):
            print("run")
            actor.doDash(actor.getFacingDirection())
        if actor.keyHeld(invkey,self.frame):
            print("pivot")
            actor.doAction('Pivot')
        if self.frame == self.last_frame:
            if actor.keyHeld('jump'):
                actor.doAction('Jump')
            else: actor.doAction('NeutralAction')

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        if isinstance(nextAction, Pivot):
            nextAction.frame = self.frame
            print(self.frame)
        
class RunPivot(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="runPivot" 
        action.Action.setUp(self, actor)
        actor.flip()
        
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_xspeed = 0
        #actor.flip()
        if isinstance(nextAction, Dash):
            nextAction.accel = False
        
        
    def stateTransitions(self, actor):
        if actor.keyHeld('jump', self.frame):
            actor.doAction('Jump')
        (key, invkey) = actor.getForwardBackwardKeys()
        if actor.keysContain(invkey):
            print("run pivot pivot")
            actor.doAction('RunPivot')
        
    def update(self,actor):
        action.Action.update(self, actor)
        if actor.grounded is False:
            actor.doAction('Fall')
        actor.accel(actor.var['static_grip'])
        if self.frame != self.last_frame:
            self.frame += 1
            actor.preferred_xspeed = actor.var['run_speed']*actor.facing
        if self.frame == self.last_frame:
            (key, _) = actor.getForwardBackwardKeys()
            if actor.keysContain(key):
                if actor.facing == 1:
                    actor.doDash(0)
                else:
                    actor.doDash(180)
            else:
                actor.doAction('NeutralAction')

class RunStop(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="runStop"
        action.Action.setUp(self, actor)
        
    def update(self, actor):
        action.Action.update(self, actor)
        actor.preferred_xspeed = 0
        if self.frame == self.last_frame:
            if actor.keyHeld('jump'):
                actor.doAction('Jump')
            else: actor.doAction('NeutralAction')
        self.frame += 1
        
    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        actor.accel(actor.var['static_grip'])
        (key,invkey) = actor.getForwardBackwardKeys()
        if actor.keyHeld(key,self.frame):
            print("run")
            actor.doDash(actor.getFacingDirection())
        if actor.keyHeld(invkey,self.frame):
            print("run pivot")
            actor.doAction('RunPivot')
        if self.frame == self.last_frame:
            if actor.keyHeld('jump', 8, 1):
                actor.doAction('Jump')
            else: actor.doAction('NeutralAction')

                
class NeutralAction(action.Action):
    def __init__(self,length=1):
        action.Action.__init__(self, length)
    
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="neutralAction"
        action.Action.setUp(self, actor)
        
    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        neutralState(actor)
    
    def update(self,actor):
        action.Action.update(self, actor)
        if self.frame == self.last_frame:
            self.frame = 0
        self.frame += 1

class Respawn(action.Action):
    def __init__(self,length=120):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="neutralAction"
        action.Action.setUp(self, actor)
        self.respawn_article = article.RespawnPlatformArticle(actor)
        
    def stateTransitions(self, actor):
        neutralState(actor)
    
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        self.respawn_article.kill()
        
    def update(self,actor):
        action.Action.update(self, actor)
        actor.ground = True
        actor.change_y = 0
        if self.frame == 0:
            actor.articles.add(self.respawn_article)
        if self.frame == self.last_frame:
            actor.doAction('Fall')
        self.frame += 1
        
class Crouch(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="crouch"
        action.Action.setUp(self, actor)
        self.direction = actor.getForwardWithOffset(0)

    def stateTransitions(self, actor):
        crouchState(actor)
        if actor.grounded is False:
            actor.doAction('Fall')
        if self.frame > 0 and actor.keyBuffered('down', 1, state = 1):
            blocks = actor.checkGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    actor.doAction('PlatformDrop')

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_xspeed = 0

    def update(self, actor):
        action.Action.update(self, actor)
        if actor.grounded is False:
            actor.doAction('Fall')
        actor.accel(actor.var['pivot_grip'])
        (key, invkey) = actor.getForwardBackwardKeys()
        if actor.keysContain(key):
            actor.preferred_xspeed = actor.var['crawl_speed']*actor.facing
        elif actor.keysContain(invkey):
            actor.preferred_xspeed = -actor.var['crawl_speed']*actor.facing
        else:
            actor.preferred_xspeed = 0
        
        self.frame += 1

class CrouchGetup(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="crouchGetup"
        action.Action.setUp(self, actor)
        
    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        elif actor.keyBuffered('down', 1, state = 1):
            blocks = actor.checkGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    actor.doAction('PlatformDrop')

    def update(self, actor):
        action.Action.update(self, actor)
        actor.preferred_xspeed = 0
        self.frame += 1
        if self.frame >= self.last_frame:
            actor.doAction('NeutralAction')

class BaseGrabbing(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self, length)

    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="baseGrabbing"
        action.Action.setUp(self, actor)
        
    def tearDown(self, actor, nextAction):
        print(self.hitboxes)
        action.Action.tearDown(self, actor, nextAction)
        if not isinstance(nextAction, BaseGrabbing) and actor.isGrabbing():
            actor.grabbing.doReleased()

    def update(self, actor):
        action.Action.update(self, actor)
        self.frame += 1

class Grabbing(BaseGrabbing):
    def __init__(self,length=0):
        BaseGrabbing.__init__(self, length)

    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="grabbing"
        action.Action.setUp(self, actor)
        actor.grabbing.flinch_damage_threshold = 9999

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.grabbing.flinch_damage_threshold = 0

    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        grabbingState(actor)
        
class HitStun(action.Action):
    def __init__(self,hitstun=1,direction=0):
        action.Action.__init__(self, hitstun)
        self.direction = direction

    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="hitStun"
        action.Action.setUp(self, actor)
        self.tech_cooldown = 5
        actor.elasticity = actor.var['hitstun_elasticity']
        
    def stateTransitions(self, actor):
        (direct,_) = actor.getDirectionMagnitude()
        if actor.keyBuffered('shield', 1) and self.tech_cooldown == 0 and not actor.grounded:
            print('Try tech')
            actor.tech_window = 7
            self.tech_cooldown = 40
            
        if self.frame == self.last_frame:
            actor.elasticity = actor.var['hitstun_elasticity']/2
        else:
            actor.elasticity = actor.var['hitstun_elasticity']
            if self.frame > 2:
                hitstunLanding(actor)
        if self.frame > 2:
            if self.frame < self.last_frame and actor.change_y >= actor.var['max_fall_speed']: #Hard landing during hitstun
                actor.ground_elasticity = actor.var['hitstun_elasticity']
            elif abs(actor.change_x) > actor.var['run_speed']: #Skid trip
                actor.ground_elasticity = 0
                if actor.grounded:
                    actor.doAction('Prone')
            elif actor.change_y < actor.var['max_fall_speed']/2.0: #Soft landing during hitstun
                actor.landing_lag = actor.var['heavy_land_lag']+self.last_frame-self.frame
                actor.ground_elasticity = 0
            else: #Firm landing during hitstun
                actor.ground_elasticity = actor.var['hitstun_elasticity']/2
        
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        if not isinstance(nextAction, Tumble):
            actor.elasticity = 0
            actor.ground_elasticity = 0
            actor.unRotate()
        
    def update(self,actor):
        action.Action.update(self, actor)
        if self.tech_cooldown > 0: self.tech_cooldown -= 1
        
        if self.frame == 0:
            (direct,mag) = actor.getDirectionMagnitude()
            print("direction:", direct)
            if direct != 0 and direct != 180:
                actor.grounded = False
                if mag > 10:
                    actor.rotateSprite(self.direction)
            
        if self.frame % 15 == 10 and self.frame < self.last_frame:
            if abs(actor.change_x) > 8 or abs(actor.change_y) > 8:
                art = article.AnimatedArticle(settingsManager.createPath('sprites/circlepuff.png'),actor,actor.rect.center,86,6)
                art.angle = actor.sprite.angle
                if actor.hit_tagged and hasattr(actor.hit_tagged, 'player_num'):
                    for image in art.imageList:
                        art.recolor(image, [255,255,255], pygame.Color(settingsManager.getSetting('playerColor' + str(actor.hit_tagged.player_num))))
                actor.articles.add(art)
                    
        if self.frame == self.last_frame:
            actor.doAction('Tumble')

        self.frame += 1

class Tumble(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
    
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="tumble"
        action.Action.setUp(self, actor)    
        self.tech_cooldown = 0
        
    def stateTransitions(self, actor):
        action.Action.stateTransitions(self, actor)
        airState(actor)
        
        (direct,_) = actor.getDirectionMagnitude()
        
        if actor.keyBuffered('shield', 1) and self.tech_cooldown == 0 and not actor.grounded:
            print('Try tech')
            actor.tech_window = 20
            self.tech_cooldown = 40
            
        if actor.change_y >= actor.var['max_fall_speed']:#Hard landing during tumble
            actor.ground_elasticity = actor.var['hitstun_elasticity']/2
        elif actor.change_y < actor.var['max_fall_speed']/2.0: #Soft landing during tumble
            actor.ground_elasticity = 0
            if actor.grounded: 
                #actor.doTrip(self.last_frame-self.frame//2, direct)
                actor.doAction('Prone')
        else: #Firm landing during tumble
            actor.ground_elasticity = 0
            if actor.grounded: 
                #actor.doTrip(self.last_frame-self.frame//2+actor.var['heavy_land_lag'], direct)
                actor.doAction('Prone')
    
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.elasticity = 0
        actor.ground_elasticity = 0
        actor.unRotate()
        
    def update(self, actor):
        action.Action.update(self, actor)
        actor.rotateSprite((actor.sprite.angle+90)+2)
        if self.tech_cooldown > 0: self.tech_cooldown -= 1
        
class Prone(action.Action):
    def __init__(self,length=40):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name == "": self.sprite_name = "prone"
        action.Action.setUp(self, actor)
        actor.rect.bottom = actor.ecb.current_ecb.rect.bottom
        actor.unRotate()
        
    def update(self, actor):
        action.Action.update(self, actor)
        if not actor.grounded:
            actor.doAction('Tumble')
        if self.frame == self.last_frame:
            actor.doAction('Getup')
        self.frame += 1
        
    def stateTransitions(self, actor):
        action.Action.stateTransitions(self, actor)
        if self.frame >= self.last_frame:
            proneState(actor)
        
class Trip(action.Action):
    def __init__(self,length=0,direction=0):
        action.Action.__init__(self, length)
        self.direction = direction
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="trip"
        action.Action.setUp(self, actor)
        actor.rect.bottom = actor.ecb.current_ecb.rect.bottom

    def update(self, actor):
        if actor.grounded is False:
            actor.doHitStun(self.last_frame-self.frame, self.direction)
        if self.frame >= self.last_frame + 60: #You aren't up yet?
            actor.doGetup(self.direction)
        self.frame += 1

    def stateTransitions(self, actor):
        if self.frame >= self.last_frame:
            proneState(actor)

class Getup(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="getup"
        action.Action.setUp(self, actor)
        
    def update(self, actor):
        action.Action.update(self, actor)
        if self.frame == self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1
        
"""
@ai-move-up
@ai-move-stop
"""
class Jump(action.Action):
    def __init__(self,length=0,jump_frame=0):
        action.Action.__init__(self, length)
        self.jump_frame = jump_frame
    
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="jump"
        action.Action.setUp(self, actor)
        
    def stateTransitions(self, actor):
        if actor.keyHeld('attack') and actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up smash")
            actor.doAction('UpSmash')
        elif actor.keyHeld('special') and actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up special")
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpGroundSpecial')
        elif self.frame > self.jump_frame+2:
            jumpState(actor)
        
    def update(self,actor):
        action.Action.update(self, actor)
        if self.frame == self.jump_frame:
            actor.grounded = False
            if actor.keysContain('jump'):
                actor.change_y = -actor.var['jump_height']
            else: actor.change_y = -actor.var['short_hop_height']
            if actor.change_x > actor.var['aerial_transition_speed']:
                actor.change_x = actor.var['aerial_transition_speed']
            elif actor.change_x < -actor.var['aerial_transition_speed']:
                actor.change_x = -actor.var['aerial_transition_speed']
        if self.frame < self.last_frame:
            self.frame += 1
        if self.frame == self.last_frame and not actor.keysContain('jump'):
            actor.doAction('Fall')

class AirJump(action.Action):
    def __init__(self,length=0,jump_frame=0):
        action.Action.__init__(self, length)
        self.jump_frame = jump_frame
        #TODO: Change to add the number of buffer frames
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="airjump"
        action.Action.setUp(self, actor)

    def stateTransitions(self, actor):
        if actor.keyHeld('attack') and actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up aerial")
            actor.doAction('UpAir')
        elif actor.keyHeld('special') and actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up special")
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpAirSpecial')
        else: 
            jumpState(actor)

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_yspeed = actor.var['max_fall_speed']
        
    def update(self,actor):
        action.Action.update(self, actor)
        if self.frame < self.jump_frame:
            actor.change_y = 0
            actor.preferred_yspeed = 0
        if self.frame == self.jump_frame:
            actor.grounded = False
            actor.change_y = -actor.var['air_jump_height']
            actor.jumps -= 1
            if actor.keysContain('left') and actor.facing == 1:
                actor.flip()
                actor.change_x = actor.facing * actor.var['max_air_speed']
            elif actor.keysContain('right') and actor.facing == -1:
                actor.flip()
                actor.change_x = actor.facing * actor.var['max_air_speed']
        if self.frame < self.last_frame:
            self.frame += 1
        if self.frame == self.last_frame:
            actor.doAction('Fall')
        
class Fall(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)

    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="fall"
        action.Action.setUp(self, actor)
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['max_fall_speed']
    
    def stateTransitions(self,actor):
        airState(actor)
        grabLedges(actor)
        
    def update(self,actor):
        action.Action.update(self, actor)
        actor.grounded = False
        self.frame += 1

class Helpless(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)
    
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="helpless"
        action.Action.setUp(self, actor)
    
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.mask = None
        
    def stateTransitions(self, actor):
        helplessControl(actor)
        grabLedges(actor)

    def update(self, actor):
        actor.grounded = False
        if self.frame == 0:
            actor.createMask([191, 63, 191], 99999, True, 16)
        self.frame += 1
            
class Land(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="land"
        action.Action.setUp(self, actor)
        actor.unRotate()
        #actor.rect.bottom = actor.ecb.current_ecb.rect.bottom


    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        #actor.preferred_xspeed = 0

    def update(self,actor):
        action.Action.update(self, actor)
        #actor.rect.bottom = actor.ecb.current_ecb.rect.bottom
        if self.frame == 0:
            actor.preferred_yspeed = actor.var['max_fall_speed']
            self.last_frame = actor.landing_lag
            if actor.keyHeld('shield', 1):
                print("l-cancel")
                self.last_frame = self.last_frame // 2

        if actor.keyHeld('down') and self.frame*2 > self.last_frame:
            blocks = actor.checkGround()
            if blocks:   
                blocks = map(lambda x: x.solid, blocks)
                if not any(blocks):
                    actor.doAction('PlatformDrop')

        if self.frame == 1:
            #actor.articles.add(article.LandingArticle(actor)) #this looks awful don't try it
            pass
        if self.frame == self.last_frame:
            actor.landing_lag = 0
            actor.doAction('NeutralAction')
            actor.platform_phase = 0
            actor.preferred_xspeed = 0
        self.frame+= 1

class HelplessLand(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="helplessLand"
        action.Action.setUp(self, actor)
        #actor.rect.bottom = actor.ecb.current_ecb.rect.bottom


    def update(self,actor):
        action.Action.update(self, actor)
        #actor.rect.bottom = actor.ecb.current_ecb.rect.bottom
        if self.frame == 0:
            actor.change_y = 0
            actor.preferred_yspeed = actor.var['max_fall_speed']
            self.last_frame = actor.landing_lag
            if actor.keyHeld('shield', 20):
                print("l-cancel")
                self.last_frame = self.last_frame // 2
        if actor.keyHeld('down', 8):
            blocks = actor.checkGround()
            if blocks:
                blocks = map(lambda x: x.solid, blocks)
                if not any(blocks):
                    actor.doAction('PlatformDrop')
        if self.frame >= self.last_frame:
            actor.landing_lag = 0
            actor.doAction('NeutralAction')
            actor.platform_phase = 0
            actor.preferred_xspeed = 0
        self.frame += 1

class PlatformDrop(action.Action):
    def __init__(self, length=1, phase_frame=1, phase_length=1):
        action.Action.__init__(self, length)
        self.phase_frame = phase_frame
        self.phase_length = phase_length
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="platformDrop"
        action.Action.setUp(self, actor)
        
    def stateTransitions(self, actor):
        if actor.keyHeld('attack') and actor.checkSmash('down') and self.frame < self.phase_frame:
            print("Platform drop cancelled into down smash")
            actor.doAction('DownSmash')
        elif actor.keyHeld('special') and actor.checkSmash('down') and self.frame < self.phase_frame:
            print("Platform drop cancelled into down special")
            if self.hasAction('DownSpecial'):
                self.doAction('DownSpecial')
            else:
                self.doAction('DownGroundSpecial')
        if self.frame > self.phase_frame:
            airControl(actor)
        
    def update(self,actor):
        action.Action.update(self, actor)
        if self.frame == self.phase_frame:
            actor.platform_phase = self.phase_length
        if self.frame == self.last_frame:
            actor.doAction('Fall')
        self.frame += 1


class Shield(action.Action):
    def __init__(self, new_shield=True):
        action.Action.__init__(self, 8)
        self.new_shield = new_shield
   
    def setUp(self, actor):
        action.Action.setUp(self, actor)
        self.forward_last = 0
        self.backward_last = 0
        self.down_last = 0
        
    def stateTransitions(self, actor):
        shieldState(actor)
        (key, invkey) = actor.getForwardBackwardKeys()
        if actor.keyBuffered(key, 1, 0.6) and self.forward_last > 0:
            actor.doAction('ForwardRoll')
        elif actor.keyBuffered(invkey, 1, 0.6) and self.backward_last > 0:
            actor.doAction('BackwardRoll')
        elif actor.keyBuffered('down', 1, 0.6) and self.down_last > 0:
            actor.doAction('SpotDodge')

        if actor.keyBuffered(key, 1, 0.6):
            self.forward_last = 9
            self.backward_last = 0
        if actor.keyBuffered(invkey, 1, 0.6):
            self.backward_last = 9
            self.forward_last = 0
        if actor.keyBuffered('down', 1, 0.6):
            self.down_last = 9
        if actor.keyBuffered('up', 1, 0.6):
            self.down_last = 0
   
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        if not isinstance(nextAction, ShieldStun):
            actor.shield = False
       
    def update(self, actor):
        if actor.grounded is False:
            actor.shield = False
            actor.doAction('Fall')
        if self.frame == 0:
            actor.shield = True
            if self.new_shield:
                actor.startShield()
            if actor.keysContain('shield'):
                self.frame += 1
            else:
                self.frame += 2
        elif self.frame == 1:
            if not actor.keysContain('shield'):
                self.frame += 1
        elif self.frame >= 2 and self.frame < self.last_frame:
            actor.shield = False
            self.frame += 1
        elif self.frame >= self.last_frame:
            actor.doAction('NeutralAction')
        else: self.frame += 1
        if self.forward_last > 0: self.forward_last -= 1
        if self.backward_last > 0: self.backward_last -= 1
        if self.down_last > 0: self.down_last -= 1

class ShieldStun(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="shieldStun"
        action.Action.setUp(self, actor)

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        if not isinstance(nextAction, Shield) and not isinstance(nextAction, ShieldStun):
            actor.shield = False

    def update(self, actor):
        if actor.grounded is False:
            actor.shield = False
            actor.doAction('Fall')
        if self.frame >= self.last_frame and actor.keysContain('shield'):
            actor.doShield(False)
        elif self.frame >= self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1

class Stunned(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
        if self.sprite_name=="": self.sprite_name ="stunned"
    
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="stunned"
        action.Action.setUp(self, actor)
    
    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)    
        actor.mask = None
        
    def update(self, actor):
        action.Action.update(self, actor)
        if self.frame == 0:
            actor.createMask([255, 0, 255], 99999, True, 8)
        if self.frame == self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1

class Trapped(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
        self.time = 0
        self.last_position = [0,0]
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="trapped"
        action.Action.setUp(self, actor)
        
    def update(self,actor):
        action.Action.update(self, actor)
        new_position = actor.getSmoothedInput()
        cross = new_position[0]*self.last_position[1]-new_position[1]*self.last_position[0]
        self.frame += (cross**2)*4
        self.last_position = new_position
        if self.frame >= self.last_frame:
            actor.doAction('Released')
        # Throws and other grabber-controlled releases are the grabber's responsibility
        # Also, the grabber should always check to see if the grabbee is still under grab
        self.frame += 1
        self.time += 1
        print(self.frame, self.time)

class Grabbed(Trapped):
    def __init__(self,height=1):
        Trapped.__init__(self, 40)
        self.height = height
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="grabbed"
        Trapped.setUp(self, actor)
        
    def update(self,actor):
        action.Action.update(self, actor)
        if self.frame == 0:
            self.last_frame = 40 + actor.damage//2
        if (self.height > actor.rect.height):
            actor.rect.top = actor.grabbed_by.rect.bottom-self.height
        else:
            actor.rect.bottom = actor.grabbed_by.rect.bottom
        actor.rect.centerx = actor.grabbed_by.rect.centerx+actor.grabbed_by.facing*actor.grabbed_by.rect.width/2.0
        Trapped.update(self, actor)

class Release(action.Action):
    def __init__(self):
        action.Action.__init__(self, 15)
    
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="release"
        action.Action.setUp(self, actor)
        
    def update(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        if self.frame >= self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1

class Released(action.Action):
    def __init__(self):
        action.Action.__init__(self, 15)

    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="released"
        action.Action.setUp(self, actor)
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['max_fall_speed']
    
    def stateTransitions(self,actor):
        (key, invkey) = actor.getForwardBackwardKeys()
        if actor.keysContain(key):
            actor.preferred_xspeed = actor.facing * actor.var['max_air_speed']
        elif actor.keysContain(invkey):
            actor.preferred_xspeed = -actor.facing * actor.var['max_air_speed']
    
        if (actor.change_x < 0) and not actor.keysContain('left'):
            actor.preferred_xspeed = 0
        elif (actor.change_x > 0) and not actor.keysContain('right'):
            actor.preferred_xspeed = 0

        if actor.change_y >= actor.var['max_fall_speed'] and actor.landing_lag < actor.var['heavy_land_lag']:
            actor.landing_lag = actor.var['heavy_land_lag']

        if actor.grounded and actor.ground_elasticity == 0:
            actor.preferred_xspeed = 0
            actor.preferred_yspeed = actor.var['max_fall_speed']
            actor.doAction('Prone')
            actor.current_action.last_frame = 15 - self.last_frame

        grabLedges(actor)
        
    def update(self,actor):
        action.Action.update(self, actor)
        actor.grounded = False
        if self.frame >= self.last_frame:
            actor.doAction('Fall')
        self.frame += 1
        
class ForwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 46)
        
    def setUp(self, actor):
        self.start_invuln_frame = 6
        self.end_invuln_frame = 34
        if self.sprite_name=="": self.sprite_name ="forwardRoll"
        action.Action.setUp(self, actor)

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_xspeed = 0
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        if self.frame == 1:
            actor.change_x = actor.facing * actor.var['dodge_speed']
        elif self.frame == self.start_invuln_frame:
            actor.createMask([255,255,255], 22, True, 24)
            actor.invulnerable = self.end_invuln_frame-self.start_invuln_frame
        elif self.frame == self.end_invuln_frame:
            actor.flip()
            actor.change_x = 0
        elif self.frame == self.last_frame:
            if 'shield' in actor.keys_held:
                actor.doShield()
            else:
                actor.doAction('NeutralAction')
        self.frame += 1

class BackwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 50)
        
    def setUp(self,actor):
        self.start_invuln_frame = 6
        self.end_invuln_frame = 34
        if self.sprite_name=="": self.sprite_name ="backwardRoll"
        action.Action.setUp(self, actor)

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_xspeed = 0
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self, actor):
        if actor.grounded is False:
            actor.doAction('Fall')
        if self.frame == 1:
            actor.change_x = actor.facing * -actor.var['dodge_speed']
        elif self.frame == self.start_invuln_frame:
            actor.createMask([255,255,255], 22, True, 24)
            actor.invulnerable = self.end_invuln_frame-self.start_invuln_frame
        elif self.frame == self.end_invuln_frame:
            actor.change_x = 0
        elif self.frame == self.last_frame:
            if 'shield' in actor.keys_held:
                actor.doShield()
            else:
                actor.doAction('NeutralAction')
        self.frame += 1
        
class SpotDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        
    def setUp(self,actor):
        self.start_invuln_frame = 4
        self.end_invuln_frame = 20
        if self.sprite_name=="": self.sprite_name ="spotDodge"
        action.Action.setUp(self, actor)

    def tearDown(self, actor, nextAction):
        action.Action.tearDown(self, actor, nextAction)
        actor.preferred_xspeed = 0
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        if actor.grounded is False:
            actor.doAction('Fall')
        actor.mask = None
        
    def update(self,actor):
        action.Action.update(self, actor)
        if actor.keyBuffered('down', 1) and self.frame > 0:
            blocks = actor.checkGround()
            if blocks:
                blocks = map(lambda x:x.solid,blocks)
                if not any(blocks):
                    actor.doAction('PlatformDrop')
        if self.frame == 1:
            actor.change_x = 0
        elif self.frame == self.start_invuln_frame:
            actor.createMask([255,255,255],16,True,24)
            actor.invulnerable = self.end_invuln_frame - self.start_invuln_frame
        elif self.frame == self.end_invuln_frame:
            pass
        elif self.frame == self.last_frame:
            if 'shield' in actor.keys_held:
                actor.doShield()
            else:
                actor.doAction('NeutralAction')
        self.frame += 1
        
class AirDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        
    def setUp(self,actor):
        if self.sprite_name=="": self.sprite_name ="airDodge"
        action.Action.setUp(self, actor)
        self.start_invuln_frame = 4
        self.end_invuln_frame = 20
        self.move_vec = [0,0]
        
        if settingsManager.getSetting('enableWavedash'):
            actor.updateLandingLag(actor.var['wavedash_lag'])
        else:
            actor.updateLandingLag(20)
        if settingsManager.getSetting('airDodgeType') == 'directional':
            self.move_vec = actor.getSmoothedInput()
            actor.change_x = self.move_vec[0]*actor.var['dodge_speed']
            actor.change_y = self.move_vec[1]*actor.var['dodge_speed']
        
    def tearDown(self,actor,nextAction):
        action.Action.tearDown(self, actor, nextAction)
        if settingsManager.getSetting('airDodgeType') == 'directional':
            actor.preferred_yspeed = actor.var['max_fall_speed']
            actor.preferred_xspeed = 0
        if actor.mask: actor.mask = None
        if actor.invulnerable > 0:
            actor.invulnerable = 0
    
    def stateTransitions(self, actor):
        if actor.grounded:
            if not settingsManager.getSetting('enableWavedash'):
                actor.change_x = 0
            actor.doAction('Land')
                
    def update(self,actor):
        action.Action.update(self, actor)
        if settingsManager.getSetting('airDodgeType') == 'directional':
            if self.frame == 0:
                actor.preferred_xspeed = actor.change_x
                actor.preferred_yspeed = actor.change_y
            elif self.frame >= 16:
                actor.change_x = 0
                actor.change_y = 0
                actor.preferred_xspeed = 0
                actor.preferred_yspeed = 0
            elif self.frame == self.last_frame:
                actor.preferred_yspeed = actor.var['max_fall_speed']
                
        if self.frame == self.start_invuln_frame:
            actor.createMask([255,255,255],16,True,24)
            actor.invulnerable = self.end_invuln_frame-self.start_invuln_frame
        elif self.frame == self.start_invuln_frame+2:
            actor.updateLandingLag(20)
        elif self.frame == self.end_invuln_frame:
            actor.landing_lag = 20
        elif self.frame == self.last_frame:
            if settingsManager.getSetting('freeDodgeSpecialFall'):
                actor.doAction('Helpless')
            else:
                actor.doAction('Fall')
        self.frame += 1
        
class LedgeGrab(action.Action):
    def __init__(self,ledge=None):
        action.Action.__init__(self, 1)
        self.ledge = ledge
        self.sweetspot_x = 0
        self.sweetspot_y = 0
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="ledgeGrab"
        action.Action.setUp(self, actor)
        actor.createMask([255,255,255], settingsManager.getSetting('ledgeInvincibilityTime'), True, 12)
        actor.invulnerable = settingsManager.getSetting('ledgeInvincibilityTime')
        if not hasattr(self, 'ledge'): self.ledge = None
        if not hasattr(self, 'sweetspot_x'): self.sweetspot_x = 0
        if not hasattr(self, 'sweetspot_y'): self.sweetspot_y = 0
        
    def tearDown(self,actor,nextAction):
        action.Action.tearDown(self, actor, nextAction)
        if self.ledge: self.ledge.fighterLeaves(actor)
        
    def stateTransitions(self,actor):
        ledgeState(actor)
        
    def update(self,actor):
        action.Action.update(self, actor)
    
        actor.jumps = actor.var['jumps']
        if self.ledge.side == 'left':
            if actor.facing == -1:
                actor.flip()
            actor.hurtbox.rect.right = self.ledge.rect.centerx + self.sweetspot_x
            actor.hurtbox.rect.top = self.ledge.rect.top + self.sweetspot_y
            actor.rect.center = actor.hurtbox.rect.center
        else:
            if actor.facing == 1:
                actor.flip()
            actor.hurtbox.rect.left = self.ledge.rect.centerx - self.sweetspot_x
            actor.hurtbox.rect.top = self.ledge.rect.top + self.sweetspot_y
            actor.rect.center = actor.hurtbox.rect.center
        actor.setSpeed(0, actor.getFacingDirection())
        self.frame += 1
        

class LedgeGetup(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
    
    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0
        actor.change_x = 0
        
    def setUp(self, actor):
        if self.sprite_name=="": self.sprite_name ="ledgeGetup"
        action.Action.setUp(self, actor)
        actor.invincibility = 12
    
    def update(self,actor):
        action.Action.update(self, actor)
        if self.frame == 0:
            actor.createMask([255,255,255], 12, True, 24)
        if self.frame >= self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1

########################################################
#                    ATTACK ACTIONS                    #
########################################################
class BaseAttack(action.Action):
    def __init__(self, length=1):
        action.Action.__init__(self, length)
        
    def tearDown(self, actor, nextAction):
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
    
    def onClank(self, actor):
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
                    
    def update(self, actor):
        action.Action.update(self, actor)
        if self.frame == self.last_frame:
            if actor.grounded:
                actor.doAction('NeutralAction')
            else:
                actor.doAction('Fall')
        for hitbox in self.hitboxes.values():
            hitbox.update()
        self.frame += 1

class AirAttack(BaseAttack):
    def __init__(self, length=1):
        BaseAttack.__init__(self, length)
        self.fastfall_frame = None
    
    def setUp(self, actor):
        BaseAttack.setUp(self, actor)
        if not hasattr(self, 'fastfall_frame'):
            self.fastfall_frame = None
    
    def onClank(self, actor):
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
                    
    def stateTransitions(self, actor):
        if self.fastfall_frame is not None and self.frame >= self.fastfall_frame:
            if actor.keysContain('down'):
                actor.platform_phase = 1
                actor.calcGrav(actor.var['fastfall_multiplier'])
        if actor.grounded and actor.ground_elasticity == 0:
            actor.preferred_xspeed = 0
            actor.preferred_yspeed = actor.var['max_fall_speed']
            actor.doAction('Land')
                
    def update(self, actor):
        BaseAttack.update(self, actor)
            
class ChargeAttack(BaseAttack):
    def __init__(self,length=1,start_charge_frame=1,end_charge_frame=1,max_charge=0):
        BaseAttack.__init__(self, length)
        self.start_charge_frame = start_charge_frame
        self.end_charge_frame = end_charge_frame
        self.max_charge = 1
        
    def setUp(self, actor):
        self.chargeLevel = 0
        BaseAttack.setUp(self, actor)
        
    def update(self, actor):
        BaseAttack.update(self, actor)
        if self.frame == self.start_charge_frame:
            if actor.keysContain('attack') and self.chargeLevel == 0:
                actor.createMask([255,255,0],72,True,32)
        
        #Find solution for multiple hitboxes
        if self.frame == self.end_charge_frame:
            if actor.keysContain('attack') and self.chargeLevel <= self.max_charge:
                for _,hitbox in self.hitboxes.iteritems():
                    hitbox.charge()
                self.chargeLevel += 1
                self.frame = self.start_charge_frame
        
        if self.frame == (self.end_charge_frame+1):
            actor.mask = None

class BaseThrow(BaseGrabbing):
    def __init__(self,length=1):
        BaseGrabbing.__init__(self, length)
        
    def update(self, actor):
        if self.frame == self.last_frame:
            if actor.grounded: actor.doAction('NeutralAction')
            else: actor.doAction('Fall')
        BaseGrabbing.update(self, actor)          
class NeutralAttack(BaseAttack):
    def __init__(self, length=0):
        BaseAttack.__init__(self, length)
                
class ForwardAttack(BaseAttack):
    def __init__(self, length=0):
        BaseAttack.__init__(self, length)

class UpAttack(BaseAttack):
    def __init__(self, length=0):
        BaseAttack.__init__(self, length)

class DownAttack(BaseAttack):
    def __init__(self, length=0):
        BaseAttack.__init__(self, length)

class ForwardSmash(ChargeAttack):
    def __init__(self,length=0):
        ChargeAttack.__init__(self, length,0,1)
        
class UpSmash(ChargeAttack):
    def __init__(self,length=0):
        ChargeAttack.__init__(self, length,0,1)
        
class DownSmash(ChargeAttack):
    def __init__(self,length=0):
        ChargeAttack.__init__(self, length,0,1)
        
class NeutralAir(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)

class ForwardAir(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)

class BackAir(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)

class UpAir(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)

class DownAir(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)

class DashAttack(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)

class NeutralSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)
                
class NeutralGroundSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)

class NeutralAirSpecial(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)
        
class ForwardSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)
                
class ForwardGroundSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)
        
class ForwardAirSpecial(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)
        
class UpSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)
                
class UpGroundSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)
        
class UpAirSpecial(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)
        
class DownSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)
                
class DownGroundSpecial(BaseAttack):
    def __init__(self,length=0):
        BaseAttack.__init__(self, length)
    
class DownAirSpecial(AirAttack):
    def __init__(self,length=0):
        AirAttack.__init__(self, length)

class ForwardThrow(BaseThrow):
    def __init__(self,length=0):
        BaseGrabbing.__init__(self, length)

class DownThrow(BaseThrow):
    def __init__(self,length=0):
        BaseGrabbing.__init__(self, length)
       
########################################################
#               TRANSITION STATES                      #
########################################################
def neutralState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('shield'):
        actor.doShield(True)
    elif actor.keyHeld('attack'):
        actor.doGroundAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doAction('Jump')
    elif actor.keysContain('down', 0.5):
        actor.doAction('Crouch')
    elif actor.keysContain(invkey):
        actor.doGroundMove(actor.getForwardWithOffset(180))
    elif actor.keysContain(key):
        actor.doGroundMove(actor.getForwardWithOffset(0))

def crouchState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('shield'):
        if actor.keysContain(invkey):
            actor.doAction('BackwardRoll')
        elif actor.keysContain(key):
            actor.doAction('ForwardRoll')
        else:
            actor.doAction('SpotDodge')
    if actor.keyHeld('attack'):
        actor.doGroundAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doAction('Jump')
    elif not actor.keysContain('down'):
        actor.doAction('CrouchGetup')

def airState(actor):
    airControl(actor)
    if actor.keyHeld('shield'):
        actor.doAction('AirDodge')
    elif actor.keyHeld('attack'):
        actor.doAirAttack()
    elif actor.keyHeld('special'):
        actor.doAirSpecial()
    elif actor.keyHeld('jump') and actor.jumps > 0:
        actor.doAction('AirJump')
    elif actor.keysContain('down'):
        actor.platform_phase = 1
        actor.calcGrav(actor.var['fastfall_multiplier'])

def tumbleState(actor):
    airControl(actor)
    if actor.keyHeld('attack'):
        actor.doAirAttack()
    elif actor.keyHeld('special'):
        actor.doAirSpecial()
    elif actor.keyHeld('jump') and actor.jumps > 0:
        actor.doAirJump()
    elif actor.keysContain('down'):
        actor.platform_phase = 1
        actor.calcGrav(actor.var['fastfall_multiplier'])
            
def moveState(actor, direction):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('shield'):
        actor.doShield(True)
    elif actor.keyHeld('attack'):
        actor.doGroundAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doAction('Jump')
    elif actor.keysContain('down', 0.5):
        actor.doAction('Crouch')
    elif not actor.keysContain('left') and not actor.keysContain('right') and not actor.keysContain('down'):
        actor.doAction('Stop')
    elif actor.preferred_xspeed < 0 and not actor.keysContain('left',1) and actor.keysContain('right',1):
        actor.doAction('Stop')
    elif actor.preferred_xspeed > 0 and not actor.keysContain('right',1) and actor.keysContain('left',1):
        actor.doAction('Stop')

def dashState(actor, direction):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keysContain('shield') and actor.keyHeld('attack'):
        actor.doAction('DashGrab')
    elif actor.keyHeld('attack'):
        if actor.checkSmash(key):
            print("Dash cancelled into forward smash")
            actor.doAction('ForwardSmash')
        else:
            actor.doAction('DashAttack')
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doAction('Jump')
    elif actor.keysContain('down', 0.5):
        actor.doAction('Stop')
    elif not actor.keysContain('left') and not actor.keysContain('right') and not actor.keysContain('down'):
        actor.doAction('RunStop')
    elif actor.preferred_xspeed < 0 and not actor.keysContain('left',1) and actor.keysContain('right',1):
        actor.doAction('RunStop')
    elif actor.preferred_xspeed > 0 and not actor.keysContain('right',1) and actor.keysContain('left',1):
        actor.doAction('RunStop')

def jumpState(actor):
    airControl(actor)
    if actor.keyHeld('shield'):
        actor.doAction('AirDodge')
    elif actor.keyHeld('attack'):
        actor.doAirAttack()
    elif actor.keyHeld('special'):
        actor.doAirSpecial()
    elif actor.keysContain('down'):
        actor.platform_phase = 1
        actor.calcGrav(actor.var['fastfall_multiplier'])
            
def shieldState(actor):
    if actor.keyHeld('attack'):
        actor.doAction('GroundGrab')
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doAction('Jump')

def ledgeState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    actor.setSpeed(0, actor.getFacingDirection())
    if actor.keyHeld('shield'):
        actor.ledge_lock = True
        actor.doAction('LedgeRoll')
    elif actor.keyHeld('attack'):
        actor.ledge_lock = True
        actor.doAction('LedgeAttack')
    elif actor.keyHeld('jump'):
        actor.ledge_lock = True
        actor.invincible = 6
        actor.doAction('Jump')
    elif actor.keyBuffered(key):
        actor.ledge_lock = True
        actor.doAction('LedgeGetup')
    elif actor.keyBuffered(invkey):
        actor.ledge_lock = True
        actor.invincible = 6
        actor.doAction('Fall')
    elif actor.keyBuffered('down'):
        actor.ledge_lock = True
        actor.invincible = 6
        actor.doAction('Fall')

def grabbingState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    # Check to see if they broke out
    # If they did, release them
    if not actor.isGrabbing():
        actor.doAction('Release')
    elif actor.keyHeld('shield', 1):
        actor.doAction('Release')
    elif actor.keyHeld('attack', 1):
        actor.doAction('Pummel')
    elif actor.keyHeld(key):
        actor.doAction('ForwardThrow')
    elif actor.keyHeld(invkey):
        actor.doAction('BackThrow')
    elif actor.keyHeld('up'):
        actor.doAction('UpThrow')
    elif actor.keyHeld('down'):
        actor.doAction('DownThrow')

def proneState(actor):
    (key, invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('attack'):
        actor.doAction('GetupAttack')
    elif actor.keyHeld('up'):
        actor.doAction('Getup')
    elif actor.keyHeld(key):
        actor.doAction('ForwardRoll')
    elif actor.keyHeld(invkey):
        actor.doAction('BackwardRoll')
    elif actor.keyHeld('down'):
        actor.doAction('SpotDodge')

########################################################
#             BEGIN HELPER METHODS                     #
########################################################

def airControl(actor):
    (key, invkey) = actor.getForwardBackwardKeys()
    if actor.keysContain(key):
        actor.preferred_xspeed = actor.facing * actor.var['max_air_speed']
    elif actor.keysContain(invkey):
        actor.preferred_xspeed = -actor.facing * actor.var['max_air_speed']
    
    if (actor.change_x < 0) and not actor.keysContain('left'):
        actor.preferred_xspeed = 0
    if (actor.change_x > 0) and not actor.keysContain('right'):
        actor.preferred_xspeed = 0

    if not (actor.change_x < -actor.var['max_air_speed'] and actor.keysContain('left')) or not (actor.change_x > actor.var['max_air_speed'] and actor.keysContain('right')):
        actor.accel(actor.var['air_control'])

    if actor.change_y >= actor.var['max_fall_speed'] and actor.landing_lag < actor.var['heavy_land_lag']:
        actor.landing_lag = actor.var['heavy_land_lag']

    if actor.grounded and actor.ground_elasticity == 0:
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['max_fall_speed']
        actor.doAction('Land')

def helplessControl(actor):
    (key, invkey) = actor.getForwardBackwardKeys()
    if actor.keysContain(key):
        actor.preferred_xspeed = actor.facing * actor.var['max_air_speed']
    elif actor.keysContain(invkey):
        actor.preferred_xspeed = -actor.facing * actor.var['max_air_speed']
    
    if (actor.change_x < 0) and not actor.keysContain('left'):
        actor.preferred_xspeed = 0
    elif (actor.change_x > 0) and not actor.keysContain('right'):
        actor.preferred_xspeed = 0

    if not (actor.change_x < -actor.var['max_air_speed'] and actor.keysContain('left')) or not (actor.change_x > actor.var['max_air_speed'] and actor.keysContain('right')):
        actor.accel(actor.var['air_control'])

    if actor.change_y >= actor.var['max_fall_speed'] and actor.landing_lag < actor.var['heavy_land_lag']:
        actor.landing_lag = actor.var['heavy_land_lag']

    if actor.grounded and actor.ground_elasticity == 0:
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['max_fall_speed']
        actor.doAction('HelplessLand')

def hitstunLanding(actor):
    if actor.grounded and actor.ground_elasticity == 0:
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['max_fall_speed']
        actor.doAction('Land')

def grabLedges(actor):
    # Check if we're colliding with any ledges.
    if not actor.ledge_lock: #If we're not allowed to re-grab, don't bother calculating
        ledge_hit_list = pygame.sprite.spritecollide(actor, actor.game_state.platform_ledges, False)
        for ledge in ledge_hit_list:
            # Don't grab any ledges if the actor is holding down
            if actor.keysContain('down') is False:
                # If the ledge is on the left side of a platform, and we're holding right
                if ledge.side == 'left' and actor.keysContain('right'):
                    ledge.fighterGrabs(actor)
                elif ledge.side == 'right' and actor.keysContain('left'):
                    ledge.fighterGrabs(actor)
                    

stateDict = {
            "neutralState": neutralState,
            "crouchState": crouchState,
            "airState": airState,
            "moveState": moveState,
            "dashState": dashState,
            "jumpState": jumpState,
            "shieldState": shieldState,
            "ledgeState": ledgeState,
            "grabbingState": grabbingState,
            "proneState": proneState,
            "airControl": airControl,
            "helplessControl": helplessControl,
            "hitstunLanding": hitstunLanding,
            "grabLedges": grabLedges     
            }
