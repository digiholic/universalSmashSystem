import os
import pygame
import sys
from builder.dataSelector import dataLine
sys.path.insert(0, '../')
import settingsManager
import inspect
import engine.abstractFighter
import subactionSelector
import engine.subaction
import xml.etree.ElementTree as ElementTree
from Tkinter import *
from tkFileDialog import askopenfile
from tkMessageBox import showinfo
from shutil import copyfile
import stages.training_stage.stage
import ttk
import builder.dataSelector as dataSelector
from engine.abstractFighter import AbstractFighter

"""
These are the global variables that multiple panels will need.
They are updated by the root window, and have an accompanied variable that the panels
can trace on, to keep updated whenever they change.
"""
fighter = None
action = None
frame = 0

"""
This dict will hold any changed actions, in the form of name -> Action
Whenever an action is loaded, if it is in the dict, it will load that action instead.
"""
changed_actions = dict()

"""
The BuilderPanel is the base class for the panels. It sets the root and parent,
as well as the traces for the root variables. The change functions do nothing unless overridden.
"""
class BuilderPanel(Frame):
    def __init__(self,_parent,_root):
        Frame.__init__(self, _parent)
        self.parent = _parent
        self.root = _root
        
        self.root.fighter_string.trace('w',self.changeFighter)
        self.root.action_string.trace('w',self.changeAction)
        self.root.frame.trace('w',self.changeFrame)
        
    def changeFighter(self,*_args):
        pass
    
    def getFighter(self):
        global fighter
        return fighter
    
    def changeAction(self,*_args):
        pass
    
    def getAction(self):
        global action
        return action
    
    def changeFrame(self,*_args):
        pass
    
    def getFrame(self):
        global frame
        return frame
    
    def getChangedActions(self):
        global changed_actions
        return changed_actions
"""
The main window, that all the other panels are child objects of.
"""
class MainFrame(Tk):
    def __init__(self):
        Tk.__init__(self)
        # Window Properties
        self.width = 640
        self.height = 480
        self.wm_title('Legacy Editor')
        #program_directory=sys.path[0]
        #self.iconphoto(True, PhotoImage(file=settingsManager.createPath('editor-0.png')))
        #self.iconbitmap(settingsManager.createPath('editor.ico'))
        if "nt" == os.name:
            self.iconbitmap(settingsManager.createPath('sprites/editor.ico'))
        else:
            self.iconbitmap('@'+settingsManager.createPath('sprites/editor.xbm'))
        self.geometry('640x480')
        
        # Variable Declaration
        self.fighter_file = None #The python or XML fighter file
        self.fighter_properties = None #The contents of fighter_file
        self.fighter_string = StringVar(self)
        self.action_string = StringVar(self)
        self.frame = IntVar(self)

        # Create and place subpanels
        self.config(menu=MenuBar(self))
        self.viewer_pane = LeftPane(self,self)
        self.action_pane = EditorPane(self)
        self.viewer_pane.grid(row=0,column=0,sticky=N+S+E+W)
        self.action_pane.grid(row=0,column=1,sticky=N+S+E+W)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=5, uniform="column")
        self.grid_columnconfigure(1, weight=4, uniform="column")
        
        self.fighter_string.trace('w',self.changeFighter)
        self.action_string.trace('w',self.changeAction)
        self.frame.trace('w',self.changeFrame)
        
        self.mainloop()
    
    def actionModified(self):
        global action
        global changed_actions
        
        if not changed_actions: #if the actions are empty
            self.wm_title(self.wm_title()+'*')
        
        if action:
            changed_actions[self.action_string.get()] = action
        
        #update the views
        """
        self.action_pane.action_selector_panel.refreshDropdowns()
        self.viewer_pane.navigator_panel.changeFrameNumber(0)
        """
        
        self.viewer_pane.viewer_panel.reloadFrame()
        
        for subact in self.action_pane.subaction_panel.subaction_list:
            subact.updateName()
            print(subact.display_name.get())
            
    def getFighterAction(self,_actionName,_getRawXml=False):
        global fighter
        if _getRawXml:return fighter.actions.actions_xml.find(_actionName)
        else: return fighter.getAction(_actionName)
    
    def addAction(self,_action):
        global fighter
        
        changed_actions[_action.name] = _action
        fighter.actions.modifyAction(_action.name, _action)
        self.action_pane.data_panel.panel_windows['Actions'].changeFighter()
        self.action_pane.data_panel.panel_windows['Actions'].scroll_frame.canvas.yview_moveto(1.0)
        #self.action_pane.action_selector_panel.refreshDropdowns()
    
    def deleteAction(self,_action):
        global fighter
        
        changed_actions[_action.name] = None
        fighter.actions.modifyAction(_action.name, None)
        self.action_pane.data_panel.panel_windows['Actions'].changeFighter()
        
    def changeFighter(self,*_args):
        global fighter
        dirname, _ = os.path.split(self.fighter_file.name)
        if self.fighter_file.name.endswith('.py'):
            fighter_module = settingsManager.importFromURI(self.fighter_file, self.fighter_file.name, True)
            if hasattr(fighter_module, 'Fighter'):
                new_fighter = fighter_module.Fighter(dirname,0)
                showinfo('Advanced mode warning','Legacy Editor cannot edit Advanced Mode (.py) fighter files. The fighter will be opened in read-only mode. Depending on the fighter, there may be inconsistencies with behavior in-game compared to what you view here.')
            else:
                showinfo('Error loading fighter','File does not contain a fighter. Are you sure you are loading the right Python file?')
                return
        else:
            new_fighter = engine.abstractFighter.AbstractFighter(dirname,0)
        
        new_fighter.loadSpriteLibrary(0)
        new_fighter.current_action = new_fighter.getAction('NeutralAction')
        new_fighter.init_boxes()
        #stage = stages.training_stage.stage.getStage()
        #new_fighter.game_state = stage
        #new_fighter.initialize()
        #stage.follows.append(new_fighter.ecb.tracking_rect)
        #stage.initializeCamera()
        new_fighter.doAction('NeutralAction')
        fighter = new_fighter
        self.wm_title('Legacy Editor - '+fighter.name)        
    
    def changeAction(self,*_args):
        global action
        global changed_actions
        global fighter
        if fighter:
            if changed_actions.has_key(self.action_string.get()):
                action = changed_actions[self.action_string.get()]
            else: action = fighter.getAction(self.action_string.get())
                
    def changeFrame(self,*_args):
        global frame
        frame = self.frame.get()
    
