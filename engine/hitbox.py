import math
import pygame
import spriteManager
import settingsManager

class HitboxLock(object):
    def __init__(self,_lockName=''):
        self.lock_name = _lockName
    # Yes, it's that goddamn simple. 
    # All the HitboxLock class does is serve as a dummy for refcounting

class Hitbox(spriteManager.RectSprite):
    def __init__(self,_owner,_lock,_variables = dict()):
        self.owner = _owner
        self.hitbox_type = 'hitbox'
        
        self.variable_dict = {
                       'center': (0,0),
                       'size': (0,0),
                       'damage': 0,
                       'base_knockback': 0,
                       'knockback_growth': 0,
                       'trajectory': 0,
                       'hitstun_multiplier': 2,
                       'charge_damage': 0,
                       'charge_base_knockback': 0,
                       'charge_knockback_growth': 0,
                       'weight_influence': 1,
                       'shield_multiplier': 1,
                       'transcendence': 0, 
                       'priority': 0,
                       'base_hitstun': 10,
                       'hitlag_multiplier': 1,
                       'damage_multiplier': 1,
                       'velocity_multiplier': 1,
                       'x_bias': 0,
                       'y_bias': 0,
                       'x_draw': 0.1,
                       'y_draw': 0.1,
                       'hp': 0,
                       'ignore_shields': False
                       }
        self.newVaraibles = _variables
        self.variable_dict.update(self.newVaraibles)
        
        #set the variables from the dict, so that we don't lose the initial value of the dict when modifying them
        #also lets us not have to go update all the old references. Score!
        for key,value in self.variable_dict.iteritems():
            setattr(self, key, value)
            
        #Flip the distance from center if the fighter is facing the _other way
        #if owner.facing == -1:
        #    self.center = (-self.center[0],self.center[1])
            
        #offset the trajectory based on facing
        self.trajectory = self.owner.getForwardWithOffset(self.trajectory)
        self.hitbox_lock = _lock
        
        spriteManager.RectSprite.__init__(self,pygame.Rect([0,0],self.size),[255,0,0])
        self.rect.center = [_owner.rect.center[0] + self.center[0], _owner.rect.center[1] + self.center[1]]
        self.article = None
        
        self.owner_on_hit_actions = []
        self.other_on_hit_actions = []
        
    def onCollision(self,_other):
        #This unbelievably convoluted function call basically means "if this thing's a fighter" without having to import fighter
        if 'AbstractFighter' in list(map(lambda x :x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]:
            _other.hitbox_contact.add(self)
            if self.hitbox_lock not in _other.hitbox_lock:
                for subact in self.owner_on_hit_actions:
                    subact.execute(self,self.owner)
                for subact in self.other_on_hit_actions:
                    subact.execute(self,_other)
                
    def update(self):
        self.rect.width = self.size[0]
        self.rect.height = self.size[1]
        if self.article is None:
            self.rect.center = [self.owner.rect.center[0] + self.center[0]*self.owner.facing, self.owner.rect.center[1] + self.center[1]]
        elif hasattr(self.article, "facing"):
            self.rect.center = [self.article.rect.center[0] + self.center[0]*self.article.facing, self.article.rect.center[1] + self.center[1]]
        else:
            self.rect.center = [self.article.rect.center[0] + self.center[0], self.article.rect.center[1] + self.center[1]]
        
    def getTrajectory(self):
        return self.trajectory

    def compareTo(self, _other):
        if (hasattr(_other, 'transcendence') and hasattr(_other, 'priority')) and not isinstance(_other, InertHitbox):
            if not self.ignore_shields or isinstance(_other, DamageHitbox) or isinstance(_other, GrabHitbox) or isinstance(_other, InvulnerableHitbox):
                if self.transcendence+_other.transcendence <= 0:
                    return (self.priority - _other.priority) >= 8
        return True
    
    def activate(self):
        pass
    
        
class Hurtbox(spriteManager.RectSprite):
    def __init__(self,_owner,_rect,_color):
        self.owner = _owner
        spriteManager.RectSprite.__init__(self, _rect, _color)
    
    """
    This function is called when a hurtbox is hit by a hitbox. Does nothing by default,
    but can be overridden for a custom Hurtbox class.
    
    @_other: The hitbox that hit this hurtbox
    """
    def onHit(self,_other):
        pass
    
class InertHitbox(Hitbox):
    def __init__(self, _owner, _hitboxLock, _hitboxVars):
        Hitbox.__init__(self, _owner, _hitboxLock, _hitboxVars)
        self.hitbox_type = 'inert'
        
class DamageHitbox(Hitbox):
    def __init__(self,_owner,_lock,_variables):
        Hitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'damage'
        self.priority += self.damage
        
    def onCollision(self,_other):
        Hitbox.onCollision(self, _other)
        #This unbelievably convoluted function call basically means "if this thing's a fighter" without having to import fighter
        if 'AbstractFighter' in list(map(lambda x :x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]:
            if _other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.base_knockback/5.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                _other.applyKnockback(self.damage, self.base_knockback, self.knockback_growth, self.trajectory, self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier)
        
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(_other)
    
    def charge(self):
        self.damage += self.charge_damage
        self.priority += self.charge_damage
        self.base_knockback += self.charge_base_knockback
        self.knockback_growth += self.charge_knockback_growth
        
class SakuraiAngleHitbox(DamageHitbox):
    def __init__(self,_owner,_lock,_variables):
        DamageHitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'sakurai'
        
    def onCollision(self, _other):
        Hitbox.onCollision(self, _other)
        if 'AbstractFighter' in list(map(lambda x :x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]:
            if _other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.base_knockback/5.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                p = float(_other.damage)
                d = float(self.damage)
                w = float(_other.var['weight']) * settingsManager.getSetting('weight')
                s = float(self.knockback_growth)
                b = float(self.base_knockback)
                total_kb = (((((p/10) + (p*d)/20) * (200/(w*self.weight_influence+100))*1.4) + 5) * s) + b

                angle = 0
                if (self.base_knockback > 0):
                    # Calculate the resulting angle
                    knockback_ratio = total_kb*self.velocity_multiplier/self.base_knockback
                    x_val = math.sqrt(knockback_ratio**2+1)/math.sqrt(2)
                    y_val = math.sqrt(knockback_ratio**2-1)/math.sqrt(2)
                    angle = math.atan2(y_val*math.sin(float(self.trajectory)/180*math.pi),x_val*math.cos(float(self.trajectory)/180*math.pi))/math.pi*180
                _other.applyKnockback(self.damage, self.base_knockback, self.knockback_growth, angle, self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(_other)

class AutolinkHitbox(DamageHitbox):
    def __init__(self,_owner,_lock,_variables):
        DamageHitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'autolink'

    def getTrajectory(self):
        if self.owner.change_y+self.y_bias == 0 and self.owner.change_x + self.x_bias == 0:
            return self.trajectory + 90
        else: 
            return self.trajectory-math.atan2(self.y_bias, self.x_bias)*180/math.pi
        
    def onCollision(self, _other):
        Hitbox.onCollision(self, _other)
        if 'AbstractFighter' in list(map(lambda x :x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]:
            if _other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.base_knockback/5.0, self.getTrajectory()+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                    velocity = math.sqrt((self.owner.change_x+self.x_bias) ** 2 + (self.owner.change_y+self.y_bias) ** 2)
                    angle = -math.atan2((self.owner.change_y+self.y_bias), (self.owner.change_x+self.x_bias))*180/math.pi
                    _other.applyKnockback(self.damage, velocity*self.velocity_multiplier+self.base_knockback, self.knockback_growth, self.owner.getForwardWithOffset(self.owner.facing*(angle+self.trajectory)), self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier)
                elif hasattr(self.article, 'change_x') and hasattr(self.article, 'change_y'):
                    velocity = math.sqrt((self.article.change_x+self.x_bias)**2 + (self.article.change_y+self.y_bias)**2)
                    angle = -math.atan2((self.article.change_y+self.y_bias), (self.article.change_x+self.x_bias))*180/math.pi
                    _other.applyKnockback(self.damage, velocity*self.velocity_multiplier+self.base_knockback, self.knockback_growth, self.owner.getForwardWithOffset(self.owner.facing*(angle+self.trajectory)), self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(_other)

class FunnelHitbox(DamageHitbox):
    def __init__(self,_owner,_lock,_variables):
        DamageHitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'funnel'

    def getTrajectory(self):
        if self.owner.change_y+self.y_bias == 0 and self.owner.change_x + self.x_bias == 0:
            return self.trajectory + 90
        else: 
            return self.trajectory-math.atan2(self.y_bias, self.x_bias)*180/math.pi
        
    def onCollision(self,_other):
        Hitbox.onCollision(self, _other)
        if 'AbstractFighter' in list(map(lambda x:x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]:
            if _other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.base_knockback/5.0, self.getTrajectory()+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                    x_diff = self.rect.centerx - _other.rect.centerx
                    y_diff = self.rect.centery - _other.rect.centery
                    x_vel = self.x_bias+self.x_draw*x_diff
                    y_vel = self.y_bias+self.y_draw*y_diff
                    _other.applyKnockback(self.damage, math.hypot(x_vel,y_vel)*self.velocity_multiplier+self.base_knockback, self.knockback_growth, self.owner.getForwardWithOffset(self.owner.facing*(math.degrees(-math.atan2(y_vel,x_vel))+self.trajectory)), self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier)
                else:
                    x_diff = self.article.rect.centerx - _other.rect.centerx
                    y_diff = self.article.rect.centery - _other.rect.centery
                    x_vel = self.x_bias+self.x_draw*x_diff
                    y_vel = self.y_bias+self.y_draw*y_diff
                    _other.applyKnockback(self.damage, math.hypot(x_vel,y_vel)*self.velocity_multiplier+self.base_knockback, self.knockback_growth, self.owner.getForwardWithOffset(self.owner.facing*(math.degrees(-math.atan2(y_vel,x_vel))+self.trajectory)), self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(_other)

class GrabHitbox(Hitbox):
    def __init__(self,_owner,_lock,_variables):
        Hitbox.__init__(self, _owner, _lock, _variables)
        self.hitbox_type = 'grab'

    def onCollision(self,_other):
        Hitbox.onCollision(self, _other)
        if 'AbstractFighter' in list(map(lambda x:x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]:
            if _other.lockHitbox(self):
                self.owner.grabbing = _other
                _other.grabbed_by = self.owner
                self.owner.doAction('Grabbing')
                _other.doAction('Grabbed')
                
    def compareTo(self, _other):
        if not isinstance(_other, DamageHitbox) and not isinstance(_other, GrabHitbox) and not isinstance(_other, InvulnerableHitbox) and _other.owner is not None:
            self.owner.grabbing = _other
            _other.grabbed_by = self.owner
            self.owner.doAction('Grabbing')
            _other.doAction('Grabbed')
            return True
        return Hitbox.compareTo(self, _other)

class ThrowHitbox(Hitbox):
    def __init__(self,_owner,_lock,_variables):
        Hitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'throw'
    
    def activate(self):
        Hitbox.activate(self)
        self.owner.grabbing.applyKnockback(self.damage, self.base_knockback, self.knockback_growth, self.trajectory, self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier)
        self.kill()
            
                
class ReflectorHitbox(InertHitbox):
    def __init__(self,_owner,_hitboxLock,_hitboxVars):
        InertHitbox.__init__(self,_owner,_hitboxLock,_hitboxVars)
        self.hitbox_type = 'reflector'
        self.priority += self.hp
        
    def compareTo(self, _other):
        if _other.article != None and _other.article.owner != self.owner and hasattr(_other.article, 'tags') and 'reflectable' in _other.article.tags and self.owner.lockHitbox(_other):
            if hasattr(_other.article, 'changeOwner'):
                _other.article.changeOwner(self.owner)
            if hasattr(_other.article, 'change_x') and hasattr(_other.article, 'change_y'):
                v_other = [_other.article.change_x, _other.article.change_y]
                v_self = getXYFromDM(self.trajectory, 1.0)
                dot = v_other[0]*v_self[0]+v_other[1]*v_self[1]
                norm_sqr = v_self[0]*v_self[0]+v_self[1]*v_self[1]
                ratio = 1 if norm_sqr == 0 else dot/norm_sqr
                projection = [v_self[0]*ratio, v_self[1]*ratio]
                (_other.article.change_x, _other.article.change_y) = (self.velocity_multiplier*(2*projection[0]-v_other[0]), -1*self.velocity_multiplier*(2*projection[1]-v_other[1]))
            if hasattr(_other, 'damage') and hasattr(_other, 'shield_multiplier'):
                self.priority -= _other.damage*_other.shield_multiplier
                self.hp -= _other.damage*_other.shield_multiplier
                _other.damage *= _other.damage*self.damage_multiplier
            elif hasattr(_other, 'damage'):
                self.priority -= _other.damage
                self.hp -= _other.damage
                _other.damage *= _other.damage*self.damage_multiplier
            prevailed = Hitbox.compareTo(self, _other)
            if not prevailed or self.hp <= 0:
                self.owner.change_y = -15
                self.owner.invulnerable = 20
                self.owner.doStunned(400)
        return True

    def onCollision(self, _other):
        Hitbox.onCollision(self, _other)
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(_other)

class AbsorberHitbox(InertHitbox):
    def __init__(self,_owner,_hitboxLock,_hitboxVars):
        InertHitbox.__init__(self,_owner,_hitboxLock,_hitboxVars)
        self.hitbox_type = 'absorber'
        
    def compareTo(self, _other):
        if _other.article != None and _other.article.owner != self.owner and hasattr(_other.article, 'tags') and 'absorbable' in _other.article.tags and self.owner.lockHitbox(_other) :
            _other.article.deactivate()
            if hasattr(_other, 'damage'):
                self.owner.dealDamage(-_other.damage*self.damage_multiplier)
        return True

    def onCollision(self, _other):
        Hitbox.onCollision(self, _other)
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(_other)

class ShieldHitbox(Hitbox):
    def __init__(self, _center, _size, _owner, _hitboxLock):
        Hitbox.__init__(self,_owner,_hitboxLock,{'center':_center,
                                                'size':_size,
                                                'transcendence':-5,
                                                'priority':_owner.shield_integrity-8
                                                })
        self.hitbox_type = 'shield'

    def update(self):
        self.priority = self.owner.shield_integrity-8
        self.rect.width = self.owner.shield_integrity*self.owner.var['shield_size']
        self.rect.height = self.owner.shield_integrity*self.owner.var['shield_size']
        Hitbox.update(self)
   
    def compareTo(self, _other):
        if (isinstance(_other, DamageHitbox) and not _other.ignore_shields) and self.owner.lockHitbox(_other):
            self.owner.shieldDamage(math.floor(_other.damage*_other.shield_multiplier), _other.base_knockback/5.0*math.cos(math.radians(_other.trajectory)), _other.hitlag_multiplier)
            self.priority = self._owner.shield_integrity-8
            prevailed = Hitbox.compareTo(self, _other)
            if not prevailed:
                self.owner.change_y = -15
                self.owner.invulnerable = 20
                self.owner.doStunned(400)
        return True

class PerfectShieldHitbox(Hitbox):
    def __init__(self, _center, _size, _owner, _hitboxLock):
        Hitbox.__init__(self,_owner,_hitboxLock,{'center':_center,
                                                'size':_size,
                                                'transcendence':-5,
                                                'priority':float("inf")
                                                })
        self.hitbox_type = 'perfectShield'

    def update(self):
        self.rect.width = self.owner.shield_integrity*self.owner.var['shield_size']
        self.rect.height = self.owner.shield_integrity*self.owner.var['shield_size']
        Hitbox.update(self)

    def compareTo(self, _other):
        if (isinstance(_other, DamageHitbox) and not _other.ignore_shields) and self.owner.lockHitbox(_other) and _other.article != None and _other.article.owner != self.owner and hasattr(_other.article, 'tags') and 'reflectable' in _other.article.tags:
            if hasattr(_other.article, 'changeOwner'):
                _other.article.changeOwner(self.owner)
            if hasattr(_other.article, 'change_x') and hasattr(_other.article, 'change_y'):
                v_other = [_other.article.change_x, _other.article.change_y]
                v_self = getXYFromDM(getDirectionBetweenPoints(self.rect.center, _other.article.rect.center)+90, 1.0)
                dot = v_other[0]*v_self[0]+v_other[1]*v_self[1]
                norm_sqr = v_self[0]*v_self[0]+v_self[1]*v_self[1]
                ratio = 1 if norm_sqr == 0 else dot/norm_sqr
                projection = [v_self[0]*ratio, v_self[1]*ratio]
                (_other.article.change_x, _other.article.change_y) = (2*projection[0]-v_other[0], 2*projection[1]-v_other[1])
        return True

class InvulnerableHitbox(Hitbox):
    def __init__(self,_owner,_hitboxLock,_hitboxVars):
        Hitbox.__init__(self, _owner, _hitboxLock, _hitboxVars)
        self.hitbox_type = 'invulnerable'

    def update(self):
        Hitbox.update(self)
   
    def compareTo(self, _other):
        self.owner.lockHitbox(_other)
        return True

def getXYFromDM(_direction,_magnitude):
    rad = math.radians(_direction)
    x = round(math.cos(rad) * _magnitude,5)
    y = -round(math.sin(rad) * _magnitude,5)
    return (x,y)

def getDirectionBetweenPoints(_p1, _p2):
    (x1, y1) = _p1
    (x2, y2) = _p2
    dx = x2 - x1
    dy = y1 - y2
    return (180 * math.atan2(dy, dx)) / math.pi 

transcendence_dict = {
                     'shield': -5,
                     'projectile': -1,
                     'grounded': 0,
                     'aerial': 1, 
                     'transcendent': 5
                     }
