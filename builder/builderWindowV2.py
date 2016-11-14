import settingsManager
from Tkinter import *
import os
import builder.dataPanel as dataPanel
from tkMessageBox import showinfo
from tkFileDialog import askopenfile
import engine.abstractFighter
import stages.training_stage

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
        
        self.fighter_file = None #The python or XML fighter file
        self.fighter_properties = None #The contents of fighter_file
        
        self.fighter_string = StringVar(self)
        self.action_string = StringVar(self)
        self.frame = IntVar(self)
        
        self.config(menu=MenuBar(self))
        
        self.viewer_pane = ViewerPane(self)
        self.editor_pane = EditorPane(self)
        
        self.viewer_pane.grid(row=0,column=0,sticky=N+S+E+W)
        self.editor_pane.grid(row=0,column=1,sticky=N+S+E+W)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3, uniform="column")
        self.grid_columnconfigure(1, weight=2, uniform="column")
        
        self.fighter_string.trace('w',self.changeFighter)
        self.action_string.trace('w',self.changeAction)
        self.frame.trace('w',self.changeFrame)
        
        self.mainloop()
    
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
        new_fighter.initialize()
        new_fighter.game_state = stages.training_stage.stage.getStage()
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
        
    def getFighter(self):
        global fighter
        return fighter
    
    def getAction(self):
        global action
        return action
    
    def getFrame(self):
        global frame
        return frame
    
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
        #CreateFighterWindow(self)
        pass
    
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
        #CreateActionWindow(self.root)
        pass
    
    def addConditional(self):
        #AddConditionalWindow(self.root)
        pass
    
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

    
class ViewerPane(Frame):
    def __init__(self,_parent):
        Frame.__init__(self, _parent, bg="pink")
        

        
if __name__== '__main__': MainFrame()