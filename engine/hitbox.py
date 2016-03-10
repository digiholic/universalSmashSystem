import spriteObject
import math

class HitboxLock(object):
    pass
    # Yes, it's that goddamn simple. 
    # All the HitboxLock class does is serve as a dummy for refcounting

class Hitbox(spriteObject.RectSprite):
    def __init__(self,center,size,owner,hitbox_lock):
        #Flip the distance from center if the fighter is facing the other way
        self.center = center
        if owner.facing == -1:
            self.center = (-self.center[0],self.center[1])
        spriteObject.RectSprite.__init__(self,[0,0],size,[255,0,0])
        self.rect.center = [owner.rect.center[0] + self.center[0], owner.rect.center[1] + self.center[1]]
        self.owner = owner
        self.article = None
        self.hitbox_lock = hitbox_lock
        self.x_offset = center[0]
        self.y_offset = center[1]
        
    def onCollision(self,other):
        #This unbelievably convoluted function call basically means "if this thing's a fighter" without having to import fighter
        if 'AbstractFighter' in map(lambda(x):x.__name__,other.__class__.__bases__) + [other.__class__.__name__]:
            other.hitboxContact.add(self)
    
    def update(self):
        return

    def recenterSelfOnOwner(self):
        self.rect.center = [self.owner.rect.center[0] + self.x_offset, self.owner.rect.center[1] + self.y_offset]
        
class DamageHitbox(Hitbox):
    def __init__(self,center,size,owner,
                 damage,baseKnockback,knockbackGrowth,trajectory,
                 hitstun,hitbox_lock,weight_influence=1,shield_multiplier=1):
        Hitbox.__init__(self,center,size,owner,hitbox_lock)
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
        if 'AbstractFighter' in map(lambda(x):x.__name__,other.__class__.__bases__) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if other.shield:
                    other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                else:
                    other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.weight_influence, self.hitstun)
        
        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)
        
    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner() 
 
    def compareTo(self,other):
        if hasattr(other, 'damage'):
            return (self.damage > other.damage)
        else:
            return True

class SakuraiAngleHitbox(DamageHitbox):
    def __init__(self,center,size,owner,
                 damage,baseKnockback,knockbackGrowth,trajectory,
                 hitstun,hitbox_lock,weight_influence=1,shield_multiplier=1):
        DamageHitbox.__init__(self, center, size, owner, damage, baseKnockback, knockbackGrowth, 
                 trajectory, hitstun, hitbox_lock, weight_influence, shield_multiplier)

    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in map(lambda(x):x.__name__,other.__class__.__bases__) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if other.shield:
                    other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                else:
                    p = float(other.damage)
                    d = float(self.damage)
                    w = float(other.var['weight'])
                    s = float(self.knockbackGrowth)
                    b = float(self.baseKnockback)
                    totalKB = (((((p/10) + (p*d)/20) * (200/(w*self.weight_influence+100))*1.4) + 5) * s) + b

                    # Calculate the resulting angle
                    knockbackRatio = totalKB/self.baseKnockback
                    xVal = math.sqrt(knockbackRatio**2+1)/math.sqrt(2)
                    yVal = math.sqrt(knockbackRatio**2-1)/math.sqrt(2)
                    angle = math.atan2(yVal*math.sin(float(self.trajectory)/180*math.pi),xVal*math.cos(float(self.trajectory)/180*math.pi))/math.pi*180

                    other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, angle, self.weight_influence, self.hitstun)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class AutolinkHitbox(DamageHitbox):
    def __init__(self,center,size,owner,damage,
                hitstun,hitbox_lock,shield_multiplier=1,velocity_multiplier=1):
        DamageHitbox.__init__(self,center,size,owner,damage,0,0,0,hitstun,hitbox_lock,0,shield_multiplier)
        self.velocity_multiplier=velocity_multiplier

    def onCollision(self, other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in map(lambda(x):x.__name__,other.__class__.__bases__) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                if other.shield:
                    other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                else:
                    velocity = math.sqrt(self.owner.change_x ** 2 + self.owner.change_y ** 2)
                    angle = math.atan2(self.owner.change_y, self.owner.change_x)
                    other.applyKnockback(self.damage, velocity*self.velocity_multiplier, 0, self.owner.getForwardWithOffset(angle), 0, self.hitstun)

        if self.article and hasattr(self.article, 'onCollision'):
            self.article.onCollision(other)

class GrabHitbox(Hitbox):
    def __init__(self,center,size,owner,hitbox_lock, height=0):
        Hitbox.__init__(self,center,size,owner,hitbox_lock)
        self.height = height;

    def onCollision(self,other):
        Hitbox.onCollision(self, other)
        if 'AbstractFighter' in map(lambda(x):x.__name__,other.__class__.__bases__) + [other.__class__.__name__]:
            if other.lockHitbox(self):
                self.owner.setGrabbing(other)
                self.owner.changeAction(self.owner.actions.Grabbing())
                other.changeAction(other.actions.Grabbed(self.height))

    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner()

