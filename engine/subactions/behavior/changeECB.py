from engine.subaction import *
import sys

if sys.version_info[0] == 3:
    from tkinter import *
else:
    from Tkinter import *

class changeECB(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('size','tuple','changeECB>size',(0,0)),
              NodeMap('offset','tuple','changeECB>offset',(0,0))
              ]
    
    def __init__(self,_size=[0,0],_ecbOffset=[0,0]):
        SubAction.__init__(self)
        self.size = _size
        self.offset = _ecbOffset
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _action.ecb_size = self.size
        _action.ecb_offset = self.offset
    
    def getDisplayName(self):
        return 'Modify Fighter Collision Box'
    
    @staticmethod
    def customBuildFromXml(_node):
        size = [0,0]
        ecb_offset = [0,0]
        if _node.find('size') is not None:
            size = map(int, _node.find('size').text.split(','))
        if _node.find('offset') is not None:
            ecb_offset = map(int, _node.find('offset').text.split(','))
        return changeECB(size,ecb_offset)
    
    def getDataLine(self, _parent):
        return ECBLine(_parent,self)
    
class ECBLine(dataSelector.dataLine):
    def __init__(self,_parent,_object):
        dataSelector.dataLine.__init__(self, _parent, _parent.interior, 'Change ECB')
        
        self.target_object = _object
        
        self.x_label = Label(self,text='X',bg=self.bg.get())
        self.y_label = Label(self,text='Y',bg=self.bg.get())
        
        self.size_label = Label(self,text='Size',bg=self.bg.get())
        self.size_x_data = StringVar()
        self.size_x_entry = Entry(self,textvariable=self.size_x_data,validate='key',validatecommand=self.validateInt,width=15)
        self.size_y_data = StringVar()
        self.size_y_entry = Entry(self,textvariable=self.size_y_data,validate='key',validatecommand=self.validateInt,width=15)
        
        self.off_label = Label(self,text='Offset',bg=self.bg.get())
        self.off_x_data = StringVar()
        self.off_x_entry = Entry(self,textvariable=self.off_x_data,validate='key',validatecommand=self.validateInt,width=15)
        self.off_y_data = StringVar()
        self.off_y_entry = Entry(self,textvariable=self.off_y_data,validate='key',validatecommand=self.validateInt,width=15)
        
        sx,sy = self.target_object.size
        ox,oy = self.target_object.offset
        self.size_x_data.set(sx)
        self.size_y_data.set(sy)
        self.off_x_data.set(ox)
        self.off_y_data.set(oy)     
        
        self.size_x_data.trace('w',self.changeVariable)
        self.size_y_data.trace('w',self.changeVariable)
        self.off_x_data.trace('w',self.changeVariable)
        self.off_y_data.trace('w',self.changeVariable)
        
    def changeVariable(self, *args):
        self.target_object.size = [self.size_x_data.get(),self.size_y_data.get()]
        self.target_object.offset = [self.off_x_data.get(),self.off_y_data.get()]
        
    def packChildren(self):
        self.label.grid(row=0,column=0)
        self.x_label.grid(row=0,column=1)
        self.y_label.grid(row=0,column=2)
        
        self.size_label.grid(row=1,column=0)
        self.size_x_entry.grid(row=1,column=1)
        self.size_y_entry.grid(row=1,column=2)
        
        self.off_label.grid(row=2,column=0)
        self.off_x_entry.grid(row=2,column=1)
        self.off_y_entry.grid(row=2,column=2)
        
    def update(self):
        self.packChildren()
