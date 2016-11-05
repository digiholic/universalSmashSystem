import spriteManager
import settingsManager
import engine.hitbox as hitbox
import pygame
import math
from global_functions import *

class Hurtbox(spriteManager.RectSprite):
    def __init__(self,_owner,_variables = dict()):
        if hasattr(_owner, 'owner'):
            self.owner = _owner.owner
        else:
            self.owner = _owner
        
        self.variable_dict = {
                       'center': (0,0),
                       'size': (0,0),
                       'fix_rect': 'bounding_rect',
                       }
        self.newVariables = _variables
        self.variable_dict.update(self.newVariables)
        
        #set the variables from the dict, so that we don't lose the initial value of the dict when modifying them
        #also lets us not have to go update all the old references. Score!
        for key,value in self.variable_dict.iteritems():
            setattr(self, key, value)

        fix_center = self.getFixCenter()
        if self.size[0] == 0: 
            working_width = self.owner.sprite.bounding_rect.width
        else: working_width = self.size[0]
        if self.size[1] == 0: 
            working_height = self.owner.sprite.bounding_rect.height
        else: working_height = self.size[1]

        spriteManager.RectSprite.__init__(self,pygame.Rect([0,0],[working_width, working_height]),[255,255,0])
        self.rect.center = [self.owner.posx + self.center[0]*self.owner.facing, self.owner.posy + self.center[1]]
        self.armor = {}
        
    #Add to later
    def getFixCenter(self):
        if self.fix_rect == 'rect':
            return (self.owner.posx, self.owner.posy)
        else:
            return (self.owner.sprite.bounding_rect.centerx, self.owner.sprite.bounding_rect.centery)

    def update(self):
        fix_center = self.getFixCenter()
        if self.size[0] == 0: 
            self.rect.width = self.owner.sprite.bounding_rect.width
        else: self.rect.width = self.size[0]
        if self.size[1] == 0: 
            self.rect.height = self.owner.sprite.bounding_rect.height
        else: self.rect.height = self.size[1]

        self.rect.center = [self.owner.posx + self.center[0]*self.owner.facing, self.owner.posy + self.center[1]]

    """
    This function is called when a hurtbox is hit by a hitbox. Registers the hit and applies the corresponding subactions by default, but can be overridden
    
    @_other: The hitbox that hit this hurtbox
    """
    def onHit(self,_hitbox):
        all_armor = self.armor.values()+self.owner.armor.values()
        # Use currying to composit everything together
        giant_filter = reduce(lambda f, g: (lambda j, k: g.filterHits(_hitbox, k, f)), all_armor, lambda x, y: self.owner.filterHits(x, y))
        return giant_filter(_hitbox, _hitbox.getOnHitSubactions(self))
    
class Armor():
    """ Armor is how a fighter manages their damage, hitstun, and knockback. It
    has a function that filters these values.
    """

    def __init__(self, _owner, _variables = dict()):
        if hasattr(_owner, 'owner'):
            self.owner = _owner.owner
        else:
            self.owner = _owner
        
        self.variable_dict = {
                       'num_hits': 1, 
                       'damage_threshold': 0, 
                       'knockback_threshold': 0, 
                       'armor_damage_multiplier': 1, 
                       'armor_knockback_multiplier': 0, 
                       'overflow_damage_multiplier': 1, 
                       'overflow_knockback_multiplier': 1
                       }
        self.newVariables = _variables
        self.variable_dict.update(self.newVariables)
        
        #set the variables from the dict, so that we don't lose the initial value of the dict when modifying them
        #also lets us not have to go update all the old references. Score!
        for key,value in self.variable_dict.iteritems():
            setattr(self, key, value)

    def filterHits(self,_hitbox,_subactions,_forward):
        """ Applies the Armor's filter to the passed subaction list. Default Armor
        simply forwards the values as given, and passes the return value up. 
        
        Parameters
        -----------
        _hitbox : Hitbox
            The hitbox that's applying the action
        _subactions : list(Subaction)
            The subaction list that the hitbox is trying to pass
        _forward : Function(_self,_hitbox,_subactions,_forward)
            The next function to receive the hit, and the one that returns to this one
        """
        return _forward(_hitbox,_subactions)
        
