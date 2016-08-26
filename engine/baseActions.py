import engine.action as action
import engine.hitbox as hitbox
import engine.article as article
import pygame
import math
import random
import settingsManager

class Move(action.Action):
    def __init__(self,_length=0):
        action.Action.__init__(self,_length) 
        
    def setUp(self,_actor):
        if self.sprite_name=="": self.sprite_name = "move"
        action.Action.setUp(self, _actor)
        self.accel = True
        self.direction = _actor.facing
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        checkGrounded(_actor)
        _actor.preferred_xspeed = _actor.var['max_ground_speed']*self.direction
        _actor.accel(_actor.var['static_grip'])

        (key,invkey) = _actor.getForwardBackwardKeys()
        if self.direction == _actor.facing:
            if _actor.keysContain(invkey):
                _actor.flip()
        else:
            if not _actor.keysContain(key):
                _actor.flip()
        
        self.frame += 1
        
        if self.frame > self.last_frame: self.frame = 0
        
    def stateTransitions(self,_actor):
        moveState(_actor,self.direction)
        (key,invkey) = _actor.getForwardBackwardKeys()
        if self.frame > 0 and _actor.keyBuffered(invkey, _state = 1):
            _actor.doDash(-_actor.getFacingDirection())
        elif self.frame > 0 and _actor.keyBuffered(key, _state = 1):
            _actor.doDash(_actor.getFacingDirection())

class Dash(action.Action):
    def __init__(self,_length=1,_runStartFrame=0): 
        action.Action.__init__(self,_length)
        self.run_start_frame = _runStartFrame
        
    def setUp(self,_actor):
        if self.sprite_name=="": self.sprite_name = "dash"
        action.Action.setUp(self, _actor)
        self.pivoted = False
        if _actor.facing == 1: self.direction = 1
        else: self.direction = -1

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0

    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.preferred_xspeed = _actor.var['run_speed']*self.direction
        (key,invkey) = _actor.getForwardBackwardKeys()
        checkGrounded(_actor)
        if not self.pivoted:
            if _actor.keysContain(invkey) and _actor.change_x != _actor.var['run_speed']*self.direction:
                _actor.flip() #Do the moonwalk!
                self.pivoted = True
        _actor.accel(_actor.var['static_grip'])

        self.frame += 1
        
        if self.frame > self.last_frame: 
            self.frame = self.run_start_frame
            
    def stateTransitions(self,_actor):
        dashState(_actor,self.direction)
        
