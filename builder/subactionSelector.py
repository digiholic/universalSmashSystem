import sys
import os

# Python 3 compatibility
if sys.version_info[0] == 3:
    import tkinter as tk
    from tkinter.filedialog import askopenfile, askdirectory
    from tkinter import ttk
else:
    import Tkinter as tk
    from tkFileDialog import askopenfile, askdirectory
    import ttk

import settingsManager

class Selector(tk.Label):
    def __init__(self,_root):
        self.display_name = StringVar()
        self.display_name.set('')
        
        self.property_frame = None
        self.data = None
        self.selected = False
        
        Label.__init__(self, _root.interior, textvariable=self.display_name, bg="white", anchor=W)
        self.root = _root.parent
        self.bind("<Button-1>", self.onClick)
        
    def onClick(self,*_args):
        if self.selected:
            self.unselect()
        else:
            self.select()
        if not self.root.selected:
            self.root.selected_string.set('')
    
    def select(self):
        self.selected = True
        self.config(bg="lightblue")
        if self.root.selected:
            self.root.selected.unselect()
        self.root.selected = self
        if self.data:
            self.root.selected_string.set(str(self.data))
    
    def unselect(self):
        self.selected = False
        self.config(bg="white")
        self.root.selected = None

    def updateName(self,_string):
        if _string: self.display_name.set(_string)
    
class SubactionSelector(Selector):
    def __init__(self,_root,_data):
        Selector.__init__(self, _root)
        
        self.data = _data
        self.display_name.set(self.data.getDisplayName())
        
        self.delete_image = PhotoImage(file=settingsManager.createPath('sprites/icons/red-x.gif'))
        self.confirm_button = PhotoImage(file=settingsManager.createPath('sprites/icons/green-check.gif'))
        self.delete_button = Button(self,image=self.delete_image,command=self.deleteSubaction)
        
        self.property_frame = _data.getPropertiesPanel(self.root.parent.subaction_property_panel)
        self.delete_button.pack(side=RIGHT)
            
    def deleteSubaction(self,*_args):
        action = self.root.getAction()
        groupMap = {"Current Frame": action.actions_at_frame[self.root.getFrame()],
                    "Set Up": action.set_up_actions,
                    "Tear Down": action.tear_down_actions,
                    "Transitions": action.state_transition_actions,
                    "Before Frames": action.actions_before_frame,
                    "After Frames": action.actions_after_frame,
                    "Last Frame": action.actions_at_last_frame}
        groupMap[self.root.group].remove(self.data)
        self.pack_forget()
        self.root.root.actionModified()

    def updateName(self,_string=None):
        Selector.updateName(self, _string)
        self.display_name.set(self.data.getDisplayName())

class PropertySelector(Selector):
    def __init__(self, _root, _owner, _varname, _fieldname, _vartype):
        Selector.__init__(self, _root)

        self.data = (_fieldname, _vartype, _owner, _varname)
        fielddata = ''
        if hasattr(_owner, _varname): fielddata = getattr(_owner, _varname)
        self.display_name.set(_fieldname+': '+ str(fielddata))
        
        self.property_frame = ChangeAttributeFrame(self.root.parent.subaction_property_panel,[self.data])
    
    def updateName(self, _string=None):
        Selector.updateName(self, _string)
        _owner = self.data[2]
        _varname = self.data[3]
        fielddata = ''
        if hasattr(_owner, _varname): fielddata = getattr(_owner, _varname)
        self.display_name.set(self.data[0]+': '+ str(fielddata))
        
