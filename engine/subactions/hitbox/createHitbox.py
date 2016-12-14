from engine.subaction import *
import ttk
from Tkinter import *

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
                     'x_bias','y_bias','x_multiplier','y_multiplier','hitlag_multiplier','hitstun_multiplier']
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

    def getDataLine(self, _parent):
        return CreateHitboxLine(_parent)
    
class CreateHitboxLine(dataSelector.dataLine):
    def __init__(self,_parent):
        dataSelector.dataLine.__init__(self, _parent, _parent.interior, 'Create Hitbox')
        
        self.hitbox = None
        
        self.name_data = StringVar()
        self.name_entry = Entry(self,textvariable=self.name_data)
        
        self.hitboxPropertiesPanel = ttk.Notebook(self)
        
        self.properties_frame = HitboxPropertiesFrame(self.hitboxPropertiesPanel)
        self.damage_frame = HitboxDamageFrame(self.hitboxPropertiesPanel)
        self.charge_frame = HitboxChargeFrame(self.hitboxPropertiesPanel)
        override_frame = ttk.Frame(self.hitboxPropertiesPanel)
        autolink_frame = ttk.Frame(self.hitboxPropertiesPanel)
        funnel_frame = ttk.Frame(self.hitboxPropertiesPanel)
        
        self.hitboxPropertiesPanel.add(self.properties_frame,text="Properties")
        self.hitboxPropertiesPanel.add(self.damage_frame,text="Damage")
        self.hitboxPropertiesPanel.add(self.charge_frame,text="Charge")
        
        self.name_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        hitboxes = self.root.getAction().hitboxes
        if hitboxes.has_key(self.name_data.get()):
            self.hitbox = hitboxes[self.name_data.get()]
        
    def packChildren(self):
        self.label.grid(row=0,column=0)
        self.name_entry.grid(row=0,column=1,sticky=E+W)
        self.hitboxPropertiesPanel.grid(row=1,column=0,columnspan=2,sticky=N+S+E+W)
        
        self.grid_columnconfigure(1, weight=1)
        
    def update(self):
        hitboxes = self.root.getAction().hitboxes
        if hitboxes.has_key(self.name_data.get()):
            self.hitbox = hitboxes[self.name_data.get()]
        
        self.properties_frame.hitbox = self.hitbox
        self.properties_frame.update()
        
        self.damage_frame.hitbox = self.hitbox
        self.damage_frame.update()
        
        self.charge_frame.hitbox = self.hitbox
        self.charge_frame.update()
        
        self.packChildren()
        
class HitboxPropertiesFrame(ttk.Frame):
    def __init__(self,_parent):
        ttk.Frame.__init__(self,_parent)
        self.hitbox = None
        
        self.type_label = Label(self,text="Type:")
        self.type_data = StringVar()
        self.type_entry = Entry(self,textvariable=self.type_data)#OptionMenu() ###
        
        self.lock_label = Label(self,text="Lock:")
        self.lock_data = StringVar()
        self.lock_entry = Entry(self,textvariable=self.lock_data)
        
        self.center_label = Label(self,text="Center:")
        self.center_x_data = IntVar()
        self.center_x_entry = Spinbox(self,from_=-255,to=255,textvariable=self.center_x_data,width=4)
        self.center_y_data = IntVar()
        self.center_y_entry = Spinbox(self,from_=-255,to=255,textvariable=self.center_y_data,width=4)
        
        self.size_label = Label(self,text="Size:")
        self.size_x_data = IntVar()
        self.size_x_entry = Spinbox(self,from_=-255,to=255,textvariable=self.size_x_data,width=4)
        self.size_y_data = IntVar()
        self.size_y_entry = Spinbox(self,from_=-255,to=255,textvariable=self.size_y_data,width=4)
        
        self.type_label.grid(row=0,column=0,sticky=E)
        self.type_entry.grid(row=0,column=1,columnspan=2)
        
        self.lock_label.grid(row=1,column=0,sticky=E)
        self.lock_entry.grid(row=1,column=1,columnspan=2)
        
        self.center_label.grid(row=2,column=0,sticky=E)
        self.center_x_entry.grid(row=2,column=1)
        self.center_y_entry.grid(row=2,column=2)
        
        self.size_label.grid(row=3,column=0,sticky=E)
        self.size_x_entry.grid(row=3,column=1)
        self.size_y_entry.grid(row=3,column=2)
        
    def changeVariable(self):
        pass
    
    def update(self):
        ttk.Frame.update(self)
        if self.hitbox:
            self.type_data.set(self.hitbox.type)
            self.lock_data.set(self.hitbox.hitbox_lock)
            self.center_x_data.set(self.hitbox.center[0])
            self.center_y_data.set(self.hitbox.center[1])
            self.size_x_data.set(self.hitbox.size[0])
            self.size_y_data.set(self.hitbox.size[1])
            
        
        