class MenuBar(Menu):
    def __init__(self,_root):
        Menu.__init__(self, _root)
        self.root = _root
        self.file_menu = Menu(self,tearoff=False)
        self.action_menu = Menu(self,tearoff=False)
        self.add_cascade(label="File", menu=self.file_menu)
        self.add_cascade(label="Action", menu=self.action_menu, state=DISABLED)
        
        self.file_menu.add_command(label="New Fighter", command=self.newFighter)
        self.file_menu.add_command(label="Load Fighter", command=self.loadFighter)
        self.file_menu.add_command(label="Save Fighter", command=self.saveFighter)
        self.file_menu.add_separator()
        #self.file_menu.add_command(label="Exit", command=self.root.destroy)
        
        self.action_menu.add_command(label="Add Action", command=self.addAction)
        self.action_menu.add_command(label="Save Action", command=self.saveAction, state=DISABLED)
        self.action_menu.add_command(label="Delete Action", command=self.deleteAction, state=DISABLED)
        self.action_menu.add_separator()
        self.action_menu.add_command(label="Add Conditional", command=self.addConditional, state=DISABLED)
        
        self.root.fighter_string.trace('w',self.changeFighter)
        self.root.action_string.trace('w',self.changeAction)
        self.root.frame.trace('w',self.changeFrame)
        
    def newFighter(self):
        CreateFighterWindow(self)
    
    def loadFighter(self):
        fighter_file = askopenfile(mode="r",initialdir=settingsManager.createPath('fighters'),filetypes=[('TUSSLE Fighters','*.xml'),('Advanced Fighters', '*.py')])
        self.root.fighter_file = fighter_file
        self.root.fighter_properties = fighter_file.read()
        self.root.fighter_string.set(fighter_file.name)
        self.entryconfig("Action", state=NORMAL)
        
    def saveFighter(self):
        global fighter
        global action
        global changed_actions
        
        for actName, new_action in changed_actions.iteritems():
            if hasattr(fighter.actions, 'modifyAction'):
                fighter.actions.modifyAction(actName, new_action) 
        if hasattr(fighter.actions,'saveActions'):
            fighter.actions.saveActions()
        
        fighter.saveFighter()
        
    def addAction(self):
        CreateActionWindow(self.root)
    
    def addConditional(self):
        AddConditionalWindow(self.root)
    
    def saveAction(self):
        pass
    
    def deleteAction(self):
        pass
    
    def changeFighter(self,*_args):
        pass
    
    def changeAction(self,*_args):
        global action
        if action:
            self.action_menu.entryconfig("Save Action", state=NORMAL)
            self.action_menu.entryconfig("Delete Action", state=NORMAL)
            self.action_menu.entryconfig("Add Conditional", state=NORMAL)
    
    def changeFrame(self,*_args):
        pass