class ChangeAttributeFrame(tk.Frame):
    def __init__(self,_root,_attribSet):
        Frame.__init__(self,_root,height=_root.winfo_height())
        self.root = _root
        
        self.data = []
        #attrib is in the form ('name','type',object,property)
        current_row = 0
        for attrib in _attribSet:
            name, vartype, obj, prop = attrib
            attrib_label = Label(self,text=name+':')
            if vartype == 'string':
                attrib_var = StringVar(self)
                attrib_var.set(str(self.getFromAttrib(obj, prop)))
                attrib_entry = Entry(self,textvariable=attrib_var)
            elif vartype == 'int':
                attrib_var = IntVar(self)
                attrib_var.set(int(self.getFromAttrib(obj, prop)))
                attrib_entry = Spinbox(self,from_=-255,to=255,textvariable=attrib_var)
            elif vartype == 'float':
                attrib_var = DoubleVar(self)
                attrib_var.set(float(self.getFromAttrib(obj, prop)))
                attrib_entry = Spinbox(self,from_=-255,to=255,textvariable=attrib_var,increment=0.01,format='%.2f')
            elif vartype == 'bool':
                attrib_var = BooleanVar(self)
                attrib_var.set(bool(self.getFromAttrib(obj, prop)))
                attrib_entry = Checkbutton(self,variable=attrib_var)
            elif vartype == 'sprite':
                attrib_var = StringVar(self)
                attrib_var.set(self.getFromAttrib(obj, prop))
                attrib_entry = OptionMenu(self,attrib_var,*self.root.getFighter().sprite.image_library["right"].keys())
            else:
                attrib_var = StringVar(self)
                attrib_var.set(str(self.getFromAttrib(obj, prop)))
                attrib_entry = Frame(self)
                
                file_name = Entry(attrib_entry,textvariable=attrib_var,state=DISABLED)
                
                if vartype == 'image':
                    fileType = 'file'
                    fileTuple = [('Image Files','*.png')]
                elif vartype == 'module':
                    fileType = 'file'
                    fileTuple = [('TUSSLE ActionScript files','*.xml'),('Python Files','*.py')]
                elif vartype == 'dir':
                    fileType = 'dir'
                    fileTuple = []
                
                loadCommand = lambda _resultVar=attrib_var,_fileType=fileType,_fileTuple=fileTuple: self.pickFile(_resultVar,_fileType,_fileTuple)
                load_file_button = Button(attrib_entry,text='...',command=loadCommand)
                
                file_name.pack(side=LEFT,fill=X)
                load_file_button.pack(side=RIGHT)

            attrib_label.grid(row=current_row,column=0)
            attrib_entry.grid(row=current_row,column=1)
            self.data.append((attrib,attrib_var))
            current_row += 1
        
        confirm_button = Button(self,text="confirm",command=self.saveData)
        confirm_button.grid(row=current_row,columnspan=2)
        
    def saveData(self,*_args):
        for data in self.data:
            _, vartype, obj, prop = data[0]
            val = data[1].get()
            #Cast it to the proper type
            if vartype == 'string': val = str(val)
            elif vartype == 'int': val = int(val)
            elif vartype == 'float': val = float(val)
            elif vartype == 'bool': val = bool(val)
            
            self.setFromAttrib(obj, prop, val)
        
        self.root.root.actionModified()
            
    def getFromAttrib(self,_obj,_prop):
        if isinstance(_obj, dict):
            return _obj[_prop]
        else:
            return getattr(_obj, _prop)
    
    def setFromAttrib(self,_obj,_prop,_val):
        if isinstance(_obj, dict):
            _obj[_prop] = _val
        else:
            setattr(_obj, _prop, _val)
    
    def pickFile(self,_resultVar, _filetype='file', _extensions=[]):
        if _filetype == 'file':
            loaded_file = askopenfile(mode="r",
                               initialdir=settingsManager.createPath('fighters'),
                               filetypes=_extensions)
            loaded_name = loaded_file.name
        elif _filetype == 'dir':
            loaded_name = askdirectory(initialdir=settingsManager.createPath(''))
        res = os.path.relpath(loaded_name,os.path.dirname(self.root.root.fighter_file.name))
        _resultVar.set(res)
        
class BasePropertiesFrame(tk.Frame):
    def __init__(self,_root,_subaction):
        Frame.__init__(self, _root, height=_root.winfo_height())
        self.root = _root
        self.subaction = _subaction
        self.changed = False
        self.variable_list = {}
        
    def addVariable(self,_varType,_name):
        var = _varType(self)
        self.variable_list[_name] = var
        
    def getVar(self,_name):
        return self.variable_list[_name]
    
    def initVars(self):
        for (val,var) in self.variable_list.items():
            var.set(getattr(self.subaction,val))
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
                
    def variableChanged(self,_var,_varname,*_args):
        setattr(self.subaction, _varname, _var.get())
        self.root.root.actionModified()    
    
class IfProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        #Create Variables
        self.addVariable(StringVar, 'variable')
        self.addVariable(StringVar, 'source')
        self.addVariable(StringVar, 'function')
        self.addVariable(StringVar, 'if_actions')
        self.addVariable(StringVar, 'else_actions')
        
        #Value is special, so they need to be made differently
        self.value_var = StringVar(self)
        self.value_var.set(_subaction.value)
        self.value_type_var = StringVar(self)
        self.value_type_var.set(type(_subaction.value).__name__)
        self.value_var.trace('w', self.valueChanged)
        self.value_type_var.trace('w', self.valueChanged)
        
        variable_label = Label(self,text="Variable:")
        source_label = Label(self,text="Source:")
        value_label = Label(self,text="Value:")
        if_label = Label(self,text="Pass:")
        else_label = Label(self,text="Fail:")
        
        variable_entry = Entry(self,textvariable=self.getVar('variable'))
        source_entry = OptionMenu(self,self.getVar('source'),*['action','fighter'])
        function_entry = OptionMenu(self,self.getVar('function'),*['==','!=','>','<','>=','<='])
        value_entry = Entry(self,textvariable=self.value_var)
        value_type_entry = OptionMenu(self,self.value_type_var,*['string','int','float','bool'])
        
        conditionals = ['']
        conditionals.extend(_root.getAction().conditional_actions.keys())
        if_entry = OptionMenu(self,self.getVar('if_actions'),*conditionals)
        else_entry = OptionMenu(self,self.getVar('else_actions'),*conditionals)
        
        self.initVars()
        
        source_label.grid(row=0,column=0,sticky=E)
        source_entry.grid(row=0,column=1,columnspan=2,sticky=E+W)
        variable_label.grid(row=1,column=0,sticky=E)
        variable_entry.grid(row=1,column=1,sticky=E+W)
        function_entry.grid(row=1,column=2,sticky=E+W)
        value_label.grid(row=2,column=0,sticky=E)
        value_entry.grid(row=2,column=1,sticky=E+W)
        value_type_entry.grid(row=2,column=2,sticky=E+W)
        if_label.grid(row=3,column=0,sticky=E)
        if_entry.grid(row=3,column=1,columnspan=2,sticky=E+W)
        else_label.grid(row=4,column=0,sticky=E)
        else_entry.grid(row=4,column=1,columnspan=2,sticky=E+W)
            
    def valueChanged(self,*_args):
        value = self.value_var.get()
        valtype = self.value_type_var.get()
        if valtype == 'int': self.subaction.value = int(value)
        elif valtype == 'float': self.subaction.value = float(value)
        elif valtype == 'bool': self.subaction.value = bool(value)
        else: self.subaction.value = value
        self.root.root.actionModified()

class IfButtonProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        #Create Variables
        self.addVariable(StringVar, 'button')
        self.addVariable(BooleanVar, 'held')
        self.addVariable(IntVar, 'buffer_time')
        self.addVariable(StringVar, 'if_actions')
        self.addVariable(StringVar, 'else_actions')
        
        button_label = Label(self,text="Button:")
        buffer_label = Label(self,text="Buffer:")
        if_label = Label(self,text="Pass:")
        else_label = Label(self,text="Fail:")
        
        button_entry = OptionMenu(self,self.getVar('button'),*['left','right','up','down','attack','jump','special','shield'])
        held_entry = Checkbutton(self,text="Held?",variable=self.getVar('held'))
        buffer_entry = Spinbox(self,textvariable=self.getVar('buffer_time'),from_=0,to=255)
        
        conditionals = ['']
        conditionals.extend(_root.getAction().conditional_actions.keys())
        if_entry = OptionMenu(self,self.getVar('if_actions'),*conditionals)
        else_entry = OptionMenu(self,self.getVar('else_actions'),*conditionals)
        
        self.initVars()
        
        button_label.grid(row=0,column=0,sticky=E)
        button_entry.grid(row=0,column=1,sticky=E+W)
        held_entry.grid(row=0,column=2)
        buffer_label.grid(row=1,column=0,sticky=E)
        buffer_entry.grid(row=1,column=1,columnspan=2,sticky=E+W)
        if_label.grid(row=2,column=0,sticky=E)
        if_entry.grid(row=2,column=1,columnspan=2,sticky=E+W)
        else_label.grid(row=3,column=0,sticky=E)
        else_entry.grid(row=3,column=1,columnspan=2,sticky=E+W)
              
class ChangeSpriteProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        sprite_label = Label(self,text="Sprite:")
        self.sprite_choice = StringVar(self)
        self.sprite_choice.set(self.subaction.sprite)
        
        sprite_vals = ['No Sprites found']
        if _root.getFighter():
            sprite_vals = _root.getFighter().sprite.image_library["right"].keys()
            
        sprites = OptionMenu(self,self.sprite_choice,*sprite_vals)
        sprites.config(width=18)
        sprite_label.grid(row=0,column=0)
        sprites.grid(row=0,column=1)
        self.sprite_choice.trace('w', self.changeActionSprite)
        
    def changeActionSprite(self,*_args):
        self.subaction.sprite = self.sprite_choice.get()
        self.root.root.actionModified()
        
class ChangeSubimageProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        subimage_label = Label(self,text="Subimage:")
        self.subimage_value = IntVar(self)
        self.subimage_value.set(self.subaction.index)
        
        if _root.getAction():
            subimage_spinner = Spinbox(self,from_=0,to=_root.getFighter().sprite.currentAnimLength()-1,textvariable=self.subimage_value)
            
        subimage_label.grid(row=0,column=0)
        subimage_spinner.grid(row=0,column=1)
        
        self.subimage_value.trace('w',self.changeSubimageValue)
        
    def changeSubimageValue(self,*_args):
        self.subaction.index = self.subimage_value.get()
        self.root.root.actionModified()
        
class ChangeSpeedProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        x_speed_label = Label(self,text="X Speed:")
        y_speed_label = Label(self,text="Y Speed:")
        
        self.addVariable(IntVar, 'speed_x')
        self.addVariable(IntVar, 'speed_y')
        self.addVariable(BooleanVar, 'x_relative')
        
        self.x_unchanged=BooleanVar(self)
        self.y_unchanged=BooleanVar(self)
        self.x_unchanged.set(not bool(self.subaction.speed_x))
        self.y_unchanged.set(not bool(self.subaction.speed_y))
        self.x_unchanged.trace('w', self.xUnchangedChanged)
        self.y_unchanged.trace('w', self.yUnchangedChanged)
        
        self.x_speed_entry = Spinbox(self,textvariable=self.getVar('speed_x'),from_=-255,to=255)
        self.x_speed_entry.config(width=4)
        self.y_speed_entry = Spinbox(self,textvariable=self.getVar('speed_y'),from_=-255,to=255)
        self.y_speed_entry.config(width=4)
        
        self.x_speed_relative = Checkbutton(self,variable=self.getVar('x_relative'),text="Relative?")
        x_unchanged_entry = Checkbutton(self,variable=self.x_unchanged,text="Leave X Unchanged")
        y_unchanged_entry = Checkbutton(self,variable=self.y_unchanged,text="Leave Y Unchanged")
        
        if self.x_unchanged.get():
            self.x_speed_entry.config(state=DISABLED)
            self.x_speed_relative.config(state=DISABLED)
        else:
            self.x_speed_entry.config(state=NORMAL)
            self.x_speed_relative.config(state=NORMAL)
            
        if self.y_unchanged.get(): self.y_speed_entry.config(state=DISABLED)
        else: self.y_speed_entry.config(state=NORMAL)
            
        self.initVars()
        
        x_unchanged_entry.grid(row=0,column=0, columnspan=3)
        x_speed_label.grid(row=1,column=0,sticky=E)
        self.x_speed_entry.grid(row=1,column=1,sticky=E+W)
        self.x_speed_relative.grid(row=1,column=2)
        y_unchanged_entry.grid(row=2,column=0, columnspan=3)
        y_speed_label.grid(row=3,column=0,sticky=E)
        self.y_speed_entry.grid(row=3,column=1,columnspan=2,sticky=E+W)
    
    def xUnchangedChanged(self,*_args): #boy this function's name is silly
        if self.x_unchanged.get():
            self.x_speed_entry.config(state=DISABLED)
            self.x_speed_relative.config(state=DISABLED)
            self.getVar('speed_x').set(0)
            self.subaction.speed_x = None
            self.root.root.actionModified()
        else:
            self.x_speed_entry.config(state=NORMAL)
            self.x_speed_relative.config(state=NORMAL)
            self.subaction.speed_x = self.getVar('speed_x').get()
            self.root.root.actionModified()
    
    def yUnchangedChanged(self,*_args):
        if self.y_unchanged.get():
            self.y_speed_entry.config(state=DISABLED)
            self.getVar('speed_y').set(0)
            self.subaction.speed_y = None
            self.root.root.actionModified()
        else:
            self.y_speed_entry.config(state=NORMAL)
            self.subaction.speed_y = self.getVar('speed_y').get()
            self.root.root.actionModified()
            
    def initVars(self):
        for (val,var) in self.variable_list.items():
            newval = getattr(self.subaction,val)
            if newval is None: var.set(0)
            else: var.set(newval)
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
    
    def variableChanged(self,_var,_varname,*_args):
        print(_var,_var.get(),_varname)
        if _varname == 'speed_x' and self.x_unchanged.get(): return
        if _varname == 'speed_y' and self.y_unchanged.get(): return
        setattr(self.subaction, _varname, _var.get())
        self.root.root.actionModified()
        
class ShiftPositionProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        x_speed_label = Label(self,text="New X:")
        y_speed_label = Label(self,text="New Y:")
        
        self.addVariable(IntVar, 'new_x')
        self.addVariable(IntVar, 'new_y')
        self.addVariable(BooleanVar, 'x_relative')
        self.addVariable(BooleanVar, 'y_relative')
        
        self.x_unchanged=BooleanVar(self)
        self.y_unchanged=BooleanVar(self)
        self.x_unchanged.set(not bool(self.subaction.new_x))
        self.y_unchanged.set(not bool(self.subaction.new_y))
        self.x_unchanged.trace('w', self.xUnchangedChanged)
        self.y_unchanged.trace('w', self.yUnchangedChanged)
        
        self.x_speed_entry = Spinbox(self,textvariable=self.getVar('new_x'),from_=-255,to=255)
        self.x_speed_entry.config(width=4)
        self.y_speed_entry = Spinbox(self,textvariable=self.getVar('new_y'),from_=-255,to=255)
        self.y_speed_entry.config(width=4)
        
        self.x_speed_relative = Checkbutton(self,variable=self.getVar('x_relative'),text="Relative?")
        self.ySpeedRelative = Checkbutton(self,variable=self.getVar('y_relative'),text="Relative?")
        x_unchanged_entry = Checkbutton(self,variable=self.x_unchanged,text="Leave X Unchanged")
        y_unchanged_entry = Checkbutton(self,variable=self.y_unchanged,text="Leave Y Unchanged")
        
        if self.x_unchanged.get():
            self.x_speed_entry.config(state=DISABLED)
            self.x_speed_relative.config(state=DISABLED)
        else:
            self.x_speed_entry.config(state=NORMAL)
            self.x_speed_relative.config(state=NORMAL)
            
        if self.y_unchanged.get():
            self.y_speed_entry.config(state=DISABLED)
            self.ySpeedRelative.config(state=DISABLED)
        else:
            self.y_speed_entry.config(state=NORMAL)
            self.ySpeedRelative.config(state=NORMAL)
            
        self.initVars()
        
        x_unchanged_entry.grid(row=0,column=0, columnspan=3)
        x_speed_label.grid(row=1,column=0,sticky=E)
        self.x_speed_entry.grid(row=1,column=1,sticky=E+W)
        self.x_speed_relative.grid(row=1,column=2)
        y_unchanged_entry.grid(row=2,column=0, columnspan=3)
        y_speed_label.grid(row=3,column=0,sticky=E)
        self.y_speed_entry.grid(row=3,column=1,sticky=E+W)
        self.ySpeedRelative.grid(row=3,column=2)
        
    def xUnchangedChanged(self,*_args): #boy this function's name is silly
        if self.x_unchanged.get():
            self.x_speed_entry.config(state=DISABLED)
            self.x_speed_relative.config(state=DISABLED)
            self.getVar('speed_x').set(0)
            self.subaction.speed_x = None
            self.root.root.actionModified()
        else:
            self.x_speed_entry.config(state=NORMAL)
            self.x_speed_relative.config(state=NORMAL)
            self.subaction.speed_x = self.getVar('speed_x').get()
            self.root.root.actionModified()
    
    def yUnchangedChanged(self,*_args):
        if self.y_unchanged.get():
            self.y_speed_entry.config(state=DISABLED)
            self.ySpeedRelative.config(state=DISABLED)
            self.getVar('speed_y').set(0)
            self.subaction.speed_y = None
            self.root.root.actionModified()
        else:
            self.y_speed_entry.config(state=NORMAL)
            self.ySpeedRelative.config(state=NORMAL)
            self.subaction.speed_y = self.getVar('speed_y').get()
            self.root.root.actionModified()
            
    def initVars(self):
        for (val,var) in self.variable_list.items():
            newval = getattr(self.subaction,val)
            if newval is None: var.set(0)
            else: var.set(newval)
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
    
    def variableChanged(self,_var,_varname,*_args):
        print(_var,_var.get(),_varname)
        if _varname == 'speed_x' and self.x_unchanged.get(): return
        if _varname == 'speed_y' and self.y_unchanged.get(): return
        setattr(self.subaction, _varname, _var.get())
        self.root.root.actionModified()

class ShiftSpriteProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        x_speed_label = Label(self,text="X Pos:")
        y_speed_label = Label(self,text="Y Pos:")
        
        self.addVariable(IntVar, 'new_x')
        self.addVariable(IntVar, 'new_y')
        self.addVariable(BooleanVar, 'x_relative')
        
        self.x_unchanged=BooleanVar(self)
        self.y_unchanged=BooleanVar(self)
        self.x_unchanged.set(not bool(self.subaction.new_x))
        self.y_unchanged.set(not bool(self.subaction.new_y))
        self.x_unchanged.trace('w', self.xUnchangedChanged)
        self.y_unchanged.trace('w', self.yUnchangedChanged)
        
        self.x_speed_entry = Spinbox(self,textvariable=self.getVar('new_x'),from_=-255,to=255)
        self.x_speed_entry.config(width=4)
        self.y_speed_entry = Spinbox(self,textvariable=self.getVar('new_y'),from_=-255,to=255)
        self.y_speed_entry.config(width=4)
        
        self.x_speed_relative = Checkbutton(self,variable=self.getVar('x_relative'),text="Relative?")
        x_unchanged_entry = Checkbutton(self,variable=self.x_unchanged,text="Leave X Unchanged")
        y_unchanged_entry = Checkbutton(self,variable=self.y_unchanged,text="Leave Y Unchanged")
        
        if self.x_unchanged.get():
            self.x_speed_entry.config(state=DISABLED)
            self.x_speed_relative.config(state=DISABLED)
        else:
            self.x_speed_entry.config(state=NORMAL)
            self.x_speed_relative.config(state=NORMAL)
            
        if self.y_unchanged.get(): self.y_speed_entry.config(state=DISABLED)
        else: self.y_speed_entry.config(state=NORMAL)
            
        self.initVars()
        
        x_unchanged_entry.grid(row=0,column=0, columnspan=3)
        x_speed_label.grid(row=1,column=0,sticky=E)
        self.x_speed_entry.grid(row=1,column=1,sticky=E+W)
        self.x_speed_relative.grid(row=1,column=2)
        y_unchanged_entry.grid(row=2,column=0, columnspan=3)
        y_speed_label.grid(row=3,column=0,sticky=E)
        self.y_speed_entry.grid(row=3,column=1,columnspan=2,sticky=E+W)
    
    def xUnchangedChanged(self,*_args): #boy this function's name is silly
        if self.x_unchanged.get():
            self.x_speed_entry.config(state=DISABLED)
            self.x_speed_relative.config(state=DISABLED)
            self.getVar('new_x').set(0)
            self.subaction.new_x = None
            self.root.root.actionModified()
        else:
            self.x_speed_entry.config(state=NORMAL)
            self.x_speed_relative.config(state=NORMAL)
            self.subaction.new_x = self.getVar('new_x').get()
            self.root.root.actionModified()
    
    def yUnchangedChanged(self,*_args):
        if self.y_unchanged.get():
            self.y_speed_entry.config(state=DISABLED)
            self.getVar('new_y').set(0)
            self.subaction.new_y = None
            self.root.root.actionModified()
        else:
            self.y_speed_entry.config(state=NORMAL)
            self.subaction.new_y = self.getVar('new_y').get()
            self.root.root.actionModified()
            
    def initVars(self):
        for (val,var) in self.variable_list.items():
            newval = getattr(self.subaction,val)
            if newval is None: var.set(0)
            else: var.set(newval)
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
    
    def variableChanged(self,_var,_varname,*_args):
        print(_var,_var.get(),_varname)
        if _varname == 'new_x' and self.x_unchanged.get(): return
        if _varname == 'new_y' and self.y_unchanged.get(): return
        setattr(self.subaction, _varname, _var.get())
        self.root.root.actionModified()
    
class UpdateLandingLagProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        self.addVariable(IntVar, 'new_lag')
        self.addVariable(BooleanVar, 'reset')
        
        lag_label = Label(self,text="New Lag:")
        
        lag_entry = Spinbox(self,textvariable=self.getVar('new_lag'),from_=0,to=255)
        reset_button = Checkbutton(self,variable=self.getVar('reset'),text="Reset even if lower?")
        
        self.initVars()
        
        lag_label.grid(row=0,column=0,sticky=E)
        lag_entry.grid(row=0,column=1,sticky=E+W)
        reset_button.grid(row=1,column=0,columnspan=2)

class ModifyFighterVarProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        self.addVariable(StringVar, 'attr')
        
        attr_label = Label(self,text="Variable:")
        value_label = Label(self,text="Value:")
            
        self.value_var = StringVar(self)
        self.value_type_var = StringVar(self)
        self.value_var.set(_subaction.val)
        self.value_type_var.set(type(_subaction.value).__name__)
        self.value_var.trace('w', self.valueChanged)
        self.value_type_var.trace('w', self.valueChanged)
        
        attr_entry = Entry(self,textvariable=self.getVar('attr'))
        value_entry = Entry(self,textvariable=self.value_var)
        value_type_entry = OptionMenu(self,self.value_type_var,*['string','int','float','bool'])
        
        self.initVars()
        
        attr_label.grid(row=0,column=0,sticky=E)
        attr_entry.grid(row=0,column=1,columnspan=2,sticky=E+W)
        value_label.grid(row=0,column=0,sticky=E)
        value_entry.grid(row=0,column=1,sticky=E+W)
        value_type_entry.grid(row=0,column=2,sticky=E+W)
        
    def valueChanged(self,*_args):
        value = self.value_var.get()
        valtype = self.value_type_var.get()
        if valtype == 'int': self.subaction.value = int(value)
        elif valtype == 'float': self.subaction.value = float(value)
        elif valtype == 'bool': self.subaction.value = bool(value)
        else: self.subaction.val = value
        self.root.root.actionModified()
 
class ChangeFrameProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        self.addVariable(IntVar, 'new_frame')
        self.addVariable(BooleanVar, 'relative')
        
        frame_label = Label(self,text="Frame:")
        
        frame_entry = Spinbox(self,textvariable=self.getVar('new_frame'),from_=-255,to=255)
        relative_entry = Checkbutton(self,variable=self.getVar('relative'),text="Relative?")
        
        self.initVars()
        
        frame_label.grid(row=0,column=0,sticky=E)
        frame_entry.grid(row=0,column=1,sticky=E+W)
        relative_entry.grid(row=0,column=2)
        
class TransitionProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        self.addVariable(StringVar, 'transition')
        transition_label = Label(self,text='Transition State:')
        import engine
        transition_entry = OptionMenu(self,self.getVar('transition'),*engine.baseActions.state_dict.keys())
        
        self.initVars()
        
        transition_label.grid(row=0,column=0,sticky=E)
        transition_entry.grid(row=0,column=1,sticky=E+W)
        
class ModifyHitboxProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction,newHitbox=False):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        import engine
        if self.subaction.hitbox_name in _root.getAction().hitboxes:
            self.hitbox = _root.getAction().hitboxes[self.subaction.hitbox_name]
        else: self.hitbox = engine.hitbox.Hitbox(_root.getFighter(),engine.hitbox.HitboxLock())
        self.variable_list = []
        
        main_frame = ttk.Notebook(self)
        properties_frame = HitboxPropertiesFrame(self,newHitbox)
        damage_frame = ttk.Frame(main_frame)
        charge_frame = ttk.Frame(main_frame)
        override_frame = ttk.Frame(main_frame)
        autolink_frame = ttk.Frame(main_frame)
        funnel_frame = ttk.Frame(main_frame)
        
        main_frame.add(properties_frame,text="Properties")
        main_frame.add(damage_frame,text="Damage")
        #if isinstance(self.root.getAction(), engine.baseActions.ChargeAttack): main_frame.add(charge_frame,text="Charge")
        main_frame.add(override_frame,text="Override")
        if isinstance(self.hitbox, engine.hitbox.AutolinkHitbox): main_frame.add(autolink_frame,text="Autolink")
        if isinstance(self.hitbox, engine.hitbox.FunnelHitbox): main_frame.add(funnel_frame,text="Funnel")
        
        main_frame.pack()
        
        """""""""""""""""""""""""""
        Build the damage Frame
        """""""""""""""""""""""""""
        damage_label = Label(damage_frame,text="Damage:")
        bkb_label = Label(damage_frame,text="Base Knockback:")
        kbg_label = Label(damage_frame,text="Knockback Growth:")
        trajectory_label = Label(damage_frame,text="Trajectory:")
        hitstun_label = Label(damage_frame,text="Hitstun Multiplier:")
        
        damageVar = DoubleVar(self)
        bkbVar = IntVar(self)
        kbgVar = DoubleVar(self)
        trajectoryVar = IntVar(self)
        hitstunVar = DoubleVar(self)
        
        self.variable_list.append((damageVar,'damage'))
        self.variable_list.append((bkbVar,'base_knockback'))
        self.variable_list.append((kbgVar,'knockback_growth'))
        self.variable_list.append((trajectoryVar,'trajectory'))
        self.variable_list.append((hitstunVar,'hitstun_multiplier'))
        
        damage_entry = Spinbox(damage_frame,textvariable=damageVar,from_=0,to=255,increment=0.5,format='%.1f')
        bkb_entry = Spinbox(damage_frame,textvariable=bkbVar,from_=-255,to=255)
        kbg_entry = Spinbox(damage_frame,textvariable=kbgVar,from_=-255,to=255,increment=0.01,format='%.2f')
        trajectory_entry = Spinbox(damage_frame,textvariable=trajectoryVar,from_=0,to=360)
        hitstun_entry = Spinbox(damage_frame,textvariable=hitstunVar,from_=0,to=255,increment=0.01,format='%.2f')
        
        damage_label.grid(row=0,column=0,sticky=E)
        damage_entry.grid(row=0,column=1)
        bkb_label.grid(row=1,column=0,sticky=E)
        bkb_entry.grid(row=1,column=1)
        kbg_label.grid(row=2,column=0,sticky=E)
        kbg_entry.grid(row=2,column=1)
        trajectory_label.grid(row=3,column=0,sticky=E)
        trajectory_entry.grid(row=3,column=1)
        hitstun_label.grid(row=4,column=0,sticky=E)
        hitstun_entry.grid(row=4,column=1)
        
        """""""""""""""""""""""""""
        Build the charge Frame
        """""""""""""""""""""""""""
        charge_damage_label = Label(charge_frame,text="Damage/charge:")
        charge_bkb_label = Label(charge_frame,text="Knockback/charge:")
        charge_kbg_label = Label(charge_frame,text="Growth/charge:")
        
        charge_damage_label.grid(row=0,column=0,sticky=E)
        charge_bkb_label.grid(row=1,column=0,sticky=E)
        charge_kbg_label.grid(row=2,column=0,sticky=E)
        
        """""""""""""""""""""""""""
        Build the override Frame
        """""""""""""""""""""""""""
        
        #Create the variable tracers
        for (var,val) in self.variable_list:
            print(var,val)
            var.set(self.populateHitboxVariable(val))
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op,))
            
    def populateHitboxVariable(self,_variable):
        if _variable in self.subaction.hitbox_vars:
            return self.subaction.hitbox_vars[_variable]
        else: return getattr(self.hitbox,_variable)
    
    def variableChanged(self,_var,_varname,*_args):
        print(_var,_varname)
        hitbox_vars = {_varname: _var.get()}
        self.subaction.hitbox_vars.update(hitbox_vars)
        self.root.root.actionModified()
    
