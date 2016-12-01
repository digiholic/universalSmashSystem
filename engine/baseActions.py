import engine.action as action
import engine.hitbox as hitbox
import engine.hurtbox as hurtbox
import engine.statusEffect as statusEffect
import pygame
import math
import random
import settingsManager
import numpy

class Move(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self,_length) 
        
    def setUp(self,_actor):
        if self.sprite_name=="": self.sprite_name = "move"
        action.Action.setUp(self, _actor)
        self.direction = _actor.facing
        self.accel = True
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if hasattr(_nextAction, 'direction'):
            _nextAction.direction *= self.direction*_actor.facing
        else:
            _actor.facing = self.direction
            if (_actor.facing == 1 and _actor.sprite.flip == "left") or (_actor.facing == -1 and _actor.sprite.flip == "right"):
                _actor.sprite.flipX()
        _actor.preferred_xspeed = 0
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        checkGrounded(_actor)
        _actor.preferred_xspeed = _actor.stats['max_ground_speed']*_actor.facing

        if not (_actor.change_x < -_actor.stats['max_ground_speed'] and _actor.facing == -1) or not (_actor.change_x > _actor.stats['max_ground_speed'] and _actor.facing == 1):
             _actor.accel(_actor.stats['static_grip'])

        (key, invkey) = _actor.getForwardBackwardKeys()
        self.direction = -_actor.facing if _actor.keysContain(invkey) else _actor.facing
        if (self.direction == 1 and _actor.sprite.flip == "left") or (self.direction == -1 and _actor.sprite.flip == "right"):
            _actor.sprite.flipX()
        
        self.frame += 1
        
        if self.frame > self.last_frame: self.frame = 0
        
    def stateTransitions(self,_actor):
        action.Action.stateTransitions(self, _actor)
        moveState(_actor)
        (key,invkey) = _actor.getForwardBackwardKeys()
        if self.frame > 0 and _actor.keyBuffered(invkey, _state = 1):
            _actor.doDash(-_actor.getFacingDirection())
            _actor.current_action.accel = False
        elif self.frame > 0 and _actor.keyBuffered(key, _state = 1):
            _actor.doDash(_actor.getFacingDirection())
            _actor.current_action.accel = False

class Dash(action.Action):
    def __init__(self,_length=1,_runStartFrame=0): 
        action.Action.__init__(self,_length)
        self.run_start_frame = _runStartFrame
        
    def setUp(self,_actor):
        if self.sprite_name=="": self.sprite_name = "dash"
        action.Action.setUp(self, _actor)
        self.direction = _actor.facing
        self.accel = True

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if hasattr(_nextAction, 'direction'):
            _nextAction.direction *= self.direction*_actor.facing
        else:
            _actor.facing = self.direction
            if (_actor.facing == 1 and _actor.sprite.flip == "left") or (_actor.facing == -1 and _actor.sprite.flip == "right"):
                _actor.sprite.flipX()
        _actor.preferred_xspeed = 0

    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.preferred_xspeed = _actor.stats['run_speed']*_actor.facing
        checkGrounded(_actor)

        (key, invkey) = _actor.getForwardBackwardKeys()
        self.direction = -_actor.facing if _actor.keysContain(invkey) else _actor.facing
        if (self.direction == 1 and _actor.sprite.flip == "left") or (self.direction == -1 and _actor.sprite.flip == "right"):
            _actor.sprite.flipX()

        if not (_actor.change_x < -_actor.stats['max_ground_speed'] and _actor.facing == -1) or not (_actor.change_x > _actor.stats['max_ground_speed'] and _actor.facing == 1):
             _actor.accel(_actor.stats['static_grip'])

        self.frame += 1
        
        if self.frame > self.last_frame: 
            self.frame = self.run_start_frame
            
    def stateTransitions(self,_actor):
        action.Action.stateTransitions(self, _actor)
        dashState(_actor)
        
