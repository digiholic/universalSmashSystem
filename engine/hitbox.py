import math
import pygame
import spriteManager

class HitboxLock(object):
    def __init__(self,lockName=''):
        self.lockName = lockName
    # Yes, it's that goddamn simple. 
    # All the HitboxLock class does is serve as a dummy for refcounting

class Hitbox(spriteManager.RectSprite):
    def __init__(self,owner,lock,variables = dict()):
        self.owner = owner
        self.hitboxType = 'hitbox'
        
        self.variableDict = {
                       'center': (0,0),
                       'size': (0,0),
                       'damage': 0,
                       'baseKnockback': 0,
                       'knockbackGrowth': 0,
                       'trajectory': 0,
                       'hitstun': 0,
                       'chargeDamage': 0,
                       'chargeBKB': 0,
                       'chargeKBG': 0,
                       'weight_influence': 1,
                       'shield_multiplier': 1,
                       'transcendence': 0, 
                       'priority': 0,
                       'base_hitstun': 1,
                       'hitlag_multiplier': 1,
                       'velocity_multiplier': 1,
                       'x_bias': 0,
                       'y_bias': 0,
                       'x_draw': 0.1,
                       'y_draw': 0.1,
                       'hp': 0
                       }
        self.newVaraibles = variables
        self.variableDict.update(self.newVaraibles)
        
        #set the variables from the dict, so that we don't lose the initial value of the dict when modifying them
        #also lets us not have to go update all the old references. Score!
        for key,value in self.variableDict.iteritems():
            setattr(self, key, value)
            
        #Flip the distance from center if the fighter is facing the other way
        #if owner.facing == -1:
        #    self.center = (-self.center[0],self.center[1])
            
        #offset the trajectory based on facing
        self.trajectory = self.owner.getForwardWithOffset(self.trajectory)
        self.hitbox_lock = lock
        
        spriteManager.RectSprite.__init__(self,pygame.Rect([0,0],self.size),[255,0,0])
        self.rect.center = [owner.rect.center[0] + self.center[0], owner.rect.center[1] + self.center[1]]
        self.x_offset = self.center[0]
        self.y_offset = self.center[1]
        self.article = None
        
        
    def onCollision(self,other):
        #This unbelievably convoluted function call basically means "if this thing's a fighter" without having to import fighter
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            other.hitboxContact.add(self)
    
    def update(self):
        self.x_offset = self.center[0]
        self.y_offset = self.center[1]
        self.rect.width = self.size[0]
        self.rect.height = self.size[1]
        if self.article is None:
            self.rect.center = [self.owner.rect.center[0] + self.x_offset*self.owner.facing, self.owner.rect.center[1] + self.y_offset]
        else:
            self.rect.center = [self.article.rect.center[0] + self.x_offset, self.article.rect.center[1] + self.y_offset]
        
        
    def compareTo(self, other):
        if (hasattr(other, 'transcendence') and hasattr(other, 'priority')) and not isinstance(other, InertHitbox):
            if self.transcendence+other.transcendence <= 0:
                return (self.priority - other.priority) >= 8
        return True
    
        
class Hurtbox(spriteManager.RectSprite):
    def __init__(self,owner,rect,color):
        self.owner = owner
        spriteManager.RectSprite.__init__(self, rect, color)

class InertHitbox(Hitbox):
    def __init__(self, owner, hitbox_lock, hitboxVars):
        Hitbox.__init__(self, owner, hitbox_lock, hitboxVars)
        self.hitboxType = 'inert'
        
class DamageHitbox(Hitbox):
    def __init__(self,owner,lock,variables):
        Hitbox.__init__(self,owner,lock,variables)
        self.hitboxType = 'damage'
        
    def onCollision(self,other):
        Hitbox.onCollision(self, other)
        #This unbelievably convoluted function call basically means "if this thing's a fighter" without having to import fighter
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.damage/4.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.weight_influence, self.hitstun, self.base_hitstun, self.hitlag_multiplier)
        
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)
    
    def compareTo(self, other):
        return Hitbox.compareTo(self, other)

    def update(self):
        Hitbox.update(self) 
    
    def charge(self):
        self.damage += self.chargeDamage
        self.baseKnockback += self.chargeBKB
        self.knockbackGrowth += self.chargeKBG
        print(self.damage)
        