class HitboxDamageFrame(ttk.Frame):
    def __init__(self,_parent):
        ttk.Frame.__init__(self,_parent)
        self.hitbox = None
        
        self.validateFloat = (_parent.register(self.validateFloat),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        self.damage_label = Label(self,text="Damage:")
        self.damage_data = IntVar()
        self.damage_entry = Spinbox(self,from_=0,to=999,textvariable=self.damage_data,width=4)
        
        self.base_label = Label(self,text="Base Knockback:")
        self.base_data = StringVar()
        self.base_entry = Entry(self,textvariable=self.base_data,validate='key',validatecommand=self.validateFloat)
        
        self.growth_label = Label(self,text="Knockback Growth:")
        self.growth_data = StringVar()
        self.growth_entry = Entry(self,textvariable=self.growth_data,validate='key',validatecommand=self.validateFloat)
        
        self.trajectory_label = Label(self,text="Trajectory:")
        self.trajectory_data = IntVar()
        self.trajectory_entry = Spinbox(self,from_=0,to=360,textvariable=self.trajectory_data,width=4)
        
        self.hitstun_label = Label(self,text="Hitstun Multiplier:")
        self.hitstun_data = StringVar()
        self.hitstun_entry = Entry(self,textvariable=self.hitstun_data,validate='key',validatecommand=self.validateFloat)
        
        self.damage_label.grid(row=0,column=0,sticky=E)
        self.damage_entry.grid(row=0,column=1,sticky=W)
        
        self.base_label.grid(row=1,column=0,sticky=E)
        self.base_entry.grid(row=1,column=1,sticky=W)
        
        self.growth_label.grid(row=2,column=0,sticky=E)
        self.growth_entry.grid(row=2,column=1,sticky=W)
        
        self.trajectory_label.grid(row=3,column=0,sticky=E)
        self.trajectory_entry.grid(row=3,column=1,sticky=W)
        
        self.hitstun_label.grid(row=4,column=0,sticky=E)
        self.hitstun_entry.grid(row=4,column=1,sticky=W)
            
    def changeVariable(self):
        pass
    
    def validateFloat(self, action, index, value_if_allowed,
        prior_value, text, validation_type, trigger_type, widget_name):
        allowed_chars = '0123456789.-+'
        # action=1 -> insert
        if(action=='1'):
            if text in allowed_chars:
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True
        
class HitboxChargeFrame(ttk.Frame):
    def __init__(self,_parent):
        ttk.Frame.__init__(self,_parent)
        self.hitbox = None
        
        self.validateFloat = (_parent.register(self.validateFloat),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        self.charge_damage_label = Label(self,text="Charge Damage:")
        self.charge_damage_data = IntVar()
        self.charge_damage_entry = Spinbox(self,from_=0,to=999,textvariable=self.charge_damage_data,width=4)
        
        self.charge_base_label = Label(self,text="Charge Base Knockback:")
        self.charge_base_data = StringVar()
        self.charge_base_entry = Entry(self,textvariable=self.charge_base_data,validate='key',validatecommand=self.validateFloat)
        
        self.charge_growth_label = Label(self,text="Charge Knockback Growth:")
        self.charge_growth_data = StringVar()
        self.charge_growth_entry = Entry(self,textvariable=self.charge_growth_data,validate='key',validatecommand=self.validateFloat)
        
        self.charge_damage_label.grid(row=0,column=0,sticky=E)
        self.charge_damage_entry.grid(row=0,column=1,sticky=W)
        
        self.charge_base_label.grid(row=1,column=0,sticky=E)
        self.charge_base_entry.grid(row=1,column=1,sticky=W)
        
        self.charge_growth_label.grid(row=2,column=0,sticky=E)
        self.charge_growth_entry.grid(row=2,column=1,sticky=W)
            
    def changeVariable(self):
        pass
    
    def validateFloat(self, action, index, value_if_allowed,
        prior_value, text, validation_type, trigger_type, widget_name):
        allowed_chars = '0123456789.-+'
        # action=1 -> insert
        if(action=='1'):
            if text in allowed_chars:
                try:
                    float(value_if_allowed)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True