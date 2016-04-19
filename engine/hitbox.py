import math
import pygame
import spriteManager
import abstractFighter

class HitboxLock(object):
    pass
    # Yes, it's that goddamn simple. 
    # All the HitboxLock class does is serve as a dummy for refcounting

class Hitbox(spriteManager.RectSprite):
    def __init__(self,center,size,owner,hitbox_lock, transcendence=0, priority=0):
        #Flip the distance from center if the fighter is facing the other way
        self.center = center
        if owner.facing == -1:
            self.center = (-self.center[0],self.center[1])
        spriteManager.RectSprite.__init__(self,pygame.Rect([0,0],size),[255,0,0])
        self.rect.center = [owner.rect.center[0] + self.center[0], owner.rect.center[1] + self.center[1]]
        self.owner = owner
        self.article = None
        self.hitbox_lock = hitbox_lock
        self.x_offset = center[0]
        self.y_offset = center[1]
        self.transcendence = transcendence
        self.priority = priority
        
    def onCollision(self,other):
        #This unbelievably convoluted function call basically means "if this thing's a fighter" without having to import fighter
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            other.hitboxContact.add(self)
    
    def update(self):
        return

    def compareTo(self, other):
        if (hasattr(other, 'transcendence') and hasattr(other, 'priority')) and not isinstance(other, ReflectorHitbox):
            if self.transcendence+other.transcendence <= 0:
                return (self.priority - other.priority) >= 8
        return True

    def recenterSelfOnOwner(self):
        self.rect.center = [self.owner.rect.center[0] + self.x_offset*self.owner.facing, self.owner.rect.center[1] + self.y_offset]
 
class Hurtbox(spriteManager.RectSprite):
    def __init__(self,owner,rect,color):
        self.owner = owner
        spriteManager.RectSprite.__init__(self, rect, color)
        
       
class DamageHitbox(Hitbox):
    def __init__(self,center,size,owner,
                 damage,baseKnockback,knockbackGrowth,trajectory,
                 hitstun,hitbox_lock,weight_influence=1,shield_multiplier=1, 
                 transcendence=0, priority_diff=0):
        Hitbox.__init__(self,center,size,owner,hitbox_lock,transcendence,damage+priority_diff)
        self.damage = damage
        self.baseKnockback = baseKnockback
        self.knockbackGrowth = knockbackGrowth
        self.trajectory = self.owner.getForwardWithOffset(trajectory)
        self.hitstun = hitstun
        self.weight_influence = weight_influence
        self.shield_multiplier = shield_multiplier
        
    def onCollision(self,other):
        Hitbox.onCollision(self, other)
        #This unbelievably convoluted function call basically means "if this thing's a fighter" without having to import fighter
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if other.shield:
                    other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                    if self.article is None:
                        self.owner.hitstop = math.floor(self.damage*self.shield_multiplier*3.0/4.0 + 2)
                else:
                    if self.article is None:
                        self.owner.hitstop = math.floor(self.damage / 4 + 2)
                    other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.weight_influence, self.hitstun)
        
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)
    
    def compareTo(self, other):
        return Hitbox.compareTo(self, other)
        
    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner() 