class Pivot(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name = "pivot"
        action.Action.setUp(self, _actor)
        num_frames = int(_actor.change_x*_actor.facing/float(_actor.stats['pivot_grip']))
        self.direction = _actor.facing
        if num_frames < self.last_frame:
            self.frame = min(self.last_frame-num_frames, self.last_frame-1)
        else:
            self.last_frame = num_frames
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if hasattr(_nextAction, 'direction'):
            _nextAction.direction *= self.direction*_actor.facing
        else:
            _actor.facing = self.direction
            if (_actor.facing == 1 and _actor.sprite.flip == "left") or (_actor.facing == -1 and _actor.sprite.flip == "right"):
                _actor.sprite.flipX()

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        stopState(_actor)
        checkGrounded(_actor)

        (key, invkey) = _actor.getForwardBackwardKeys()
        if (self.direction == 1 and _actor.sprite.flip == "left") or (self.direction == -1 and _actor.sprite.flip == "right"):
            _actor.sprite.flipX()

        if self.frame == self.last_frame:
            if _actor.keysContain(invkey):
                if _actor.keyHeld(invkey, max(min(int(_actor.key_bindings.timing_window['repeat_window'])+1, _actor.last_input_frame), 1), 1, 0):
                    if _actor.facing == 1:
                        _actor.doDash(180)
                    else:
                        _actor.doDash(0)
                else:
                    if _actor.facing == 1:
                        _actor.doGroundMove(180)
                    else:
                        _actor.doGroundMove(0)
            elif _actor.keysContain(key):
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
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.flip()
        if self.frame != self.last_frame:
            self.frame += 1
        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keysContain(key) and _actor.keysContain(invkey):
            _actor.preferred_xspeed = _actor.stats['max_ground_speed']*_actor.facing
            _actor.accel(_actor.stats['static_grip'])
        else:
            _actor.preferred_xspeed = 0
            _actor.accel(_actor.stats['pivot_grip'])
          
class Stop(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name = "stop"
        action.Action.setUp(self, _actor)
        self.direction = _actor.facing
        num_frames = int(_actor.change_x*_actor.facing/float(_actor.stats['pivot_grip']))
        if num_frames < self.last_frame:
            self.frame = min(self.last_frame-num_frames, self.last_frame-1)
        else:
            self.last_frame = num_frames
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keysContain(key) and _actor.keysContain(invkey):
            _actor.preferred_xspeed = _actor.stats['max_ground_speed']*_actor.facing
            _actor.accel(_actor.stats['static_grip'])
        else:
            _actor.preferred_xspeed = 0
            _actor.accel(_actor.stats['pivot_grip'])
        self.frame += 1
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        stopState(_actor)
        checkGrounded(_actor)
        (key, invkey) = _actor.getForwardBackwardKeys()

        if (self.direction == 1 and _actor.sprite.flip == "left") or (self.direction == -1 and _actor.sprite.flip == "right"):
            _actor.sprite.flipX()
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if hasattr(_nextAction, 'direction'):
            _nextAction.direction *= self.direction*_actor.facing
        else:
            _actor.facing = self.direction
            if (_actor.facing == 1 and _actor.sprite.flip == "left") or (_actor.facing == -1 and _actor.sprite.flip == "right"):
                _actor.sprite.flipX()
            
class RunPivot(action.Action):
    def __init__(self,length=1):
        action.Action.__init__(self, length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="runPivot" 
        action.Action.setUp(self, _actor)
        self.direction = _actor.facing
        num_frames = int(_actor.change_x*_actor.facing/float(_actor.stats['static_grip']))
        if num_frames < self.last_frame:
            self.frame = min(self.last_frame-num_frames, self.last_frame-1)
        else:
            self.last_frame = num_frames
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if hasattr(_nextAction, 'direction'):
            _nextAction.direction *= self.direction*_actor.facing
        else:
            _actor.facing = self.direction
            if (_actor.facing == 1 and _actor.sprite.flip == "left") or (_actor.facing == -1 and _actor.sprite.flip == "right"):
                _actor.sprite.flipX()
        _actor.preferred_xspeed = 0
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        runStopState(_actor)
        checkGrounded(_actor)

        (key, invkey) = _actor.getForwardBackwardKeys()
        if (self.direction == 1 and _actor.sprite.flip == "left") or (self.direction == -1 and _actor.sprite.flip == "right"):
            _actor.sprite.flipX()

        if self.frame == self.last_frame:
            (key, invkey) = _actor.getForwardBackwardKeys()
            if _actor.keysContain(invkey):
                if _actor.facing == 1:
                    _actor.doDash(0)
                else:
                    _actor.doDash(180)
            if _actor.keysContain(key):
                if _actor.facing == 1:
                    _actor.doDash(0)
                else:
                    _actor.doDash(180)
            else:
                _actor.doAction('NeutralAction')
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        _actor.accel(_actor.stats['static_grip'])
        if self.frame == 0:
            _actor.flip()
        if self.frame != self.last_frame:
            self.frame += 1
        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keysContain(key) and _actor.keysContain(invkey):
            _actor.preferred_xspeed = _actor.stats['run_speed']*_actor.facing
        else:
            _actor.preferred_xspeed = 0

class RunStop(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="runStop"
        action.Action.setUp(self, _actor)
        self.direction = _actor.facing
        num_frames = int(_actor.change_x*_actor.facing/float(_actor.stats['static_grip']))
        if num_frames < self.last_frame:
            self.frame = min(self.last_frame-num_frames, self.last_frame-1)
        else:
            self.last_frame = num_frames
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keysContain(key) and _actor.keysContain(invkey):
            _actor.preferred_xspeed = _actor.stats['run_speed']*_actor.facing
        else:
            _actor.preferred_xspeed = 0
        _actor.accel(_actor.stats['static_grip'])
        self.frame += 1
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        runStopState(_actor)
        checkGrounded(_actor)

        (key, invkey) = _actor.getForwardBackwardKeys()
        if (self.direction == 1 and _actor.sprite.flip == "left") or (self.direction == -1 and _actor.sprite.flip == "right"):
            _actor.sprite.flipX()

        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if hasattr(_nextAction, 'direction'):
            _nextAction.direction *= self.direction*_actor.facing
        else:
            _actor.facing = self.direction
            if (_actor.facing == 1 and _actor.sprite.flip == "left") or (_actor.facing == -1 and _actor.sprite.flip == "right"):
                _actor.sprite.flipX()
                
class NeutralAction(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="neutralAction"
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        checkGrounded(_actor)
        neutralState(_actor)
    
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == self.last_frame:
            self.frame = 0
        self.frame += 1

class Respawn(action.Action):
    def __init__(self,_length=360):
        action.Action.__init__(self, settingsManager.getSetting('respawnLifetime'))
        
    def setUp(self, _actor):
        import engine.article as article
        if self.sprite_name=="": self.sprite_name ="neutralAction"
        action.Action.setUp(self, _actor)
        _actor.armor['respawn_invuln'] = hurtbox.Intangibility(_actor)
        self.respawn_article = article.RespawnPlatformArticle(_actor)
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.frame > settingsManager.getSetting('respawnDowntime'):
            neutralState(_actor)
        if self.frame == self.last_frame:
            _actor.doAction('Fall')
    
    def tearDown(self, _actor, _nextAction):
        import engine.article as article
        action.Action.tearDown(self, _actor, _nextAction)
        if 'respawn_invuln' in _actor.armor:
            del _actor.armor['respawn_invuln']
        apply_invuln = statusEffect.TemporaryHitFilter(_actor,hurtbox.Intangibility(_actor),settingsManager.getSetting('respawnInvincibility'))
        apply_invuln.activate()
        self.respawn_article.deactivate()
        
    def update(self,_actor):
        import engine.article as article
        action.Action.update(self, _actor)
        _actor.grounded = True
        _actor.change_y = 0
        if self.frame == 0:
            self.respawn_article = article.RespawnPlatformArticle(_actor)
            _actor.createMask([255,128,255], settingsManager.getSetting('respawnDowntime'), True, 12)
            _actor.articles.append(self.respawn_article)
        if self.frame == 180:
            _actor.createMask([255,255,255], settingsManager.getSetting('respawnLifetime') - settingsManager.getSetting('respawnDowntime'), True, 12)
        self.frame += 1
        
class Crouch(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="crouch"
        action.Action.setUp(self, _actor)
        _actor.armor['crouch_cancel'] = hurtbox.CrouchCancel(_actor)

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        crouchState(_actor)
        checkGrounded(_actor)
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
        if not isinstance(_nextAction, CrouchGetup) and 'crouch_cancel' in _actor.armor:
            del _actor.armor['crouch_cancel']

    def update(self, _actor):
        action.Action.update(self, _actor)
        _actor.accel(_actor.stats['pivot_grip'])
        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keysContain(key):
            _actor.preferred_xspeed = _actor.stats['crawl_speed']*_actor.facing
        elif _actor.keysContain(invkey):
            _actor.preferred_xspeed = -_actor.stats['crawl_speed']*_actor.facing
        else:
            _actor.preferred_xspeed = 0
        self.frame += 1
        if self.frame > self.last_frame:
            self.frame = self.last_frame

class CrouchGetup(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="crouchGetup"
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if 'crouch_cancel' in _actor.armor:
            del _actor.armor['crouch_cancel']
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        crouchState(_actor)
        checkGrounded(_actor)
        if _actor.keyBuffered('down', _state = 1):
            blocks = _actor.checkGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    _actor.doAction('PlatformDrop')
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')

    def update(self, _actor):
        action.Action.update(self, _actor)
        _actor.preferred_xspeed = 0
        self.frame += 1

########################################################
#                  Grab Actions                        #
########################################################

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

    def stateTransitions(self,_actor):
        action.Action.stateTransitions(self,_actor)
        if self.frame >= self.last_frame:
            _actor.doAction('Released')
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        new_position = _actor.getSmoothedInput()
        cross = new_position[0]*self.last_position[1]-new_position[1]*self.last_position[0]
        self.held_time += (cross**2)*4
        if self.held_time >= 1:
            self.frame += int(self.held_time)
            self.held_time -= int(self.held_time)
        self.last_position = new_position
        # Throws and other grabber-controlled releases are the grabber's responsibility
        # Also, the grabber should always check to see if the grabbee is still under grab
        self.frame += 1
        self.time += 1
        print("In trapped: " + str((self.frame, self.time)))

class BaseGrab(action.Action):
    def __init__(self,_length=1):
        action.Action.__init__(self, _length)
        self.escapable = False
        self.escape_pause = False
        self.hold_point = (0,0)
        
    def setUp(self, _actor):
        action.Action.setUp(self, _actor)
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if not isinstance(_nextAction, BaseGrab):
            if isinstance(_actor.grabbing.current_action,Grabbed):
                _actor.grabbing.doAction('Released')

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.frame >= self.last_frame:
            _actor.doAction('Release')
    
    def update(self, _actor):
        action.Action.update(self, _actor)       
        self.hold_point = (self.hold_point[0],self.hold_point[1])

class GrabReeling(BaseGrab):
    def __init__(self,_length=1):
        BaseGrab.__init__(self, _length)
        self.escape_pause = True

    def setUp(self, _actor):
        BaseGrab.setUp(self, _actor)
        self.target_point = (16, -16)
        self.reel_speed = 10
        if self.sprite_name=="": self.sprite_name ="grabreeling"

    def tearDown(self, _actor, _nextAction):
        print(_nextAction.__class__.__name__)
        BaseGrab.tearDown(self, _actor, _nextAction)
    
    def stateTransitions(self, _actor):
        BaseGrab.stateTransitions(self, _actor)
        grabbingState(_actor)
        if self.frame > 0 and (_actor.grabbing is None or not isinstance(_actor.grabbing.current_action, Grabbed)):
            _actor.doAction('Release')
        if self.frame >= self.last_frame:
            _actor.doAction('Grabbing')
            
    def update(self, _actor):
        BaseGrab.update(self, _actor)
        if _actor.grabbing is not None:
            self.dist = _actor.posx + (hold_x * _actor.facing) + (_actor.grabbing.grab_point[0] * -_actor.grabbing.facing) - _actor.grabbing.posx
            self.last_frame = abs(self.dist - self.reel_speed)
            self.hold_point = (self.dist + self.target_point[0], self.target_point[1])
            #If they're both facing the same way, flip the foe so they are facing you
            if _actor.grabbing.facing == _actor.facing:
                _actor.grabbing.flip()
            if dist > 0:
                self.hold_point[0] -= self.reel_speed
            else:
                self.hold_point[0] += self.reel_speed
        self.frame += 1
        
class Grabbing(BaseGrab):
    def __init__(self,_length=1):
        BaseGrab.__init__(self, _length)
    
    def setUp(self, _actor):
        BaseGrab.setUp(self, _actor)
        self.hold_point = (16,-16)
        if self.sprite_name=="": self.sprite_name ="grabbing"
        
    def tearDown(self, _actor, _nextAction):
        print(_nextAction.__class__.__name__)
        BaseGrab.tearDown(self, _actor, _nextAction)
        #TODO release
    
    def stateTransitions(self, _actor):
        BaseGrab.stateTransitions(self, _actor)
        grabbingState(_actor)
        #If you aren't holding anything, let go
        if (_actor.grabbing is None or not isinstance(_actor.grabbing.current_action, Grabbed)):
            _actor.doAction('Release')
            return
            
    def update(self, _actor):
        BaseGrab.update(self, _actor)
        #If they're both facing the same way, flip the foe so they are facing you
        if _actor.grabbing is not None and _actor.grabbing.facing == _actor.facing:
            _actor.grabbing.flip()
        self.frame += 1
        if self.frame >= self.last_frame:
            self.frame = 0
        
class Grabbed(Trapped):
    def __init__(self,_length=1):
        Trapped.__init__(self, _length)
        
    def setUp(self, _actor):
        Trapped.setUp(self, _actor)
        if self.sprite_name=="": self.sprite_name ="grabbed"
        #Set the last frame based on damage
        self.last_frame = 40 + _actor.damage//2
        
    def tearDown(self, _actor, _nextAction):
        Trapped.tearDown(self, _actor, _nextAction)
        _actor.grabbed_by = None

    def stateTransitions(self, _actor):
        Trapped.stateTransitions(self, _actor)
        grabber = _actor.grabbed_by
        #release if you're not being held
        if self.frame > 0 and grabber is None or (not (grabber.grabbing == _actor)):
            print('No one is holding me, gonna break out.')
            _actor.doAction('Released')
        elif self.frame >= self.last_frame:
            #If the grabber's action doesn't have "escapable" set or if it is set to True, break out on last frame
            if (not hasattr(grabber.current_action, 'escapable')) or grabber.current_action.escapable:
                _actor.doAction('Released')
                grabber.doAction('Release')
            else:
                print('Cant break free')
        
    def update(self, _actor):
        hold_frame = self.frame
        Trapped.update(self, _actor)
        grabber = _actor.grabbed_by
        
        _actor.change_y = 0

        if grabber is not None:
            #snap to hold point
            if hasattr(grabber.current_action, 'hold_point'):
                (hold_x,hold_y) = grabber.current_action.hold_point
            else:
                (hold_x,hold_y) = (0,0)
            _actor.posx = grabber.posx + (hold_x * grabber.facing) + (_actor.grab_point[0] * -_actor.facing)
            _actor.posy = grabber.posy + (hold_y) + (_actor.grab_point[1])
            if hasattr(grabber.current_action, 'escape_pause') and grabber.current_action.escape_pause:
                self.frame = hold_frame

class Release(action.Action):
    def __init__(self):
        action.Action.__init__(self, 15)
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="release"
        action.Action.setUp(self, _actor)
        _actor.grabbing = None

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        checkGrounded(_actor)
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        self.frame += 1

class Released(action.Action):
    def __init__(self):
        action.Action.__init__(self, 15)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="released"
        action.Action.setUp(self, _actor)
        _actor.preferred_xspeed = 0
        _actor.change_x = -10 * _actor.facing
        #_actor.preferred_yspeed = _actor.stats['max_fall_speed']
        _actor.grabbed_by = None
    
    def stateTransitions(self,_actor):
        action.Action.stateTransitions(self, _actor)
        if self.frame >= self.last_frame:
            _actor.doAction('Fall')

    def update(self,_actor):
        action.Action.update(self, _actor)
        tapReversible(_actor)

        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keysContain(key):
            _actor.preferred_xspeed = _actor.facing * _actor.stats['max_air_speed']
        elif _actor.keysContain(invkey):
            _actor.preferred_xspeed = -_actor.facing * _actor.stats['max_air_speed']
    
        if (_actor.change_x < 0) and not _actor.keysContain('left'):
            _actor.preferred_xspeed = 0
        elif (_actor.change_x > 0) and not _actor.keysContain('right'):
            _actor.preferred_xspeed = 0
        _actor.landing_lag = 0

        self.frame += 1
        
class HitStun(action.Action):
    def __init__(self,_hitstun=1,_direction=0):
        action.Action.__init__(self, _hitstun)
        self.angle = _direction
        self.do_slow_getup = False
        self.feet_planted = True #A variable to check if we ever leave the ground

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="hitStun"
        action.Action.setUp(self, _actor)
        self.tech_cooldown = 0
        if not hasattr(self, 'do_slow_getup'):
            self.do_slow_getup = False
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        (direct,_) = _actor.getDirectionMagnitude()

        if _actor.tech_window > 0:
            _actor.ground_elasticity = 0
            if _actor.grounded and not self.feet_planted:
                _actor.doTech()
        else:
            if self.last_frame > 15 and self.frame > 2:
                if _actor.change_y >= _actor.stats['max_fall_speed']: 
                    _actor.ground_elasticity = _actor.stats['hitstun_elasticity']
                elif abs(_actor.change_x) > _actor.stats['run_speed']: #Skid trip
                    _actor.ground_elasticity = 0
                    if _actor.grounded and not self.feet_planted:
                        _actor.doAction('Prone')
                elif _actor.change_y < _actor.stats['max_fall_speed']/2.0: 
                    _actor.ground_elasticity = 0
                    if _actor.grounded and not self.feet_planted: 
                        _actor.doAction('Prone')
                else: 
                    _actor.ground_elasticity = _actor.stats['hitstun_elasticity']/2
            elif self.last_frame <= 15:
                _actor.ground_elasticity = 0
            else:
                _actor.ground_elasticity = _actor.stats['hitstun_elasticity']

        if self.frame == self.last_frame:
            if self.last_frame > 15:
                if _actor.grounded:
                    _actor.doAction('NeutralAction')
                else: _actor.doAction('Tumble')
            else:
                if _actor.grounded:
                    if self.do_slow_getup:
                        print("Successful jab reset")
                        _actor.doAction('SlowGetup')
                    else:
                        _actor.doAction('NeutralAction')
                else:
                    _actor.landing_lag = _actor.stats['heavy_land_lag']
                    _actor.doAction('Fall')
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if not isinstance(_nextAction, Tumble):
            _actor.elasticity = 0
            _actor.ground_elasticity = 0
            _actor.tech_window = 0
            _actor.unRotate()
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.last_frame > 15 and _actor.keyBuffered('shield', 5) and self.tech_cooldown == 0 and not _actor.grounded:
            print('Try tech')
            _actor.tech_window = 12
            anti_grab = statusEffect.TemporaryHitFilter(_actor,hurtbox.GrabImmunity(_actor), 10)
            anti_grab.activate()
            self.tech_cooldown = 40
        if _actor.tech_window > 0:
            _actor.elasticity = 0
        else:
            _actor.elasticity = _actor.stats['hitstun_elasticity']
        self.feet_planted = _actor.grounded
        if self.tech_cooldown > 0: self.tech_cooldown -= 1
        if self.frame == 0:
            anti_grab = statusEffect.TemporaryHitFilter(_actor,hurtbox.GrabImmunity(_actor), 10)
            anti_grab.activate()
            (direct,mag) = _actor.getDirectionMagnitude()
            print("direction:", direct)
            if direct != 0 and direct != 180:
                _actor.grounded = False
                if mag > 10:
                    _actor.rotateSprite(self.angle)
            
        if self.frame % max(1,int(100.0/max(math.hypot(_actor.change_x, _actor.change_y), 1))) == 0 and self.frame < self.last_frame:
            import engine.article as article
            art = article.HitArticle(_actor, (_actor.posx, _actor.posy), 1, math.degrees(math.atan2(_actor.change_y, -_actor.change_x))+random.randrange(-30, 30), .5*math.hypot(_actor.change_x, _actor.change_y), .02*(math.hypot(_actor.change_x, _actor.change_y)+1), _actor.trail_color)
            _actor.articles.append(art)

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
        
        if _actor.tech_window > 0:
            _actor.ground_elasticity = 0
            if _actor.grounded:
                _actor.doTech()
        else:
            if _actor.change_y >= _actor.stats['max_fall_speed']:#Hard landing during tumble
                _actor.ground_elasticity = _actor.stats['hitstun_elasticity']/2
            elif _actor.change_y < _actor.stats['max_fall_speed']/2.0: #Soft landing during tumble
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
        
        if _actor.keyBuffered('shield', 5) and self.tech_cooldown == 0 and not _actor.grounded:
            print('Try tech')
            _actor.tech_window = 20
            anti_grab = statusEffect.TemporaryHitFilter(_actor,hurtbox.GrabImmunity(_actor), 10)
            anti_grab.activate()
            self.tech_cooldown = 40

        if _actor.tech_window > 0:
            _actor.elasticity = 0
        else:
            _actor.elasticity = _actor.stats['hitstun_elasticity']/2
        _actor.rotateSprite((_actor.sprite.angle+90)+2)
        if self.tech_cooldown > 0: self.tech_cooldown -= 1
        
class Prone(action.Action):
    def __init__(self,_length=25):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name == "": self.sprite_name = "prone"
        action.Action.setUp(self, _actor)
        anti_grab = statusEffect.TemporaryHitFilter(_actor,hurtbox.GrabImmunity(_actor), 30)
        anti_grab.activate()

        block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, _actor.checkGround(), None)
        if not block is None:
            _actor.change_y = block.change_y
            _actor.posy = block.rect.top - _actor.ecb.current_ecb.rect.height/2.0
        _actor.unRotate()
        (key, invkey) = _actor.getForwardBackwardKeys()
        if _actor.keyHeld(key):
            _actor.change_x += _actor.facing*2
        if _actor.keyHeld(invkey):
            _actor.change_x -= _actor.facing*2

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if isinstance(_nextAction, HitStun):
            _nextAction.do_slow_getup = True
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == self.last_frame:
            self.frame = self.last_frame - 1
        self.frame += 1
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if not _actor.grounded:
            _actor.doAction('Tumble')
        if self.frame >= self.last_frame-2:
            proneState(_actor)

class Getup(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="getup"
        action.Action.setUp(self, _actor)  
        anti_grab = statusEffect.TemporaryHitFilter(_actor,hurtbox.GrabImmunity(_actor), 10)
        anti_grab.activate()

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        checkGrounded(_actor)
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        self.frame += 1

class SlowGetup(action.Action):
    def __init__(self):
        action.Action.__init__(self, 30)
        
    def setUp(self, _actor):
        if self.sprite_name == "": self.sprite_name = "prone"
        action.Action.setUp(self, _actor)
        
        if self.last_frame < 30: self.last_frame = 30 #slow getups must be this long
        _actor.unRotate()
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        self.frame += 1
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.frame == self.last_frame:
            _actor.doAction('Getup')

class Jump(action.Action):
    def __init__(self,_length=1,_jumpFrame=0):
        action.Action.__init__(self, _length)
        self.jump_frame = _jumpFrame
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="jump"
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if _actor.keyHeld('shield'):
            _actor.doAction('AirDodge')
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
        if self.frame >= self.last_frame:
            _actor.doAction('Fall')
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == self.jump_frame:
            _actor.grounded = False
            if _actor.keysContain('jump'):
                _actor.change_y = -_actor.stats['jump_height']
            else: _actor.change_y = -_actor.stats['short_hop_height']
            if _actor.change_x > _actor.stats['aerial_transition_speed']:
                _actor.change_x = _actor.stats['aerial_transition_speed']
            elif _actor.change_x < -_actor.stats['aerial_transition_speed']:
                _actor.change_x = -_actor.stats['aerial_transition_speed']
        self.frame += 1

class AirJump(action.Action):
    def __init__(self,_length=1,_jumpFrame=0):
        action.Action.__init__(self, _length)
        self.jump_frame = _jumpFrame
        
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="airjump"
        action.Action.setUp(self, _actor)

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
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
        if self.frame >= self.last_frame:
            _actor.doAction('Fall')

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_yspeed = _actor.stats['max_fall_speed']
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame < self.jump_frame:
            _actor.change_y = 0
            _actor.preferred_yspeed = 0
        if self.frame == self.jump_frame:
            _actor.grounded = False
            _actor.change_y = -_actor.stats['air_jump_height']
            _actor.jumps -= 1
            if _actor.keysContain('left') and _actor.facing == 1:
                _actor.flip()
                _actor.change_x = _actor.facing * _actor.stats['max_air_speed']
            elif _actor.keysContain('right') and _actor.facing == -1:
                _actor.flip()
                _actor.change_x = _actor.facing * _actor.stats['max_air_speed']
        self.frame += 1
        
class Fall(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="fall"
        action.Action.setUp(self, _actor)
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.stats['max_fall_speed']
    
    def stateTransitions(self,_actor):
        action.Action.stateTransitions(self, _actor)
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
        action.Action.stateTransitions(self, _actor)
        helplessControl(_actor)
        grabLedges(_actor)

    def update(self, _actor):
        action.Action.update(self, _actor)
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

        block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, _actor.checkGround(), None)
        if not block is None:
            _actor.change_y = block.change_y
            _actor.posy = block.rect.top - _actor.ecb.previous_ecb.rect.height/2.0

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        #_actor.preferred_xspeed = 0

    def stateTransitions(self, _actor):
        action.Action.update(self, _actor)
        if self.frame >= self.last_frame:
            _actor.landing_lag = 0
            _actor.doAction('NeutralAction')
            _actor.platform_phase = 0
            _actor.preferred_xspeed = 0
        checkGrounded(_actor)

    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.preferred_yspeed = _actor.stats['max_fall_speed']
            self.last_frame = _actor.landing_lag
            lcancel = settingsManager.getSetting('lagCancel')
            if lcancel == 'normal':
                if _actor.keyHeld('shield', 4) and not _actor.keyBuffered('shield', 20, 0.1, 4):
                    print("l-cancel")
                    self.last_frame = self.last_frame // 2
            elif lcancel == 'auto':
                print("l-cancel")
                self.last_frame = self.last_frame // 2
        if self.frame == 1:
            #_actor.articles.append(article.LandingArticle(_actor)) #this looks awful don't try it
            pass
        self.frame += 1

class HelplessLand(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="helplessLand"
        action.Action.setUp(self, _actor)
        block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, _actor.checkGround(), None)
        if not block is None:
            _actor.change_y = block.change_y
            _actor.posy = block.rect.top - _actor.ecb.previous_ecb.rect.height/2.0

    def stateTransitions(self, _actor):
        action.Action.update(self, _actor)
        if self.frame >= self.last_frame:
            _actor.landing_lag = 0
            _actor.doAction('NeutralAction')
            _actor.platform_phase = 0
            _actor.preferred_xspeed = 0
        checkGrounded(_actor)

    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.change_y = 0
            _actor.preferred_yspeed = _actor.stats['max_fall_speed']
            self.last_frame = _actor.landing_lag
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
        action.Action.stateTransitions(self, _actor)
        if _actor.keyHeld('attack') and _actor.checkSmash('down') and self.frame < self.phase_frame:
            print("Platform drop cancelled into down smash")
            _actor.doAction('DownSmash')
        elif _actor.keyHeld('special') and _actor.checkSmash('down') and self.frame < self.phase_frame:
            print("Platform drop cancelled into down special")
            if self.hasAction('DownSpecial'):
                self.doAction('DownSpecial')
            else:
                self.doAction('DownGroundSpecial')
        if self.frame >= self.last_frame:
            _actor.doAction('Fall')
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == self.phase_frame:
            _actor.platform_phase = self.phase_length
        if self.frame > self.phase_frame:
            tapReversible(_actor)
            airControl(_actor)
        self.frame += 1

class Shield(action.Action):
    def __init__(self, _newShield=True):
        action.Action.__init__(self, 12)
        self.new_shield = _newShield
   
    def setUp(self, _actor):
        if not hasattr(self, 'new_shield'):
            self.new_shield = True
        action.Action.setUp(self, _actor)
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        shieldState(_actor)
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')
        if self.frame == 4:
            if not _actor.keysContain('shield'):
                if self.new_shield:
                    print(_actor.shield_integrity)
                    _actor.doAction('Parry')
   
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if not isinstance(_nextAction, ShieldStun):
            _actor.shield = False
       
    def update(self, _actor):
        action.Action.update(self, _actor)
        if _actor.grounded is False:
            _actor.shield = False
            _actor.doAction('Fall')
        if self.frame == 4:
            _actor.shield = True
            if self.new_shield:
                _actor.startShield()
            self.frame += 1
            if not _actor.keysContain('shield'):
                if not self.new_shield:
                    self.frame += 1
        elif self.frame == 5:
            if not _actor.keysContain('shield'):
                self.frame += 1
        elif self.frame >= 6 and self.frame < self.last_frame:
            _actor.shield = False
            self.frame += 1
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

    def stateTransitions(self, _actor):
        action.Action.update(self, _actor)
        if _actor.grounded is False:
            _actor.shield = False
            _actor.doAction('Fall')
        if self.frame >= self.last_frame and _actor.keysContain('shield'):
            _actor.doShield(False)
        elif self.frame >= self.last_frame:
            _actor.landing_lag = 6
            _actor.doAction('Land')

    def update(self, _actor):
        action.Action.update(self, _actor)
        self.frame += 1

class Parry(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)

    def setUp(self, _actor):
        from engine.subactions import control
        if self.sprite_name=="": self.sprite_name="parry"
        _actor.grabbing = None
        self.takedown_hitbox = hitbox.ThrowHitbox(_actor, hitbox.HitboxLock(), 
                                                  {
                                                   'base_knockback': 10,
                                                   'knockback_growth': 0,
                                                   'trajectory': 270,
                                                   'hitstun_multiplier': 0,
                                                   'base_hitstun': 15
                                                  })
        self.takedown_hitbox.other_on_hit_actions.append(control.setVar.setVar(_source="action", _attr="do_slow_getup", _val=True))
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.shield = False
        if 'parry_invuln' in _actor.armor:
            del _actor.armor['parry_invuln']

    def stateTransitions(self, _actor):
        action.Action.update(self, _actor)
        if _actor.grounded is False:
            _actor.shield = False
            _actor.doAction('Fall')
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')

    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.shield = True
            _actor.startParry()
        elif self.frame == 5:
            _actor.shield = False
        elif self.frame == self.last_frame - 1:
            self.takedown_hitbox.activate()
                
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
        if 'stun_invuln' in _actor.armor:
            del _actor.armor['stun_invuln'] 
        _actor.mask = None

    def stateTransitions(self, _actor):
        action.Action.update(self, _actor)
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == 0:
            _actor.createMask([255, 0, 255], 99999, True, 8)
            _actor.armor['stun_invuln'] = hurtbox.Intangibility(_actor)
        if self.frame == 40:
            if 'stun_invuln' in _actor.armor:
                del _actor.armor['stun_invuln']
        self.frame += 1
        
class ForwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 32)
        
    def setUp(self, _actor):
        self.start_invuln_frame = 5
        self.end_invuln_frame = 22
        if self.sprite_name=="": self.sprite_name ="forwardRoll"
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        if 'dodge_invuln' in _actor.armor:
            del _actor.armor['dodge_invuln']
        _actor.mask = None

    def stateTransitions(self, _actor):
        action.Action.update(self, _actor)
        if _actor.keyHeld('attack') and self.frame < 8:
            _actor.doAction('DashGrab')
        if _actor.grounded is False:
            _actor.doAction('Fall')
        if self.frame >= self.last_frame:
            if 'shield' in _actor.keys_held:
                _actor.doShield()
            else:
                _actor.doAction('NeutralAction')
        
    def update(self, _actor):
        action.Action.update(self,_actor)
        if self.frame == 1:
            _actor.change_x = _actor.facing * _actor.stats['dodge_speed']
        elif self.frame == self.start_invuln_frame:
            _actor.createMask([255,255,255], self.end_invuln_frame-self.start_invuln_frame, True, 24)
            _actor.armor['dodge_invuln'] = hurtbox.Intangibility(_actor)
        elif self.frame == self.end_invuln_frame:
            if 'dodge_invuln' in _actor.armor:
                del _actor.armor['dodge_invuln']
            _actor.flip()
            _actor.change_x = 0
        self.frame += 1

class BackwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 32)
        
    def setUp(self,_actor):
        self.start_invuln_frame = 5
        self.end_invuln_frame = 22
        if self.sprite_name=="": self.sprite_name ="backwardRoll"
        action.Action.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        if 'dodge_invuln' in _actor.armor:
            del _actor.armor['dodge_invuln']
        _actor.mask = None

    def stateTransitions(self, _actor):
        action.Action.update(self, _actor)
        if _actor.keyHeld('attack') and self.frame < 8:
            _actor.doAction('DashGrab')
        if _actor.grounded is False:
            _actor.doAction('Fall')
        if self.frame >= self.last_frame:
            if 'shield' in _actor.keys_held:
                _actor.doShield()
            else:
                _actor.doAction('NeutralAction')
        
    def update(self, _actor):
        action.Action.update(self, _actor)
        if self.frame == 1:
            _actor.change_x = _actor.facing * -_actor.stats['dodge_speed']
        elif self.frame == self.start_invuln_frame:
            _actor.createMask([255,255,255], self.end_invuln_frame-self.start_invuln_frame, True, 24)
            _actor.armor['dodge_invuln'] = hurtbox.Intangibility(_actor)
        elif self.frame == self.end_invuln_frame:
            if 'dodge_invuln' in _actor.armor:
                del _actor.armor['dodge_invuln']
            _actor.change_x = 0
        self.frame += 1
        
class SpotDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        
    def setUp(self,_actor):
        self.start_invuln_frame = 4
        self.end_invuln_frame = 18
        if self.sprite_name=="": self.sprite_name ="spotDodge"
        action.Action.setUp(self, _actor)

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if _actor.keyBuffered('down', 1) and self.frame > 0 and self.frame < 8:
            blocks = _actor.checkGround()
            if blocks:
                blocks = map(lambda x:x.solid,blocks)
                if not any(blocks):
                    _actor.doAction('PlatformDrop')
        if self.frame >= self.last_frame:
            if 'shield' in _actor.keys_held:
                _actor.doShield()
            else:
                _actor.doAction('NeutralAction')

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        _actor.preferred_xspeed = 0
        if 'dodge_invuln' in _actor.armor:
            del _actor.armor['dodge_invuln']
        if _actor.grounded is False:
            _actor.doAction('Fall')
        _actor.mask = None
        
    def update(self,_actor):
        action.Action.update(self, _actor)
        if self.frame == 1:
            _actor.change_x = 0
        elif self.frame == self.start_invuln_frame:
            _actor.createMask([255,255,255], self.end_invuln_frame-self.start_invuln_frame, True, 24)
            _actor.armor['dodge_invuln'] = hurtbox.Intangibility(_actor)
        elif self.frame == self.end_invuln_frame:
            if 'dodge_invuln' in _actor.armor:
                del _actor.armor['dodge_invuln']
        self.frame += 1
        
class AirDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 30)
        
    def setUp(self,_actor):
        if self.sprite_name=="": self.sprite_name ="airDodge"
        action.Action.setUp(self, _actor)
        self.start_invuln_frame = 4
        self.end_invuln_frame = 20
        self.move_vec = [0,0]
        
        if settingsManager.getSetting('airDodgeType') == 'directional':
            self.move_vec = _actor.getSmoothedInput(int(_actor.key_bindings.timing_window['smoothing_window']))
            _actor.change_x = self.move_vec[0]*_actor.stats['dodge_speed']
            _actor.change_y = self.move_vec[1]*_actor.stats['dodge_speed']
        if not settingsManager.getSetting('freeDodgeSpecialFall') and settingsManager.getSetting('airDodgeType') == 'directional':
            _actor.airdodges = 0

        if settingsManager.getSetting('enableWavedash'):
            _actor.updateLandingLag(_actor.stats['wavedash_lag'])
        else:
            _actor.updateLandingLag(int(settingsManager.getSetting('airDodgeLag')))
        
    def tearDown(self,_actor,_nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if settingsManager.getSetting('airDodgeType') == 'directional' and not isinstance(_nextAction, AirGrab):
            _actor.preferred_yspeed = _actor.stats['max_fall_speed']
            _actor.preferred_xspeed = 0
        if _actor.mask: _actor.mask = None
        if 'dodge_invuln' in _actor.armor:
            del _actor.armor['dodge_invuln']
    
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.frame >= self.end_invuln_frame:
            grabLedges(_actor)
        if _actor.keyHeld('attack') and self.frame < 8:
            if _actor.hasAction('AirGrab'):
                _actor.doAction('AirGrab')
        if _actor.grounded:
            if not settingsManager.getSetting('enableWavedash'):
                _actor.change_x = 0
            _actor.doAction('Land')
        if self.frame >= self.last_frame:
            if settingsManager.getSetting('freeDodgeSpecialFall'):
                _actor.doAction('Helpless')
            else:
                _actor.doAction('Fall')
                
    def update(self,_actor):
        action.Action.update(self, _actor)
        if settingsManager.getSetting('airDodgeType') == 'directional':
            if self.frame == 0:
                _actor.preferred_xspeed = _actor.change_x
                _actor.preferred_yspeed = _actor.change_y
            #elif self.frame >= self.end_invuln_frame:
            elif self.frame == self.last_frame:
                _actor.change_x = 0
                _actor.change_y = 0
                _actor.preferred_xspeed = 0
                _actor.preferred_yspeed = _actor.stats['max_fall_speed']
        if self.frame == self.start_invuln_frame:
            _actor.updateLandingLag(settingsManager.getSetting('airDodgeLag'))
            (key, invkey) = _actor.getForwardBackwardKeys()
            if _actor.keysContain(invkey, 1):
                _actor.flip()
            _actor.createMask([255,255,255], self.end_invuln_frame-self.start_invuln_frame, True, 24)
            _actor.armor['dodge_invuln'] = hurtbox.Intangibility(_actor)
        elif self.frame == self.end_invuln_frame:
            if 'dodge_invuln' in _actor.armor:
                del _actor.armor['dodge_invuln']
            _actor.landing_lag = settingsManager.getSetting('airDodgeLag')
        self.frame += 1

class BaseTech(action.Action):
    def __init__(self, _length):
        action.Action.__init__(self, _length)

    def setUp(self, _actor):
        action.Action.setUp(self, _actor)
        self.start_invuln_frame = -1
        self.end_invuln_frame = -1
        block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, _actor.checkGround(), None)
        anti_grab = statusEffect.TemporaryHitFilter(_actor,hurtbox.GrabImmunity(_actor), 10)
        anti_grab.activate()
        if not block is None:
            _actor.change_y = block.change_y
            _actor.posy = block.rect.top - _actor.ecb.previous_ecb.rect.height/2.0
        _actor.unRotate()

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if _actor.grounded is False:
            _actor.doAction('Fall')
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')

    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if 'dodge_invuln' in _actor.armor:
            del _actor.armor['dodge_invuln']
        _actor.mask = None
        _actor.preferred_xspeed = 0

    def update(self, _actor):
        action.Action.update(self,_actor)
        if self.frame == self.start_invuln_frame:
            _actor.createMask([255,255,255], self.end_invuln_frame-self.start_invuln_frame, True, 24)
            _actor.armor['dodge_invuln'] = hurtbox.Intangibility(_actor)
        if self.frame == self.end_invuln_frame:
            if 'dodge_invuln' in _actor.armor:
                del _actor.armor['dodge_invuln']
        self.frame += 1

class ForwardTech(BaseTech):
    def __init__(self):
        BaseTech.__init__(self, 32)
        
    def setUp(self, _actor):
        self.start_invuln_frame = 5
        self.end_invuln_frame = 22
        if self.sprite_name=="": self.sprite_name ="forwardRoll"
        
    def update(self, _actor):
        BaseTech.update(self,_actor)
        if self.frame == 1:
            _actor.change_x = _actor.facing * _actor.stats['dodge_speed']
        elif self.frame == self.end_invuln_frame:
            _actor.flip()
            _actor.change_x = 0

class BackwardTech(BaseTech):
    def __init__(self):
        BaseTech.__init__(self, 32)
        
    def setUp(self,_actor):
        self.start_invuln_frame = 5
        self.end_invuln_frame = 22
        if self.sprite_name=="": self.sprite_name ="backwardRoll"
        BaseTech.setUp(self, _actor)
        
    def update(self, _actor):
        BaseTech.update(self, _actor)
        if self.frame == 1:
            _actor.change_x = _actor.facing * -_actor.stats['dodge_speed']
        elif self.frame == self.end_invuln_frame:
            _actor.change_x = 0

class DodgeTech(BaseTech):
    def __init__(self):
        BaseTech.__init__(self, 24)
        
    def setUp(self,_actor):
        self.start_invuln_frame = 4
        self.end_invuln_frame = 18
        if self.sprite_name=="": self.sprite_name ="spotDodge"
        BaseTech.setUp(self, _actor)
        
    def update(self,_actor):
        BaseTech.update(self, _actor)
        if self.frame == 1:
            _actor.change_x = 0

class NormalTech(BaseTech):
    def __init__(self):
        BaseTech.__init__(self, 16)

    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name="getup"
        BaseTech.setUp(self, _actor)
        
class BaseLedge(action.Action):
    def __init__(self, _ledge=None,_length=1):
        action.Action.__init__(self, _length)
        self.sweetspot_x = 0
        self.sweetspot_y = 0
        self.ledge = _ledge
    
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        if isinstance(_nextAction, BaseLedge):
            _nextAction.ledge = self.ledge
        else:
            if self.ledge: self.ledge.fighterLeaves(_actor)
            _actor.preferred_yspeed = _actor.stats['max_fall_speed']
        print(_nextAction)
            
    def setUp(self, _actor):
        action.Action.setUp(self, _actor)
        if not hasattr(self, 'ledge'): self.ledge = None
        if not hasattr(self, 'sweetspot_x'): self.sweetspot_x = 0
        if not hasattr(self, 'sweetspot_y'): self.sweetspot_y = 0
        _actor.change_x = 0
        _actor.change_y = 0
        
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.ledge is None:
            _actor.doAction('Fall')
            
    def update(self, _actor):
        action.Action.update(self, _actor)
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = 0
        
class LedgeGrab(BaseLedge):
    def __init__(self,_ledge=None,_length=1):
        BaseLedge.__init__(self,_ledge,_length)
    
    def setUp(self, _actor):
        if self.sprite_name=="": self.sprite_name ="ledgeGrab"
        BaseLedge.setUp(self, _actor)
        _actor.createMask([255,255,255], settingsManager.getSetting('ledgeInvincibilityTime'), True, 12)
        _actor.armor['ledge_invuln'] = hurtbox.Intangibility(_actor)
        _actor.last_input_frame = 0
        
    def tearDown(self, _actor, _nextAction):
        BaseLedge.tearDown(self, _actor, _nextAction)
        if 'ledge_invuln' in _actor.armor:
            del _actor.armor['ledge_invuln']
    
    def stateTransitions(self, _actor):
        BaseLedge.stateTransitions(self, _actor)
        ledgeState(_actor)
        
    def update(self, _actor):
        BaseLedge.update(self, _actor)
        _actor.jumps = _actor.stats['jumps']
        _actor.airdodges = 1
        if self.ledge.side == 'left':
            if _actor.facing == -1:
                _actor.flip()
        else:
            if _actor.facing == 1:
                _actor.flip()

        if self.frame == settingsManager.getSetting('ledgeInvincibilityTime'):
            if 'ledge_invuln' in _actor.armor:
                del _actor.armor['ledge_invuln']
        
        _actor.posx = self.ledge.rect.centerx + (self.sweetspot_x * -_actor.facing)
        _actor.posy = self.ledge.rect.centery + (self.sweetspot_y)
        _actor.change_x = 0
        _actor.change_y = 0
        
        self.frame += 1
        
class BaseLedgeGetup(BaseLedge):
    def __init__(self, _ledge=None, _length=3, _upFrame=1, _sideFrame=2):
        BaseLedge.__init__(self, _ledge, _length)
        self.up_frame = _upFrame
        self.side_frame = _sideFrame
        
    def setUp(self, _actor):
        BaseLedge.setUp(self, _actor)
        _actor.armor['ledge_getup_invuln'] = hurtbox.Intangibility(_actor)
        if not hasattr(self, 'up_frame'): self.up_frame = 1
        if not hasattr(self, 'side_frame'): self.side_frame = 2
        if self.ledge:
            if self.ledge.side == 'left':
                if _actor.facing == -1:
                    _actor.flip()
            else:
                if _actor.facing == 1:
                    _actor.flip()
            self.target_height = self.ledge.platform.rect.top
            if self.ledge.side == 'left': self.target_x = self.ledge.platform.rect.left + _actor.ecb.current_ecb.rect.width/2.0
            else: self.target_x = self.ledge.platform.rect.right - _actor.ecb.current_ecb.rect.width/2.0
            self.diff = self.ledge.platform.rect.top - _actor.ecb.current_ecb.rect.height/2.0 - _actor.posy
            print(self.diff)

    def tearDown(self, _actor, _nextAction):
        BaseLedge.tearDown(self, _actor, _nextAction)
        if 'ledge_getup_invuln' in _actor.armor:
            del _actor.armor['ledge_getup_invuln']
        _actor.invulnerable = 0
        _actor.mask = None
        _actor.change_x = 0
        _actor.change_y = 0

    def stateTransitions(self, _actor):
        BaseLedge.stateTransitions(self, _actor)
        if self.frame >= self.last_frame:
            _actor.doAction('NeutralAction')

    def update(self, _actor):
        BaseLedge.update(self, _actor)
        if self.frame == 0:
            _actor.createMask([255,255,255], _actor.invulnerable, True, 24)
        if self.frame < self.up_frame:
            _actor.preferred_yspeed = float(self.diff)/self.up_frame
            _actor.change_y = float(self.diff)/self.up_frame

        if self.frame >= self.up_frame and self.frame < self.side_frame:
            _actor.preferred_yspeed = 0
            _actor.change_y = 0
            _actor.posy = self.target_height - _actor.ecb.current_ecb.rect.height/2.0
            if self.ledge.side == 'left':
                _actor.change_x = _actor.ecb.current_ecb.rect.width/(self.side_frame-self.up_frame)
                _actor.preferred_xspeed = _actor.ecb.current_ecb.rect.width/(self.side_frame-self.up_frame)
            else:
                _actor.change_x = -_actor.ecb.current_ecb.rect.width/(self.side_frame-self.up_frame)
                _actor.preferred_xspeed = -_actor.ecb.current_ecb.rect.width/(self.side_frame-self.up_frame)
        
        if self.frame == self.side_frame:
            _actor.posx = self.target_x
            _actor.preferred_xspeed = 0
            _actor.change_x = 0
                
        self.frame += 1
        
########################################################
#                    ATTACK ACTIONS                    #
########################################################
class BaseAttack(action.Action):
    def __init__(self, _length=1):
        action.Action.__init__(self, _length)
        
    def tearDown(self, _actor, _nextAction):
        action.Action.tearDown(self, _actor, _nextAction)
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
    
    def onClank(self, _actor, _hitbox, _other):
        action.Action.onClank(self, _actor, _hitbox, _other)
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()

    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.frame >= self.last_frame:
            if _actor.grounded:
                _actor.doAction('NeutralAction')
            else:
                _actor.doAction('Fall')
                    
    def update(self, _actor):
        action.Action.update(self, _actor)
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
    
    def onClank(self, _actor, _hitbox, _other):
        for _,hitbox in self.hitboxes.iteritems():
            hitbox.kill()
                    
    def stateTransitions(self, _actor):
        action.Action.stateTransitions(self, _actor)
        if self.fastfall_frame is not None and self.frame >= self.fastfall_frame:
            if _actor.keysContain('down'):
                _actor.platform_phase = 1
                if not _actor.keyHeld('down', _actor.key_bindings.timing_window['smash_window'], _to=1):
                    _actor.calcGrav(_actor.stats['fastfall_multiplier'])
        if _actor.grounded and _actor.ground_elasticity == 0:
            _actor.preferred_xspeed = 0
            _actor.preferred_yspeed = _actor.stats['max_fall_speed']
            _actor.doAction('Land')
        if self.frame >= self.last_frame:
            if _actor.grounded:
                _actor.doAction('NeutralAction')
            else:
                _actor.doAction('Fall')
        
                
    def update(self, _actor):
        BaseAttack.update(self, _actor)
            
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

class ForwardSmash(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
        
class UpSmash(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
        
class DownSmash(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
        
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

class GroundGrab(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)

    def setUp(self, _actor):
        BaseAttack.setUp(self, _actor)
        from engine import subactions
        for hitbox in self.hitboxes.values():
            if not hitbox.owner_on_hit_actions: 
                if _actor.hasAction('GrabReeling'): hitbox.owner_on_hit_actions.append(subactions.control.doAction.doAction('GrabReeling'))
                else: hitbox.owner_on_hit_actions.append(subactions.control.doAction.doAction('Grabbing'))
            if not hitbox.other_on_hit_actions: hitbox.other_on_hit_actions.append(subactions.control.doAction.doAction('Grabbed'))

class DashGrab(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)

    def setUp(self, _actor):
        BaseAttack.setUp(self, _actor)
        from engine import subactions
        for hitbox in self.hitboxes.values():
            if not hitbox.owner_on_hit_actions: 
                if _actor.hasAction('GrabReeling'): hitbox.owner_on_hit_actions.append(subactions.control.doAction.doAction('GrabReeling'))
                else: hitbox.owner_on_hit_actions.append(subactions.control.doAction.doAction('Grabbing'))
            if not hitbox.other_on_hit_actions:  hitbox.other_on_hit_actions.append(subactions.control.doAction.doAction('Grabbed'))

class AirGrab(AirAttack):
    def __init__(self, _length=0):
        AirAttack.__init__(self, _length)
        
    def setUp(self,_actor):
        AirAttack.setUp(self,_actor)
        if not settingsManager.getSetting('freeDodgeSpecialFall') and settingsManager.getSetting('airDodgeType') == 'directional':
            _actor.airdodges = 0

        if settingsManager.getSetting('enableWavedash'):
            _actor.updateLandingLag(_actor.stats['wavedash_lag'])
        else:
            _actor.updateLandingLag(int(settingsManager.getSetting('airDodgeLag')))
        
    def tearDown(self,_actor,_nextAction):
        AirAttack.tearDown(self, _actor, _nextAction)
        if settingsManager.getSetting('airDodgeType') == 'directional':
            _actor.preferred_yspeed = _actor.stats['max_fall_speed']
            _actor.preferred_xspeed = 0
    
    def stateTransitions(self, _actor):
        AirAttack.stateTransitions(self, _actor)
        if self.frame >= self.last_frame:
            if settingsManager.getSetting('freeDodgeSpecialFall'):
                _actor.doAction('Helpless')
            else:
                _actor.doAction('Fall')
                
    def update(self,_actor):
        AirAttack.update(self, _actor)
        if _actor.grounded:
            if not settingsManager.getSetting('enableWavedash'):
                _actor.change_x = 0
        
class BaseThrow(BaseGrab):
    def __init__(self,_length=1):
        BaseGrab.__init__(self, _length)

    def setUp(self, _actor):
        BaseGrab.setUp(self, _actor)
        self.hold_point = (16,-16)

    def stateTransitions(self, _actor):
        BaseGrab.stateTransitions(self, _actor)
        if self.frame >= self.last_frame:
            if _actor.grounded: _actor.doAction('NeutralAction')
            else: _actor.doAction('Fall')
        
    def update(self, _actor):
        for hitbox in self.hitboxes.values():
            hitbox.update()
        BaseGrab.update(self, _actor)
        self.frame += 1

class Pummel(BaseGrab):
    def __init__(self,_length=1):
        BaseGrab.__init__(self, _length)

    def stateTransitions(self, _actor):
        BaseGrab.stateTransitions(self, _actor)
        if self.frame >= self.last_frame:
            _actor.doAction('Grabbing')

    def update(self, _actor):
        for hitbox in self.hitboxes.values():
            hitbox.update()
        BaseGrab.update(self, _actor)
        self.frame += 1
    
class ForwardThrow(BaseThrow):
    def __init__(self,_length=0):
        BaseGrab.__init__(self, _length)

class DownThrow(BaseThrow):
    def __init__(self,_length=0):
        BaseGrab.__init__(self, _length)
        
class UpThrow(BaseThrow):
    def __init__(self,_length=0):
        BaseGrab.__init__(self, _length)

class BackThrow(BaseThrow):
    def __init__(self,_length=0):
        BaseGrab.__init__(self, _length)

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
       
class GetupAttack(BaseAttack):
    def __init__(self,_length=0):
        BaseAttack.__init__(self, _length)
        anti_grab = statusEffect.TemporaryHitFilter(_actor,hurtbox.GrabImmunity(_actor), 10)
        anti_grab.activate()

class LedgeGetup(BaseLedgeGetup):
    def __init__(self, _length=3):
        BaseLedgeGetup.__init__(self, None, _length)

class LedgeAttack(BaseLedgeGetup):
    def __init__(self, _length=3):
        BaseLedgeGetup.__init__(self, None, _length)

class LedgeRoll(BaseLedgeGetup):
    def __init__(self, _length=3):
        BaseLedgeGetup.__init__(self, None, _length)

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
        print(_actor.player_num,_actor.keys_held)
        if _actor.checkTap('down', 0.5):
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
        if _actor.checkTap(invkey, 0.1):
            _actor.doDash(-_actor.getFacingDirection())
        else:
            _actor.doGroundMove(_actor.getForwardWithOffset(180))
    elif _actor.keysContain(key):
        if _actor.checkTap(key, 0.1):
            _actor.doDash(_actor.getFacingDirection())
        else:
            _actor.doGroundMove(_actor.getForwardWithOffset(0))

def crouchState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    tapReversible(_actor)
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
    elif not _actor.keysContain('down') and not isinstance(_actor.current_action, CrouchGetup):
        _actor.doAction('CrouchGetup')

def airState(_actor):
    airControl(_actor)
    if _actor.change_x < 0 and _actor.facing == 1 and _actor.checkTap('left', 1):
        _actor.flip()
        print ("Reverse")
    if _actor.change_x > 0 and _actor.facing == -1 and _actor.checkTap('right', 1):
        _actor.flip()
        print ("Reverse")
    if _actor.keyHeld('shield') and _actor.airdodges == 1:
        _actor.doAction('AirDodge')
    elif _actor.keyHeld('attack'):
        if _actor.keysContain('shield'):
            _actor.doAction('AirGrab')
        else:
            _actor.doAirAttack()
    elif _actor.keyHeld('special'):
        _actor.doAirSpecial()
    elif _actor.keyHeld('jump') and _actor.jumps > 0:
        _actor.doAction('AirJump')
    elif _actor.keysContain('down'):
        _actor.platform_phase = 1
        if not _actor.keyHeld('down', _actor.key_bindings.timing_window['smash_window'], _to=1):
            print("Trying to fastfall")
            _actor.calcGrav(_actor.stats['fastfall_multiplier'])

def tumbleState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key):
        _actor.preferred_xspeed = _actor.facing * _actor.stats['max_air_speed']
    elif _actor.keysContain(invkey):
        _actor.preferred_xspeed = -_actor.facing * _actor.stats['max_air_speed']
    
    if (_actor.change_x < 0) and not _actor.keysContain('left'):
        _actor.preferred_xspeed = 0
    if (_actor.change_x > 0) and not _actor.keysContain('right'):
        _actor.preferred_xspeed = 0

    if not (_actor.change_x < -_actor.stats['max_air_speed'] and _actor.keysContain('left')) or not (_actor.change_x > _actor.stats['max_air_speed'] and _actor.keysContain('right')):
        _actor.accel(_actor.stats['air_control'])

    if _actor.change_y >= _actor.stats['max_fall_speed'] and _actor.landing_lag < _actor.stats['heavy_land_lag']:
        _actor.landing_lag = _actor.stats['heavy_land_lag']

    if _actor.tech_window == 0:
        tapReversible(_actor)

    if _actor.keyHeld('attack'):
        if _actor.keysContain('shield'):
            _actor.doAction('AirGrab')
        _actor.doAirAttack()
    elif _actor.keyHeld('special'):
        _actor.doAirSpecial()
    elif _actor.keyHeld('jump') and _actor.jumps > 0:
        _actor.doAction('AirJump')
    elif _actor.keysContain('down'):
        _actor.platform_phase = 1
        if not _actor.keyHeld('down', _actor.key_bindings.timing_window['smash_window'], _to=1):
            _actor.calcGrav(_actor.stats['fastfall_multiplier'])
            
def moveState(_actor):
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
    elif _actor.keyHeld(key, max(min(int(_actor.key_bindings.timing_window['repeat_window'])+1, _actor.last_input_frame), 1)):
        _actor.doDash(_actor.getFacingDirection())
        _actor.current_action.accel = False
    elif _actor.keyHeld(invkey, _state=1) and not _actor.keysContain(key):
        print("pivot")
        _actor.doAction('Pivot')

def runStopState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    if _actor.keyHeld('shield'):
        _actor.doAction('ForwardRoll')
    if _actor.keyHeld('attack'):
        if _actor.keysContain('shield'):
            _actor.doAction('DashGrab')
        else:
            _actor.doAction('DashAttack')
    elif _actor.keyHeld('special'):
        _actor.doGroundSpecial()
    elif _actor.keyHeld('jump'):
        _actor.doAction('Jump')
    elif _actor.keyHeld(key, max(min(int(_actor.key_bindings.timing_window['repeat_window'])+1, _actor.last_input_frame), 1)):
        print("run")
        _actor.doDash(_actor.getFacingDirection())
        _actor.current_action.accel = False
    elif _actor.keyHeld(invkey, _state=1) and not _actor.keysContain(key):
        print("run pivot")
        _actor.doAction('RunPivot')

def dashState(_actor):
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
        _actor.doAction('RunStop')
    elif not _actor.keysContain('left') and not _actor.keysContain('right') and not _actor.keysContain('down'):
        _actor.doAction('RunStop')
    elif _actor.preferred_xspeed < 0 and not _actor.keysContain('left',1) and _actor.keysContain('right',1):
        _actor.doAction('RunStop')
    elif _actor.preferred_xspeed > 0 and not _actor.keysContain('right',1) and _actor.keysContain('left',1):
        _actor.doAction('RunStop')

def jumpState(_actor):
    airControl(_actor)
    tapReversible(_actor)
    if _actor.keyHeld('shield') and _actor.airdodges == 1:
        _actor.doAction('AirDodge')
    elif _actor.keyHeld('attack'):
        _actor.doAirAttack()
    elif _actor.keyHeld('special'):
        _actor.doAirSpecial()
    elif _actor.keysContain('down'):
        _actor.platform_phase = 1
        if not _actor.keyHeld('down', _actor.key_bindings.timing_window['smash_window'], _to=1):
            _actor.calcGrav(_actor.stats['fastfall_multiplier'])
            
def shieldState(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.checkTap(key) and not _actor.keyBuffered(invkey, int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6):
        _actor.doAction('ForwardRoll')
    elif _actor.checkTap(invkey) and not _actor.keyBuffered(key, int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6):
        _actor.doAction('BackwardRoll')
    elif _actor.checkTap('down') and not _actor.keyBuffered('up', int(_actor.key_bindings.timing_window['repeat_window'])+1, 0.6):
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
        apply_invuln = statusEffect.TemporaryHitFilter(_actor,hurtbox.Intangibility(_actor),6)
        apply_invuln.activate()
        _actor.doAction('Jump')
    elif _actor.keyHeld(key):
        _actor.ledge_lock = True
        _actor.doAction('LedgeGetup')
    elif _actor.keyHeld(invkey):
        _actor.ledge_lock = True
        apply_invuln = statusEffect.TemporaryHitFilter(_actor,hurtbox.Intangibility(_actor),6)
        apply_invuln.activate()
        _actor.doAction('Fall')
    elif _actor.keyHeld('down'):
        _actor.ledge_lock = True
        apply_invuln = statusEffect.TemporaryHitFilter(_actor,hurtbox.Intangibility(_actor),6)
        apply_invuln.activate()
        _actor.doAction('Fall')

def grabbingState(_actor):
    (key,invkey) = _actor.getForwardBackwardKeys()
    direct = _actor.netDirection([key, invkey, 'up', 'down'])
    # Check to see if they broke out
    # If they did, release them
    if _actor.grabbing is None:
        _actor.doAction('Release')
    elif _actor.keyHeld('shield'):
        _actor.doAction('Release')
    elif _actor.keyHeld('attack'):
        _actor.doAction('Pummel')
    elif direct == key:
        _actor.doAction('ForwardThrow')
    elif direct == invkey:
        _actor.doAction('BackThrow')
    elif direct == 'up':
        _actor.doAction('UpThrow')
    elif direct == 'down':
        _actor.doAction('DownThrow')

def proneState(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    direct = _actor.netDirection(['up', key, invkey, 'down'])
    if _actor.keysContain('attack'):
        print("Selecting getup attack")
        _actor.doAction('GetupAttack')
    elif direct == 'up':
        print("Selecting normal getup")
        _actor.doAction('Getup')
    elif direct == key:
        print("Selecting forward getup")
        _actor.doAction('ForwardRoll')
    elif direct == invkey:
        print("Selecting backward getup")
        _actor.doAction('BackwardRoll')
    elif direct == 'down':
        print("Selecting spotdodge getup")
        _actor.doAction('SpotDodge')

########################################################
#             BEGIN HELPER METHODS                     #
########################################################

def airControl(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key):
        _actor.preferred_xspeed = _actor.facing * _actor.stats['max_air_speed']
    elif _actor.keysContain(invkey):
        _actor.preferred_xspeed = -_actor.facing * _actor.stats['max_air_speed']
    
    if (_actor.change_x < 0) and not _actor.keysContain('left'):
        _actor.preferred_xspeed = 0
    if (_actor.change_x > 0) and not _actor.keysContain('right'):
        _actor.preferred_xspeed = 0

    if not (_actor.change_x < -_actor.stats['max_air_speed'] and _actor.keysContain('left')) or not (_actor.change_x > _actor.stats['max_air_speed'] and _actor.keysContain('right')):
        _actor.accel(_actor.stats['air_control'])

    if _actor.change_y >= _actor.stats['max_fall_speed'] and _actor.landing_lag < _actor.stats['heavy_land_lag']:
        _actor.landing_lag = _actor.stats['heavy_land_lag']

    if _actor.grounded and _actor.ground_elasticity == 0 and _actor.tech_window == 0:
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.stats['max_fall_speed']
        _actor.doAction('Land')

def helplessControl(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key):
        _actor.preferred_xspeed = _actor.facing * _actor.stats['max_air_speed']
    elif _actor.keysContain(invkey):
        _actor.preferred_xspeed = -_actor.facing * _actor.stats['max_air_speed']
    
    if (_actor.change_x < 0) and not _actor.keysContain('left'):
        _actor.preferred_xspeed = 0
    elif (_actor.change_x > 0) and not _actor.keysContain('right'):
        _actor.preferred_xspeed = 0

    if not (_actor.change_x < -_actor.stats['max_air_speed'] and _actor.keysContain('left')) or not (_actor.change_x > _actor.stats['max_air_speed'] and _actor.keysContain('right')):
        _actor.accel(_actor.stats['air_control'])

    if _actor.change_y >= _actor.stats['max_fall_speed'] and _actor.landing_lag < _actor.stats['heavy_land_lag']:
        _actor.landing_lag = _actor.stats['heavy_land_lag']

    if _actor.grounded and _actor.ground_elasticity == 0 and _actor.tech_window == 0:
        _actor.preferred_xspeed = 0
        _actor.preferred_yspeed = _actor.stats['max_fall_speed']
        _actor.doAction('HelplessLand')

def grabLedges(_actor):
    # Check if we're colliding with any ledges.
    if not _actor.ledge_lock: #If we're not allowed to re-grab, don't bother calculating
        ledge_hit_list = pygame.sprite.spritecollide(_actor.ecb.current_ecb, _actor.game_state.platform_ledges, False)
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
    if _actor.checkTap(invkey):
        _actor.flip()
        print("Reverse")

def shieldCancellable(_actor):
    if _actor.keyBuffered('shield') and _actor.grounded:
        _actor.doAction('Shield')
    elif _actor.keyBuffered('shield') and _actor.netDirection(['up', forward, backward, 'down']) == 'neutral' and not _actor.grounded:
        _actor.doAction('Fall')

def dodgeCancellable(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    direct = self.netDirection([key, invkey, 'down'])
    if _actor.keyBuffered('shield'):
        if _actor.keysContain(key, 0.6) and _actor.grounded: _actor.changeAction('ForwardRoll')
        elif _actor.keysContain(invkey, 0.6) and _actor.grounded: _actor.changeAction('BackwardRoll')
        elif _actor.keysContain('down', 0.6) and _actor.grounded: _actor.changeAction('SpotDodge')
    elif _actor.netDirection(['up', forward, backward, 'down']) != 'neutral' and not _actor.grounded and _actor.airdodges == 1:
        _actor.changeAction('AirDodge')
        
def autoDodgeCancellable(_actor):
    (key, invkey) = _actor.getForwardBackwardKeys()
    if _actor.keysContain(key, 0.6) and _actor.grounded:
        _actor.changeAction('ForwardRoll')
    elif _actor.keysContain(invkey, 0.6) and _actor.grounded:
        _actor.changeAction('BackwardRoll')
    elif _actor.keysContain('down', 0.6) and _actor.grounded:
        _actor.changeAction('SpotDodge')
    elif not _actor.grounded and _actor.airdodges == 1:
        _actor.changeAction('AirDodge')
    elif not _actor.grounded:
        _actor.changeAction('Fall')

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
            "grabLedges": grabLedges,     
            "checkGrounded": checkGrounded,
            "tiltReversible": tiltReversible,
            "tapReversible": tapReversible,
            "shieldCancellable": shieldCancellable,
            "dodgeCancellable": dodgeCancellable,
            "autoDodgeCancellable": autoDodgeCancellable,
            "jumpCancellable": jumpCancellable
            }