"""""""""""""""""""""""""""
Build the properties Frame
"""""""""""""""""""""""""""
class HitboxPropertiesFrame(ttk.Frame):
    def __init__(self, _parent, _newHitbox=False):
        ttk.Frame.__init__(self, _parent)
        self.parent = _parent
        
        self.subaction = _parent.subaction
        self.hitbox = _parent.hitbox
        
        name_label = Label(self,text="Hitbox Name:")
        type_label = Label(self,text="Type:")
        center_label = Label(self,text="Center:")
        size_label = Label(self,text="Size:")
        lock_label = Label(self,text="Lock:")
        
        self.hitbox_name = StringVar(self)
        self.hitbox_type = StringVar(self)
        self.hitbox_lock = StringVar(self)
        self.center_x = IntVar(self)
        self.center_y = IntVar(self)
        self.size_x = IntVar(self)
        self.size_y = IntVar(self)
        
        self.hitbox_name.set(self.subaction.hitbox_name)
        self.hitbox_type.set(self.hitbox.hitbox_type)
        self.hitbox_lock.set(self.hitbox.hitbox_lock.lock_name)
        
        self.name = self.hitbox_name.get()
        
        center = self.populateHitboxVariable('center')
        self.center_x.set(center[0])
        self.center_y.set(center[1])
        size = self.populateHitboxVariable('size')
        self.size_x.set(size[0])
        self.size_y.set(size[1])
        
        if _newHitbox:
            hitbox_types = ['damage','sakurai','autolink','funnel','grab','reflector']
            
            name_entry = Entry(self,textvariable=self.hitbox_name)
            type_entry = OptionMenu(self,self.hitbox_type,*hitbox_types)
            lock_entry = Entry(self,textvariable=self.hitbox_lock)
        else:
            hitbox_vals = ['No Hitboxes found']
            if _parent.root.getAction():
                hitbox_vals = _parent.root.getAction().hitboxes.keys()
                
            name_entry = OptionMenu(self,self.hitbox_name,*hitbox_vals)
            type_entry = Entry(self,textvariable=self.hitbox_type,state=DISABLED)
            lock_entry = Entry(self,textvariable=self.hitbox_lock,state=DISABLED)
        
        self.hitbox_name.trace('w',self.nameChanged)
        self.hitbox_type.trace('w',self.typeChanged)
        self.hitbox_lock.trace('w',self.lockChanged)
        
        center_x_entry = Spinbox(self,from_=-255,to=255,textvariable=self.center_x,width=4)
        center_y_entry = Spinbox(self,from_=-255,to=255,textvariable=self.center_y,width=4)
        size_x_entry = Spinbox(self,from_=-255,to=255,textvariable=self.size_x,width=4)
        size_y_entry = Spinbox(self,from_=-255,to=255,textvariable=self.size_y,width=4)
        
        self.center_x.trace('w',self.centerChanged)
        self.center_y.trace('w',self.centerChanged)
        self.size_x.trace('w',self.sizeChanged)
        self.size_y.trace('w',self.sizeChanged)
        
        name_label.grid(row=0,column=0,sticky=E)
        name_entry.grid(row=0,column=1,columnspan=2,sticky=E+W)
        type_label.grid(row=1,column=0,sticky=E)
        type_entry.grid(row=1,column=1,columnspan=2,sticky=E+W)
        lock_label.grid(row=2,column=0,sticky=E)
        lock_entry.grid(row=2,column=1,columnspan=2,sticky=E+W)
        center_label.grid(row=3,column=0,sticky=E)
        center_x_entry.grid(row=3,column=1)
        center_y_entry.grid(row=3,column=2)
        size_label.grid(row=4,column=0,sticky=E)
        size_x_entry.grid(row=4,column=1)
        size_y_entry.grid(row=4,column=2)
    
    def nameChanged(self,*_args):
        old_name = self.name
        new_name = self.hitbox_name.get()
        self.name = new_name
        self.subaction.hitbox_name = new_name
        
        #we need something in the action so that we can select it from a dropdown later
        if not new_name in self.parent.root.getAction().hitboxes: #Set our working Hitbox to the action
            self.parent.root.getAction().hitboxes[new_name] = self.hitbox
        if old_name in self.parent.root.getAction().hitboxes: #Set it to the Old one if it exists
            self.parent.root.getAction().hitboxes[new_name] = self.parent.root.getAction().hitboxes[old_name]
            del(self.parent.root.getAction().hitboxes[old_name])
        self.parent.root.root.actionModified()
        
    def typeChanged(self,*_args):
        new_type = self.hitbox_type.get()
        self.subaction.hitbox_type = new_type
        self.parent.root.root.actionModified()
        
    def lockChanged(self,*_args):
        new_lock = self.hitbox_lock.get()
        self.subaction.hitboxLock = new_lock
        self.parent.root.root.actionModified()
        
    def centerChanged(self,*_args):
        center = (self.center_x.get(),self.center_y.get())
        hitbox_vars = {"center": center}
        self.subaction.hitbox_vars.update(hitbox_vars)
        self.parent.root.root.actionModified()
        
    def sizeChanged(self,*_args):
        size = (self.size_x.get(),self.size_y.get())
        hitbox_vars = {"size": size}
        self.subaction.hitbox_vars.update(hitbox_vars)
        self.parent.root.root.actionModified()
        
    def populateHitboxVariable(self,_variable):
        if _variable in self.subaction.hitbox_vars:
            return self.subaction.hitbox_vars[_variable]
        else: return getattr(self.hitbox,_variable)
        
class UpdateHitboxProperties(BasePropertiesFrame):
    def __init__(self,_root,_subaction):
        BasePropertiesFrame.__init__(self, _root, _subaction)
        
        self.addVariable(StringVar, 'hitbox_name')
        
        hitbox_vals = ['No Hitboxes found']
        if _root.getAction():
            hitbox_vals = _root.getAction().hitboxes.keys()
        
        hitbox_label = Label(self,text="Hitbox:")
        hitbox_entry = OptionMenu(self,self.getVar('hitbox_name'),*hitbox_vals)
        
        self.initVars()
        
        hitbox_label.grid(row=0,column=0,sticky=E)
        hitbox_entry.grid(row=0,column=1,sticky=E+W)
