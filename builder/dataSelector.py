from Tkinter import *
import settingsManager
                
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
        
        Frame.__init__(self, _parent, bg="white",anchor=W)
        self.root = _parent
        
        self.label = Label(self,textvariable=self.display_name)
        
        self.label.pack(side=LEFT)
        self.visible = True
        
    def pack(self, cnf={}, **kw):
        if self.visible: Label.pack(self, cnf=cnf, **kw)
        
    def setButtons(self,_buttons):
        for button in _buttons:
            button.pack(side=RIGHT)
        
    def updateName(self,_string):
        if _string: self.display_name.set(_string)
        
class dataSelector(dataLine):
    """
    Data Selector is a dataLine that can be selected. These will usually open up a config window.
    """
    def __init__(self,_parent,_name=''):
        dataLine.__init__(self, _parent, _name)
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