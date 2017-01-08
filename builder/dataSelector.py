from Tkinter import *
import settingsManager
from idlelib.ObjectBrowser import _object_browser
from tkFileDialog import askopenfile,askdirectory
import os
import tkMessageBox
import engine.action
import inspect

class dataLine(Frame):
    """
    A DataLine is an object that can be displayed in the right panel.
    This is the base class for those lines. It itself just displays text,
    with no functionality.
    """
    def __init__(self,_root,_parent,_name=''):
        """
        Parameters
        -----------
        _parent : tk
            The panel that this line belongs to
        _name : string
            The default name
        """
        self.display_name = StringVar()
        self.display_name.set(_name)
        
        self.bg = StringVar()
        self.bg.trace('w', self.changebg)
        
        Frame.__init__(self, _parent, bg="white")
        self.parent = _parent
        self.root = _root
        
        self.label = Label(self,textvariable=self.display_name)
        
        self.bg.set("gainsboro") #it's a real color. Who knew?
        self.visible = True
        
        self.target_object = None
        self.var_name = None
        
        #Use this to validate number fields
        self.validateFloat = (_parent.register(self.validateFloat),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        self.validateInt = (_parent.register(self.validateInt),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
    def changebg(self,*args):
        self.config(bg=self.bg.get())
        self.label.config(bg=self.bg.get())
        
    def packChildren(self):
        self.label.pack(side=LEFT)
        
    def pack(self, cnf={}, **kw):
        #if self.visible: 
        Frame.pack(self, cnf=cnf, **kw)
        
    def setButtons(self,_buttons):
        for button in _buttons:
            button.pack(side=RIGHT)
        
    def updateName(self,_string):
        if _string: self.display_name.set(_string)
       
    def changeVariable(self,*args):
        if isinstance(self.target_object, engine.action.Action):
            #need to update the changed actions
            self.root.getChangedActions()[self.root.action_name] = self.target_object
            self.root.root.updateViewer()
    
    """Validate method for numbers"""
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
             
    def validateInt(self, action, index, value_if_allowed,
        prior_value, text, validation_type, trigger_type, widget_name):
        allowed_chars = '0123456789-+'
        # action=1 -> insert
        if(action=='1'):
            if text in allowed_chars:
                try:
                    int(value_if_allowed)
                    return True
                except ValueError:
                    return False
            else:
                return False
        else:
            return True    
        
class dataSelector(dataLine):
    """
    Data Selector is a dataLine that can be selected. These will usually open up a config window.
    """
    def __init__(self,_root,_parent,_name=''):
        dataLine.__init__(self, _root, _parent, _name)
        self.selected = False
        self.bind("<Button-1>", self.onClick)
        self.label.bind("<Button-1>", self.onClick)
        self.bg.set('white')
        
    def onClick(self,*_args):
        if self.selected:
            self.unselect()
        else:
            self.select()
        #if not self.root.selected:
            #self.root.selected_string.set('')
    
    def select(self):
        self.selected = True
        self.bg.set('lightblue')
        if self.root.selected:
            self.root.selected.unselect()
        self.root.selected = self
        
    def unselect(self):
        self.selected = False
        self.bg.set('white')
        self.root.selected = None

class InfoLine(dataLine):
    def __init__(self,_root,_parent,_name):
        dataLine.__init__(self, _root, _parent, _name)
        
    def packChildren(self):
        dataLine.packChildren(self)
        
    def update(self):
        self.packChildren()


class StringLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.string_data = StringVar()
        self.string_entry = Entry(self,textvariable=self.string_data)
        
        self.string_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.string_data.get())
        dataLine.changeVariable(self)
        
    def packChildren(self):
        dataLine.packChildren(self)
        self.string_entry.pack(side=LEFT,fill=BOTH)
    
    def update(self):
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.string_data.set(getattr(self.target_object, self.var_name))
            self.string_entry.config(state=NORMAL)
        else:
            self.string_entry.config(state=DISABLED)
        
        self.packChildren()

class BoolLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.bool_data = IntVar()
        self.bool_button = Checkbutton(self,text=_name,variable=self.bool_data,anchor="w")
        self.bool_button.config(bg=self.bg.get())
        
        self.bool_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,bool(self.bool_data.get()))
        dataLine.changeVariable(self)
        
    def packChildren(self):
        self.bool_button.pack(side=LEFT,fill=BOTH,expand=TRUE)
        
    def update(self):
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            if getattr(self.target_object, self.var_name):
                self.bool_data.set(1)
            else: self.bool_data.set(0)
            self.bool_button.config(state=NORMAL)
        else:
            self.bool_button.config(state=DISABLED)
        
        self.packChildren()
                
class ImageLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.image_data = StringVar()
        self.image_entry = Entry(self,textvariable=self.image_data)
        self.image_button = Button(self,text='...',command=self.loadImage)
        self.image_entry.config(state=DISABLED)
        
        self.image_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.image_data.get())
        dataLine.changeVariable(self)
        
    def packChildren(self):
        dataLine.packChildren(self)
        self.image_entry.pack(side=LEFT,fill=BOTH)
        self.image_button.pack(side=LEFT)
    
    def update(self):
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.image_data.set(getattr(self.target_object, self.var_name))
            self.image_button.config(state=NORMAL)
        else:
            self.image_button.config(state=DISABLED)
        
        self.packChildren()
    
    def loadImage(self):
        if self.target_object:
            imgfile = askopenfile(mode="r",initialdir=self.target_object.base_dir,filetypes=[('Image Files','*.png')])
            self.image_data.set(os.path.relpath(imgfile.name, self.target_object.base_dir))

class DirLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.dir_data = StringVar()
        self.dir_entry = Entry(self,textvariable=self.dir_data)
        self.dir_button = Button(self,text='...',command=self.loadDir)
        self.dir_entry.config(state=DISABLED)
        
        self.dir_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.dir_data.get())
        dataLine.changeVariable(self)
        
    def packChildren(self):
        dataLine.packChildren(self)
        self.dir_entry.pack(side=LEFT,fill=BOTH)
        self.dir_button.pack(side=LEFT)
    
    def update(self):
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.dir_data.set(getattr(self.target_object, self.var_name))
            self.dir_button.config(state=NORMAL)
        else:
            self.dir_button.config(state=DISABLED)
        
        self.packChildren()
    
    def loadDir(self):
        if self.target_object:
            directory = askdirectory(initialdir=self.target_object.base_dir)
            self.dir_data.set(os.path.relpath(directory, self.target_object.base_dir))

class ModuleLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.module_data = StringVar()
        self.module_entry = Entry(self,textvariable=self.module_data)
        self.module_button = Button(self,text='...',command=self.loadImage)
        self.module_entry.config(state=DISABLED)
        
        self.module_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.module_data.get())
        dataLine.changeVariable(self)
        
    def packChildren(self):
        dataLine.packChildren(self)
        self.module_entry.pack(side=LEFT,fill=BOTH)
        self.module_button.pack(side=LEFT)
    
    def update(self):
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.module_data.set(getattr(self.target_object, self.var_name))
            self.module_button.config(state=NORMAL)
        else:
            self.module_button.config(state=DISABLED)
        
        self.packChildren()
    
    def loadImage(self):
        if self.target_object:
            modulefile = askopenfile(mode="r",initialdir=self.target_object.base_dir,filetypes=[('TUSSLE ActionScript files','*.xml'),('Python Files','*.py')])
            self.module_data.set(os.path.relpath(modulefile.name, self.target_object.base_dir))

class NumLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname,_int=False):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        self.int_only = _int
        
        self.num_data = StringVar()
        validate = self.validateFloat
        if _int: validate = self.validateInt
        self.num_entry = Entry(self,textvariable=self.num_data,validate='key',validatecommand=validate)
        
        self.num_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            if self.int_only: num = int(self.num_data.get())
            else: num = float(self.num_data.get())
            setattr(self.target_object,self.var_name,num)
        dataLine.changeVariable(self)
        
    def packChildren(self):
        dataLine.packChildren(self)
        self.num_entry.pack(side=LEFT,fill=BOTH)
    
    def update(self):
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.num_data.set(getattr(self.target_object, self.var_name))
            self.num_entry.config(state=NORMAL)
        else:
            self.num_entry.config(state=DISABLED)
        
        self.packChildren()

class SpriteLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        
        self.sprite_data = StringVar(self)
        
        sprite_vals = ['No Sprites found']
        if self.root.getFighter():
            sprite_vals = self.root.getFighter().sprite.image_library["right"].keys()
            
        self.sprite_entry = OptionMenu(self,self.sprite_data,*sprite_vals)
        self.sprite_entry.config(width=18)
        self.sprite_data.trace('w', self.changeVariable)
        
        self.sprite_data.set(getattr(self.target_object, self.var_name))
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.sprite_data.get())
        dataLine.changeVariable(self)
            
    def packChildren(self):
        dataLine.packChildren(self)
        self.sprite_entry.pack(side=LEFT,fill=BOTH)
    
    def update(self):
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.sprite_data.set(getattr(self.target_object, self.var_name))
            self.sprite_entry.config(state=NORMAL)
        else:
            self.sprite_entry.config(state=DISABLED)
        
        self.packChildren()
   
class ActionLine(dataSelector):
    def __init__(self,_root,_parent,_action,_target_object):
        dataSelector.__init__(self, _root, _parent, _action)
        
        self.target_object = _target_object
        self.action_name = _action
        
        self.edit_button = Button(self,text='Edit',command=self.editAction)
        self.delete_button = Button(self,text='Delete',command=self.deleteAction)
    
    def select(self):
        dataSelector.select(self)    
        self.root.setAction(self.action_name)
        
    def changeVariable(self,*args):
        pass
    
    def packChildren(self):
        dataSelector.packChildren(self)
        self.delete_button.pack(side=RIGHT)
        self.edit_button.pack(side=RIGHT)
        
    def update(self):
        self.packChildren()
        
    def editAction(self,*args):
        self.root.parent.addActionPane(self.action_name)
        
    def deleteAction(self,*args):
        choice = tkMessageBox.askquestion("Delete", "Are You Sure you want to delete the action "+self.display_name.get()+"?", icon='warning')
        if choice == 'yes':
            self.root.deleteAction(self.action_name)
        
class NewActionLine(dataLine):
    def __init__(self,_root,_parent,_target_object):
        dataLine.__init__(self, _root, _parent, 'Create New Action...')
        
        self.button = Button(self,text='Create New Action...',bg="aquamarine",command=self.addAction)
        self.config(bg="aquamarine")
        self.label.config(bg="aquamarine")
            
    def update(self):
        self.packChildren()
        
    def packChildren(self):
        self.button.pack(side=LEFT,fill=BOTH,expand=TRUE)
        
    def addAction(self,*args):
        self.root.addAction()

class CloseActionLine(dataLine):
    def __init__(self,_root,_parent):
        dataLine.__init__(self, _root, _parent, 'Close Tab')
        
        self.button = Button(self,text='Close Tab',bg="light coral",command=self.closeTab)
        
    def update(self):
        self.packChildren()
        
    def packChildren(self):
        self.button.pack(side=LEFT,fill=BOTH,expand=TRUE)
        
    def closeTab(self,*args):
        self.root.closeTab()

class GroupLine(dataLine):
    """
    A group selector has an expand/collapse button to view or hide its children.
    """
    def __init__(self,_root,_parent,_name):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.expanded = False
        #self.collapsed_image = PhotoImage(file=settingsManager.createPath('sprites/icons/right.png'))
        #self.expanded_image  = PhotoImage(file=settingsManager.createPath('sprites/icons/down.png'))
        self.toggle_button = Button(self,text='- '+_name,command=self.toggleCollapse,anchor="w")
        
        self.childElements = []
        
    def update(self):
        if self.expanded: #If we're expanded
            self.toggle_button.config(text='- '+self.display_name.get())
            self.toggle_button.config(relief=SUNKEN)
            
        else: #If we're collapsed
            self.toggle_button.config(text='+ '+self.display_name.get())
            self.toggle_button.config(relief=RAISED)
            
        self.packChildren()
    
    def clearChildren(self):
        for child in self.childElements:
            child.pack_forget()
        
    def pack(self, cnf={}, **kw):
        self.clearChildren()
        dataLine.pack(self, cnf=cnf, **kw)
        if self.expanded:
            for child in self.childElements:
                child.update()
                child.pack(cnf=cnf,**kw)
        
    def packChildren(self):
        self.toggle_button.pack(side=LEFT,fill=BOTH,expand=TRUE)
        
    def toggleCollapse(self):
        self.expanded = not self.expanded
        self.update()
        self.root.loadDataList()

