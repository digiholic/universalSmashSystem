from engine.subaction import *

# Create a new hitbox
class createHitbox(SubAction):
    subact_group = 'Hitbox'
    
    def __init__(self, _name='', _hitboxType='damage', _hitboxLock='', _variables={}, _owner_event = '', _other_event = ''):
        SubAction.__init__(self)
        
        self.hitbox_name = _name
        self.hitbox_type = _hitboxType if _hitboxType is not None else "damage"
        self.hitbox_lock = _hitboxLock
        self.hitbox_vars = _variables
        self.owner_event = _owner_event
        self.other_event = _other_event
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)

        if self.hitbox_name == '': return #Don't make a hitbox without a name or we'll lose it
        #Use an existing hitbox lock by name, or create a new one
        
        if self.hitbox_lock and _action.hitbox_locks.has_key(self.hitbox_lock):
            hitbox_lock = _action.hitbox_locks[self.hitbox_lock]
        else:
            hitbox_lock = engine.hitbox.HitboxLock(self.hitbox_lock)
            _action.hitbox_locks[self.hitbox_lock] = hitbox_lock
        
        #Create the hitbox of the right type    
        if self.hitbox_type == "damage":
            hitbox = engine.hitbox.DamageHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "sakurai":
            hitbox = engine.hitbox.SakuraiAngleHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "autolink":
            hitbox = engine.hitbox.AutolinkHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "funnel":
            hitbox = engine.hitbox.FunnelHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "grab":
            hitbox = engine.hitbox.GrabHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "reflector":
            hitbox = engine.hitbox.ReflectorHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "absorber":
            hitbox = engine.hitbox.AbsorberHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "invulnerable":
            hitbox = engine.hitbox.InvulnerableHitbox(_actor, hitbox_lock, self.hitbox_vars)
        elif self.hitbox_type == "shield":
            hitbox = engine.hitbox.ShieldHitbox(_actor, hitbox_lock, self.hitbox_vars)
        elif self.hitbox_type == "throw":
            hitbox = engine.hitbox.ThrowHitbox(_actor, hitbox_lock, self.hitbox_vars)
            
        
        if _action is not None:
            if hasattr(_action, 'events'): #Articles don't have events, and this can be called from article
                if _action.events.has_key(self.owner_event):
                    hitbox.owner_on_hit_actions = _action.events[self.owner_event]
                elif _actor.events.has_key(self.owner_event):
                    hitbox.owner_on_hit_actions = [_actor.events[self.owner_event]]
                if _action.events.has_key(self.other_event):
                    hitbox.other_on_hit_actions = _action.events[self.other_event]
                elif _actor.events.has_key(self.other_event):
                    hitbox.other_on_hit_actions = [_actor.events[self.other_event]]
            _action.hitboxes[self.hitbox_name] = hitbox
    
    def getDisplayName(self):
        return 'Create New Hitbox: ' + self.hitbox_name
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyHitboxProperties(_root,self,newHitbox=True)
       
    def getXmlElement(self):
        elem = ElementTree.Element('createHitbox')
        elem.attrib['type'] = self.hitbox_type
        name_elem = ElementTree.Element('name')
        name_elem.text = self.hitbox_name
        elem.append(name_elem)
        for tag,value in self.hitbox_vars.iteritems():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        lock_elem = ElementTree.Element('hitboxLock')
        lock_elem.text = self.hitbox_lock
        elem.append(lock_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        #mandatory fields
        hitbox_type = _node.attrib['type'] if _node.attrib.has_key('type') else "damage"
        
        #build the variable dict
        variables = {}
        #these lists let the code know which keys should be which types.
        tuple_type = ['center','size']
        float_type = ['damage','base_knockback','knockback_growth','hitsun','damage_multiplier','velocity_multiplier',
                     'weight_influence','shield_multiplier','priority_diff','charge_damage','charge_base_knockback','charge_knockback_growth',
                     'x_bias','y_bias','x_draw','y_draw','hitlag_multiplier','hitstun_multiplier']
        int_type = ['trajectory','hp','transcendence','base_hitstun']
        boolean_type = ['ignore_shields', 'ignore_armor']
        hitbox_lock = None
            
        for child in _node:
            tag = child.tag
            val = child.text
            
            owner_event = ''
            other_event = ''
            #special cases
            if tag == 'name':
                name = val
            elif tag == 'hitboxLock':
                hitbox_lock = val
            elif tag == 'onHitOwner':
                owner_event = val
            elif tag == 'onHitOther':
                other_event = val
            elif tag in tuple_type:
                variables[tag] = make_tuple(val)
            elif tag in float_type:
                variables[tag] = float(val)
            elif tag in int_type:
                variables[tag] = int(val)
            else:
                variables[tag] = val
            
        return createHitbox(name, hitbox_type, hitbox_lock, variables, owner_event, other_event)