class CreateActionWindow(Toplevel):
    def __init__(self,_root):
        Toplevel.__init__(self)
        self.title("Create a new Action")
        self.root = _root
        name_label = Label(self,text="Action Name: ")
        self.name = Entry(self)
        button = Button(self, text="Confirm", command=self.submit)
        
        sep = ttk.Separator(self,orient=HORIZONTAL)
        sep_text = Label(self,text="Or choose a Basic Action to implement:")
        
        basic_list = []
                    
        for name, obj in inspect.getmembers(sys.modules[engine.baseActions.__name__]):
            if inspect.isclass(obj):
                if not name in self.root.action_pane.data_panel.panel_windows['Actions'].act_list:
                    #print(basic_list)
                    basic_list.append(name)
                    
        self.basic_choice = StringVar(self)
        basic_box = OptionMenu(self,self.basic_choice,*basic_list)
        basic_button = Button(self,text="Confirm",command=self.submitBasic)
        
        name_label.grid(row=0,column=0)
        self.name.grid(row=0,column=1)
        button.grid(row=0,column=2)
        sep.grid(row=1,columnspan=3,sticky=E+W)
        sep_text.grid(row=1,columnspan=3)
        basic_box.grid(row=2,columnspan=2,sticky=E+W)
        basic_button.grid(row=2,column=2)
        
    def submit(self,*_args):
        global fighter
        global changed_actions
        
        name = self.name.get()
        print(name)
        if name:
            if not fighter.actions.hasAction(name): #if it doesn't already exist
                if not changed_actions.has_key(name): #and we didn't already make one
                    act = engine.action.Action()
                    act.name = name
                    self.root.addAction(act)
                    self.destroy()
    
    def submitBasic(self,*_args):
        global fighter
        global changed_actions
        
        name = self.basic_choice.get()
        if name:
            if not fighter.actions.hasAction(name): #if it doesn't already exist
                if not changed_actions.has_key(name): #and we didn't already make one
                    print('create action: ' + name)
                    if hasattr(engine.baseActions, name):
                        act = getattr(engine.baseActions, name)()
                        act.name = name
                        self.root.addAction(act)
                        self.destroy()
                
class AddConditionalWindow(Toplevel):
    def __init__(self,_root):
        Toplevel.__init__(self)
        self.title("Create a new Conditional Group")
        self.root = _root
        name_label = Label(self,text="Conditional Name: ")
        self.name = Entry(self)
        name_label.grid(row=0,column=0)
        self.name.grid(row=0,column=1)
        
        button = Button(self, text="Confirm", command=self.submit)
        button.grid(row=1,columnspan=2)
        
    def submit(self,*_args):
        global fighter
        global action
        
        name = self.name.get()
        if name and not action.conditional_actions.has_key(name):
            action.conditional_actions[name] = []
            self.root.actionModified()
            self.destroy()
 
class CreateFighterWindow(Toplevel):
    def __init__(self,_parent):
        Toplevel.__init__(self)
        self.parent = _parent
        self.root = _parent.root
        
        # Labels
        folder_name_label = Label(self,text='Folder Name')
        confirm_button = Button(self,text='Confirm',command=self.submit)
        
        # Variables
        self.folder_name_var = StringVar(self)
        self.generate_action_xml_var = BooleanVar(self)
        self.generate_action_py_var = BooleanVar(self)
        
        # Setters
        folder_name_entry = Entry(self,textvariable = self.folder_name_var)
        generate_action_xml_entry = Checkbutton(self,variable=self.generate_action_xml_var,text="Generate Actions XML File")
        generate_action_py_entry = Checkbutton(self,variable=self.generate_action_py_var,text="Generate Actions PY File")
        
        # Placement
        folder_name_label.grid(row=0,column=0,sticky=E)
        folder_name_entry.grid(row=0,column=1,sticky=E+W)
        generate_action_xml_entry.grid(row=1,column=0)
        generate_action_py_entry.grid(row=1,column=1)
        confirm_button.grid(row=2,columnspan=2)
        
        """
        TODO: Allow this to be made with icons and stuff chosen ahead of time.
        Use file pickers to choose locations and copy them over.
        """
        
    def submit(self):
        path = settingsManager.createPath('fighters/'+self.folder_name_var.get())
            
        if os.path.exists(path):
            print('path exists')
            self.destroy()
        else:
            os.makedirs(path)
            new_fighter = engine.abstractFighter.AbstractFighter(path,0)
            #create sprite dir
            sprite_path = os.path.join(path,'sprites')
            os.makedirs(sprite_path)
            copyfile(settingsManager.createPath('sprites/sandbag_idle.png'), os.path.join(sprite_path,'sandbag_idle.png'))
            copyfile(settingsManager.createPath('sprites/default_franchise_icon.png'), os.path.join(sprite_path,'franchise_icon.png'))
            copyfile(settingsManager.createPath('sprites/icon_unknown.png'), os.path.join(sprite_path,'icon_unknown.png'))
            
            #create __init__.py
            init_py = open(os.path.join(path,'__init__.py'),'w+')
            init_py.close()
            
            #check for and create actions files
            if self.generate_action_xml_var.get():
                action_xml = open(os.path.join(path,self.folder_name_var.get()+'_actions.xml'),'w+')
                action_xml.write('<actionList />')
                new_fighter.action_file = self.folder_name_var.get()+'_actions.xml'
                action_xml.close()
            if self.generate_action_py_var.get():
                action_py = open(os.path.join(path,self.folder_name_var.get()+'_actions.py'),'w+')
                new_fighter.action_file = self.folder_name_var.get()+'_actions.py'
                action_py.close()
                
            #copy over icons?
            new_fighter.saveFighter()
            self.destroy()
            
        fighter_file = open(os.path.join(path,'fighter.xml'),'r')
        self.root.fighter_file = fighter_file
        self.root.fighter_properties = fighter_file.read()
        self.root.fighter_string.set(fighter_file.name)
        self.parent.entryconfig("Action", state=NORMAL)
            
            