class Pivot(action.Action):
    def __init__(self,_length=0):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name = "pivot"
        action.Action.setUp(self, _actor)
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if isinstance(_nextAction, Move):
            _nextAction.accel = False

    def stateTransitions(self, _actor):
        if _actor.keyHeld('shield'):
            _actor.doAction('Shield')
        elif _actor.keyHeld('attack'):
            if _actor.keysContain('shield'):
                _actor.doAction('GroundGrab')
            else:
                _actor.doGroundAttack()
        elif _actor.keyHeld('special'):
            _actor.doGroundSpecial()
        else:
            stopState(_actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        _actor.accel(_actor.var['pivot_grip'])
        if self.frame == 0:
            _actor.flip()
        checkGrounded(_actor)
        if self.frame != self.last_frame:
            self.frame += 1
            _actor.preferred_xspeed = 0
        if self.frame == self.last_frame:
            (key, _) = _actor.getForwardBackwardKeys()
            if _actor.keysContain(key):
                if _actor.keyHeld(key, max(min(int(_actor.key_bindings.timing_window['repeat_window'])+1, _actor.last_input_frame), 1), 1, 0):
                    if _actor.facing == 1:
                        _actor.doDash(0)
                    else:
                        _actor.doDash(180)
                else:
                    if _actor.facing == 1:
                        _actor.doGroundMove(0)
                    else:
                        _actor.doGroundMove(180)
            else:
                _actor.doAction('NeutralAction')
          
class Stop(action.Action):
    def __init__(self,_length=0):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name = "stop"
        action.Action.setUp(self, _actor)
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        #print(self.frame,_actor.sprite.index)
        _actor.preferred_xspeed = 0
        checkGrounded(_actor)
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1
        
    def stateTransitions(self, _actor):
        stopState(_actor)

    def tearDown(self, _actor, nextAction):
        action.Action.tearDown(self, _actor, nextAction)
        _actor.accel(_actor.var['static_grip'])
        if isinstance(nextAction, Pivot):
            nextAction.frame = self.frame
            print(self.frame)
        
class RunPivot(action.Action):
    def __init__(self,length=0):
        action.Action.__init__(self, length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="runPivot" 
        action.Action.setUp(self, _actor)
        _actor.flip()
        
    def tearDown(self, _actor, nextAction):
        action.Action.tearDown(self, _actor, nextAction)
        _actor.preferred_xspeed = 0
        #_actor.flip()
        if isinstance(nextAction, Dash):
            nextAction.accel = False
        
    def stateTransitions(self, _actor):
        if _actor.keyHeld('shield'):
            _actor.doAction('ForwardRoll')
        if _actor.keyHeld('attack'):
            if _actor.keysContain('shield'):
                _actor.doAction('DashGrab')
            else:
                _actor.doAction('DashAttack')
        elif _actor.keyHeld('special'):
            _actor.doGroundSpecial()
        else:
            runStopState(_actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if _actor.grounded is False:
            _actor.doAction('Fall')
        _actor.accel(_actor.var['static_grip'])
        checkGrounded(_actor)
        if self.frame != self.last_frame:
            self.frame += 1
            _actor.preferred_xspeed = _actor.var['run_speed']*_actor.facing
        if self.frame == self.last_frame:
            (key, _) = _actor.getForwardBackwardKeys()
            if _actor.keysContain(key):
                if _actor.facing == 1:
                    _actor.doDash(0)
                else:
                    _actor.doDash(180)
            else:
                _actor.doAction('NeutralAction')

class RunStop(action.Action):
    def __init__(self,_length=0):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="runStop"
        action.Action.setUp(self, _actor)
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        _actor.preferred_xspeed = 0
        checkGrounded(_actor)
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1
        
    def stateTransitions(self, _actor):
        runStopState(_actor)

                
class NeutralAction(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="neutralAction"
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        checkGrounded(_actor)
        neutralState(_actor)
    
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == self.last_frame:
            self.frame = 0
        self.frame += 1

class Respawn(action.Action):
    def __init__(self,_length=480):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="neutralAction"
        action.Action.setUp(self, _actor)
        self.respawn_article = article.RespawnPlatformArticle(_actor)
        
    def stateTransitions(self, _actor):
        if self.frame > 120:
            neutralState(_actor)
    
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.respawn_invincibility = 120
        self.respawn_article.kill()
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        _actor.ground = True
        _actor.change_y = 0
        if self.frame == 0:
            _actor.articles.add(self.respawn_article)
        if self.frame == self.last_frame:
            _actor.doAction('Fall')
        self.frame += 1
        
class Crouch(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="crouch"
        action.Action.setUp(self, _actor)
        self.direction = _actor.getForwardWithOffset(0)

    def stateTransitions(self, _actor):
        crouchState(_actor)
        if self.frame > 0 and _actor.keyBuffered('down', _state = 1):
            blocks = _actor.checkGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    _actor.doAction('PlatformDrop')

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0

    def update(self, _actor):
        action.Action.update(self, _actor)
        _actor.accel(_actor.var['pivot_grip'])
        (key, invkey) = _actor.getForwardBackwardKeys()
        checkGrounded(_actor)
        if _actor.keysContain(key):
            _actor.preferred_xspeed = _actor.var['crawl_speed']*_actor.facing
        elif _actor.keysContain(invkey):
            _actor.preferred_xspeed = -_actor.var['crawl_speed']*_actor.facing
        else:
            _actor.preferred_xspeed = 0
        
        self.frame += 1

class CrouchGetup(action.Action):
    def __init__(self,_length=0):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="crouchGetup"
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        if _actor.keyBuffered('down', _state = 1):
            blocks = _actor.checkGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    _actor.doAction('PlatformDrop')

    def update(self, _actor):
        action.Action.update(self, _actor)
        _actor.preferred_xspeed = 0
        checkGrounded(_actor)
        self.frame += 1
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')

########################################################
#                  Grab Actions                        #
########################################################
class BaseGrabbing(action.Action):
    def __init__(self,_length=0):
        action.Action.__init__(self, _length)
        self.hold_point = (0,0)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="baseGrabbing"
        action.Action.setUp(self, _actor)
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if not isinstance(_nextAction, BaseGrabbing) and _actor.isGrabbing():
            _actor.grabbing.doReleased()

    def update(self, _actor):
        action.Action.update(self, _actor)
        self.frame += 1

class Grabbing(BaseGrabbing):
    def __init__(self,_length=0):
        BaseGrabbing.__init__(self, _length)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="grabbing"
        action.Action.setUp(self, _actor)
        _actor.grabbing.flinch_damage_threshold = 9999

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.grabbing.flinch_damage_threshold = 0

    def stateTransitions(self, _actor):
        grabbingState(_actor)

    def update(self, _actor):
        BaseGrabbing.update(self, _actor)
        checkGrounded(_actor)
        
class HitStun(action.Action):
    def __init__(self,_hitstun=1,_direction=0):
        action.Action.__init__(self, _hitstun)
        self.direction = _direction

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="hitStun"
        action.Action.setUp(self, _actor)
        self.tech_cooldown = 5
        _actor.elasticity = _actor.var['hitstun_elasticity']
        
    def stateTransitions(self, _actor):
        (direct,_) = _actor.getDirectionMagnitude()
        if _actor.keyBuffered('shield', 1) and self.tech_cooldown == 0 and not _actor.grounded:
            print('Try tech')
            _actor.tech_window = 7
            self.tech_cooldown = 40
        _actor.elasticity = _actor.var['hitstun_elasticity']
        if self.frame > 2:
            if self.frame < self.last_frame and _actor.change_y >= _actor.var['max_fall_speed']: 
                _actor.ground_elasticity = _actor.var['hitstun_elasticity']
            elif abs(_actor.change_x) > _actor.var['run_speed']: #Skid trip
                _actor.ground_elasticity = 0
                if _actor.grounded:
                    _actor.doAction('Prone')
            elif _actor.change_y < _actor.var['max_fall_speed']/2.0: 
                _actor.ground_elasticity = 0
                if self.last_frame > 10:
                    if _actor.grounded: 
                        _actor.doAction('Prone')
                else:
                    _actor.landing_lag = _actor.var['heavy_land_lag']
                    hitstunLanding(_actor)
            else: 
                _actor.ground_elasticity = _actor.var['hitstun_elasticity']/2
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if not isinstance(_nextAction, Tumble):
            _actor.elasticity = 0
            _actor.ground_elasticity = 0
            _actor.tech_window = 0
            _actor.unRotate()
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.tech_cooldown > 0: self.tech_cooldown -= 1
        
        if self.frame == 0:
            (direct,mag) = _actor.getDirectionMagnitude()
            print("direction:", direct)
            if direct != 0 and direct != 180:
                _actor.grounded = False
                if mag > 10:
                    _actor.rotateSprite(self.direction)
            
        if self.frame % max(1,int(100.0/max(math.hypot(_actor.change_x, _actor.change_y), 1))) == 0 and self.frame < self.last_frame:
            art = article.HitArticle(_actor, _actor.rect.center, 1, math.degrees(math.atan2(_actor.change_y, -_actor.change_x))+random.randrange(-30, 30), .5*math.hypot(_actor.change_x, _actor.change_y), 0.5)
            #if _actor.hit_tagged and hasattr(_actor.hit_tagged, 'player_num'):
            #    art.recolor(art.image, [0,0,0], pygame.Color(settingsManager.getSetting('playerColor' + str(_actor.hit_tagged.player_num))))
            _actor.articles.add(art)
                    
        if self.frame == self.last_frame:
            _actor.doAction('Tumble')

        self.frame += 1

class Tumble(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="tumble"
        action.Action.setUp(self, _actor)    
        self.tech_cooldown = 0
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        tumbleState(_actor)
        
        (direct,_) = _actor.getDirectionMagnitude()

        _actor.elasticity = _actor.var['hitstun_elasticity']/2
        
        if _actor.keyBuffered('shield', 1) and self.tech_cooldown == 0 and not _actor.grounded:
            print('Try tech')
            _actor.tech_window = 20
            self.tech_cooldown = 40
            
        if _actor.change_y >= _actor.var['max_fall_speed']:#Hard landing during tumble
            _actor.ground_elasticity = _actor.var['hitstun_elasticity']/2
        elif _actor.change_y < _actor.var['max_fall_speed']/2.0: #Soft landing during tumble
            _actor.ground_elasticity = 0
            if _actor.grounded: 
                _actor.doAction('Prone')
        else: #Firm landing during tumble
            _actor.ground_elasticity = 0
            if _actor.grounded: 
                _actor.doAction('Prone')
    
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.elasticity = 0
        _actor.ground_elasticity = 0
        _actor.tech_window = 0
        _actor.unRotate()
        _actor.preferred_xspeed = 0
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        _actor.rotateSprite((_actor.sprite.angle+90)+2)
        if self.tech_cooldown > 0: self.tech_cooldown -= 1
        
class Prone(action.Action):
    def __init__(self,_length=40):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name == "": self.sprite_name = "prone"
        action.Action.setUp(self, _actor)

        ground_blocks = _actor.checkGround()
        block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, ground_blocks, None)
        if not block is None:
            _actor.change_y = block.change_y

        _actor.rect.bottom = _actor.ecb.current_ecb.rect.bottom
        _actor.unRotate()
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        if not _actor.grounded:
            _actor.doAction('Tumble')
        if self.frame == self.last_frame:
            _actor.doAction('Getup')
        self.frame += 1
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.frame >= self.last_frame-2:
            proneState(_actor)

class Getup(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="getup"
        action.Action.setUp(self, _actor)
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        checkGrounded(_actor)
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1
        
"""
@ai-move-up
@ai-move-stop
"""
class Jump(action.Action):
    def __init__(self,_length=0,_jumpFrame=0):
        action.Action.__init__(self, _length)
        self.jump_frame = _jumpFrame
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="jump"
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        if _actor.keyHeld('attack') and _actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up smash")
            _actor.doAction('UpSmash')
        elif _actor.keyHeld('special') and _actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up special")
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpGroundSpecial')
        elif self.frame > self.jump_frame:
            jumpState(_actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == self.jump_frame:
            _actor.grounded = False
            if _actor.keysContain('jump'):
                _actor.change_y = -_actor.var['jump_height']
            else: _actor.change_y = -_actor.var['short_hop_height']
            if _actor.change_x > _actor.var['aerial_transition_speed']:
                _actor.change_x = _actor.var['aerial_transition_speed']
            elif _actor.change_x < -_actor.var['aerial_transition_speed']:
                _actor.change_x = -_actor.var['aerial_transition_speed']
        if self.frame < self.last_frame:
            self.frame += 1
        if self.frame == self.last_frame and not _actor.keysContain('jump'):
            _actor.doAction('Fall')

class AirJump(action.Action):
    def __init__(self,_length=0,_jumpFrame=0):
        action.Action.__init__(self, _length)
        self.jump_frame = _jumpFrame
        #TODO: Change to add the number of buffer frames
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="airjump"
        action.Action.setUp(self, _actor)

    def stateTransitions(self, _actor):
        if _actor.keyHeld('attack') and _actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up aerial")
            _actor.doAction('UpAir')
        elif _actor.keyHeld('special') and _actor.checkSmash('up') and self.frame < self.jump_frame:
            print("Jump cancelled into up special")
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpAirSpecial')
        else: 
            jumpState(_actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame < self.jump_frame:
            _actor.change_y = 0
            _actor.preferred_yspeed = 0
        if self.frame == self.jump_frame:
            _actor.grounded = False
            _actor.change_y = -_actor.var['air_jump_height']
            _actor.jumps -= 1
            if _actor.keysContain('left') and _actor.facing == 1:
                _actor.flip()
                _actor.change_x = _actor.facing * _actor.var['max_air_speed']
            elif _actor.keysContain('right') and _actor.facing == -1:
                _actor.flip()
                _actor.change_x = _actor.facing * _actor.var['max_air_speed']
        if self.frame < self.last_frame:
            self.frame += 1
        if self.frame == self.last_frame:
            _actor.doAction('Fall')
        
class Fall(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="fall"
        action.Action.setUp(self, _actor)
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
    
    def stateTransitions(self,_actor):
        airState(_actor)
        grabLedges(_actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        _actor.grounded = False
        self.frame += 1

class Helpless(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="helpless"
        action.Action.setUp(self, _actor)
    
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.mask = None
        
    def stateTransitions(self, _actor):
        helplessControl(_actor)
        grabLedges(_actor)

    def update(self, _actor):
        _actor.grounded = False
        if self.frame == 0:
            _actor.createMask([191, 63, 191], 99999, True, 16)
        self.frame += 1
            
class Land(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="land"
        action.Action.setUp(self, _actor)
        _actor.unRotate()

        ground_blocks = _actor.checkGround()
        block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, ground_blocks, None)
        if not block is None:
            _actor.change_y = block.change_y
        #_actor.rect.bottom = _actor.ecb.current_ecb.rect.bottom


    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        #_actor.preferred_xspeed = 0

    def update(self,_actor):
        action.Action.update(self, _actor)
        #_actor.rect.bottom = _actor.ecb.current_ecb.rect.bottom
        if self.frame == 0:
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            self.last_frame = _actor.landing_lag
            if _actor.keyHeld('shield', 1) and not _actor.keyBuffered('shield', 20, 0.1, 1):
                print("l-cancel")
                self.last_frame = self.last_frame // 2

        if self.frame == 1:
            #_actor.articles.add(article.LandingArticle(_actor)) #this looks awful don't try it
            pass
        if self.frame == self.last_frame:
            _actor.landing_lag = 0
            _actor.doAction('NeutralAction')
            _actor.platform_phase = 0
            _actor.preferred_xspeed = 0
        self.frame+= 1

class HelplessLand(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="helplessLand"
        action.Action.setUp(self, _actor)
        #_actor.rect.bottom = _actor.ecb.current_ecb.rect.bottom


    def update(self,_actor):
        action.Action.update(self, _actor)
        #_actor.rect.bottom = _actor.ecb.current_ecb.rect.bottom
        if self.frame == 0:
            _actor.change_y = 0
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            self.last_frame = _actor.landing_lag
        if self.frame >= self.last_frame:
            _actor.landing_lag = 0
            _actor.doAction('NeutralAction')
            _actor.platform_phase = 0
            _actor.preferred_xspeed = 0
        self.frame += 1

class PlatformDrop(action.Action):
    def __init__(self, _length=1, _phaseFrame=1, _phaseLength=1):
        action.Action.__init__(self, _length)
        self.phase_frame = _phaseFrame
        self.phase_length = _phaseLength
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="platformDrop"
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        if _actor.keyHeld('attack') and _actor.checkSmash('down') and self.frame < self.phase_frame:
            print("Platform drop cancelled into down smash")
            _actor.doAction('DownSmash')
        elif _actor.keyHeld('special') and _actor.checkSmash('down') and self.frame < self.phase_frame:
            print("Platform drop cancelled into down special")
            if self.hasAction('DownSpecial'):
                self.doAction('DownSpecial')
            else:
                self.doAction('DownGroundSpecial')
        if self.frame > self.phase_frame:
            tapReversible(_actor)
            airControl(_actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == self.phase_frame:
            _actor.platform_phase = self.phase_length
        if self.frame == self.last_frame:
            _actor.doAction('Fall')
        self.frame += 1


class Shield(action.Action):
    def __init__(self, _newShield=True):
        action.Action.__init__(self, 8)
        self.new_shield = _newShield
   
    def setUp(self, _actor):
        if not hasattr(self, 'new_shield'):
            self.new_shield = True
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        shieldState(_actor)
   
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if not isinstance(_nextAction, ShieldStun):
            _actor.shield = False
       
    def update(self, _actor):
        if _actor.grounded is False:
            _actor.shield = False
            _actor.doAction('Fall')
        if self.frame == 0:
            _actor.shield = True
            if self.new_shield:
                _actor.startShield()
            if _actor.keysContain('shield'):
                self.frame += 1
            else:
                self.frame += 2
        elif self.frame == 1:
            if not _actor.keysContain('shield'):
                self.frame += 1
        elif self.frame >= 2 and self.frame < self.last_frame:
            _actor.shield = False
            self.frame += 1
        elif self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')
        else: self.frame += 1

class ShieldStun(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="shieldStun"
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if not isinstance(_nextAction, Shield) and not isinstance(_nextAction, ShieldStun):
            _actor.shield = False

    def update(self, _actor):
        if _actor.grounded is False:
            _actor.shield = False
            _actor.doAction('Fall')
        if self.frame >= self.last_frame and _actor.keysContain('shield'):
            _actor.doShield(False)
        elif self.frame >= self.last_frame:
            _actor.landing_lag = 6
            _actor.doAction('Land')
        self.frame += 1

class Stunned(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        if self.sprite_name=="": self.sprite_name ="stunned"
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="stunned"
        action.Action.setUp(self, _actor)
    
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)    
        _actor.mask = None
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.createMask([255, 0, 255], 99999, True, 8)
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1

class Trapped(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        self.time = 0
        self.held_time = 0
        self.last_position = [0,0]
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="trapped"
        action.Action.setUp(self, _actor)
        self.last_position = [0,0]
        self.held_time = 0
        self.time = 0
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        new_position = _actor.getSmoothedInput()
        cross = new_position[0]*self.last_position[1]-new_position[1]*self.last_position[0]
        self.held_time += (cross**2)*4
        if self.held_time >= 1:
            self.frame += int(self.held_time)
            self.held_time -= int(self.held_time)
        self.last_position = new_position
        if self.frame >= self.last_frame:
            _actor.doAction('Released')
        # Throws and other grabber-controlled releases are the grabber's responsibility
        # Also, the grabber should always check to see if the grabbee is still under grab
        self.frame += 1
        self.time += 1
        print(self.frame, self.time)

class Grabbed(Trapped):
    def __init__(self,_height=1):
        Trapped.__init__(self, 40)
        self.height = _height
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="grabbed"
        Trapped.setUp(self, _actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            self.last_frame = 40 + _actor.damage//2
        if (self.height > _actor.rect.height):
            _actor.rect.top = _actor.grabbed_by.rect.bottom-self.height
        else:
            _actor.rect.bottom = _actor.grabbed_by.rect.bottom
        _actor.rect.centerx = _actor.grabbed_by.rect.centerx+_actor.grabbed_by.facing*_actor.grabbed_by.rect.width/2.0
        Trapped.update(self, _actor)

class Release(action.Action):
    def __init__(self, _height=30):
        action.Action.__init__(self, 15)
        self.height = _height
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="release"
        action.Action.setUp(self, _actor)
        
    def update(self, _actor):
        checkGrounded(_actor)
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1

class Released(action.Action):
    def __init__(self):
        action.Action.__init__(self, 15)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="released"
        action.Action.setUp(self, _actor)
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
    
    def stateTransitions(self,_actor):
        tapReversible(_actor)

        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keysContain(key):
            _actor.preferred_xspeed = _actor.facing * _actor.var['max_air_speed']
        elif _actor.keysContain(invkey):
            _actor.preferred_xspeed = -_actor.facing * _actor.var['max_air_speed']
    
        if (_actor.change_x < 0) and not _actor.keysContain('left'):
            _actor.preferred_xspeed = 0
        elif (_actor.change_x > 0) and not _actor.keysContain('right'):
            _actor.preferred_xspeed = 0

        if _actor.change_y >= _actor.var['max_fall_speed'] and _actor.landing_lag < _actor.var['heavy_land_lag']:
            _actor.landing_lag = _actor.var['heavy_land_lag']

        if _actor.grounded and _actor.ground_elasticity == 0:
            _actor.preferred_xspeed = 0
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            _actor.doAction('Prone')
            _actor.current_action.last_frame = self.last_frame - self.frame

        grabLedges(_actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame >= self.last_frame:
            _actor.doAction('Fall')
        self.frame += 1
        
class ForwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 46)
        
    def setUp(self, _actor):
        self.start_invuln_frame = 6
        self.end_invuln_frame = 34
        if self.sprite_name=="": self.sprite_name ="forwardRoll"
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        if _actor.invulnerable > 0:
            _actor.invulnerable = 0
        _actor.mask = None
        
    def update(self, _actor):
        action.Action.update(self,_actor)
        if _actor.keyHeld('attack') and self.frame < 8:
            _actor.doAction('DashGrab')
        if _actor.grounded is False:
            _actor.doAction('Fall')
        if self.frame == 1:
            _actor.change_x = _actor.facing * _actor.var['dodge_speed']
        elif self.frame == self.start_invuln_frame:
            _actor.createMask([255,255,255], 22, True, 24)
            _actor.invulnerable = self.end_invuln_frame-self.start_invuln_frame
        elif self.frame == self.end_invuln_frame:
            _actor.flip()
            _actor.change_x = 0
        elif self.frame == self.last_frame:
            if 'shield' in _actor.keys_held:
                _actor.doShield()
            else:
                _actor.doAction('NeutralAction')
        self.frame += 1

class BackwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 50)
        
    def setUp(self,_actor):
        self.start_invuln_frame = 6
        self.end_invuln_frame = 34
        if self.sprite_name=="": self.sprite_name ="backwardRoll"
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        if _actor.invulnerable > 0:
            _actor.invulnerable = 0
        _actor.mask = None
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        if _actor.keyHeld('attack') and self.frame < 8:
            _actor.doAction('GroundGrab')
        if _actor.grounded is False:
            _actor.doAction('Fall')
        if self.frame == 1:
            _actor.change_x = _actor.facing * -_actor.var['dodge_speed']
        elif self.frame == self.start_invuln_frame:
            _actor.createMask([255,255,255], 22, True, 24)
            _actor.invulnerable = self.end_invuln_frame-self.start_invuln_frame
        elif self.frame == self.end_invuln_frame:
            _actor.change_x = 0
        elif self.frame == self.last_frame:
            if 'shield' in _actor.keys_held:
                _actor.doShield()
            else:
                _actor.doAction('NeutralAction')
        self.frame += 1
        
class SpotDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        
    def setUp(self,_actor):
        self.start_invuln_frame = 4
        self.end_invuln_frame = 20
        if self.sprite_name=="": self.sprite_name ="spotDodge"
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        if _actor.invulnerable > 0:
            _actor.invulnerable = 0
        if _actor.grounded is False:
            _actor.doAction('Fall')
        _actor.mask = None
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if _actor.keyBuffered('down', 1) and self.frame > 0:
            blocks = _actor.checkGround()
            if blocks:
                blocks = map(lambda x:x.solid,blocks)
                if not any(blocks):
                    _actor.doAction('PlatformDrop')
        if self.frame == 1:
            _actor.change_x = 0
        elif self.frame == self.start_invuln_frame:
            _actor.createMask([255,255,255],16,True,24)
            _actor.invulnerable = self.end_invuln_frame - self.start_invuln_frame
        elif self.frame == self.end_invuln_frame:
            pass
        elif self.frame == self.last_frame:
            if 'shield' in _actor.keys_held:
                _actor.doShield()
            else:
                _actor.doAction('NeutralAction')
        self.frame += 1
        
class AirDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        
    def setUp(self,_actor):
        if self.sprite_name=="": self.sprite_name ="airDodge"
        action.Action.setUp(self, _actor)
        self.start_invuln_frame = 4
        self.end_invuln_frame = 20
        self.wavedash_lag = 8
        self.move_vec = [0,0]
        
        if settingsManager.getSetting('airDodgeType') == 'directional':
            self.move_vec = _actor.getSmoothedInput(int(_actor.key_bindings.timing_window['smoothing_window']))
            _actor.change_x = self.move_vec[0]*_actor.var['dodge_speed']
            _actor.change_y = self.move_vec[1]*_actor.var['dodge_speed']
        
    def tearDown(self,_actor,_nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if settingsManager.getSetting('airDodgeType') == 'directional':
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            _actor.preferred_xspeed = 0
        if _actor.mask: _actor.mask = None
        if _actor.invulnerable > 0:
            _actor.invulnerable = 0
    
    def stateTransitions(self, _actor):
        if self.frame == 0:
            if settingsManager.getSetting('enableWavedash'):
                _actor.updateLandingLag(self.wavedash_lag)
            else:
                _actor.updateLandingLag(20)
        if _actor.grounded:
            if not settingsManager.getSetting('enableWavedash'):
                _actor.change_x = 0
            _actor.doAction('Land')
                
    def update(self,_actor):
        action.Action.update(self, _actor)
        if settingsManager.getSetting('airDodgeType') == 'directional':
            if self.frame == 0:
                _actor.preferred_xspeed = _actor.change_x
                _actor.preferred_yspeed = _actor.change_y
            elif self.frame >= self.end_invuln_frame:
                _actor.change_x = 0
                _actor.change_y = 0
                _actor.preferred_xspeed = 0
                _actor.preferred_yspeed = 0
            elif self.frame == self.last_frame:
                _actor.preferred_yspeed = _actor.var['max_fall_speed']

        if self.frame == 6:
            _actor.updateLandingLag(20)
        if self.frame == self.start_invuln_frame:
            (key, invkey) = _actor.getForwardBackwardKeys()
            if _actor.keysContain(invkey, 1):
                _actor.flip()
            _actor.createMask([255,255,255],self.end_invuln_frame-self.start_invuln_frame,True,24)
            _actor.invulnerable = self.end_invuln_frame-self.start_invuln_frame
        elif self.frame == self.end_invuln_frame:
            _actor.landing_lag = 20
        elif self.frame == self.last_frame:
            if settingsManager.getSetting('freeDodgeSpecialFall'):
                _actor.doAction('Helpless')
            else:
                _actor.doAction('Fall')
        self.frame += 1
        
class LedgeGrab(action.Action):
    def __init__(self,_ledge=None):
        action.Action.__init__(self, 1)
        self.ledge = _ledge
        self.sweetspot_x = 0
        self.sweetspot_y = 0
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="ledgeGrab"
        action.Action.setUp(self, _actor)
        _actor.createMask([255,255,255], settingsManager.getSetting('ledgeInvincibilityTime'), True, 12)
        _actor.invulnerable = settingsManager.getSetting('ledgeInvincibilityTime')
        if not hasattr(self, 'ledge'): self.ledge = None
        if not hasattr(self, 'sweetspot_x'): self.sweetspot_x = 0
        if not hasattr(self, 'sweetspot_y'): self.sweetspot_y = 0
        
    def tearDown(self,_actor,_nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if self.ledge: self.ledge.fighterLeaves(_actor)
        
    def stateTransitions(self,_actor):
        ledgeState(_actor)
        
    def update(self,_actor):
        action.Action.update(self, _actor)
    
        _actor.jumps = _actor.var['jumps']
        if self.ledge.side == 'left':
            if _actor.facing == -1:
                _actor.flip()
            _actor.hurtbox.rect.right = self.ledge.rect.centerx + self.sweetspot_x
            _actor.hurtbox.rect.top = self.ledge.rect.top + self.sweetspot_y
            _actor.rect.center = _actor.hurtbox.rect.center
        else:
            if _actor.facing == 1:
                _actor.flip()
            _actor.hurtbox.rect.left = self.ledge.rect.centerx - self.sweetspot_x
            _actor.hurtbox.rect.top = self.ledge.rect.top + self.sweetspot_y
            _actor.rect.center = _actor.hurtbox.rect.center
        _actor.setSpeed(0, _actor.getFacingDirection())
        self.frame += 1
        

class LedgeGetup(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
    
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        _actor.change_x = 0
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="ledgeGetup"
        action.Action.setUp(self, _actor)
        _actor.invincibility = 12
    
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.createMask([255,255,255], 12, True, 24)
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1

class LedgeRoll(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
    
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        _actor.change_x = 0
        _actor.mask = None
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.invulnerable = 37
            _actor.createMask([255,255,255], 32, True, 24)
            
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1
        
########################################################
#                    ATTACK ACTIONS                    #
########################################################
class BaseAttack(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        
    def tearDown(self, _actor, nextAction):
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
    
    def onClank(self, _actor):
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
                    
    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == self.last_frame:
            if _actor.grounded:
                _actor.doAction('NeutralAction')
            else:
                _actor.doAction('Fall')
        for hitbox in self.hitboxes.values():
            hitbox.update()
        self.frame += 1

class AirAttack(BaseAttack):
    def __init__(self, _length=1):
        BaseAttack.__init__(self, _length)
        self.fastfall_frame = None
    
    def setUp(self, _actor):
        BaseAttack.setUp(self, _actor)
        if not hasattr(self, 'fastfall_frame'):
            self.fastfall_frame = None
    
    def onClank(self, _actor):
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
                    
    def stateTransitions(self, _actor):
        if self.fastfall_frame is not None and self.frame >= self.fastfall_frame:
            if _actor.keysContain('down'):
                _actor.platform_phase = 1
                _actor.calcGrav(_actor.var['fastfall_multiplier'])
        if _actor.grounded and _actor.ground_elasticity == 0:
            _actor.preferred_xspeed = 0
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            _actor.doAction('Land')
                
    def update(self, _actor):
        BaseAttack.update(self, _actor)
            
class ChargeAttack(BaseAttack):
    def __init__(self,_length=1,_startChargeFrame=1,_endChargeFrame=1,_maxCharge=0):
        BaseAttack.__init__(self, _length)
        self.start_charge_frame = _startChargeFrame
        self.end_charge_frame = _endChargeFrame
        self.max_charge = 1
        
    def setUp(self, _actor):
        self.chargeLevel = 0
        BaseAttack.setUp(self, _actor)
        
    def update(self, _actor):
        BaseAttack.update(self, _actor)
        if self.frame == self.start_charge_frame:
            if _actor.keysContain('attack') and self.chargeLevel == 0:
                _actor.createMask([255,255,0],72,True,32)
        
        #Find solution for multiple hitboxes
        if self.frame == self.end_charge_frame:
            if _actor.keysContain('attack') and self.chargeLevel <= self.max_charge:
                for _,hitbox in self.hitboxes.iteritems():
                    hitbox.charge()
                self.chargeLevel += 1
                self.frame = self.start_charge_frame
        
        if self.frame == (self.end_charge_frame+1):
            _actor.mask = None

class BaseThrow(BaseGrabbing):
    def __init__(self,_length=1):
        BaseGrabbing.__init__(self, _length)
        
    def update(self, _actor):
        if self.frame == self.last_frame:
            if _actor.grounded: _actor.doAction('NeutralAction')
            else: _actor.doAction('Fall')
        BaseGrabbing.update(self, _actor)                  

class NeutralAttack(BaseAttack):
    def __init__(self, _length=0):
        BaseAttack.__init__(self, _length)
                
class ForwardAttack(BaseAttack):
    def __init__(self, _length=0):
        BaseAttack.__init__(self, _length)

class UpAttack(BaseAttack):
    def __init__(self, _length=0):
        BaseAttack.__init__(self, _length)

class DownAttack(BaseAttack):
    def __init__(self, _length=0):
        BaseAttack.__init__(self, _length)

class ForwardSmash(ChargeAttack):
    def __init__(self,_length=0):
        ChargeAttack.__init__(self, _length,0,1)
        
class UpSmash(ChargeAttack):
    def __init__(self,_length=0):
        ChargeAttack.__init__(self, _length,0,1)
        
class DownSmash(ChargeAttack):
    def __init__(self,_length=0):
        ChargeAttack.__init__(self, _length,0,1)
        
class NeutralAir(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)

class ForwardAir(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)

class BackAir(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)

class UpAir(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)

class DownAir(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)

class DashAttack(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)

class NeutralSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
                
class NeutralGroundSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)

class NeutralAirSpecial(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)
        
class ForwardSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
                
class ForwardGroundSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
        
class ForwardAirSpecial(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)
        
class UpSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
                
class UpGroundSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
        
class UpAirSpecial(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)
        
class DownSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
                
class DownGroundSpecial(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
    
class DownAirSpecial(AirAttack):
    def __init__(self,_length=0):
        AirAttack.__init__(self, _length)

class ForwardThrow(BaseThrow):
    def __init__(self,_length=0):
        BaseGrabbing.__init__(self, _length)

class DownThrow(BaseThrow):
    def __init__(self,_length=0):
        BaseGrabbing.__init__(self, _length)
       
class GetupAttack(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
########################################################
#               TRANSITION STATES                      #
########################################################
def neutralState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyHeld('shield'):
        _actor.doShield(True)
    elif _actor.keyHeld('attack'):
        _actor.doGroundAttack()
    elif _actor.keyHeld('special'):
        _actor.doGroundSpecial()
    elif _actor.keyHeld('jump'):
        _actor.doAction('Jump')
    elif _actor.keysContain('down', 0.5):
        if _actor.keyBuffered('down', int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.5, 1):

            blocks = _actor.checkGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    _actor.doAction('PlatformDrop')
                else:
                    _actor.doAction('Crouch')
            else:
                _actor.doAction('Crouch')
        else:
            _actor.doAction('Crouch')
    elif _actor.keysContain(invkey):
        if _actor.keyBuffered(invkey, int(_actor.key_bindings.timing_window['repeat_window'])+1, _to=1):
            _actor.doDash(-_actor.getFacingDirection())
        else:
            _actor.doGroundMove(_actor.getForwardWithOffset(180))
    elif _actor.keysContain(key):
        if _actor.keyBuffered(key, int(_actor.key_bindings.timing_window['repeat_window'])+1, _to=1):
            _actor.doDash(_actor.getFacingDirection())
        else:
            _actor.doGroundMove(_actor.getForwardWithOffset(0))

def crouchState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyHeld('shield'):
        if _actor.keysContain(invkey):
            _actor.doAction('BackwardRoll')
        elif _actor.keysContain(key):
            _actor.doAction('ForwardRoll')
        else:
            _actor.doAction('SpotDodge')
    if _actor.keyHeld('attack'):
        _actor.doGroundAttack()
    elif _actor.keyHeld('special'):
        _actor.doGroundSpecial()
    elif _actor.keyHeld('jump'):
        _actor.doAction('Jump')
    elif not _actor.keysContain('down'):
        _actor.doAction('CrouchGetup')

def airState(_actor):
    airControl(_actor)
    if _actor.change_x < 0 and _actor.facing == 1 and _actor.keyBuffered('left', 1) and _actor.keyBuffered('left', int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6, 1):
        _actor.flip()
        print ("Reverse")
    if _actor.change_x > 0 and _actor.facing == -1 and _actor.keyBuffered('right', 1) and _actor.keyBuffered('right', int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6, 1):
        _actor.flip()
        print ("Reverse")
    if _actor.keyHeld('shield'):
        _actor.doAction('AirDodge')
    elif _actor.keyHeld('attack'):
        _actor.doAirAttack()
    elif _actor.keyHeld('special'):
        _actor.doAirSpecial()
    elif _actor.keyHeld('jump') and _actor.jumps > 0:
        _actor.doAction('AirJump')
    elif _actor.keysContain('down'):
        _actor.platform_phase = 1
        _actor.calcGrav(_actor.var['fastfall_multiplier'])

def tumbleState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key):
        _actor.preferred_xspeed = _actor.facing * _actor.var['max_air_speed']
    elif _actor.keysContain(invkey):
        _actor.preferred_xspeed = -_actor.facing * _actor.var['max_air_speed']
    
    if (_actor.change_x < 0) and not _actor.keysContain('left'):
        _actor.preferred_xspeed = 0
    if (_actor.change_x > 0) and not _actor.keysContain('right'):
        _actor.preferred_xspeed = 0

    if not (_actor.change_x < -_actor.var['max_air_speed'] and _actor.keysContain('left')) or not (_actor.change_x > _actor.var['max_air_speed'] and _actor.keysContain('right')):
        _actor.accel(_actor.var['air_control'])

    if _actor.change_y >= _actor.var['max_fall_speed'] and _actor.landing_lag < _actor.var['heavy_land_lag']:
        _actor.landing_lag = _actor.var['heavy_land_lag']

    if _actor.tech_window == 0:
        tapReversible(_actor)

    if _actor.keyHeld('attack'):
        _actor.doAirAttack()
    elif _actor.keyHeld('special'):
        _actor.doAirSpecial()
    elif _actor.keyHeld('jump') and _actor.jumps > 0:
        _actor.doAirJump()
    elif _actor.keysContain('down'):
        _actor.platform_phase = 1
        _actor.calcGrav(_actor.var['fastfall_multiplier'])
            
def moveState(_actor, direction):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyHeld('shield'):
        _actor.doAction('Shield')
    elif _actor.keyHeld('attack'):
        if _actor.keysContain('shield'):
            _actor.doAction('GroundGrab')
        else:
            _actor.doGroundAttack()
    elif _actor.keyHeld('special'):
        _actor.doGroundSpecial()
    elif _actor.keyHeld('jump'):
        _actor.doAction('Jump')
    elif _actor.keysContain('down', 0.5):
        _actor.doAction('Crouch')
    elif not _actor.keysContain('left') and not _actor.keysContain('right') and not _actor.keysContain('down'):
        _actor.doAction('Stop')
    elif _actor.preferred_xspeed < 0 and not _actor.keysContain('left',1) and _actor.keysContain('right',1):
        _actor.doAction('Stop')
    elif _actor.preferred_xspeed > 0 and not _actor.keysContain('right',1) and _actor.keysContain('left',1):
        _actor.doAction('Stop')

def stopState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyHeld('jump'):
        _actor.doAction('Jump')
    elif _actor.keyHeld(key, max(min(int(_actor.key_bindings.timing_window['repeat_window'])+1, _actor.last_input_frame), 1)):
        print("run")
        _actor.doDash(_actor.getFacingDirection())
    elif _actor.keyHeld(invkey):
        print("pivot")
        _actor.doAction('Pivot')

def runStopState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyHeld('jump'):
        _actor.doAction('Jump')
    elif _actor.keyHeld(key, max(min(int(_actor.key_bindings.timing_window['repeat_window'])+1, _actor.last_input_frame), 1)):
        print("run")
        _actor.doDash(_actor.getFacingDirection())
    elif _actor.keyHeld(invkey):
        print("run pivot")
        _actor.doAction('RunPivot')

def dashState(_actor, direction):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyHeld('shield'):
        _actor.doAction('ForwardRoll')
    if _actor.keyHeld('attack'):
        if _actor.keysContain('shield'):
            _actor.doAction('DashGrab')
        elif _actor.checkSmash(key):
            print("Dash cancelled into forward smash")
            _actor.doAction('ForwardSmash')
        else:
            _actor.doAction('DashAttack')
    elif _actor.keyHeld('special'):
        _actor.doGroundSpecial()
    elif _actor.keyHeld('jump'):
        _actor.doAction('Jump')
    elif _actor.keysContain('down', 0.5):
        _actor.doAction('Stop')
    elif not _actor.keysContain('left') and not _actor.keysContain('right') and not _actor.keysContain('down'):
        _actor.doAction('RunStop')
    elif _actor.preferred_xspeed < 0 and not _actor.keysContain('left',1) and _actor.keysContain('right',1):
        _actor.doAction('RunStop')
    elif _actor.preferred_xspeed > 0 and not _actor.keysContain('right',1) and _actor.keysContain('left',1):
        _actor.doAction('RunStop')

def jumpState(_actor):
    airControl(_actor)
    tapReversible(_actor)
    if _actor.keyHeld('shield'):
        _actor.doAction('AirDodge')
    elif _actor.keyHeld('attack'):
        _actor.doAirAttack()
    elif _actor.keyHeld('special'):
        _actor.doAirSpecial()
    elif _actor.keysContain('down'):
        _actor.platform_phase = 1
        _actor.calcGrav(_actor.var['fastfall_multiplier'])
            
def shieldState(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyBuffered(key, 1, 0.6) and _actor.keyBuffered(key, int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6, 1) and not _actor.keyBuffered(invkey, int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6):
        _actor.doAction('ForwardRoll')
    elif _actor.keyBuffered(invkey, 1, 0.6) and _actor.keyBuffered(invkey, int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6, 1) and not _actor.keyBuffered(key, int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6):
        _actor.doAction('BackwardRoll')
    elif _actor.keyBuffered('down', 1, 0.6) and _actor.keyBuffered('down', int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6, 1) and not _actor.keyBuffered('up', int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6):
        _actor.doAction('SpotDodge')
    elif _actor.keyHeld('attack'):
        _actor.doAction('GroundGrab')
    elif _actor.keyHeld('special'):
        _actor.doGroundSpecial()
    elif _actor.keyHeld('jump'):
        _actor.doAction('Jump')

def ledgeState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    _actor.setSpeed(0, _actor.getFacingDirection())
    if _actor.keyHeld('shield'):
        _actor.ledge_lock = True
        _actor.doAction('LedgeRoll')
    elif _actor.keyHeld('attack'):
        _actor.ledge_lock = True
        _actor.doAction('LedgeAttack')
    elif _actor.keyHeld('jump'):
        _actor.ledge_lock = True
        _actor.invincible = 6
        _actor.doAction('Jump')
    elif _actor.keyHeld(key):
        _actor.ledge_lock = True
        _actor.doAction('LedgeGetup')
    elif _actor.keyHeld(invkey):
        _actor.ledge_lock = True
        _actor.invincible = 6
        _actor.doAction('Fall')
    elif _actor.keyHeld('down'):
        _actor.ledge_lock = True
        _actor.invincible = 6
        _actor.doAction('Fall')

def grabbingState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    # Check to see if they broke out
    # If they did, release them
    if not _actor.isGrabbing():
        _actor.doAction('Release')
    elif _actor.keyHeld('shield'):
        _actor.doAction('Release')
    elif _actor.keyHeld('attack'):
        _actor.doAction('Pummel')
    elif _actor.keyHeld(key):
        _actor.doAction('ForwardThrow')
    elif _actor.keyHeld(invkey):
        _actor.doAction('BackThrow')
    elif _actor.keyHeld('up'):
        _actor.doAction('UpThrow')
    elif _actor.keyHeld('down'):
        _actor.doAction('DownThrow')

def proneState(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain('attack'):
        print("Selecting getup attack")
        _actor.doAction('GetupAttack')
    elif _actor.keysContain('up'):
        print("Selecting normal getup")
        _actor.doAction('Getup')
    elif _actor.keysContain(key):
        print("Selecting forward getup")
        _actor.doAction('ForwardRoll')
    elif _actor.keysContain(invkey):
        print("Selecting backward getup")
        _actor.doAction('BackwardRoll')
    elif _actor.keysContain('down'):
        print("Selecting spotdodge getup")
        _actor.doAction('SpotDodge')

########################################################
#             BEGIN HELPER METHODS                     #
########################################################

def airControl(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key):
        _actor.preferred_xspeed = _actor.facing * _actor.var['max_air_speed']
    elif _actor.keysContain(invkey):
        _actor.preferred_xspeed = -_actor.facing * _actor.var['max_air_speed']
    
    if (_actor.change_x < 0) and not _actor.keysContain('left'):
        _actor.preferred_xspeed = 0
    if (_actor.change_x > 0) and not _actor.keysContain('right'):
        _actor.preferred_xspeed = 0

    if not (_actor.change_x < -_actor.var['max_air_speed'] and _actor.keysContain('left')) or not (_actor.change_x > _actor.var['max_air_speed'] and _actor.keysContain('right')):
        _actor.accel(_actor.var['air_control'])

    if _actor.change_y >= _actor.var['max_fall_speed'] and _actor.landing_lag < _actor.var['heavy_land_lag']:
        _actor.landing_lag = _actor.var['heavy_land_lag']

    if _actor.grounded and _actor.ground_elasticity == 0 and _actor.tech_window == 0:
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
        _actor.doAction('Land')

def helplessControl(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key):
        _actor.preferred_xspeed = _actor.facing * _actor.var['max_air_speed']
    elif _actor.keysContain(invkey):
        _actor.preferred_xspeed = -_actor.facing * _actor.var['max_air_speed']
    
    if (_actor.change_x < 0) and not _actor.keysContain('left'):
        _actor.preferred_xspeed = 0
    elif (_actor.change_x > 0) and not _actor.keysContain('right'):
        _actor.preferred_xspeed = 0

    if not (_actor.change_x < -_actor.var['max_air_speed'] and _actor.keysContain('left')) or not (_actor.change_x > _actor.var['max_air_speed'] and _actor.keysContain('right')):
        _actor.accel(_actor.var['air_control'])

    if _actor.change_y >= _actor.var['max_fall_speed'] and _actor.landing_lag < _actor.var['heavy_land_lag']:
        _actor.landing_lag = _actor.var['heavy_land_lag']

    if _actor.grounded and _actor.ground_elasticity == 0 and _actor.tech_window == 0:
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
        _actor.doAction('HelplessLand')

def hitstunLanding(_actor):
    if _actor.grounded and _actor.ground_elasticity == 0 and _actor.tech_window == 0:
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
        _actor.doAction('Land')

def grabLedges(_actor):
    # Check if we're colliding with any ledges.
    if not _actor.ledge_lock: #If we're not allowed to re-grab, don't bother calculating
        ledge_hit_list = pygame.sprite.spritecollide(_actor, _actor.game_state.platform_ledges, False)
        for ledge in ledge_hit_list:
            # Don't grab any ledges if the _actor is holding down
            if _actor.keysContain('down') is False:
                # If the ledge is on the left side of a platform, and we're holding right
                if ledge.side == 'left' and _actor.keysContain('right'):
                    ledge.fighterGrabs(_actor)
                elif ledge.side == 'right' and _actor.keysContain('left'):
                    ledge.fighterGrabs(_actor)

def checkGrounded(_actor):
    if not _actor.grounded:
        _actor.doAction('Fall')

def tiltReversible(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyBuffered(invkey, _state=0.3):
        _actor.flip()
        print("Reverse")

def tapReversible(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyBuffered(invkey, _state=1) and _actor.keyBuffered(invkey, min(int(_actor.key_bindings.timing_window['repeat_window'])+1, _actor.last_input_frame), 0.6, 1):
        _actor.flip()
        print("Reverse")

def shieldCancellable(_actor):
    if _actor.keyBuffered('shield') and _actor.grounded:
        _actor.doAction('Shield')
    elif _actor.keyBuffered('shield') and not (_actor.keysContain('left', 0.2) or _actor.keysContain('right', 0.2) or _actor.keysContain('up', 0.2) or _actor.keysContain('down', 0.2)) and not _actor.grounded:
        _actor.doAction('Fall')

def dodgeCancellable(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyBuffered('shield') and _actor.keysContain(key, 0.6) and _actor.grounded:
        _actor.changeAction('ForwardRoll')
    elif _actor.keyBuffered('shield') and _actor.keysContain(invkey, 0.6) and _actor.grounded:
        _actor.changeAction('BackwardRoll')
    elif _actor.keyBuffered('shield') and _actor.keysContain('down', 0.6) and _actor.grounded:
        _actor.changeAction('SpotDodge')
    elif _actor.keyBuffered('shield') and (_actor.keysContain('left', 0.2) or _actor.keysContain('right', 0.2) or _actor.keysContain('up', 0.2) or _actor.keysContain('down', 0.2)) and not _actor.grounded:
        _actor.changeAction('AirDodge')
        
def autoDodgeCancellable(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key, 0.6) and _actor.grounded:
        _actor.changeAction('ForwardRoll')
    elif _actor.keysContain(invkey, 0.6) and _actor.grounded:
        _actor.changeAction('BackwardRoll')
    elif _actor.keysContain('down', 0.6) and _actor.grounded:
        _actor.changeAction('SpotDodge')
    elif (_actor.keysContain('left', 0.2) or _actor.keysContain('right', 0.2) or _actor.keysContain('up', 0.2) or _actor.keysContain('down', 0.2)) and not _actor.grounded:
        _actor.changeAction('AirDodge')

def jumpCancellable(_actor):
    if _actor.keyBuffered('jump') and _actor.grounded:
        _actor.changeAction('Jump')
    elif _actor.keyBuffered('jump') and _actor.jumps > 0 and not _actor.grounded:
        _actor.changeAction('AirJump')
                    

state_dict = {
            "neutralState": neutralState,
            "crouchState": crouchState,
            "airState": airState,
            "moveState": moveState,
            "stopState": stopState,
            "runStopState": runStopState,
            "dashState": dashState,
            "jumpState": jumpState,
            "shieldState": shieldState,
            "ledgeState": ledgeState,
            "grabbingState": grabbingState,
            "proneState": proneState,
            "airControl": airControl,
            "helplessControl": helplessControl,
            "hitstunLanding": hitstunLanding,
            "grabLedges": grabLedges,     
            "checkGrounded": checkGrounded,
            "tiltReversible": tiltReversible,
            "tapReversible": tapReversible,
            "shieldCancellable": shieldCancellable,
            "dodgeCancellable": dodgeCancellable,
            "autoDodgeCancellable": autoDodgeCancellable,
            "jumpCancellable": jumpCancellable
            }

"""
Work in progress
class Grabbing(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
    
    def setUp(self, _actor):
        action.Action.setUp(self, _actor)
        self.hold_point = (0,0)
        if self.sprite_name=="": self.sprite_name ="grabbing"
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        #TODO release
    
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        
class Grabbed(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
    
    def setUp(self, _actor):
        action.Action.setUp(self, _actor)
        if self.sprite_name=="": self.sprite_name ="grabbed"
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        #TODO release
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        grabber = _actor.grabbed_by
        
        #release if you're not being held
        if grabber is None or not (grabber.grabbing == _actor):
            _actor.doAction('grabRelease')
        
        #snap to hold point
        (hold_x,hold_y) = grabber.current_action.hold_point
        _actor.rect.centerx = grabber.rect.x + (hold_x * grabber.facing) + (_actor.grab_point[0] * _actor.facing)
        _actor.rect.centery = grabber.rect.y + (hold_y * grabber.facing) + (_actor.grab_point[1] * _actor.facing)
        
        #Set the last frame based on damage
        if self.frame == 0:
            self.last_frame = 40 + _actor.damage//2
"""