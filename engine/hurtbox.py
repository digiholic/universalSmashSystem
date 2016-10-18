import spriteManager
import pygame

class Hurtbox(spriteManager.RectSprite):
    def __init__(self,_owner,_variables = dict()):
        self.owner = _owner
        
        self.variable_dict = {
                       'center': (0,0),
                       'size': (0,0),
                       'fix_rect': 'bounding_rect',
                       # Soon:
                       #'fix_size_multiplier': (0,0),
                       #'self_size_multiplier': (0,0)
                       }
        self.newVariables = _variables
        self.variable_dict.update(self.newVariables)
        
        #set the variables from the dict, so that we don't lose the initial value of the dict when modifying them
        #also lets us not have to go update all the old references. Score!
        for key,value in self.variable_dict.iteritems():
            setattr(self, key, value)

        fix_rect = self.getFixRect()
        if self.size[0] == 0: working_width = fix_rect.width
        else: working_width = self.size[0]
        if self.size[1] == 0: working_height = fix_rect.height
        else: working_height = self.size[1]

        spriteManager.RectSprite.__init__(self,pygame.Rect([0,0],[working_width, working_height]),[255,255,0])
        self.rect.center = [_owner.rect.center[0] + self.center[0], _owner.rect.center[1] + self.center[1]]
        self.article = None
        self.armor = DefaultArmor()
        
    #Add to later
    def getFixRect(self):
        if self.fix_rect == 'rect':
            return self.owner.sprite.rect
        else:
            return self.owner.sprite.bounding_rect
        

    def update(self):
        fix_rect = self.getFixRect()
        if self.size[0] == 0: self.rect.width = fix_rect.width
        else: self.rect.width = self.size[0]
        if self.size[1] == 0: self.rect.height = fix_rect.height
        else: self.rect.height = self.size[1]

        if self.article is None:
            self.rect.center = [fix_rect.center[0] + self.center[0]*self.owner.facing, fix_rect.center[1] + self.center[1]]
        elif hasattr(self.article, "facing"):
            self.rect.center = [fix_rect.center[0] + self.center[0]*self.article.facing, fix_rect.center[1] + self.center[1]]
        else:
            self.rect.center = [fix_rect.center[0] + self.center[0], fix_rect.center[1] + self.center[1]]

    
    """
    This function is called when a hurtbox is hit by a hitbox. Does nothing by default,
    but can be overridden for a custom Hurtbox class.
    
    @_other: The hitbox that hit this hurtbox
    """
    def onHit(self,_other):
        pass
    
    
class Armor():
    """ Armor is how a fighter manages their damage, hitstun, and knockback. It
    has a filterHitbox function that returns a dict of values that the fighter
    will need to launch itself.
    """
    
    def __init__(self):
        pass
    
    def identity_dict(self,_hitbox):
        """ The identity dict just takes fields from the hitbox and returns them.
        It is usually modified and returned by the filter.
        
        Parameters
        -----------
        _hitbox : Hitbox
            The Hitbox to pull data through
        """
        return {
            'damage' : _hitbox.damage,
            'knockback' : _hitbox.base_knockback,
            'knockback_growth': _hitbox.knockback_growth,
            'trajectory' : _hitbox.trajectory,
            'wieght_influence' : _hitbox.weight_influence,
            'hitstun' : _hitbox.histstun_multiplier,
            'base_hitstun' : _hitbox.base_hitstun,
            'hitlag' : _hitbox.hitlag_multiplier,
            }
    
    def filterHitbox(self,_hitbox):
        """ Applies the Armor's filter to the Hitbox. If the hitbox is set to ignore armor,
        returns the identity_dict instead. 
        
        Parameters
        -----------
        _hitbox : Hitbox
            The hitbox to filter
        """
        return self.identity_dict(_hitbox)
        
class DefaultArmor(Armor):
    """ Default Armor just passes the hitbox variables straight through, no modification required"""
    def filterHitbox(self, _hitbox):
        Armor.filterHitbox(_hitbox)
        return self.identity_dict(_hitbox)
    
class HyperArmor(Armor):
    """ Hyper Armor means damage, but no knockback, no matter what. """
    def filterHitbox(self, _hitbox):
        if _hitbox.ignore_armor:
            return self.identity_dict(_hitbox)
        armor_dict = self.identity_dict(_hitbox)
        armor_dict['hitstun'] = 0
        armor_dict['base_hitstun'] = 0
        armor_dict['knockback'] = 0
        armor_dict['knockback_growth'] = 0
        armor_dict['hitlag'] = 0
        return armor_dict
    
class SuperArmor(Armor):
    """ Super Armor means damage, but no knockback for a certain number of hits.
    Defaults to 1 hit of Super Armor """
    def __init__(self,_armoredHits = 1):
        self.armored_hits = _armoredHits
        
    def filterHitbox(self, _hitbox):
        if _hitbox.ignore_armor:
            return self.identity_dict(_hitbox)
        if self.armored_hits > 0: #If there's any armor left
            armor_dict = self.identity_dict(_hitbox)
            armor_dict['hitstun'] = 0
            armor_dict['base_hitstun'] = 0
            armor_dict['knockback'] = 0
            armor_dict['knockback_growth'] = 0
            armor_dict['hitlag'] = 0
            self.armored_hits -= 1
            return armor_dict
        else:
            return self.identity_dict(_hitbox)
        
class HeavyArmor(Armor):
    """ Heavy Armor ignores knockback below a certain threshold """
    pass