class LeftPane(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.viewer_panel = ViewerPanel(self,_root)
        self.navigator_panel = NavigatorPanel(self,_root)
        
        self.viewer_panel.pack(fill=BOTH,expand=TRUE)
        self.navigator_panel.pack(fill=X)
        
#I'm modifying this one soon
class ViewerPanel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.config(bg="pink")
        #Create Pygame Panel
        os.environ['SDL_WINDOWID'] = str(self.winfo_id())
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        else:
            os.environ['SDL_VIDEODRIVER'] = 'x11'
        
        pygame.display.init()
        pygame.mixer.init()
        _root.update()
        
        print("Before!")
        print (self.winfo_width())
        print (self.winfo_height())
        self.screen = pygame.display.set_mode((self.winfo_width(), self.winfo_height()),pygame.RESIZABLE)
        print("After!")
        self.center = (0,0)
        self.scale = 1.0
        
        self.gameLoop()
        
    def gameLoop(self):
        global fighter
        #TODO figure out that window snap thing that's messing up a lot
        self.screen = pygame.display.set_mode((self.winfo_width(), self.winfo_height()),pygame.RESIZABLE)
        if fighter: self.centerFighter()
        
        self.screen.fill(pygame.Color("pink"))
        if fighter:
            fighter.mask = None #These don't work inside of the builder
            fighter.draw(self.screen, fighter.sprite.rect.topleft, self.scale)
            for hbox in fighter.active_hitboxes:
                hbox.draw(self.screen,hbox.rect.topleft,self.scale)        
            
        pygame.display.flip()
        #self.after(5, self.gameLoop) #Loop every 5ms
        
    def centerFighter(self):
        global fighter
        
        if fighter:
            fighter.posx = self.screen.get_rect().centerx + self.center[0]
            fighter.posy = self.screen.get_rect().centery + self.center[1]
            fighter.updatePosition()
    
    def reloadFrame(self):
        global fighter
        global action
        global frame
        
        if action:
            fighter.changeAction(action)
            action.frame = 0
            while action.frame <= frame:
                action.updateAnimationOnly(fighter)
                
        self.gameLoop()
                
    ####################
    # TRACER FUNCTIONS #
    ####################
    def changeFighter(self,*_args):
        self.centerFighter()
        self.reloadFrame()
        
    def changeFrame(self,*_args):
        self.reloadFrame()
            
    def changeAction(self,*_args):
        global action
        global fighter
        if action: fighter.changeAction(action)
        self.reloadFrame()
        
class NavigatorPanel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.config(bg="white",height=50)
        
        self.frame_changer_panel = Frame(self)
        
        self.button_minus_five = Button(self.frame_changer_panel, text="-5", command=lambda:self.changeFrameNumber(-5),state=DISABLED)
        self.button_minus = Button(self.frame_changer_panel, text="-1", command=lambda:self.changeFrameNumber(-1),state=DISABLED)
        self.current_frame = Label(self.frame_changer_panel,text="0/1",state=DISABLED)
        self.button_plus = Button(self.frame_changer_panel, text="+1", command=lambda:self.changeFrameNumber(1),state=DISABLED)
        self.button_plus_five = Button(self.frame_changer_panel, text="+5", command=lambda:self.changeFrameNumber(5),state=DISABLED)
        
        self.frame_changer_panel.pack()
        
        self.button_minus_five.grid(row=0,column=0)
        self.button_minus.grid(row=0,column=1)
        self.current_frame.grid(row=0,column=2)
        self.button_plus.grid(row=0,column=3)
        self.button_plus_five.grid(row=0,column=4)
        
    def changeFrameNumber(self, _amount):
        global action
        frame = self.root.frame.get()
        if action:
            frame = max(0,frame + _amount)
            frame = min(frame,action.last_frame)
            
            self.current_frame.config(text=str(frame)+"/"+str(action.last_frame))
            
            #Enable buttons
            self.button_minus_five.config(state=NORMAL)
            self.button_minus.config(state=NORMAL)
            self.current_frame.config(state=NORMAL)
            self.button_plus.config(state=NORMAL)
            self.button_plus_five.config(state=NORMAL)
            2
            #Disable ones that shouldn't be clicked anymore
            if frame == 0:
                self.button_minus.config(state=DISABLED)
                self.button_minus_five.config(state=DISABLED)
            if frame == action.last_frame:
                self.button_plus.config(state=DISABLED)
                self.button_plus_five.config(state=DISABLED)
            
            self.root.frame.set(frame)
        else: #If no action, disable everything
            self.button_minus_five.config(state=DISABLED)
            self.button_minus.config(state=DISABLED)
            self.current_frame.config(state=DISABLED)
            self.button_plus.config(state=DISABLED)
            self.button_plus_five.config(state=DISABLED)
    
    def changeAction(self, *_args):
        global action
        if action:
            self.root.frame.set(0)
            self.changeFrameNumber(0)
                
class RightPane(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.action_selector_panel = SelectorPanel(self,_root)
        self.subaction_panel = Subaction_panel(self,_root)
        
        self.subaction_property_panel = PropertiesPanel(self,_root)
        
        self.action_selector_panel.pack(fill=X)
        self.subaction_panel.pack(fill=BOTH,expand=TRUE)
        self.subaction_property_panel.pack(fill=X)
        
class SelectorPanel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.config(bg="purple",height=50)
        
        #Create Action dropdown menu
        self.current_action = StringVar(self)
        self.current_action.set("Fighter Properties")
        self.current_action.trace('w', self.changeActionDropdown)
        self.act_list = ['Fighter Properties']
        self.action = OptionMenu(self,self.current_action,*self.act_list)
        
        #Create Group dropdown menu
        self.current_group = StringVar(self)
        self.current_group.set("SetUp")
        self.default_group_list = ["Properties","Current Frame","Set Up","Tear Down","Transitions","Before Frames","After Frames","Last Frame"] 
        self.group_list = self.default_group_list[:] #have to do this to copy be value instead of reference
        self.group = OptionMenu(self,self.current_group,*self.group_list)
        
    def changeFighter(self, *_args):
        global fighter
        self.act_list = ["Fighter Properties"]
        if isinstance(fighter.actions, engine.actionLoader.ActionLoader):
            self.act_list.extend(fighter.actions.getAllActions())
        else:
            for name,_ in inspect.getmembers(fighter.actions, inspect.isclass):
                self.act_list.append(name)
        self.refreshDropdowns()
        self.current_action.set('Fighter Properties')
    
    def changeActionDropdown(self,*_args):
        global action
        if self.current_action.get() == 'Fighter Properties':
            self.group.pack_forget()
            self.group_list = ["Fighter","Attributes"]
            for i in range(0,8):
                self.group_list.append("Color "+str(i))
            self.refreshDropdowns()
            self.current_group.set('Fighter')
        else:
            self.root.action_string.set(self.current_action.get())
            self.refreshDropdowns()
            self.current_group.set('Properties')
    
    def refreshDropdowns(self):
        global changed_actions
        global action
        
        for changed_action in changed_actions.keys():
            if not changed_action in self.act_list:
                self.act_list.append(changed_action)
        
        if self.current_action.get() == 'Fighter Properties':
            self.group_list = ["Fighter","Attributes"]
            for i in range(0,8):
                self.group_list.append("Color "+str(i))
            self.current_group.set('Fighter')
        else:
            self.group_list = self.default_group_list[:]
            if action and isinstance(action, engine.action.Action):
                for group in action.events.keys():
                    self.group_list.append('Cond: '+ group)
                            
        self.action.destroy()
        self.action = OptionMenu(self,self.current_action,*self.act_list)
        self.action.config(width=18)
        
        self.group.destroy()
        self.group = OptionMenu(self,self.current_group,*self.group_list)
        self.group.config(width=10)
        
        self.action.pack_forget()
        self.group.pack_forget()
        
        self.action.pack(side=LEFT)
        self.group.pack(side=LEFT)      
        
class Subaction_panel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.config(bg="blue")
        
        self.parent.action_selector_panel.current_action.trace('w',self.changeActionDropdown)
        self.parent.action_selector_panel.current_group.trace('w',self.groupChanged)
        
        self.subaction_list = []
        self.current_frame_subacts = []
        
        self.scroll_frame = VerticalScrolledFrame(self,bg="blue")
        self.scroll_frame.config(width=self.winfo_width())
        
        self.text_field = Text(self,wrap=NONE)
        self.x_scroll_bar = Scrollbar(self.text_field, orient=HORIZONTAL, command=self.text_field.xview)
        self.y_scroll_bar = Scrollbar(self.text_field, orient=VERTICAL, command=self.text_field.yview)
        self.text_field.configure(xscrollcommand=self.x_scroll_bar.set, yscrollcommand=self.y_scroll_bar.set)
        
        self.text_field.pack(fill=BOTH,expand=TRUE)
        self.y_scroll_bar.pack(side=RIGHT, fill=Y)
        self.x_scroll_bar.pack(side=BOTTOM, fill=X)
        
        self.selected_string = StringVar(self)
        self.selected = None
    
    """
    When displaying text instead of a modifiable subaction list,
    switch to the textField.
    """
    def showTextField(self):
        self.text_field.pack(fill=BOTH,expand=TRUE)
        self.y_scroll_bar.pack(side=RIGHT, fill=Y)
        self.x_scroll_bar.pack(side=BOTTOM, fill=X)
        self.clearSubActList()
    
    """
    When displaying a modifiable subaction list instead of text,
    switch to the list.
    """
    def showSubactionList(self): 
        #Show subaction selector
        self.text_field.pack_forget()
        self.y_scroll_bar.pack_forget()
        self.x_scroll_bar.pack_forget()
        
        self.scroll_frame.pack(fill=BOTH,expand=TRUE)
        for subact in self.subaction_list:
            subact.pack(fill=X)
    
    def clearSubActList(self):
        self.scroll_frame.pack_forget()
        
        for subact in self.subaction_list:
            subact.destroy()
        self.subaction_list = []
        
    def loadText(self,_text):
        try:
            act = self.xmlToActions(_text)
        except: #It is not XML
            act = _text
        self.text_field.delete("1.0", END)
        self.text_field.insert(INSERT, act)
    
    def xmlToActions(self,_xml,_prefix=''):
        root = ElementTree.fromstring(_xml)
        text = ""
        for child in root:
            text += self.printNode(child)
        return text
    
    def printNode(self,_node,_prefix=''):
        text = _prefix
        text += _node.tag+': '
        text += _node.text.lstrip() if _node.text is not None else ''
        if len(_node.attrib) > 0: #if it has attributes
            text += ' ('
            for name,atr in _node.attrib.iteritems():
                text+=name+': '+str(atr)
                text+=','
            text = text[:-1] #chop off the last comma
            text += ')'
            
        if len(list(_node)) > 0: #if it has children
            text += '\n'
            for child in _node:
                text += self.printNode(child,'  '+_prefix)
        else: text += '\n'
        return text
        
    def changeActionDropdown(self, *_args):
        global fighter
        
        self.unselect()
            
        new_action = self.parent.action_selector_panel.current_action.get()
        if new_action == 'Fighter Properties':
            self.parent.action_selector_panel.current_group.set('Fighter')
        else:
            self.text_field.delete("1.0", END)
            self.text_field.insert(INSERT, str(action))
    
    def refreshSubactionNames(self):
        for subact in self.subaction_list:
            subact.updateName()
            
    def groupChanged(self,*_args):
        global fighter
        global action
            
        self.group = self.parent.action_selector_panel.current_group.get()
        new_action = self.parent.action_selector_panel.current_action.get()
        
        self.unselect()
            
        self.clearSubActList()
        if self.group == "Fighter":
            name_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'name', 'Name', 'string')
            icon_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'franchise_icon_path', 'Icon', 'image')
            css_icon_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'css_icon_path', 'CSS Icon', 'image')
            scale_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter.sprite, 'scale', 'Scale', 'float')
            sprite_directory_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'sprite_directory', 'Sprite Directory', 'dir')
            sprite_prefix_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'sprite_prefix', 'Sprite Prefix', 'string')
            sprite_width_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'sprite_width', 'Sprite Width', 'int')
            default_sprite_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'default_sprite', 'Default Sprite', 'string')
            article_path_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'article_path', 'Article Path', 'dir')
            actions_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'action_file', 'Actions File', 'module')
            
            self.subaction_list.append(name_panel)
            self.subaction_list.append(icon_panel)
            self.subaction_list.append(css_icon_panel)
            self.subaction_list.append(scale_panel)
            self.subaction_list.append(sprite_directory_panel)
            self.subaction_list.append(sprite_prefix_panel)
            self.subaction_list.append(sprite_width_panel)
            self.subaction_list.append(default_sprite_panel)
            self.subaction_list.append(article_path_panel)
            self.subaction_list.append(actions_panel)
            
            self.showSubactionList()
        elif self.group == 'Attributes':
            for tag,val in fighter.var.iteritems():
                panel = subactionSelector.SubactionSelector(self.scroll_frame,[(tag,type(val).__name__,fighter.var,tag)],tag+': '+str(val))
                self.subaction_list.append(panel)
            
            self.showSubactionList()
        elif isinstance(action,engine.action.Action):
            subact_group = []
            if self.group == 'Set Up':
                subact_group = action.set_up_actions
            elif self.group == 'Tear Down':
                subact_group = action.tear_down_actions
            elif self.group == 'Transitions':
                subact_group = action.state_transition_actions
            elif self.group == 'Before Frames':
                subact_group = action.actions_before_frame
            elif self.group == 'After Frames':
                subact_group = action.actions_after_frame
            elif self.group == 'Last Frame':
                subact_group = action.actions_at_last_frame
            elif self.group == 'Current Frame':
                subact_group = self.current_frame_subacts
            elif self.group.startswith('Cond:'):
                subact_group = action.conditional_actions[self.group[6:]]
            
            for subact in subact_group:
                selector = subactionSelector.SubactionSelector(self.scroll_frame,subact)
                selector.subaction = subact
                selector.updateName()
                self.subaction_list.append(selector)
            
            
            self.showSubactionList()
            if self.group == 'Properties':
                pass
                """
                length_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Length','int',action,'last_frame')],'Length: '+str(action.last_frame))
                sprite_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Sprite','sprite',action,'sprite_name')],'Sprite Name: '+str(action.sprite_name))
                sprite_rate_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Sprite Rate','int',action,'sprite_rate')],'Sprite Rate: '+str(action.sprite_rate))
                loop_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Loop','bool',action,'loop')],'Loop:'+str(action.loop))
                
                self.subaction_list.append(length_panel)
                self.subaction_list.append(sprite_panel)
                self.subaction_list.append(sprite_rate_panel)
                self.subaction_list.append(loop_panel)
                
                self.showSubactionList()
                #node = self.root.getFighterAction(new_action,True)
                #self.loadText(ElementTree.tostring(node))
                #self.showTextField()
                """
                
        else:
            self.loadText('Advanced action from '+str(fighter.actions))
    
    def addSubactionPanel(self,_subact):
        selector = subactionSelector.SubactionSelector(self.scroll_frame,_subact)
        selector.updateName()
        self.subaction_list.append(selector)
        selector.pack(fill=X)
        
    def changeFrame(self, *_args):
        global frame
        
        self.unselect()
        
        self.current_frame_subacts = []
        for subact in action.actions_at_frame[frame]:
            self.current_frame_subacts.append(subact)
        if self.parent.action_selector_panel.current_group.get() == 'Current Frame':
            self.clearSubActList()
            for subact in self.current_frame_subacts:
                selector = subactionSelector.SubactionSelector(self.scroll_frame,subact)
                selector.subaction = subact
                selector.updateName()
                self.subaction_list.append(selector)
            self.showSubactionList()
            
    
    def unselect(self):
        if self.selected:
            self.selected.unselect()
            self.selected_string.set('')
                
