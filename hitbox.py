import spriteObject

class Hitbox(spriteObject.RectSprite):
    def __init__(self,topleft,size,owner,id=0):
        spriteObject.RectSprite.__init__(self,[owner.rect.topleft[0] + topleft[0],
                                               owner.rect.topleft[1] + topleft[1]],size,[255,0,0])
        self.topleft = topleft
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
    def __init__(self,topleft,size,owner,
                 damage,baseKnockback,knockbackGrowth,trajectory):
        Hitbox.__init__(self,topleft,size,owner,0)
        self.damage = damage
        self.baseKnockback = baseKnockback
        self.knockbackGrowth = knockbackGrowth
        self.trajectory = trajectory
        
    def onCollision(self,other):
        other.dealDamage(self.damage)
        other.applyKnockback(self.baseKnockback, self.knockbackGrowth, self.trajectory)
        print other.damage
        self.kill()
        
    def update(self):
        Hitbox.update(self)
        self.recenterSelfOnOwner() 
        