class HyperArmor(Armor):
    """ Hyper Armor means damage, but no knockback, no matter what. """

    def __init__(self, _owner, _variables=dict()):
        Armor.__init__(self, _owner, _variables)
        self.armor_type = 'hyper'
        
    def filterHits(self, _hitbox, _subactions, _forward):
        if isinstance(_hitbox, hitbox.DamageHitbox) and not _hitbox.ignore_armor:
            import engine.subaction as subaction
            _subactions = filter(lambda k: not isinstance(k, subaction.applyHitstop) and not isinstance(k, subaction.dealDamage) and not isinstance(k, subaction.ApplyScaledKnockback) and not isinstance(k, subaction.CompensateResistance), _subactions)
            for subact in _subactions:
                if isinstance(subact, subaction.dealDamage):
                    subact.damage *= self.armor_damage_multiplier
                if isinstance(subact, subaction.applyScaledKnockback):
                    subact.base_knockback *= self.armor_knockback_multiplier
                    subact.knockback_growth *= self.armor_knockback_multiplier
                if isinstance(subact, subaction.compensateResistance):
                    subact.frames *= self.armor_knockback_multiplier
        return _forward(_hitbox, _subactions)
    
class SuperArmor(Armor):
    """ Super Armor means damage, but no knockback for a certain number of hits.
    Defaults to 1 hit of Super Armor """

    def __init__(self, _owner, _variables=dict()):
        Armor.__init__(self, _owner, _variables)
        self.armor_type = 'super'

    def filterHits(self, _hitbox, _subactions, _forward):
        if isinstance(_hitbox, hitbox.DamageHitbox) and self.num_hits > 0 and not _hitbox.ignore_armor:
            import engine.subaction as subaction
            _subactions = filter(lambda k: not isinstance(k, subaction.applyHitstop) and not isinstance(k, subaction.dealDamage) and not isinstance(k, subaction.ApplyScaledKnockback) and not isinstance(k, subaction.CompensateResistance), _subactions)
            for subact in _subactions:
                if isinstance(subact, subaction.dealDamage):
                    subact.damage *= self.armor_damage_multiplier
                if isinstance(subact, subaction.applyScaledKnockback):
                    subact.base_knockback *= self.armor_knockback_multiplier
                    subact.knockback_growth *= self.armor_knockback_multiplier
                if isinstance(subact, subaction.compensateResistance):
                    subact.frames *= self.armor_knockback_multiplier
            self.num_hits -= 1
        return _forward(_hitbox, _subactions)
        
class HeavyArmor(Armor):
    def __init__(self, _owner, _variables=dict()):
        Armor.__init__(self, _owner, _variables)
        self.armor_type = 'heavy'
        
    def filterHits(self, _hitbox, _subactions, _forward):
        if isinstance(_hitbox, hitbox.DamageHitbox) and not _hitbox.ignore_armor:

            # Calculate knockback
            percent_portion = (self.owner.damage/10.0) + (self.owner.damage*_hitbox.damage)/20.0
            weight_portion = 200.0/(self.owner.stats['weight']*settingsManager.getSetting('weight')*_hitbox.weight_influence+100)
            total_kb = (((percent_portion * weight_portion *1.4) + 5) * _hitbox.knockback_growth) + _hitbox.base_knockback
            if self.damage_threshold > _hitbox.damage and self.knockback_threshold > total_kb:
                import engine.subaction as subaction
                _subactions = filter(lambda k: not isinstance(k, subaction.applyHitstop) and not isinstance(k, subaction.dealDamage) and not isinstance(k, subaction.ApplyScaledKnockback) and not isinstance(k, subaction.CompensateResistance), _subactions)
                for subact in _subactions:
                    if isinstance(subact, subaction.dealDamage):
                        subact.damage *= self.armor_damage_multiplier
                    if isinstance(subact, subaction.applyScaledKnockback):
                        subact.base_knockback *= self.armor_knockback_multiplier
                        subact.knockback_growth *= self.armor_knockback_multiplier
                    if isinstance(subact, subaction.compensateResistance):
                        subact.frames *= self.armor_knockback_multiplier
            else:
                for subact in _subactions:
                    if isinstance(subact, subaction.dealDamage):
                        subact.damage *= self.overflow_damage_multiplier
                    if isinstance(subact, subaction.applyScaledKnockback):
                        subact.base_knockback *= self.overflow_knockback_multiplier
                        subact.knockback_growth *= self.overflow_knockback_multiplier
                    if isinstance(subact, subaction.compensateResistance):
                        subact.frames *= self.overflow_knockback_multiplier
                    if isinstance(subact, subaction.applyHitstun):
                        subact.base_knockback *= self.overflow_knockback_multiplier
                        subact.knockback_growth *= self.overflow_knockback_multiplier
        return _forward(_hitbox, _subactions)