class PropertiesPanel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.config(bg="red",height=200)
        self.selected = None
        self.parent.subaction_panel.selected_string.trace('w',self.onSelect)
        
        self.new_subaction_frame = ttk.Notebook(self)
        
        self.control_window = ttk.Frame(self.new_subaction_frame)
        self.sprite_window = ttk.Frame(self.new_subaction_frame)
        self.behavior_window = ttk.Frame(self.new_subaction_frame)
        self.hitbox_window = ttk.Frame(self.new_subaction_frame)
        self.article_window = ttk.Frame(self.new_subaction_frame)
        
        subact_windows = {'Control': self.control_window,
                         'Sprite': self.sprite_window,
                         'Behavior': self.behavior_window,
                         'Hitbox': self.hitbox_window,
                         'Article': self.article_window
                         }
        
        for name,window in subact_windows.iteritems():
            self.new_subaction_frame.add(window,text=name)
            
        subaction_lists = {'Control':[],
                          'Sprite':[],
                          'Behavior':[],
                          'Hitbox':[],
                          'Article':[]}
        
        for name,subact in engine.subaction.subaction_dict.iteritems():
            if subact.subact_group in subact_windows.keys():
                short_name = (name[:19] + '..') if len(name) > 22 else name
                button = Button(subact_windows[subact.subact_group],text=short_name,command=lambda subaction=subact: self.addSubaction(subaction))
                subaction_lists[subact.subact_group].append(button)
                
        for group in subaction_lists.values():
            x = 0
            y = 0
            for button in group:
                button.grid(row=y,column=x,sticky=E+W)
                x += 1
                if x > 1:
                    y += 1
                    x = 0
        
        self.sub_frame = self.new_subaction_frame
        self.sub_frame.pack(fill=BOTH)
        
    def addSubaction(self,_subaction):
        global action
        global frame
        
        group_to_action = {'Current Frame': action.actions_at_frame[frame],
                         'Set Up': action.set_up_actions,
                         'Tear Down': action.tear_down_actions,
                         'Transitions': action.state_transition_actions,
                         'Before Frames': action.actions_before_frame,
                         'After Frames': action.actions_after_frame,
                         'Last Frame': action.actions_at_last_frame}
        group = self.parent.action_selector_panel.current_group.get()
        if group_to_action.has_key(group) or group.startswith('Cond:'):
            subact = _subaction()
            if group.startswith('Cond:'):
                action.conditional_actions[group[6:]].append(subact)
            else: group_to_action[group].append(subact)
            self.root.actionModified()
            #self.parent.subaction_panel.addSubactionPanel(subact)
                    
    def onSelect(self,*_args):
        self.selected = self.parent.subaction_panel.selected
        self.sub_frame.pack_forget()
        
        if self.selected:
            if self.selected.property_frame:
                self.sub_frame = self.selected.property_frame
                self.sub_frame.pack(fill=BOTH)
        else:
            self.sub_frame = self.new_subaction_frame
            self.sub_frame.pack(fill=BOTH)
            
