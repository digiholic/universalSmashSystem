from engine.subaction import *
from Tkinter import *

class applyHitstop(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('frames', 'int', 'applyHitstop>frames', 0),
              NodeMap('pushback', 'float', 'applyHitstop>pushback', 0.0),
              NodeMap('trajectory', 'float', 'applyHitstop>trajectory', 0.0)]

    def __init__(self, _frames=0, _pushback=0.0, _trajectory=0.0):
        SubAction.__init__(self)
        self.frames = _frames
        self.pushback = _pushback
        self.trajectory = _trajectory

    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner
        _actor.applyPushback(self.pushback, self.trajectory, self.frames)

    def getPropertiesPanel(self, _root):
        return SubAction.getPropertiesPanel(self, _root)

    def getDisplayName(self):
        return 'Apply hitstop'

    def getDataLine(self, _parent):
        return HitstopLine(_parent,_parent.interior,self)
    
class HitstopLine(dataSelector.dataLine):
    def __init__(self,_root,_parent,_target_object):
        dataSelector.dataLine.__init__(self, _root, _parent, 'Apply Hitstop')
        
        self.target_object = _target_object
        
        self.frame_label = Label(self,text='Frames:',bg=self.bg.get())
        self.frame_data = StringVar()
        self.frame_entry = Entry(self,textvariable=self.frame_data,validate='key',validatecommand=self.validateInt)
        
        self.push_label = Label(self,text='Pushback',bg=self.bg.get())
        self.push_data = StringVar()
        self.push_entry = Entry(self,textvariable=self.push_data,validate='key',validatecommand=self.validateFloat)
        
        self.trajectory_label = Label(self,text='Trajectory',bg=self.bg.get())
        self.trajectory_data = StringVar()
        self.trajectory_entry = Entry(self,textvariable=self.trajectory_data,validate='key',validatecommand=self.validateInt)
        
        self.frame_data.trace('w',self.changeVariable)
        self.push_data.trace('w', self.changeVariable)
        self.trajectory_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            self.target_object.frames = self.frame_data.get()
            self.target_object.pushback = self.push_data.get()
            self.target_object.trajectory = self.trajectory_data.get()
            
        dataSelector.dataLine.changeVariable(self)
        
    def packChildren(self):
        self.label.grid(row=0,column=0,sticky=N+S+E+W)
        self.frame_label.grid(row=1,column=0,sticky=N+S+E+W)
        self.frame_entry.grid(row=1,column=1,sticky=N+S+E+W)
        
        self.push_label.grid(row=2,column=0,sticky=N+S+E+W)
        self.push_entry.grid(row=2,column=1,sticky=N+S+E+W)
        
        self.trajectory_label.grid(row=3,column=0,sticky=N+S+E+W)
        self.trajectory_entry.grid(row=3,column=1,sticky=N+S+E+W)
        
    def update(self):
        """
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.string_data.set(getattr(self.target_object, self.var_name))
            self.string_entry.config(state=NORMAL)
        else:
            self.string_entry.config(state=DISABLED)
        """
        self.packChildren()