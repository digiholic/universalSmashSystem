import spriteManager
import settingsManager
import engine.hitbox as hitbox
import pygame
import math

class Hurtbox(spriteManager.RectSprite):
    def __init__(self,_owner,_variables = dict()):
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

        fix_rect = self.getFixRect()
        if self.size[0] == 0: working_width = fix_rect.width
        else: working_width = self.size[0]
        if self.size[1] == 0: working_height = fix_rect.height
        else: working_height = self.size[1]

        spriteManager.RectSprite.__init__(self,pygame.Rect([0,0],[working_width, working_height]),[255,255,0])
        self.rect.center = [_owner.rect.center[0] + self.center[0], _owner.rect.center[1] + self.center[1]]
        self.article = None
        self.armor = []
        
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
    This function is called when a hurtbox is hit by a hitbox. Registers the hit and applies the corresponding subactions by default, but can be overridden
    
    @_other: The hitbox that hit this hurtbox
    """
    def onHit(self,_hitbox):
        all_armor = self.armor+self.owner.armor
        # Use currying to composit everything together
        giant_filter = reduce(lambda f, g: (lambda k: f.filterValues(_hitbox, k, g)), all_armor, lambda y: self.owner.applySubactions(y))
        return giant_filter(_hitbox.getOnHitSubactions(self))
    
class Armor():
    """ Armor is how a fighter manages their damage, hitstun, and knockback. It
    has a function that filters these values.
    """

    def filterValues(self,_hitbox,_subactions,_forward):
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
    def filterValues(self, _hitbox, _subactions, _forward):
        if isinstance(_hitbox, hitbox.DamageHitbox) and not _hitbox.ignore_armor:
            import engine.subaction as subaction
            _subactions = filter(lambda k: not isinstance(k, subaction.dealDamage), _subactions)
        return _forward(_hitbox, _subactions)
    
class SuperArmor(Armor):
    """ Super Armor means damage, but no knockback for a certain number of hits.
    Defaults to 1 hit of Super Armor """

    # TODO: Scrap self when a hit registers
    def filterValues(self, _hitbox, _subactions, _forward):
        if isinstance(_hitbox, hitbox.DamageHitbox) and not _hitbox.ignore_armor:
            import engine.subaction as subaction
            _subactions = filter(lambda k: not isinstance(k, subaction.dealDamage), _subactions)
        return _forward(_hitbox, _subactions)
        
class HeavyArmor(Armor):
    """ Heavy Armor ignores knockback below a certain threshold """
    pass
