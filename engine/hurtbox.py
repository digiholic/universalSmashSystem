import spriteManager
import settingsManager
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
        self.armor = Armor()
        
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
    def onHit(self,_hitbox,_data=dict()):
        # Owner Variables
        if hasattr(self.owner,'damage'):
            percent = float(self.owner.damage)
        else: percent = 0
        
        if hasattr(self.owner, 'weight'):
            weight = float(self.owner.stats['weight']) * settingsManager.getSetting('weight')
        else: weight = 100 * settingsManager.getSetting('weight')
        
        if _data.has_key('damage'):
            damage = _data['damage']
        else: damage = float(_hitbox.damage)
        
        # Data Variables
        if _data.has_key('knockback_growth'):
            knockback_growth = _data['knockback_growth']
        else: knockback_growth = float(_hitbox.knockback_growth)
        
        if _data.has_key('base_knockback'):
            base_knockback = _data['base_knockback']
        else: base_knockback = float(_hitbox.base_knockback)
        
        if _data.has_key('base_hitstun'):
            base_hitstun = _data['base_hitstun']
        else: base_hitstun = _hitbox.base_hitstun
        
        if _data.has_key('hitstun_multiplier'):
            hitstun_multiplier = _data['hitstun_multiplier']
        else: hitstun_multiplier = _hitbox.hitstun_multiplier
        
        if _data.has_key('hitlag_multiplier'):
            hitlag_multiplier = _data['hitlag_multiplier']
        else: hitlag_multiplier = _hitbox.hitlag_multiplier
        
        if _data.has_key('trajectory'):
            trajectory = _data['trajectory']
        else: trajectory = _hitbox.trajectory
        
        # Thank you, ssbwiki!
        percent_portion = (percent/10.0) + (percent*damage)/20.0
        weight_portion = 200.0/(weight*_hitbox.weight_influence+100)
        
        scaled_kb = (((percent_portion * weight_portion *1.4) + 5) * knockback_growth) 
        
        if self.owner.current_action.name in ('Crouch', 'CrouchCancel'):
            base_hitstun *= 0.5
            scaled_kb *= 0.9
            base_hitstun *= 0.5
            hitstun_multiplier *= 0.8
        
        # Get trajectory as a vector
        trajectory_vec = [math.cos(trajectory/180*math.pi), math.sin(trajectory/180*math.pi)] 
        
        # This is applying some hella math magic to compensate for air resistance and gravity.
        # This makes linking hitboxes actually work
        additional_kb = .5 * base_hitstun * math.sqrt(abs(trajectory_vec[0])*(self.owner.stats['air_resistance']*settingsManager.getSetting('airControl'))**2+abs(trajectory_vec[1])*(self.owner.stats['gravity']*settingsManager.getSetting('gravity'))**2)

        total_kb = scaled_kb + base_knockback + additional_kb
        
        # Filter all of the values on the current Armor
        damage, total_kb, hitstun_multiplier,base_hitstun = self.armor.filterValues(damage,total_kb,hitstun_multiplier,base_hitstun)
        if hasattr(self.owner, 'dealDamage'):
            self.owner.dealDamage(damage)
        if hasattr(self.owner, 'applyHitstop'):
            self.owner.applyHitstop(damage,hitlag_multiplier)
        if hasattr(self.owner, 'applyKnockback'):
            self.owner.applyKnockback(total_kb, trajectory)
        if hasattr(self.owner, 'applyHitstun'):
            self.owner.applyHitstun(total_kb,hitstun_multiplier,base_hitstun,trajectory)
    
class Armor():
    """ Armor is how a fighter manages their damage, hitstun, and knockback. It
    has a function that filters these values.
    """
    def filterValues(self,_damage,_total_kb,_hitstun_multiplier,_base_hitstun):
        """ Applies the Armor's filter to the Hitbox. Default Armor
        simply returns the values as given.
        
        Parameters
        -----------
        _damage : int
            The damage the attack dealt
        _total_kb : float
            The total knockback dealt
        _hitstun_multiplier : float
            The hitstun multiplier of the attack
        _base_hitstun : float
            The base hitstun of the attack
        """
        return (_damage, _total_kb, _hitstun_multiplier,_base_hitstun)
        
class HyperArmor(Armor):
    """ Hyper Armor means damage, but no knockback, no matter what. """
    def filterValues(self, _damage, _total_kb, _hitstun_multiplier, _base_hitstun):
        return (_damage, 0, 0, 0)
    
class SuperArmor(Armor):
    """ Super Armor means damage, but no knockback for a certain number of hits.
    Defaults to 1 hit of Super Armor """
    def __init__(self,_armoredHits = 1):
        self.armored_hits = _armoredHits
        
    def filterValues(self, _damage, _total_kb, _hitstun_multiplier, _base_hitstun):
        if self.armored_hits > 0: #If there's any armor left
            return _damage, 0, 0, 0
        else:
            return Armor.filterValues(self, _damage, _total_kb, _hitstun_multiplier, _base_hitstun)
        
class HeavyArmor(Armor):
    """ Heavy Armor ignores knockback below a certain threshold """
    pass
