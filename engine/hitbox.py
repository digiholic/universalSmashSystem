import math
import random
import pygame
import spriteManager
import settingsManager
from global_functions import *

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
                       'hp': 50,
                       'ignore_shields': False,
                       'ignore_armor': False, 
                       'trail_color': None,
                       'charge_source': 'charge'
                       }
        self.newVariables = _variables
        self.variable_dict.update(self.newVariables)
        
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
        self.rect.center = [_owner.posx + self.center[0], _owner.posy + self.center[1]]
        self.article = None

        if self.trail_color is None: 
            if self.article is None:
                self.trail_color = settingsManager.getSetting('playerColor' + str(self.owner.player_num))
            else:
                self.trail_color = settingsManager.getSetting('playerColor' + str(self.article.owner.player_num))
        
        self.owner_on_hit_actions = []
        self.other_on_hit_actions = []
        self.charge = 0

    def getOnHitSubactions(self, _other):
        return self.other_on_hit_actions
        
    def onCollision(self,_other):
        if _other.onHit(self):
            if self.owner_on_hit_actions:
                for subact in self.owner_on_hit_actions:
                    subact.execute(self.owner.current_action,self.owner)
            return True
        return False
                
    def update(self):
        self.rect.width = self.size[0]
        self.rect.height = self.size[1]
        if self.article is None:
            self.rect.center = [self.owner.posx + self.center[0]*self.owner.facing, self.owner.posy + self.center[1]]
        elif hasattr(self.article, "facing"):
            self.rect.center = [self.article.rect.center[0] + self.center[0]*self.article.facing, self.article.rect.center[1] + self.center[1]]
        else:
            self.rect.center = [self.article.rect.center[0] + self.center[0], self.article.rect.center[1] + self.center[1]]
        if self.article == None:
            if hasattr(self.owner.current_action, self.charge_source):
                self.charge = getattr(self.owner.current_action, self.charge_source)
        else:
            if hasattr(self.article, self.charge_source):
                self.charge = getattr(self.article, self.charge_source)
        
    def getTrajectory(self):
        return self.trajectory

    def compareTo(self, _other):
        if not isinstance(_other, InertHitbox) and (isinstance(_other, DamageHitbox) or isinstance(_other, GrabHitbox)) and self.owner != _other.owner and _other.hitbox_lock not in self.owner.hitbox_lock:
            if self.transcendence + _other.transcendence > 0: return 0
            elif self.priority - _other.priority >= 8: return 1
            else: return -1
        else: return 0
    
    def activate(self):
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
        self.variable_dict['priority'] += self.damage

    def getOnHitSubactions(self, _other):
        import engine.subaction as subaction
        hitstun_subaction = subaction.applyHitstun(self.damage+self.charge_damage*self.charge, self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, self.trajectory, self.weight_influence, self.base_hitstun, self.hitstun_multiplier)
        knockback_subaction = subaction.applyScaledKnockback(self.damage+self.charge_damage*self.charge, self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, self.trajectory, self.weight_influence)
        damage_subaction = subaction.dealDamage(self.damage+self.charge_damage*self.charge)
        compensation_subaction = subaction.compensateResistance(self.base_hitstun/2.0)
        hitstop_subaction = subaction.applyHitstop(((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier, (self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.getTrajectory())
        return [hitstun_subaction,damage_subaction,knockback_subaction,compensation_subaction,hitstop_subaction]+self.other_on_hit_actions
        
    def onCollision(self,_other):
        if Hitbox.onCollision(self, _other):
            if self.article is None:
                self.owner.applyPushback((self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.trajectory+180, ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier)
            self.owner.data_log.addToData('Damage Dealt',self.damage)
            _other.owner.trail_color = self.trail_color
            
            offset = random.randrange(0, 359)
            hit_intersection = self.rect.clip(_other.rect).center
            hitlag = ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier
            from article import HitArticle
            for i in range(int(hitlag)):
                art = HitArticle(self.owner, hit_intersection, 0.5, offset+i*360/int(hitlag), 0.5*hitlag, .4, self.trail_color)
                self.owner.articles.add(art)
        
            if self.article and hasattr(self.article, 'onCollision'):
                self.article.onCollision(_other.owner)
            return True
        return False
        
    def compareTo(self, _other):
        clank_state = Hitbox.compareTo(self, _other)
        if clank_state == -1:
            if self.article is None:
                self.owner.applyPushback((self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.getTrajectory()+180, ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier + ((_other.damage+_other.charge_damage*_other.charge) / 4.0 + 2.0)*_other.hitlag_multiplier)
            return -1
        else: return clank_state
        
class SakuraiAngleHitbox(DamageHitbox):
    def __init__(self,_owner,_lock,_variables):
        DamageHitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'sakurai'

    def getOnHitSubactions(self, _other):
        import engine.subaction as subaction
        p = float(_other.owner.damage)
        d = float(self.damage+self.charge_damage*self.charge)
        w = float(_other.owner.stats['weight']) * settingsManager.getSetting('weight')
        s = float(self.knockback_growth+self.charge_knockback_growth*self.charge)
        b = float(self.base_knockback+self.charge_base_knockback*self.charge)
        total_kb = (((((p/10) + (p*d)/20) * (200/(w*self.weight_influence+100))*1.4) + 5) * s) + b
        angle = 0
        if (self.base_knockback > 0):
            # Calculate the resulting angle
            knockback_ratio = total_kb*self.velocity_multiplier/self.base_knockback
            x_val = math.sqrt(knockback_ratio**2+1)/math.sqrt(2)
            y_val = math.sqrt(knockback_ratio**2-1)/math.sqrt(2)
            angle = math.atan2(y_val*math.sin(float(self.trajectory)/180*math.pi),x_val*math.cos(float(self.trajectory)/180*math.pi))/math.pi*180

        hitstun_subaction = subaction.applyHitstun(self.damage+self.charge_damage*self.charge, self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, angle, self.weight_influence, self.base_hitstun, self.hitstun_multiplier)
        knockback_subaction = subaction.applyScaledKnockback(self.damage+self.charge_damage*self.charge, self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, angle, self.weight_influence)
        damage_subaction = subaction.dealDamage(self.damage+self.charge_damage*self.charge)
        compensation_subaction = subaction.compensateResistance(self.base_hitstun/2.0)
        hitstop_subaction = subaction.applyHitstop(((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier, (self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.getTrajectory())
        return [hitstun_subaction,damage_subaction,knockback_subaction,compensation_subaction,hitstop_subaction]+self.other_on_hit_actions
        
    def onCollision(self, _other):
        if Hitbox.onCollision(self, _other):
            if self.article is None:
                self.owner.applyPushback((self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.trajectory+180, ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier)
            self.owner.data_log.addToData('Damage Dealt',self.damage)
            _other.owner.trail_color = self.trail_color
            offset = random.randrange(0, 359)
            hit_intersection = self.rect.clip(_other.rect).center
            ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier
            from article import HitArticle
            for i in range(int(hitlag)):
                art = HitArticle(self.owner, hit_intersection, 0.5, offset+i*360/int(hitlag), 0.5*hitlag, .4, self.trail_color)
                self.owner.articles.add(art)

            if self.article and hasattr(self.article, 'onCollision'):
                self.article.onCollision(_other.owner)
            return True
        return False
    
class AutolinkHitbox(DamageHitbox):
    def __init__(self,_owner,_lock,_variables):
        DamageHitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'autolink'

    def getOnHitSubactions(self, _other):
        import engine.subaction as subaction
        if self.article is None:
            velocity = math.sqrt((self.owner.change_x+self.x_bias) ** 2 + (self.owner.change_y+self.y_bias) ** 2)
            angle = -math.atan2((self.owner.change_y+self.y_bias), (self.owner.change_x+self.x_bias))*180/math.pi
            angle = self.owner.getForwardWithOffset(self.owner.facing*(angle+self.trajectory))
        elif hasattr(self.article, 'change_x') and hasattr(self.article, 'change_y'):
            velocity = math.sqrt((self.article.change_x+self.x_bias)**2 + (self.article.change_y+self.y_bias)**2)
            angle = -math.atan2((self.article.change_y+self.y_bias), (self.article.change_x+self.x_bias))*180/math.pi
            angle = getForwardWithOffset(self.article.facing*(angle+self.trajectory), self.article)

        hitstun_subaction = subaction.applyHitstun(self.damage+self.charge_damage*self.charge, velocity*self.velocity_multiplier+self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, angle, self.weight_influence, self.base_hitstun, self.hitstun_multiplier)
        knockback_subaction = subaction.applyScaledKnockback(self.damage+self.charge_damage*self.charge, velocity*self.velocity_multiplier+self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, angle, self.weight_influence)
        damage_subaction = subaction.dealDamage(self.damage+self.charge_damage*self.charge)
        compensation_subaction = subaction.compensateResistance(self.base_hitstun/2.0)
        hitstop_subaction = subaction.applyHitstop(((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier, (self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.getTrajectory())
        return [hitstun_subaction,damage_subaction,knockback_subaction,compensation_subaction,hitstop_subaction]+self.other_on_hit_actions

    def getTrajectory(self):
        if self.owner.change_y+self.y_bias == 0 and self.owner.change_x + self.x_bias == 0:
            return self.trajectory + 90
        else: 
            return self.trajectory-math.atan2(self.y_bias, self.x_bias)*180/math.pi
        
    def onCollision(self, _other):
        if Hitbox.onCollision(self, _other):
            if self.article is None:
                self.owner.applyPushback((self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.getTrajectory()+180, ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier)
            self.owner.data_log.addToData('Damage Dealt',self.damage)
            _other.owner.trail_color = self.trail_color
            offset = random.randrange(0, 359)
            hit_intersection = self.rect.clip(_other.rect).center
            hitlag = ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier
            from article import HitArticle
            for i in range(int(hitlag)):
                art = HitArticle(self.owner, hit_intersection, 0.5, offset+i*360/int(hitlag), 0.5*hitlag, .4, self.trail_color)
                self.owner.articles.add(art)

            if self.article and hasattr(self.article, 'onCollision'):
                self.article.onCollision(_other.owner)
            return True
        return False
    
class FunnelHitbox(DamageHitbox):
    def __init__(self,_owner,_lock,_variables):
        DamageHitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'funnel'

    def getOnHitSubactions(self, _other):
        import engine.subaction as subaction
        if self.article is None:
            x_diff = self.rect.centerx - _other.owner.posx
            y_diff = self.rect.centery - _other.owner.posy
        elif hasattr(self.article, 'change_x') and hasattr(self.article, 'change_y'):
            x_diff = self.article.rect.centerx - _other.owner.posx
            y_diff = self.article.rect.centery - _other.owner.posy

        x_vel = self.x_bias+self.x_draw*x_diff
        y_vel = self.y_bias+self.y_draw*y_diff
        velocity = math.hypot(x_vel, y_vel)
        angle = self.owner.getForwardWithOffset(self.owner.facing*(math.degrees(-math.atan2(y_vel,x_vel))+self.trajectory))

        hitstun_subaction = subaction.applyHitstun(self.damage+self.charge_damage*self.charge, velocity*self.velocity_multiplier+self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, angle, self.weight_influence, self.base_hitstun, self.hitstun_multiplier)
        knockback_subaction = subaction.applyScaledKnockback(self.damage+self.charge_damage*self.charge, velocity*self.velocity_multiplier+self.base_knockback+self.charge_base_knockback*self.charge, self.knockback_growth+self.charge_knockback_growth*self.charge, angle, self.weight_influence)
        damage_subaction = subaction.dealDamage(self.damage+self.charge_damage*self.charge)
        compensation_subaction = subaction.compensateResistance(self.base_hitstun/2.0)
        hitstop_subaction = subaction.applyHitstop(((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier, (self.base_knockback+self.charge_base_knockback*self.charge)/5.0, self.getTrajectory())
        return [hitstun_subaction,damage_subaction,knockback_subaction,compensation_subaction,hitstop_subaction]+self.other_on_hit_actions

    def getTrajectory(self):
        if self.owner.change_y+self.y_bias == 0 and self.owner.change_x + self.x_bias == 0:
            return self.trajectory + 90
        else: 
            return self.trajectory-math.atan2(self.y_bias, self.x_bias)*180/math.pi
        
    def onCollision(self,_other):
        if Hitbox.onCollision(self, _other):
            if self.article is None:
                self.owner.applyPushback(self.base_knockback/5.0, self.getTrajectory()+180, ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier)
            self.owner.data_log.addToData('Damage Dealt',self.damage)
                
            _other.owner.trail_color = self.trail_color
            offset = random.randrange(0, 359)
            hit_intersection = self.rect.clip(_other.rect).center
            hitlag = ((self.damage+self.charge_damage*self.charge) / 4.0 + 2.0)*self.hitlag_multiplier
            from article import HitArticle
            for i in range(int(hitlag)):
                art = HitArticle(self.owner, hit_intersection, 0.5, offset+i*360/int(hitlag), 0.5*hitlag, .4, self.trail_color)
                self.owner.articles.add(art)

            if self.article and hasattr(self.article, 'onCollision'):
                self.article.onCollision(_other.owner)
            return True
        return False
    
class GrabHitbox(Hitbox):
    def __init__(self,_owner,_lock,_variables):
        Hitbox.__init__(self, _owner, _lock, _variables)
        self.hitbox_type = 'grab'

    def onCollision(self,_other):
        from engine import baseActions
        if hasClass(_other.owner, 'AbstractFighter') and ((not isinstance(_other.owner.current_action, baseActions.Trapped) and _other.owner.tech_window == 0) or self.ignore_armor) and Hitbox.onCollision(self, _other):
            if self.article is None:
                self.owner.grabbing = _other.owner
                _other.owner.grabbed_by = self.owner
            #TODO: Add functionality for article command grabs
            return True
        return False
    
    def compareTo(self, _other):
        clank_state = Hitbox.compareTo(self, _other)
        if clank_state == 1:
            return 1
        elif clank_state == 0:
            return 0
        else: 
            if self.article is None:
                self.owner.applyPushback(self.base_knockback/5.0, self.getTrajectory()+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier + (_other.damage / 4.0 + 2.0)*_other.hitlag_multiplier)
            return -1

class ThrowHitbox(Hitbox):
    def __init__(self,_owner,_lock,_variables):
        Hitbox.__init__(self,_owner,_lock,_variables)
        self.hitbox_type = 'throw'
    
    def activate(self):
        Hitbox.activate(self)
        if (self.owner == self.owner.grabbing.grabbed_by):
            self.owner.data_log.addToData('Damage Dealt',self.damage)
            self.owner.grabbing.applyKnockback(self.damage, self.base_knockback, self.knockback_growth, self.trajectory, self.weight_influence, self.hitstun_multiplier, self.base_hitstun, self.hitlag_multiplier, self.ignore_armor)
            self.owner.grabbing.trail_color = self.trail_color
            self.kill()
            
class ReflectorHitbox(InertHitbox):
    def __init__(self,_owner,_hitboxLock,_hitboxVars):
        InertHitbox.__init__(self,_owner,_hitboxLock,_hitboxVars)
        self.hitbox_type = 'reflector'
        self.priority += self.hp
        self.variable_dict['priority'] += self.hp
        
    def compareTo(self, _other):
        clank_state = Hitbox.compareTo(self, _other)
        if clank_state == 1 and self.hp >= 0:
            if not isinstance(_other, InertHitbox) and (isinstance(_other, DamageHitbox) or isinstance(_other, GrabHitbox)) and self.owner != _other.owner and _other.hitbox_lock not in self.owner.hitbox_lock and _other.article != None and _other.article.owner != self.owner and hasattr(_other.article, 'tags') and 'reflectable' in _other.article.tags:
                if hasattr(_other.article, 'changeOwner'):
                    _other.article.changeOwner(self.owner)
                if hasattr(_other.article, 'change_x') and hasattr(_other.article, 'change_y'):
                    if self.article is None:
                        x_diff = self.rect.centerx - _other.article.rect.centerx
                        y_diff = self.rect.centery - _other.article.rect.centery
                    else:
                        x_diff = self.article.rect.centerx - _other.article.rect.centerx
                        y_diff = self.article.rect.centery - _other.article.rect.centery
                    x_vel = self.x_bias+self.x_draw*x_diff
                    y_vel = self.y_bias+self.y_draw*y_diff
                    reflect_deviation = math.degrees(math.atan2(-y_vel,x_vel))+self.owner.getForwardWithOffset(self.trajectory)*(1 if _other.article.facing == -1 else -1)
                    reflect_angle = math.degrees(math.atan2(_other.article.change_y, _other.article.change_x*(-1 if _other.article.facing == -1 else 1)))+180+reflect_deviation
                    reflect_speed = math.hypot(_other.article.change_x, _other.article.change_y)
                    (_other.article.change_x, _other.article.change_y) = getXYFromDM(reflect_angle, reflect_speed)
                if hasattr(_other, 'damage') and hasattr(_other, 'shield_multiplier'):
                    self.priority -= _other.damage*_other.shield_multiplier
                    self.hp -= _other.damage*_other.shield_multiplier
                    _other.damage *= self.damage_multiplier
                elif hasattr(_other, 'damage'):
                    self.priority -= _other.damage
                    self.hp -= _other.damage
                    _other.damage *= self.damage_multiplier
            return 1
        elif clank_state == -1:
            self.owner.change_y = -15
            self.owner.invulnerable = 20
            self.owner.doStunned(400)
            return -1
        else: return 0

    def onCollision(self, _other):
        if Hitbox.onCollision(self, _other):
            if self.article and hasattr(self.article, 'onCollision'):
                self.article.onCollision(_other.owner)
            return True
        return False

class AbsorberHitbox(InertHitbox):
    def __init__(self,_owner,_hitboxLock,_hitboxVars):
        InertHitbox.__init__(self,_owner,_hitboxLock,_hitboxVars)
        self.hitbox_type = 'absorber'
        
    def compareTo(self, _other):
        if Hitbox.compareTo(self, _other) == 1:
            if not isinstance(_other, InertHitbox) and (isinstance(_other, DamageHitbox) or isinstance(_other, GrabHitbox)) and self.owner != _other.owner and _other.article != None and _other.article.owner != self.owner and hasattr(_other.article, 'tags') and 'absorbable' in _other.article.tags:
                _other.article.deactivate()
                if hasattr(_other, 'damage'):
                    self.owner.dealDamage(-_other.damage*self.damage_multiplier)
        return 0

    def onCollision(self, _other):
        if Hitbox.onCollision(self, _other):
            if self.article and hasattr(self.article, 'onCollision'):
                self.article.onCollision(_other.owner)
            return True
        return False

class ShieldHitbox(Hitbox):
    def __init__(self, _owner, _hitboxLock, _hitboxVars):
        Hitbox.__init__(self,_owner,_hitboxLock,_hitboxVars)
        self.hitbox_type = 'shield'

    def update(self):
        Hitbox.update(self)
   
    def compareTo(self, _other):
        clank_state = Hitbox.compareTo(self, _other)
        if clank_state == 1 and self.hp >= 0:
            if not isinstance(_other, InertHitbox) and (isinstance(_other, DamageHitbox) or isinstance(_other, GrabHitbox)) and not _other.ignore_shields and self.owner.lockHitbox(_other):
                if hasattr(_other, 'damage') and hasattr(_other, 'shield_multiplier'):
                    self.priority -= _other.damage*_other.shield_multiplier
                    self.hp -= _other.damage*_other.shield_multiplier
                elif hasattr(_other, 'damage'):
                    self.priority -= _other.damage
                    self.hp -= _other.damage
                if _other.article is None:
                    _other.owner.applyPushback(_other.base_knockback/5.0, _other.getTrajectory()+180, (_other.damage / 4.0 + 2.0)*_other.hitlag_multiplier)
            return 1
        elif clank_state == -1 or self.hp < 0:
            self.owner.change_y = -15
            self.owner.invulnerable = 20
            self.owner.doStunned(400)
            return -1
        else:
            return 0

class InvulnerableHitbox(Hitbox):
    def __init__(self,_owner,_hitboxLock,_hitboxVars):
        Hitbox.__init__(self, _owner, _hitboxLock, _hitboxVars)
        self.hitbox_type = 'invulnerable'

    def update(self):
        Hitbox.update(self)
   
    def compareTo(self, _other):
        if not isinstance(_other, InertHitbox) and isinstance(_other, DamageHitbox) and not _other.ignore_shields and self.owner.lockHitbox(_other):
            if self.article is None:
                self.owner.applyPushback(_other.base_knockback/5.0, _other.getTrajectory(), (_other.damage / 4.0 + 2.0)*_other.hitlag_multiplier)
            if _other.article is None:
                _other.owner.applyPushback(_other.base_knockback/5.0, _other.getTrajectory()+180, (_other.damage / 4.0 + 2.0)*_other.hitlag_multiplier)
            return 1
        return 0

def getForwardWithOffset(_angle, _article):
    if _article.facing == 1:
        return _angle
    else:
        return 180 - _angle