class NewSubactionLine(dataLine):
    def __init__(self,_root,_parent):
        dataLine.__init__(self, _root, _parent, 'Add Subaction...')
        
        self.button = Button(self,text='Add Subaction...',bg="aquamarine",command=self.addSubaction)
        self.config(bg="aquamarine")
        self.label.config(bg="aquamarine")
            
    def update(self):
        self.packChildren()
        
    def packChildren(self):
        self.button.pack(side=LEFT,fill=BOTH,expand=TRUE)
        
    def addSubaction(self,*args):
        #self.root.addAction()
        pass

class XYDataLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_xvarname,_yvarname,_xrelvarname=None,_yrelvarname=None):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        
        self.x_var_name = _xvarname
        self.y_var_name = _yvarname
        self.x_rel_var_name = _xrelvarname
        self.y_rel_var_name = _yrelvarname
        
        self.enable_label = Label(self,text='Edit',bg=self.bg.get())
        self.relative_label = Label(self,text='Relative?',bg=self.bg.get())
        
        self.x_enabled_data = IntVar()
        self.x_enabled_button = Checkbutton(self,variable=self.x_enabled_data,anchor="w",bg=self.bg.get())
        
        self.x_label = Label(self,text='X: ',bg=self.bg.get())
        self.x_data = StringVar()
        self.x_entry = Entry(self,textvariable=self.x_data,validate='key',validatecommand=self.validateInt)
        
        if self.x_rel_var_name:
            self.x_relative_data = IntVar()
            self.x_relative_button = Checkbutton(self,variable=self.x_relative_data,anchor="w",bg=self.bg.get())
        
        self.y_enabled_data = IntVar()
        self.y_enabled_button = Checkbutton(self,variable=self.y_enabled_data,anchor="w",bg=self.bg.get())
        
        self.y_label = Label(self,text='Y: ',bg=self.bg.get())
        self.y_data = StringVar()
        self.y_entry = Entry(self,textvariable=self.y_data,validate='key',validatecommand=self.validateInt)
        
        if self.y_rel_var_name:
            self.y_relative_data = IntVar()
            self.y_relative_button = Checkbutton(self,variable=self.x_relative_data,anchor="w",bg=self.bg.get())
        
        x_value = getattr(self.target_object, self.x_var_name)
        y_value = getattr(self.target_object, self.y_var_name)
        
        self.x_data.set(x_value)
        self.y_data.set(y_value)
        
        self.x_data.trace('w', self.changeVariable)
        self.y_data.trace('w', self.changeVariable)
        if self.x_rel_var_name:
            self.x_relative_data.trace('w',self.changeVariable)
        if self.y_rel_var_name:
            self.y_relative_data.trace('w',self.changeVariable)
        
        self.x_enabled_data.trace('w', self.changeEnabled)
        self.y_enabled_data.trace('w', self.changeEnabled)
        
        if x_value is not None:
            self.x_enabled_data.set(1)
        if y_value is not None:
            self.y_enabled_data.set(1)
            
    def changeVariable(self, *args):
        if hasattr(self.target_object, self.x_var_name):
            if bool(self.x_enabled_data.get()): #if it's disabled, set it to None
                x = float(self.x_data.get()) if not self.x_data.get() == '' else 0
                setattr(self.target_object, self.x_var_name, x)
            else:
                setattr(self.target_object, self.x_var_name, None)
                
        if hasattr(self.target_object, self.y_var_name):
            if bool(self.y_enabled_data.get()):
                y = float(self.y_data.get()) if not self.y_data.get() == '' else 0
                setattr(self.target_object, self.y_var_name, y)
            else:
                setattr(self.target_object, self.y_var_name, None)
                
        if self.x_rel_var_name and hasattr(self.target_object, self.x_rel_var_name):
            setattr(self.target_object, self.x_rel_var_name, self.x_relative_data.get())
        if self.y_rel_var_name and hasattr(self.target_object, self.y_rel_var_name):
            setattr(self.target_object, self.y_rel_var_name, self.x_relative_data.get())
        
    def packChildren(self):
        self.label.grid(row=0,column=0,columnspan=2)
        self.enable_label.grid(row=0,column=2)
        if self.x_rel_var_name or self.y_rel_var_name:
            self.relative_label.grid(row=0,column=3)
        #x row
        self.x_label.grid(row=1,column=0)
        self.x_entry.grid(row=1,column=1)
        self.x_enabled_button.grid(row=1,column=2)
        if self.x_rel_var_name:
            self.x_relative_button.grid(row=1,column=3)
        
        #y row
        self.y_label.grid(row=2,column=0)
        self.y_entry.grid(row=2,column=1)
        self.y_enabled_button.grid(row=2,column=2)
        if self.y_rel_var_name:
            self.y_relative_button.grid(row=2,column=3)
    
    def update(self):
        self.changeEnabled()
        self.packChildren()
        
    def changeEnabled(self,*args):
        if bool(self.x_enabled_data.get()):
            self.x_entry.config(state=NORMAL)
            if self.x_rel_var_name:
                self.x_relative_button.config(state=NORMAL)
        else:
            self.x_entry.config(state=DISABLED)
            self.x_data.set(0)
            if self.x_rel_var_name:
                self.x_relative_button.config(state=DISABLED)
        
        if bool(self.y_enabled_data.get()):
            self.y_entry.config(state=NORMAL)
            if self.y_rel_var_name:
                self.y_relative_button.config(state=NORMAL)
        else:
            self.y_entry.config(state=DISABLED)
            self.y_data.set(0)
            if self.y_rel_var_name:
                self.y_relative_button.config(state=DISABLED)
                
        self.changeVariable()
        
class ActionSelectorLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.act_list = []
        
        if self.root.getFighter():
            fighter = self.root.getFighter()
            if isinstance(fighter.actions, engine.actionLoader.ActionLoader):
                self.act_list.extend(fighter.actions.getAllActions())
            else:
                for name,_ in inspect.getmembers(fighter.actions, inspect.isclass):
                    self.act_list.append(name)
        
        self.action_data = StringVar()
        self.action_entry = OptionMenu(self,self.action_data,*self.act_list)
        
        self.action_data.trace('w', self.changeVariable)
       
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.action_data.get())
        dataLine.changeVariable(self)
        
    def packChildren(self):
        dataLine.packChildren(self)
        self.action_entry.pack(side=LEFT,fill=BOTH)
    
    def update(self):
        if self.root.getFighter():
            fighter = self.root.getFighter()
            if isinstance(fighter.actions, engine.actionLoader.ActionLoader):
                self.act_list.extend(fighter.actions.getAllActions())
            else:
                for name,_ in inspect.getmembers(fighter.actions, inspect.isclass):
                    self.act_list.append(name)
        if self.target_object:            
            self.action_data.set(getattr(self.target_object, self.var_name))
        
        self.packChildren()
        
class TransitionLine(dataLine):
    def __init__(self,_root,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _root, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.tran_list = engine.baseActions.state_dict.keys()
        
        self.tran_data = StringVar()
        self.tran_entry = OptionMenu(self,self.tran_data,*self.tran_list)
        
        self.tran_data.trace('w', self.changeVariable)
       
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.tran_data.get())
        dataLine.changeVariable(self)
        
    def packChildren(self):
        dataLine.packChildren(self)
        self.tran_entry.pack(side=LEFT,fill=BOTH)
    
    def update(self):
        if self.target_object:            
            self.tran_data.set(getattr(self.target_object, self.var_name))
        self.packChildren()