"""
Scrolling frame, since TKinter doesn't do this for some reason.
Source: http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
"""
class VerticalScrolledFrame(Frame):
    def __init__(self, _parent, *_args, **_kw):
        Frame.__init__(self, _parent, *_args, **_kw)            
        self.parent = _parent
        
        # create a canvas object and a vertical scrollbar for scrolling it
        v_scroll_bar = Scrollbar(self, orient=VERTICAL)
        v_scroll_bar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=v_scroll_bar.set,bg="blue")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        v_scroll_bar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(self.canvas)
        interior_id = self.canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(_event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            self.canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                self.canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(_event):
            if interior.winfo_reqwidth() != self.canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                self.canvas.itemconfigure(interior_id, width=self.canvas.winfo_width())
        self.canvas.bind('<Configure>', _configure_canvas)

        return


class EditorPane(Frame):
    def __init__(self,_parent):
        Frame.__init__(self, _parent, bg="blue")
        self.root = _parent
        
        self.data_panel = SidePanel(self,self.root)
        
        self.data_panel.pack(fill=BOTH,expand=TRUE)
        
class SidePanel(ttk.Notebook):
    """
    The tabbed panel (Notebook) that will contain the side panel of the builder.
    """
    def __init__(self,_parent,_root):
        ttk.Notebook.__init__(self, _parent)
        self.root = _root
        
        fighter_properties = FighterPropertiesPanel(self,_root)
        fighter_actions = ActionListPanel(self,_root)
        
        
        self.panel_windows = {
            'Properties': fighter_properties,
            'Actions': fighter_actions
            }
        
        for name,window in self.panel_windows.iteritems():
            self.add(window,text=name,sticky=N+S+E+W)
        
    def addActionPane(self,_actionName):
        actionPanel = ActionPanel(self,self.root,_actionName)
        self.panel_windows[_actionName] = actionPanel
        self.add(actionPanel,text=_actionName,sticky=N+S+E+W)
        
    def closeActionPane(self,_actionName):
        self.forget(self.panel_windows[_actionName])
        self.panel_windows.pop(_actionName,None)
    
class dataPanel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        
        # A list of dataLines to draw
        self.data_list = []
        
        self.scroll_frame = VerticalScrolledFrame(self,bg="red")
        self.interior = self.scroll_frame.interior
        
        self.selected_string = StringVar(self)
        self.selected = None
        
    def loadDataList(self):
        self.scroll_frame.pack(fill=BOTH,expand=TRUE)
        for data in self.data_list:
            data.pack(fill=X) #the data line will hide itself if it's not expanded
            
    def changeFighter(self, *_args):
        global fighter
        
        for panel in self.data_list:
            panel.target_object = fighter
            panel.update()
            
class FighterPropertiesPanel(dataPanel):
    def __init__(self,_parent,_root):
        dataPanel.__init__(self, _parent, _root)
        self.config(bg="green")
        
        self.panels = [
            dataSelector.StringLine(self,self.interior,'Name:',None,'name'),
            dataSelector.ImageLine(self,self.interior,'Franchise Icon:',None,'franchise_icon_path'),
            dataSelector.ImageLine(self,self.interior,'CSS Icon:',None,'css_icon_path'),
            dataSelector.ImageLine(self,self.interior,'CSS Portrait:',None,'css_portrait_path'),
            dataSelector.DirLine(self,self.interior,'Sprite Path:',None,'sprite_directory'),
            dataSelector.StringLine(self,self.interior,'Sprite Prefix:',None,'sprite_prefix'),
            dataSelector.NumLine(self,self.interior,'Sprite Width:',None,'sprite_width'),
            dataSelector.NumLine(self,self.interior,'Sprite Scale:',None,'scale'),
            dataSelector.StringLine(self,self.interior,'Default Sprite:',None,'default_sprite'),
            dataSelector.DirLine(self,self.interior,'Article Path:',None,'article_path'),
            dataSelector.ModuleLine(self,self.interior,'Articles:',None,'article_file'),
            dataSelector.DirLine(self,self.interior,'Sound Path:',None,'sound_path'),
            dataSelector.ModuleLine(self,self.interior,'Actions:',None,'action_file')
            ]
        
        for panel in self.panels:
            self.data_list.append(panel)
            
        self.loadDataList()
        
class ActionListPanel(dataPanel):
    def __init__(self,_parent,_root):
        dataPanel.__init__(self, _parent, _root)
        self.config(bg="teal")
        self.act_list = []
        
    def changeFighter(self, *_args):
        global fighter
        for data in self.data_list:
            data.pack_forget()
        
        self.data_list = []
        self.act_list = []
        
        self.scroll_frame.canvas.yview_moveto(0.0)
        
        if isinstance(fighter.actions, engine.actionLoader.ActionLoader):
            self.act_list.extend(fighter.actions.getAllActions())
        else:
            for name,_ in inspect.getmembers(fighter.actions, inspect.isclass):
                self.act_list.append(name)
        
        for action in self.act_list:
            #Once we have action selector lines, replace this
            dataLine = dataSelector.ActionLine(self,self.interior,action,fighter)
            self.data_list.append(dataLine)
        self.data_list.append(dataSelector.NewActionLine(self,self.interior,fighter))
        self.loadDataList()
        
        dataPanel.changeFighter(self, *_args)
    
    def addAction(self):
        CreateActionWindow(self.root)
        
    def deleteAction(self,_actionName):
        global fighter
        action = fighter.getAction(_actionName)
        self.root.deleteAction(action)
        
    def setAction(self,_actionName):
        print('setting action ' + _actionName)
        self.root.action_string.set(_actionName)
        
class ActionPanel(dataPanel):
    def __init__(self,_parent,_root,_actionName):
        global fighter
        global changed_actions
        
        dataPanel.__init__(self, _parent, _root)
        self.config(bg="light coral")
        
        if changed_actions.has_key(_actionName):
            self.action = changed_actions[_actionName]
        else: self.action = fighter.getAction(_actionName)
        
        self.action_name = _actionName
        self.data_list.append(dataSelector.CloseActionLine(self,self.interior))
        
        #Action Properties
        self.data_list.append(dataSelector.NumLine(self,self.interior,'Length: ',self.action,'last_frame'))
        self.data_list.append(dataSelector.SpriteLine(self,self.interior,'Sprite: ',self.action,'sprite_name'))
        self.data_list.append(dataSelector.NumLine(self,self.interior,'Sprite Rate: ',self.action,'sprite_rate'))
        self.data_list.append(dataSelector.BoolLine(self,self.interior,'Loop',self.action,'loop'))
        
        self.loadDataList()
        
    def loadDataList(self):
        dataPanel.loadDataList(self)
        
    def closeTab(self):
        self.parent.closeActionPane(self.action_name)