class SakuraiAngleHitbox(DamageHitbox):
    def __init__(self,owner,lock,variables):
        DamageHitbox.__init__(self,owner,lock,variables)
        self.hitboxType = 'sakurai'
        
    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.damage/4.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                p = float(other.damage)
                d = float(self.damage)
                w = float(other.var['weight'])
                s = float(self.knockbackGrowth)
                b = float(self.baseKnockback)
                totalKB = (((((p/10) + (p*d)/20) * (200/(w*self.weight_influence+100))*1.4) + 5) * s) + b

                angle = 0
                if (self.baseKnockback > 0):
                    # Calculate the resulting angle
                    knockbackRatio = totalKB/self.baseKnockback
                    xVal = math.sqrt(knockbackRatio**2+1)/math.sqrt(2)
                    yVal = math.sqrt(knockbackRatio**2-1)/math.sqrt(2)
                    angle = math.atan2(yVal*math.sin(float(self.trajectory)/180*math.pi),xVal*math.cos(float(self.trajectory)/180*math.pi))/math.pi*180
                other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, angle, self.weight_influence, self.hitstun, self.base_hitstun, self.hitlag_multiplier)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class AutolinkHitbox(DamageHitbox):
    def __init__(self,owner,lock,variables):
        DamageHitbox.__init__(self,owner,lock,variables)
        self.hitboxType = 'autolink'
        
    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.damage/4.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                    velocity = math.sqrt((self.owner.change_x+self.x_bias) ** 2 + (self.owner.change_y+self.y_bias) ** 2)
                    angle = -math.atan2((self.owner.change_y+self.y_bias), (self.owner.change_x+self.x_bias))*180/math.pi
                    other.applyKnockback(self.damage, velocity*self.velocity_multiplier, 0, angle, 0, self.hitstun, self.base_hitstun, self.hitlag_multiplier)
                elif hasattr(self.article, 'change_x') and hasattr(self.article, 'change_y'):
                    velocity = math.sqrt((self.article.change_x+self.x_bias)**2 + (self.article.change_y+self.y_bias)**2)
                    angle = -math.atan2((self.article.change_y+self.y_bias), (self.article.change_x+self.x_bias))*180/math.pi
                    other.applyKnockback(self.damage, velocity*self.velocity_multiplier, 0, angle, 0, self.hitstun, self.base_hitstun, self.hitlag_multiplier)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class FunnelHitbox(DamageHitbox):
    def __init__(self,owner,lock,variables):
        DamageHitbox.__init__(self,owner,lock,variables)
        self.hitboxType = 'funnel'
        
    def onCollision(self,other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x:x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if self.article is None:
                    self.owner.applyPushback(self.damage/4.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                    x_diff = self.rect.centerx - other.rect.centerx
                    y_diff = self.rect.centery - other.rect.centery
                    (x_vel, y_vel) = getXYFromDM(self.trajectory, self.baseKnockback)
                    x_vel += self.x_draw*x_diff
                    y_vel += self.y_draw*y_diff
                    other.applyKnockback(self.damage, math.hypot(x_vel,y_vel), 0, math.atan2(-y_vel,x_vel)*180.0/math.pi, 0, self.hitstun, self.base_hitstun, self.hitlag_multiplier)
                else:
                    x_diff = self.article.rect.centerx - other.rect.centerx
                    y_diff = self.article.rect.centery - other.rect.centery
                    (x_vel, y_vel) = getXYFromDM(self.trajectory, self.baseKnockback)
                    x_vel += self.x_draw*x_diff
                    y_vel += self.y_draw*y_diff
                    other.applyKnockback(self.damage, math.hypot(x_vel,y_vel), 0, math.atan2(-y_vel,x_vel)*180.0/math.pi, 0, self.hitstun, self.base_hitstun, self.hitlag_multiplier)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class GrabHitbox(Hitbox):
    def __init__(self,owner,lock,variables):
        Hitbox.__init__(self, owner, lock, variables)
        
        self.hitboxType = 'grab'

    def onCollision(self,other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x:x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                self.owner.setGrabbing(other)
                self.owner.doAction('Grabbing')
                other.doGrabbed(self.height)
                
    def compareTo(self, other):
        if not isinstance(other, DamageHitbox) and not isinstance(other, GrabHitbox) and other.owner is not None:
            self.owner.setGrabbing(other.owner)
            self.owner.changeAction(self.owner.actions.Grabbing())
            other.owner.changeAction(other.owner.actions.Grabbed(self.height))
            return True
        return Hitbox.compareTo(self, other)

class ReflectorHitbox(InertHitbox):
    def __init__(self,owner,hitbox_lock,hitboxVars):
        InertHitbox.__init__(self,owner,hitbox_lock,hitboxVars)
        self.hitboxType = 'reflector'
        
    def compareTo(self, other):
        if self.owner.lockHitbox(other) and other.article != None and other.article.owner != self.owner and hasattr(other.article, 'tags') and 'reflectable' in other.article.tags:
            if hasattr(other.article, 'changeOwner'):
                other.article.changeOwner(self.owner)
            if hasattr(other.article, 'change_x') and hasattr(other.article, 'change_y'):
                v_other = [other.article.change_x, other.article.change_y]
                v_self = getXYFromDM(self.trajectory, 1.0)
                dot = v_other[0]*v_self[0]+v_other[1]*v_self[1]
                normsqr = v_self[0]*v_self[0]+v_self[1]*v_self[1]
                ratio = 1 if normsqr == 0 else dot/normsqr
                projection = [v_self[0]*ratio, v_self[1]*ratio]
                (other.article.change_x, other.article.change_y) = (self.velocity_multiplier*(2*projection[0]-v_other[0]), -1*self.velocity_multiplier*(2*projection[1]-v_other[1]))
            if hasattr(other, 'damage') and hasattr(other, 'shield_multiplier'):
                self.priority -= other.damage*other.shield_multiplier
                other.damage *= other.damage*self.damage_multiplier
            elif hasattr(other, 'damage'):
                self.priority -= other.damage
                other.damage *= other.damage*self.damage_multiplier
            prevailed = Hitbox.compareTo(self, other)
            if not prevailed:
                self.owner.change_y = -15
                self.owner.invincible = 20
                self.owner.doStunned(200)
        return True

    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class ShieldHitbox(Hitbox):
    def __init__(self, center, size, owner, hitbox_lock):
        Hitbox.__init__(self,owner,hitbox_lock,{'center':center,
                                                'size':size,
                                                'transcendence':-5,
                                                'priority':owner.shieldIntegrity-8
                                                })
        self.hitboxType = 'shield'

    def update(self):
        self.priority = self.owner.shieldIntegrity-8
        self.rect.width = self.owner.shieldIntegrity*self.owner.var['shieldSize']
        self.rect.height = self.owner.shieldIntegrity*self.owner.var['shieldSize']
        Hitbox.update(self)
   
    def compareTo(self, other):
        if isinstance(other, DamageHitbox) and self.owner.lockHitbox(other):
            self.owner.shieldDamage(math.floor(other.damage*other.shield_multiplier))
            prevailed = Hitbox.compareTo(self, other)
            if not prevailed:
                self.owner.change_y = -15
                self.owner.invincible = 20
                self.owner.doStunned(200)
        return True

class PerfectShieldHitbox(Hitbox):
    def __init__(self, center, size, owner, hitbox_lock):
        Hitbox.__init__(self,owner,hitbox_lock,{'center':center,
                                                'size':size,
                                                'transcendence':-5,
                                                'priority':float("inf")
                                                })
        self.hitboxType = 'perfectShield'

    def update(self):
        self.rect.width = self.owner.shieldIntegrity*self.owner.var['shieldSize']
        self.rect.height = self.owner.shieldIntegrity*self.owner.var['shieldSize']
        Hitbox.update(self)

    def compareTo(self, other):
        if self.owner.lockHitbox(other) and other.article != None and other.article.owner != self.owner and hasattr(other.article, 'tags') and 'reflectable' in other.article.tags:
            if hasattr(other.article, 'changeOwner'):
                other.article.changeOwner(self.owner)
            if hasattr(other.article, 'change_x') and hasattr(other.article, 'change_y'):
                v_other = [other.article.change_x, other.article.change_y]
                v_self = getXYFromDM(getDirectionBetweenPoints(self.rect.center, other.article.rect.center)+90, 1.0)
                dot = v_other[0]*v_self[0]+v_other[1]*v_self[1]
                normsqr = v_self[0]*v_self[0]+v_self[1]*v_self[1]
                ratio = 1 if normsqr == 0 else dot/normsqr
                projection = [v_self[0]*ratio, v_self[1]*ratio]
                (other.article.change_x, other.article.change_y) = (2*projection[0]-v_other[0], 2*projection[1]-v_other[1])
        return True

def getXYFromDM(direction,magnitude):
    rad = math.radians(direction)
    x = round(math.cos(rad) * magnitude,5)
    y = -round(math.sin(rad) * magnitude,5)
    return (x,y)

def getDirectionBetweenPoints(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    dx = x2 - x1
    dy = y1 - y2
    return (180 * math.atan2(dy, dx)) / math.pi 