class Invulnerability(Armor):
    """ Invulnerability does not pass actions down, but pretends as if it did. """

    def __init__(self, _owner, _variables=dict()):
        Armor.__init__(self, _owner, _variables)
        self.armor_type = 'invulnerable'

    def filterHits(self, _hitbox, _subactions, _forward):
        import engine.subaction as subaction
        _subactions = filter(lambda k: not isinstance(k, subaction.applyHitstop), _subactions)
        return _forward(_hitbox, _subactions)

class Intangibility(Armor):
    """ Intangibility tells the truth when it passes nothing down. """
    def __init__(self, _owner, _variables=dict()):
        Armor.__init__(self, _owner, _variables)
        self.armor_type = 'intangible'

    def filterHits(self, _hitbox, _subactions, _forward):
        return False

class CumulativeArmor(Armor):
    def __init__(self, _owner, _variables=dict()):
        Armor.__init__(self, _owner, _variables)
        self.armor_type = 'heavy'
        
    def filterHits(self, _hitbox, _subactions, _forward):
        if self.damage_threshold > 0 and self.knockback_threshold > 0 and isinstance(_hitbox, hitbox.DamageHitbox) and not _hitbox.ignore_armor:
            # Calculate knockback
            percent_portion = (self.owner.damage/10.0) + (self.owner.damage*_hitbox.damage)/20.0
            weight_portion = 200.0/(self.owner.stats['weight']*settingsManager.getSetting('weight')*_hitbox.weight_influence+100)
            total_kb = (((percent_portion * weight_portion *1.4) + 5) * _hitbox.knockback_growth) + _hitbox.base_knockback
            self.damage_threshold -= _hitbox.damage
            self.knockback_threshold -= total_kb
            if self.damage_threshold > _hitbox.damage and self.knockback_threshold > total_kb:
                import engine.subaction as subaction
                _subactions = filter(lambda k: not isinstance(k, subaction.applyHitstop) and not isinstance(k, subaction.dealDamage) and not isinstance(k, subaction.ApplyScaledKnockback) and not isinstance(k, subaction.CompensateResistance), _subactions)
                for subact in _subactions:
                    if isinstance(subact, subaction.dealDamage):
                        subact.damage *= self.armor_damage_multiplier
                    if isinstance(subact, subaction.applyScaledKnockback):
                        subact.base_knockback *= self.armor_knockback_multiplier
                        subact.knockback_growth *= self.armor_knockback_multiplier
                    if isinstance(subact, subaction.compensateResistance):
                        subact.frames *= self.armor_knockback_multiplier
            else:
                for subact in _subactions:
                    if isinstance(subact, subaction.dealDamage):
                        subact.damage *= self.overflow_damage_multiplier
                    if isinstance(subact, subaction.applyScaledKnockback):
                        subact.base_knockback *= self.overflow_knockback_multiplier
                        subact.knockback_growth *= self.overflow_knockback_multiplier
                    if isinstance(subact, subaction.compensateResistance):
                        subact.frames *= self.overflow_knockback_multiplier
                    if isinstance(subact, subaction.applyHitstun):
                        subact.base_knockback *= self.overflow_knockback_multiplier
                        subact.knockback_growth *= self.overflow_knockback_multiplier
        return _forward(_hitbox, _subactions)

class CrouchCancel(Armor):
    """ Crouch cancelling reduces knockback and hitstun values while crouching. """
    def __init__(self, _owner, _variables=dict()):
        Armor.__init__(self, _owner, _variables=dict())
        self.armor_type = 'crouch_cancel'

    def filterHits(self, _hitbox, _subactions, _forward):
        import engine.subaction as subaction
        for subact in _subactions:
            if isinstance(subact, subaction.applyScaledKnockback):
                subact.base_knockback *= 0.5
                subact.knockback_growth *= 0.8
            if isinstance(subact, subaction.applyHitstun):
                subact.base_knockback *= 0.5
                subact.knockback_growth *= 0.8
                subact.base_hitstun *= 0.6
                subact.hitstun_multiplier *= 0.9
            if isinstance(subact, subaction.compensateResistance):
                subact.frames *= 0.5
            if isinstance(subact, subaction.applyHitstop):
                subact.pushback = 0
        print(_hitbox)
        print(_subactions)
        print(_forward)
        return _forward(_hitbox, _subactions)
