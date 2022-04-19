from engine.subaction import *
import sys

if sys.version_info[0] == 3:
    from tkinter import *
else:
    from Tkinter import *

# Change the frame of the action to a value.
class changeActionFrame(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('new_frame','int','setFrame',0),
              NodeMap('relative','bool','setFrame|relative',None)
              ]
    
    def __init__(self,_newFrame=0,_relative=False):
        SubAction.__init__(self)
        self.new_frame = _newFrame
        self.relative = _relative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.relative: _action.frame += self.new_frame
        else: _action.frame = self.new_frame
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeFrameProperties(_root,self)
    
    def getDisplayName(self):
        if self.relative:
            return 'Change Frame By: ' + str(self.new_frame)
        else:
            return 'Set Frame: ' + str(self.new_frame)

    def getDataLine(self, _parent):
        return SetFrameLine(_parent,_parent.interior,self)

class SetFrameLine(dataSelector.NumLine):
    def __init__(self,_root,_parent,_target_object):
        dataSelector.NumLine.__init__(self, _root, _parent, 'Set Frame:',_target_object,'new_frame',True)
        
        self.bool_data = IntVar()
        self.bool_button = Checkbutton(self,text="Relative?",variable=self.bool_data,anchor="w")
        self.bool_button.config(bg=self.bg.get())
        
        self.bool_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,int(self.num_data.get()))
        dataSelector.NumLine.changeVariable(self)
        
    def packChildren(self):
        dataSelector.NumLine.packChildren(self)
        self.num_entry.pack(side=LEFT,fill=BOTH)
        self.bool_button.pack(side=LEFT,fill=BOTH)
        
    def update(self):
        # If the object exists and has the attribute, set the variable
        self.num_data.set(self.target_object.new_frame)
        self.bool_data.set(self.target_object.relative)
        self.packChildren()
