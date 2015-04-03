import spriteObject

class Hitbox(spriteObject.RectSprite):
    def __init__(self,center,size,owner,id=0):
        #Flip the distance from center if the fighter is facing the other way
        self.center = center
        if owner.facing == -1:
            self.center[0] = -self.center[0]
        print self.center, owner.rect.center
        spriteObject.RectSprite.__init__(self,[0,0],size,[255,0,0])
        self.rect.center = [owner.rect.center[0] + self.center[0], owner.rect.center[1] + self.center[1]]
        self.owner = owner
        self.id = id
        
    def onCollision(self,other):
        return
    
    def update(self):
        return

    def recenterSelfOnOwner(self):
        self.rect.topleft = [self.owner.rect.topleft[0] + self.topleft[0],
                             self.owner.rect.topleft[1] + self.topleft[1]]
        
    
class DamageHitbox(Hitbox):
    def __init__(self,center,size,owner,
                 damage,baseKnockback,knockbackGrowth,trajectory):
        Hitbox.__init__(self,center,size,owner,0)
        self.damage = damage
        self.baseKnockback = baseKnockback
        self.knockbackGrowth = knockbackGrowth
        self.trajectory = self.owner.getForwardWithOffset(trajectory)
        
    def onCollision(self,other):
        other.dealDamage(self.damage)
        
        other.applyKnockback(self.baseKnockback, self.knockbackGrowth, self.trajectory)
        print other.damage
        self.kill()
        
    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner() 
        