class SakuraiAngleHitbox(DamageHitbox):
    def __init__(self,center,size,owner,
                 damage,baseKnockback,knockbackGrowth,trajectory,
                 hitstun,hitbox_lock,weight_influence=1,shield_multiplier=1,
                 transcendence=0,priority_diff=0):
        DamageHitbox.__init__(self, center, size, owner, damage, baseKnockback, knockbackGrowth, 
                 trajectory, hitstun, hitbox_lock, weight_influence, shield_multiplier,
                 transcendence,priority_diff)

    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if other.shield:
                    other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                    if self.article is None:
                        self.owner.hitstop = math.floor(self.damage*self.shield_multiplier*3.0/4.0 + 2)
                else:
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

                    if self.article is None:
                        self.owner.hitstop = math.floor(self.damage / 4.0 + 2)
                    other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, angle, self.weight_influence, self.hitstun)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class AutolinkHitbox(DamageHitbox):
    def __init__(self,center,size,owner,damage,
                hitstun,hitbox_lock,x_bias=0,y_bias=0,shield_multiplier=1,
                velocity_multiplier=1,transcendence=0,priority_diff=0):
        DamageHitbox.__init__(self,center,size,owner,damage,0,0,0,hitstun,hitbox_lock,0,shield_multiplier,
                transcendence,priority_diff)
        self.velocity_multiplier=velocity_multiplier
        self.x_bias=x_bias
        self.y_bias=y_bias

    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if other.shield:
                    other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                    if self.article is None:
                        self.owner.hitstop = math.floor(self.damage*self.shield_multiplier*3.0/4.0 + 2)
                else:
                    if self.article is None:
                        velocity = math.sqrt((self.owner.change_x+self.x_bias) ** 2 + (self.owner.change_y+self.y_bias) ** 2)
                        angle = -math.atan2((self.owner.change_y+self.y_bias), (self.owner.change_x+self.x_bias))*180/math.pi
                        self.owner.hitstop = math.floor(self.damage / 4.0 + 2)
                        other.applyKnockback(self.damage, velocity*self.velocity_multiplier, 0, angle, 0, self.hitstun)
                    elif hasattr(self.article, 'change_x') and hasattr(self.article, 'change_y'):
                        velocity = math.sqrt((self.article.change_x+self.x_bias)**2 + (self.article.change_y+self.y_bias)**2)
                        angle = -math.atan2((self.article.change_y+self.y_bias), (self.article.change_x+self.x_bias))*180/math.pi
                        other.applyKnockback(self.damage, velocity*self.velocity_multiplier, 0, angle, 0, self.hitstun)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class FunnelHitbox(DamageHitbox):
    def __init__(self,center,size,owner,damage,knockback,trajectory,
                hitstun,hitbox_lock,x_draw=0.1,y_draw=0.1,
                shield_multiplier=1,transcendence=0,priority_diff=0):
        DamageHitbox.__init__(self,center,size,owner,damage,knockback,0,trajectory,hitstun,hitbox_lock,0,shield_multiplier,
                transcendence,priority_diff)
        self.x_draw=x_draw
        self.y_draw=y_draw

    def onCollision(self,other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x:x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if other.shield:
                    other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                    if self.article is None:
                        self.owner.hitstop = math.floor(self.damage*self.shield_multiplier*3.0/4.0 + 2)
                else:
                    if self.article is None:
                        x_diff = self.rect.centerx - other.rect.centerx
                        y_diff = self.rect.centery - other.rect.centery
                        (x_vel, y_vel) = abstractFighter.getXYFromDM(self.trajectory, self.baseKnockback)
                        x_vel += self.x_draw*x_diff
                        y_vel += self.y_draw*y_diff
                        self.owner.hitstop = math.floor(self.damage / 4.0 + 2)
                        other.applyKnockback(self.damage, math.hypot(x_vel,y_vel), 0, math.atan2(-y_vel,x_vel)*180.0/math.pi, 0, self.hitstun)
                    else:
                        x_diff = self.article.rect.centerx - other.rect.centerx
                        y_diff = self.article.rect.centery - other.rect.centery
                        (x_vel, y_vel) = abstractFighter.getXYFromDM(self.trajectory, self.baseKnockback)
                        x_vel += self.x_draw*x_diff
                        y_vel += self.y_draw*y_diff
                        other.applyKnockback(self.damage, math.hypot(x_vel,y_vel), 0, math.atan2(-y_vel,x_vel)*180.0/math.pi, 0, self.hitstun)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner()

class GrabHitbox(Hitbox):
    def __init__(self,center,size,owner,hitbox_lock, height=0, transcendence=-1, priority=0):
        Hitbox.__init__(self,center,size,owner,hitbox_lock,transcendence,priority)
        self.height = height;

    def onCollision(self,other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in list(map(lambda x:x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                self.owner.setGrabbing(other)
                self.owner.changeAction(self.owner.actions.Grabbing())
                other.changeAction(other.actions.Grabbed(self.height))

    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner()

class ReflectorHitbox(Hitbox):
    def __init__(self, center, size, owner, hitbox_lock, damage_multiplier, velocity_multiplier, hp, angle=90, transcendence=2):
        Hitbox.__init__(self,center,size,owner,hitbox_lock,transcendence,hp)
        self.damage_multiplier = damage_multiplier
        self.velocity_multiplier = velocity_multiplier
        self.angle = angle

    def compareTo(self, other):
        if other.article != None and other.article.owner != self.owner and hasattr(other.article, 'tags') and 'reflectable' in other.article.tags:
            if hasattr(other.article, 'changeOwner'):
                other.article.changeOwner(self.owner)
            if hasattr(other.article, 'change_x') and hasattr(other.article, 'change_y'):
                v_other = [other.article.change_x, other.article.change_y]
                v_self = abstractFighter.getXYFromDM(self.angle, 1.0)
                print(v_self)
                dot = v_other[0]*v_self[0]+v_other[1]*v_self[1]
                normsqr = v_self[0]*v_self[0]+v_self[1]*v_self[1]
                ratio = 1 if normsqr == 0 else dot/normsqr
                projection = [v_self[0]*ratio, v_self[1]*ratio]
                (other.article.change_x, other.article.change_y) = (self.velocity_multiplier*(2*projection[0]-v_other[0]), self.velocity_multiplier*(2*projection[1]-v_other[1]))
            if hasattr(other, 'damage') and hasattr(other, 'shield_multiplier'):
                self.priority -= other.damage*other.shield_multiplier
                other.damage *= other.damage*self.damage_multiplier
            elif hasattr(other, 'damage'):
                self.priority -= other.damage
                other.damage *= other.damage*self.damage_multiplier
        
        return Hitbox.compareTo(self, other)

    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner()

class PerfectShieldHitbox(ReflectorHitbox):
    def __init__(self, center, size, owner, hitbox_lock):
        ReflectorHitbox.__init__(self,center,size,owner,hitbox_lock,1,1,9999,0, -5)

    def compareTo(self, other):
        if other.article != None and other.article.owner != self.owner and hasattr(other.article, 'tags') and 'reflectable' in other.article.tags:
            if hasattr(other.article, 'changeOwner'):
                other.article.changeOwner(self.owner)
            if hasattr(other.article, 'change_x') and hasattr(other.article, 'change_y'):
                v_other = [other.article.change_x, other.article.change_y]
                v_self = abstractFighter.getXYFromDM(abstractFighter.getDirectionBetweenPoints(self.rect.center, other.article.rect.center)+90, 1.0)
                dot = v_other[0]*v_self[0]+v_other[1]*v_self[1]
                normsqr = v_self[0]*v_self[0]+v_self[1]*v_self[1]
                ratio = 1 if normsqr == 0 else dot/normsqr
                projection = [v_self[0]*ratio, v_self[1]*ratio]
                (other.article.change_x, other.article.change_y) = (self.velocity_multiplier*(2*projection[0]-v_other[0]), self.velocity_multiplier*(2*projection[1]-v_other[1]))

            if hasattr(other, 'damage'):
                self.priority -= other.damage
                other.damage = int(math.floor(other.damage*self.damage_multiplier))
        return Hitbox.compareTo(self, other)
