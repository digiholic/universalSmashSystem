from engine.subaction import *
from Tkinter import *
from tkColorChooser import askcolor 

class createMask(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('color','string','createMask>color','#FFFFFF'),
              NodeMap('duration','int','createMask>duration',0),
              NodeMap('pulse_length','int','createMask>pulse',0)
              ]
    
    def __init__(self,_color='#FFFFFF',_duration=0,_pulseLength=0):
        SubAction.__init__(self)
        self.color = _color
        self.duration = _duration
        self.pulse_length = _pulseLength
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        pulse = True if self.pulse_length > 0 else False
        colorobj = pygame.color.Color(self.color)
        color = [colorobj.r,colorobj.g,colorobj.b]
        _actor.createMask(color,self.duration,pulse,self.pulse_length)
    
    def getDisplayName(self):
        return 'Create Color Mask: ' + str(self.color)

    def getDataLine(self, _parent):
        return MaskLine(_parent,_parent.interior,self)
    
class MaskLine(dataSelector.dataLine):
    def __init__(self,_root,_parent,_target_object):
        dataSelector.dataLine.__init__(self, _root, _parent, 'Create Mask')
        
        self.target_object = _target_object
        
        self.color_data = StringVar()
        self.color_data.set('#000000')
        self.color_button = Button(self,text='   ',bg=self.color_data.get(),command=self.changeColor)
        
        self.duration_label = Label(self,text='Duration: ',bg=self.bg.get())
        self.duration_data = IntVar()
        self.duration_entry = Spinbox(self,from_=0,to=999,width=3,textvariable=self.duration_data)
        
        self.pulse_label = Label(self,text='Pulse: ',bg=self.bg.get())
        self.pulse_data = IntVar()
        self.pulse_entry = Spinbox(self,from_=0,to=999,width=3,textvariable=self.pulse_data)
        
        self.color_data.trace('w', self.changeVariable)
        self.duration_data.trace('w', self.changeVariable)
        self.pulse_data.trace('w', self.changeVariable)
        
    def changeColor(self,*args):
        color = askcolor(self.color_data.get())
        self.color_data.set(color[1])
        
    def changeVariable(self,*args):
        if self.target_object:
            self.target_object.color = self.color_data.get()
            self.target_object.duration = self.duration_data.get()
            self.target_object.pulse_length = self.pulse_data.get()
            
        dataSelector.dataLine.changeVariable(self)
        self.color_button.config(bg=self.color_data.get())
        
    def packChildren(self):
        dataSelector.dataLine.packChildren(self)
        self.color_button.pack(side=LEFT)
        self.duration_label.pack(side=LEFT)
        self.duration_entry.pack(side=LEFT)
        self.pulse_label.pack(side=LEFT)
        self.pulse_entry.pack(side=LEFT)
        
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