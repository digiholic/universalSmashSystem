from Tkinter import *
import settingsManager
from idlelib.ObjectBrowser import _object_browser
from tkFileDialog import askopenfile,askdirectory
import os

class dataLine(Frame):
    """
    A DataLine is an object that can be displayed in the right panel.
    This is the base class for those lines. It itself just displays text,
    with no functionality.
    """
    def __init__(self,_parent,_name=''):
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
        self.root = _parent
        
        self.label = Label(self,textvariable=self.display_name)
        
        self.bg.set("gainsboro") #it's a real color. Who knew?
        self.visible = True
        
    def changebg(self,*args):
        self.config(bg=self.bg.get())
        self.label.config(bg=self.bg.get())
        
    def packChildren(self):
        self.label.pack(side=LEFT)
        
    def pack(self, cnf={}, **kw):
        if self.visible: Frame.pack(self, cnf=cnf, **kw)
        
    def setButtons(self,_buttons):
        for button in _buttons:
            button.pack(side=RIGHT)
        
    def updateName(self,_string):
        if _string: self.display_name.set(_string)
    
class StringLine(dataLine):
    def __init__(self,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.string_data = StringVar()
        self.string_entry = Entry(self,textvariable=self.string_data)
        
        self.update()
        
        self.string_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.string_data.get())
            print(getattr(self.target_object,self.var_name))
    
    def packChildren(self):
        dataLine.packChildren(self)
        self.string_entry.pack(side=LEFT,fill=BOTH)
    
    def update(self):
        print('Updating string panel')
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.string_data.set(getattr(self.target_object, self.var_name))
            self.string_entry.config(state=NORMAL)
        else:
            self.string_entry.config(state=DISABLED)
        
        self.packChildren()
        
class ImageLine(dataLine):
    def __init__(self,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.image_data = StringVar()
        self.image_entry = Entry(self,textvariable=self.image_data)
        self.image_button = Button(self,text='...',command=self.loadImage)
        self.image_entry.config(state=DISABLED)
        
        self.update()
        
        self.image_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.image_data.get())
    
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
    def __init__(self,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.dir_data = StringVar()
        self.dir_entry = Entry(self,textvariable=self.dir_data)
        self.dir_button = Button(self,text='...',command=self.loadDir)
        self.dir_entry.config(state=DISABLED)
        
        self.update()
        
        self.dir_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.dir_data.get())
    
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
    def __init__(self,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.module_data = StringVar()
        self.module_entry = Entry(self,textvariable=self.module_data)
        self.module_button = Button(self,text='...',command=self.loadImage)
        self.module_entry.config(state=DISABLED)
        
        self.update()
        
        self.module_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.module_data.get())
    
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
    def __init__(self,_parent,_name,_target_object,_varname):
        dataLine.__init__(self, _parent, _name)
        
        self.target_object = _target_object
        self.var_name = _varname
        
        self.num_data = StringVar()
        vcmd = (_parent.register(self.validate),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.num_entry = Entry(self,textvariable=self.num_data,validate='key',validatecommand=vcmd)
        
        self.update()
        
        self.num_data.trace('w', self.changeVariable)
        
    def changeVariable(self,*args):
        if self.target_object:
            setattr(self.target_object,self.var_name,self.num_data.get())
            print(getattr(self.target_object,self.var_name))
    
    def packChildren(self):
        dataLine.packChildren(self)
        self.num_entry.pack(side=LEFT,fill=BOTH)
    
    def update(self):
        print('Updating string panel')
        # If the object exists and has the attribute, set the variable
        if self.target_object and hasattr(self.target_object, self.var_name):
            self.num_data.set(getattr(self.target_object, self.var_name))
            self.num_entry.config(state=NORMAL)
        else:
            self.num_entry.config(state=DISABLED)
        
        self.packChildren()

    def validate(self, action, index, value_if_allowed,
        prior_value, text, validation_type, trigger_type, widget_name):
        # action=1 -> insert
        if(action=='1'):
            if text in '0123456789.-+':
                try:
                    float(value_if_allowed)
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
    def __init__(self,_parent,_name=''):
        dataLine.__init__(self, _parent, _name)
        self.bind("<Button-1>", self.onClick)
        self.bg.set("white")
        
    def onClick(self,*_args):
        if self.selected:
            self.unselect()
        else:
            self.select()
        if not self.root.selected:
            self.root.selected_string.set('')
    
    def select(self):
        self.selected = True
        self.bg.set('lightblue')
        if self.root.selected:
            self.root.selected.unselect()
        self.root.selected = self
        if self.data:
            self.root.selected_string.set(str(self.data))
    
    def unselect(self):
        self.selected = False
        self.config(bg="white")
        self.root.selected = None

class SubactionSelector(dataSelector):
    """
    The Data Selector for subactions.
    """
    def __init__(self,_root,_subaction):
        dataSelector.__init__(self, _root,_subaction.getDisplayName())
        
        self.subaction = _subaction
        
        self.delete_image = PhotoImage(file=settingsManager.createPath('sprites/icons/red-x.gif'))
        self.confirm_button = PhotoImage(file=settingsManager.createPath('sprites/icons/green-check.gif'))
        self.delete_button = Button(self,image=self.delete_image,command=self.deleteSubaction)
        
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
        dataSelector.updateName(self, _string)
        self.display_name.set(self.data.getDisplayName())

class PropertySelector(dataSelector):
    """
    The data selector for properties, such as fighter stats
    """
    def __init__(self, _root, _owner, _fieldname, _displayName, _vartype):
        dataSelector.__init__(self, _root)

        self.owner = _owner
        self.fieldname = _fieldname
        self.display_name = _displayName
        self.vartype = _vartype
        
        self.updateName()
        
    def updateName(self, _string=None):
        fielddata = ''
        if hasattr(self.owner, self.fieldname): fielddata = getattr(self.owner, self.fieldname)
        self.display_name.set(self.display_name+': '+ str(fielddata))

class GroupSelector(dataLine):
    """
    A group selector has an expand/collapse button to view or hide its children.
    """
    def __init__(self,_parent,_name):
        dataLine.__init__(self, _parent, _name)
        
        self.expanded = True
        self.collapsed_image = PhotoImage(file=settingsManager.createPath('sprites/icons/right.png'))
        self.expanded_image  = PhotoImage(file=settingsManager.createPath('sprites/icons/down.png'))
        self.toggle_button   = Button(self,image=self.expanded_image,command=self.toggleCollapse())
        
        self.toggle_button.pack(side=RIGHT)
        
        self.children = []
        
    def toggleCollapse(self):
        self.expanded = not self.expanded
        
        if self.expanded: #If we're expanded
            self.toggle_button.config(image=self.expanded_image)
            for child in self.children:
                child.visible = True
        else: #If we're collapsed
            self.toggle_button.config(image=self.collapsed_image)
            for child in self.children:
                child.visible = False
        """ TODO Redraw the parent panel """
        
class NewSubactionLine(dataSelector):
    """
    Prompts the user with a subaction config panel when clicked. Adds to the proper group.
    """
    pass