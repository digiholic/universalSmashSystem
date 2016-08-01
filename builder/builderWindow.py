import os
import pygame
import sys
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
import ttk
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
changedActions = dict()

"""
The BuilderPanel is the base class for the panels. It sets the root and parent,
as well as the traces for the root variables. The change functions do nothing unless overridden.
"""
class BuilderPanel(Frame):
    def __init__(self,parent,root):
        Frame.__init__(self, parent)
        self.parent = parent
        self.root = root
        
        self.root.fighterString.trace('w',self.changeFighter)
        self.root.actionString.trace('w',self.changeAction)
        self.root.frame.trace('w',self.changeFrame)
        
    def changeFighter(self,*args):
        pass
    
    def getFighter(self):
        global fighter
        return fighter
    
    def changeAction(self,*args):
        pass
    
    def getAction(self):
        global action
        return action
    
    def changeFrame(self,*args):
        pass
    
    def getFrame(self):
        global frame
        return frame
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
        self.fighterFile = None #The python or XML fighter file
        self.fighterProperties = None #The contents of fighterFile
        self.fighterString = StringVar(self)
        self.actionString = StringVar(self)
        self.frame = IntVar(self)

        # Create and place subpanels
        self.config(menu=MenuBar(self))
        self.viewerPane = LeftPane(self,self)
        self.actionPane = RightPane(self,self)
        self.viewerPane.grid(row=0,column=0,sticky=N+S+E+W)
        self.actionPane.grid(row=0,column=1,sticky=N+S+E+W)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3, uniform="column")
        self.grid_columnconfigure(1, weight=2, uniform="column")
        self.fighterString.trace('w',self.changeFighter)
        self.actionString.trace('w',self.changeAction)
        self.frame.trace('w',self.changeFrame)
        
        self.mainloop()
    
    def actionModified(self):
        global action
        global changedActions
        
        if not changedActions: #if the actions are empty
            self.wm_title(self.wm_title()+'*')
        
        changedActions[self.actionString.get()] = action
        
        #update the views
        self.actionPane.actionSelectorPanel.refreshDropdowns()
        self.viewerPane.viewerPanel.reloadFrame()
        for subact in self.actionPane.subactionPanel.subActionList:
            subact.updateName()
                
    def getFighterAction(self,actionName,getRawXml=False):
        global fighter
        if getRawXml:return fighter.actions.actionsXML.find(actionName)
        else: return fighter.getAction(actionName)
    
    def addAction(self,actionName):
        global fighter
        changedActions[actionName] = engine.action.DynamicAction(1)
        fighter.actions.modifyAction(actionName, changedActions[actionName])
        self.actionPane.actionSelectorPanel.refreshDropdowns()
    
    def changeFighter(self,*args):
        global fighter
        dirname, _ = os.path.split(self.fighterFile.name)
        if self.fighterFile.name.endswith('.py'):
            fighterModule = settingsManager.importFromURI(self.fighterFile, self.fighterFile.name, True)
            if hasattr(fighterModule, 'Fighter'):
                newfighter = fighterModule.Fighter(dirname,0)
                showinfo('Advanced mode warning','Legacy Editor cannot edit Advanced Mode (.py) fighter files. The fighter will be opened in read-only mode. Depending on the fighter, there may be inconsistencies with behavior in-game compared to what you view here.')
            else:
                showinfo('Error loading fighter','File does not contain a fighter. Are you sure you are loading the right Python file?')
                return
        else:
            newfighter = engine.abstractFighter.AbstractFighter(dirname,0)
            
        newfighter.initialize()
        fighter = newfighter
        self.wm_title('Legacy Editor - '+fighter.name)        
    
    def changeAction(self,*args):
        global action
        global changedActions
        global fighter
        if fighter:
            if changedActions.has_key(self.actionString.get()):
                action = changedActions[self.actionString.get()]
            else: action = fighter.getAction(self.actionString.get())
                
    def changeFrame(self,*args):
        global frame
        frame = self.frame.get()
    
class MenuBar(Menu):
    def __init__(self,root):
        Menu.__init__(self, root)
        self.root = root
        self.fileMenu = Menu(self,tearoff=False)
        self.actionMenu = Menu(self,tearoff=False)
        self.add_cascade(label="File", menu=self.fileMenu)
        self.add_cascade(label="Action", menu=self.actionMenu, state=DISABLED)
        
        self.fileMenu.add_command(label="New Fighter", command=self.newFighter)
        self.fileMenu.add_command(label="Load Fighter", command=self.loadFighter)
        self.fileMenu.add_command(label="Save Fighter", command=self.saveFighter)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.root.destroy)
        
        self.actionMenu.add_command(label="Add Action", command=self.addAction)
        self.actionMenu.add_command(label="Save Action", command=self.saveAction, state=DISABLED)
        self.actionMenu.add_command(label="Delete Action", command=self.deleteAction, state=DISABLED)
        self.actionMenu.add_separator()
        self.actionMenu.add_command(label="Add Conditional", command=self.addConditional, state=DISABLED)
        
        
        self.root.fighterString.trace('w',self.changeFighter)
        self.root.actionString.trace('w',self.changeAction)
        self.root.frame.trace('w',self.changeFrame)
        
    def newFighter(self):
        CreateFighterWindow(self)
    
    def loadFighter(self):
        fighterFile = askopenfile(mode="r",initialdir=settingsManager.createPath('fighters'),filetypes=[('TUSSLE Fighters','*.xml'),('Advanced Fighters', '*.py')])
        self.root.fighterFile = fighterFile
        self.root.fighterProperties = fighterFile.read()
        self.root.fighterString.set(fighterFile.name)
        self.entryconfig("Action", state=NORMAL)
        
    def saveFighter(self):
        global fighter
        global action
        global changedActions
        
        for actName, newAction in changedActions.iteritems():
            fighter.actions.modifyAction(actName, newAction) 
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
    
    def changeFighter(self,*args):
        pass
    
    def changeAction(self,*args):
        global action
        if action:
            self.actionMenu.entryconfig("Save Action", state=NORMAL)
            self.actionMenu.entryconfig("Delete Action", state=NORMAL)
            self.actionMenu.entryconfig("Add Conditional", state=NORMAL)
    
    def changeFrame(self,*args):
        pass

class CreateActionWindow(Toplevel):
    def __init__(self,root):
        Toplevel.__init__(self)
        self.title("Create a new Action")
        self.root = root
        nameLabel = Label(self,text="Action Name: ")
        self.name = Entry(self)
        button = Button(self, text="Confirm", command=self.submit)
        
        sep = ttk.Separator(self,orient=HORIZONTAL)
        septext = Label(self,text="Or choose a Basic Action to implement:")
        
        basicList = []
        for name, obj in inspect.getmembers(sys.modules[engine.baseActions.__name__]):
            if inspect.isclass(obj):
                if not name in self.root.actionPane.actionSelectorPanel.actList:
                    basicList.append(name)
        
        self.basicChoice = StringVar(self)
        basicBox = OptionMenu(self,self.basicChoice,*basicList)
        basicButton = Button(self,text="Confirm",command=self.submitBasic)
        
        nameLabel.grid(row=0,column=0)
        self.name.grid(row=0,column=1)
        button.grid(row=0,column=2)
        sep.grid(row=1,columnspan=3,sticky=E+W)
        septext.grid(row=1,columnspan=3)
        basicBox.grid(row=2,columnspan=2,sticky=E+W)
        basicButton.grid(row=2,column=2)
        
        
        
    def submit(self,*args):
        global fighter
        global changedActions
        
        name = self.name.get()
        print(name)
        if name:
            if not fighter.actions.hasAction(name): #if it doesn't already exist
                if not changedActions.has_key(name): #and we didn't already make one
                    print('create action: ' + name)
                    self.root.addAction(name)
                    self.destroy()
    
    def submitBasic(self,*args):
        global fighter
        global changedActions
        
        name = self.basicChoice.get()
        if name:
            if not fighter.actions.hasAction(name): #if it doesn't already exist
                if not changedActions.has_key(name): #and we didn't already make one
                    print('create action: ' + name)
                    self.root.addAction(name)
                    self.destroy()
                
class AddConditionalWindow(Toplevel):
    def __init__(self,root):
        Toplevel.__init__(self)
        self.title("Create a new Conditional Group")
        self.root = root
        nameLabel = Label(self,text="Conditional Name: ")
        self.name = Entry(self)
        nameLabel.grid(row=0,column=0)
        self.name.grid(row=0,column=1)
        
        button = Button(self, text="Confirm", command=self.submit)
        button.grid(row=1,columnspan=2)
        
    def submit(self,*args):
        global fighter
        global action
        
        name = self.name.get()
        if name and not action.conditionalActions.has_key(name):
            action.conditionalActions[name] = []
            self.root.actionModified()
            self.destroy()
 
class CreateFighterWindow(Toplevel):
    def __init__(self,parent):
        Toplevel.__init__(self)
        self.parent = parent
        self.root = parent.root
        
        # Labels
        folderNameLabel = Label(self,text='Folder Name')
        confirmButtom = Button(self,text='Confirm',command=self.submit)
        
        # Variables
        self.folderNameVar = StringVar(self)
        self.generateActionXmlVar = BooleanVar(self)
        self.generateActionPyVar = BooleanVar(self)
        
        # Setters
        folderNameEntry = Entry(self,textvariable = self.folderNameVar)
        generateActionXmlEntry = Checkbutton(self,variable=self.generateActionXmlVar,text="Generate Actions XML File")
        generateActionPyEntry = Checkbutton(self,variable=self.generateActionPyVar,text="Generate Actions PY File")
        
        # Placement
        folderNameLabel.grid(row=0,column=0,sticky=E)
        folderNameEntry.grid(row=0,column=1,sticky=E+W)
        generateActionXmlEntry.grid(row=1,column=0)
        generateActionPyEntry.grid(row=1,column=1)
        confirmButtom.grid(row=2,columnspan=2)
        
        """
        TODO: Allow this to be made with icons and stuff chosen ahead of time.
        Use file pickers to choose locations and copy them over.
        """
        
    def submit(self):
        path = settingsManager.createPath('fighters/'+self.folderNameVar.get())
            
        if os.path.exists(path):
            print('path exists')
            self.destroy()
        else:
            os.makedirs(path)
            newFighter = engine.abstractFighter.AbstractFighter(path,0)
            #create sprite dir
            spritePath = os.path.join(path,'sprites')
            os.makedirs(spritePath)
            copyfile(settingsManager.createPath('sprites/sandbag_idle.png'), os.path.join(spritePath,'sandbag_idle.png'))
            copyfile(settingsManager.createPath('sprites/default_franchise_icon.png'), os.path.join(spritePath,'franchise_icon.png'))
            
            #create __init__.py
            initpy = open(os.path.join(path,'__init__.py'),'w+')
            initpy.close()
            
            #check for and create actions files
            if self.generateActionXmlVar.get():
                actionxml = open(os.path.join(path,self.folderNameVar.get()+'_actions.xml'),'w+')
                actionxml.close()
            if self.generateActionPyVar.get():
                actionpy = open(os.path.join(path,self.folderNameVar.get()+'_actions.py'),'w+')
                actionpy.close()
                
            #copy over icons?
            newFighter.saveFighter()
            self.destroy()
            
        fighterFile = open(os.path.join(path,'fighter.xml'),'r')
        self.root.fighterFile = fighterFile
        self.root.fighterProperties = fighterFile.read()
        self.root.fighterString.set(fighterFile.name)
        self.parent.entryconfig("Action", state=NORMAL)
            
            
class LeftPane(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.viewerPanel = ViewerPanel(self,root)
        self.navigatorPanel = NavigatorPanel(self,root)
        
        self.viewerPanel.pack(fill=BOTH,expand=TRUE)
        self.navigatorPanel.pack(fill=X)
        
class ViewerPanel(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.config(bg="pink")
        #Create Pygame Panel
        os.environ['SDL_WINDOWID'] = str(self.winfo_id())
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        else:
            os.environ['SDL_VIDEODRIVER'] = 'x11'
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.winfo_width(), self.winfo_height()),pygame.RESIZABLE)
        self.center = (0,0)
        self.scale = 1.0
        
        self.game_loop()
        
    def game_loop(self):
        global fighter
        #TODO figure out that window snap thing that's messing up a lot
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((self.winfo_width(), self.winfo_height()),pygame.RESIZABLE)
                if fighter: self.centerFighter()
        
        self.screen.fill(pygame.Color("pink"))
        if fighter:
            fighter.mask = None #These don't work inside of the builder
            fighter.draw(self.screen, fighter.rect.topleft, self.scale)
            for hbox in fighter.active_hitboxes:
                hbox.draw(self.screen,hbox.rect.topleft,self.scale)
                
            
        pygame.display.flip()
        self.after(5, self.game_loop) #Loop every 5ms
    
    def centerFighter(self):
        fighter.rect.centerx = self.screen.get_rect().centerx + self.center[0]
        fighter.rect.centery = self.screen.get_rect().centery + self.center[1]
    
    def reloadFrame(self):
        global fighter
        global action
        global frame
        
        if action:
            fighter.changeAction(action)
            action.frame = 0
            while action.frame <= frame:
                action.updateAnimationOnly(fighter)
                
    ####################
    # TRACER FUNCTIONS #
    ####################
    def changeFighter(self,*args):
        global fighter
        self.centerFighter()
        
    def changeFrame(self,*args):
        global fighter
        global action
        global frame
        
        if action:
            fighter.changeAction(action)
            action.frame = 0
            while action.frame <= frame:
                action.updateAnimationOnly(fighter)
        for hbox in fighter.active_hitboxes:
            print(hbox.center,hbox.x_offset)
            
    def changeAction(self,*args):
        global action
        global fighter
        if action: fighter.changeAction(action)
        
class NavigatorPanel(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.config(bg="white",height=50)
        
        self.frameChangerPanel = Frame(self)
        
        self.buttonMinusFive = Button(self.frameChangerPanel, text="-5", command=lambda:self.changeFrameNumber(-5),state=DISABLED)
        self.buttonMinus = Button(self.frameChangerPanel, text="-1", command=lambda:self.changeFrameNumber(-1),state=DISABLED)
        self.currentFrame = Label(self.frameChangerPanel,text="0/1",state=DISABLED)
        self.buttonPlus = Button(self.frameChangerPanel, text="+1", command=lambda:self.changeFrameNumber(1),state=DISABLED)
        self.buttonPlusFive = Button(self.frameChangerPanel, text="+5", command=lambda:self.changeFrameNumber(5),state=DISABLED)
        
        self.frameChangerPanel.pack()
        
        self.buttonMinusFive.grid(row=0,column=0)
        self.buttonMinus.grid(row=0,column=1)
        self.currentFrame.grid(row=0,column=2)
        self.buttonPlus.grid(row=0,column=3)
        self.buttonPlusFive.grid(row=0,column=4)
        
    def changeFrameNumber(self, amount):
        global action
        frame = self.root.frame.get()
        if action:
            frame = max(0,frame + amount)
            frame = min(frame,action.lastFrame)
            
            self.currentFrame.config(text=str(frame)+"/"+str(action.lastFrame))
            
            #Enable buttons
            self.buttonMinusFive.config(state=NORMAL)
            self.buttonMinus.config(state=NORMAL)
            self.currentFrame.config(state=NORMAL)
            self.buttonPlus.config(state=NORMAL)
            self.buttonPlusFive.config(state=NORMAL)
            
            #Disable ones that shouldn't be clicked anymore
            if frame == 0:
                self.buttonMinus.config(state=DISABLED)
                self.buttonMinusFive.config(state=DISABLED)
            if frame == action.lastFrame:
                self.buttonPlus.config(state=DISABLED)
                self.buttonPlusFive.config(state=DISABLED)
            
            self.root.frame.set(frame)
        else: #If no action, disable everything
            self.buttonMinusFive.config(state=DISABLED)
            self.buttonMinus.config(state=DISABLED)
            self.currentFrame.config(state=DISABLED)
            self.buttonPlus.config(state=DISABLED)
            self.buttonPlusFive.config(state=DISABLED)
    
    def changeAction(self, *args):
        global action
        if action:
            self.root.frame.set(0)
            self.changeFrameNumber(0)
                
class RightPane(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.actionSelectorPanel = SelectorPanel(self,root)
        self.subactionPanel = SubactionPanel(self,root)
        self.subactionPropertyPanel = PropertiesPanel(self,root)
        
        self.actionSelectorPanel.pack(fill=X)
        self.subactionPanel.pack(fill=BOTH,expand=TRUE)
        self.subactionPropertyPanel.pack(fill=X)
        
class SelectorPanel(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.config(bg="purple",height=50)
        
        #Create Action dropdown menu
        self.currentAction = StringVar(self)
        self.currentAction.set("Fighter Properties")
        self.currentAction.trace('w', self.changeActionDropdown)
        self.actList = ['Fighter Properties']
        self.action = OptionMenu(self,self.currentAction,*self.actList)
        
        #Create Group dropdown menu
        self.currentGroup = StringVar(self)
        self.currentGroup.set("SetUp")
        self.defaultGroupList = ["Properties","Current Frame","Set Up","Tear Down","Transitions","Before Frames","After Frames","Last Frame"] 
        self.groupList = self.defaultGroupList[:] #have to do this to copy be value instead of reference
        self.group = OptionMenu(self,self.currentGroup,*self.groupList)
        
    def changeFighter(self, *args):
        global fighter
        self.actList = ["Fighter Properties"]
        if isinstance(fighter.actions, engine.actionLoader.ActionLoader):
            self.actList.extend(fighter.actions.getAllActions())
        else:
            for name,_ in inspect.getmembers(fighter.actions, inspect.isclass):
                self.actList.append(name)
        self.refreshDropdowns()
        self.currentAction.set('Fighter Properties')
    
    def changeActionDropdown(self,*args):
        global action
        if self.currentAction.get() == 'Fighter Properties':
            self.group.pack_forget()
            self.groupList = ["Fighter","Attributes"]
            for i in range(0,8):
                self.groupList.append("Color "+str(i))
            self.refreshDropdowns()
            self.currentGroup.set('Fighter')
        else:
            self.root.actionString.set(self.currentAction.get())
            self.refreshDropdowns()
            self.currentGroup.set('Properties')
    
    def refreshDropdowns(self):
        global changedActions
        global action
        
        for changedaction in changedActions.keys():
            if not changedaction in self.actList:
                self.actList.append(changedaction)
        
        if self.currentAction.get() == 'Fighter Properties':
            self.groupList = ["Fighter","Attributes"]
            for i in range(0,8):
                self.groupList.append("Color "+str(i))
            self.currentGroup.set('Fighter')
        else:
            self.groupList = self.defaultGroupList[:]
            if action and isinstance(action, engine.action.DynamicAction):
                for group in action.conditionalActions.keys():
                    self.groupList.append('Cond: '+ group)
                            
        self.action.destroy()
        self.action = OptionMenu(self,self.currentAction,*self.actList)
        self.action.config(width=18)
        
        self.group.destroy()
        self.group = OptionMenu(self,self.currentGroup,*self.groupList)
        self.group.config(width=10)
        
        self.action.pack_forget()
        self.group.pack_forget()
        
        self.action.pack(side=LEFT)
        self.group.pack(side=LEFT)      
        
class SubactionPanel(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.config(bg="blue")
        
        self.parent.actionSelectorPanel.currentAction.trace('w',self.changeActionDropdown)
        self.parent.actionSelectorPanel.currentGroup.trace('w',self.groupChanged)
        
        self.subActionList = []
        self.currentFrameSubacts = []
        
        self.scrollFrame = VerticalScrolledFrame(self,bg="blue")
        self.scrollFrame.config(width=self.winfo_width())
        
        self.textfield = Text(self,wrap=NONE)
        self.xscrollbar = Scrollbar(self.textfield, orient=HORIZONTAL, command=self.textfield.xview)
        self.yscrollbar = Scrollbar(self.textfield, orient=VERTICAL, command=self.textfield.yview)
        self.textfield.configure(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        
        self.textfield.pack(fill=BOTH,expand=TRUE)
        self.yscrollbar.pack(side=RIGHT, fill=Y)
        self.xscrollbar.pack(side=BOTTOM, fill=X)
        
        self.selectedString = StringVar(self)
        self.selected = None
    
    """
    When displaying text instead of a modifiable subaction list,
    switch to the textField.
    """
    def showTextField(self):
        self.textfield.pack(fill=BOTH,expand=TRUE)
        self.yscrollbar.pack(side=RIGHT, fill=Y)
        self.xscrollbar.pack(side=BOTTOM, fill=X)
        self.clearSubActList()
    
    """
    When displaying a modifiable subaction list instead of text,
    switch to the list.
    """
    def showSubactionList(self):
        #Show subaction selector
        self.textfield.pack_forget()
        self.yscrollbar.pack_forget()
        self.xscrollbar.pack_forget()
        
        self.scrollFrame.pack(fill=BOTH,expand=TRUE)
        for subAct in self.subActionList:
            subAct.pack(fill=X)
    
    def clearSubActList(self):
        self.scrollFrame.pack_forget()
        
        for subAct in self.subActionList:
            subAct.destroy()
        self.subActionList = []
        
    def loadText(self,text):
        try:
            act = self.xmlToActions(text)
        except: #It is not XML
            act = text
        self.textfield.delete("1.0", END)
        self.textfield.insert(INSERT, act)
    
    def xmlToActions(self,xml,prefix=''):
        root = ElementTree.fromstring(xml)
        text = ""
        for child in root:
            text += self.printNode(child)
        return text
    
    def printNode(self,node,prefix=''):
        text = prefix
        text += node.tag+': '
        text += node.text.lstrip() if node.text is not None else ''
        if len(node.attrib) > 0: #if it has attributes
            text += ' ('
            for name,atr in node.attrib.iteritems():
                text+=name+': '+str(atr)
                text+=','
            text = text[:-1] #chop off the last comma
            text += ')'
            
        if len(list(node)) > 0: #if it has children
            text += '\n'
            for child in node:
                text += self.printNode(child,'  '+prefix)
        else: text += '\n'
        return text
        
           
    def changeActionDropdown(self, *args):
        global fighter
        
        if self.selected:
            self.selected.unselect()
            self.selectedString.set('')
            
        newAction = self.parent.actionSelectorPanel.currentAction.get()
        if newAction == 'Fighter Properties':
            self.parent.actionSelectorPanel.currentGroup.set('Fighter')
        else:
            self.textfield.delete("1.0", END)
            self.textfield.insert(INSERT, str(action))
    
    def groupChanged(self,*args):
        global fighter
        global action
            
        self.group = self.parent.actionSelectorPanel.currentGroup.get()
        newAction = self.parent.actionSelectorPanel.currentAction.get()
        
        if self.selected:
            self.selected.unselect()
            self.selectedString.set('')
            
        self.clearSubActList()
        if self.group == "Fighter":
            namePanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Name','string',fighter,'name')],'Name: ' + fighter.name)
            
            iconPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Icon',
                                                                   ('file',[('Image Files','*.png')]),
                                                                   fighter,
                                                                   'franchise_icon_path')],
                                                            'Franchise Icon')
            cssIconPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('CSS Icon',
                                                                     ('file',[('Image Files','*.png')]),
                                                                     fighter,
                                                                     'css_icon_path')],
                                                               'CSS Icon')
            scalePanel = subactionSelector.SubactionSelector(self.scrollFrame,[('scale','float',fighter.sprite,'scale')],'Sprite Scale')
            spriteDirectoryPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Sprite Directory',
                                                                          ('dir',[]),
                                                                          fighter,
                                                                          'sprite_directory')],
                                                                       'Sprite Directory')
            spriteWidthPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Sprite Width','int',fighter,'sprite_width')],'Sprite Width')
            defaultSpritePanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Default Sprite','string',fighter,'default_sprite')],'Default Sprite')
            articlePathPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Article Path',('dir',[]),fighter,'article_path_short')],'Article Path')
            actionsPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Actions File',
                                                                      ('file',[('TUSSLE ActionScript files','*.xml'),
                                                                               ('Python Files','*.py')]),
                                                                      fighter,
                                                                      'action_file')],'Actions')
            self.subActionList.append(namePanel)
            self.subActionList.append(iconPanel)
            self.subActionList.append(cssIconPanel)
            self.subActionList.append(scalePanel)
            self.subActionList.append(spriteDirectoryPanel)
            self.subActionList.append(spriteWidthPanel)
            self.subActionList.append(defaultSpritePanel)
            self.subActionList.append(articlePathPanel)
            self.subActionList.append(actionsPanel)
            
            self.showSubactionList()
        elif self.group == 'Attributes':
            for tag,val in fighter.var.iteritems():
                panel = subactionSelector.SubactionSelector(self.scrollFrame,[(tag,type(val).__name__,fighter.var,tag)],tag+': '+str(val))
                self.subActionList.append(panel)
            
            self.showSubactionList()
        elif isinstance(action,engine.action.DynamicAction):
            subActGroup = []
            if self.group == 'Set Up':
                subActGroup = action.setUpActions
            elif self.group == 'Tear Down':
                subActGroup = action.tearDownActions
            elif self.group == 'Transitions':
                subActGroup = action.stateTransitionActions
            elif self.group == 'Before Frames':
                subActGroup = action.actionsBeforeFrame
            elif self.group == 'After Frames':
                subActGroup = action.actionsAfterFrame
            elif self.group == 'Last Frame':
                subActGroup = action.actionsAtLastFrame
            elif self.group == 'Current Frame':
                subActGroup = self.currentFrameSubacts
            elif self.group.startswith('Cond:'):
                subActGroup = action.conditionalActions[self.group[6:]]
            
            for subact in subActGroup:
                selector = subactionSelector.SubactionSelector(self.scrollFrame,subact)
                selector.updateName()
                self.subActionList.append(selector)
            
            
            self.showSubactionList()
            if self.group == 'Properties':
                lengthPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Length','int',action,'lastFrame')],'Length: '+str(action.lastFrame))
                spritePanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Sprite','sprite',action,'spriteName')],'Sprite Name: '+str(action.spriteName))
                spriteRatePanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Sprite Rate','int',action,'spriteRate')],'Sprite Rate: '+str(action.spriteRate))
                loopPanel = subactionSelector.SubactionSelector(self.scrollFrame,[('Loop','bool',action,'loop')],'Loop:'+str(action.loop))
                
                self.subActionList.append(lengthPanel)
                self.subActionList.append(spritePanel)
                self.subActionList.append(spriteRatePanel)
                self.subActionList.append(loopPanel)
                
                self.showSubactionList()
                #node = self.root.getFighterAction(newAction,True)
                #self.loadText(ElementTree.tostring(node))
                #self.showTextField()
                
        else:
            self.loadText('Advanced action from '+str(fighter.actions))
    
    def addSubactionPanel(self,subact):
        selector = subactionSelector.SubactionSelector(self.scrollFrame,subact)
        selector.updateName()
        self.subActionList.append(selector)
        selector.pack(fill=X)
        
    def changeFrame(self, *args):
        global frame
        
        if self.selected:
            self.selected.unselect()
            self.selectedString.set('')
            
        self.currentFrameSubacts = []
        for subact in action.actionsAtFrame[frame]:
            self.currentFrameSubacts.append(subact)
        if self.parent.actionSelectorPanel.currentGroup.get() == 'Current Frame':
            self.clearSubActList()
            for subact in self.currentFrameSubacts:
                selector = subactionSelector.SubactionSelector(self.scrollFrame,subact)
                selector.updateName()
                self.subActionList.append(selector)
            self.showSubactionList()
            
        
class PropertiesPanel(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.config(bg="red",height=200)
        self.selected = None
        self.parent.subactionPanel.selectedString.trace('w',self.onSelect)
        
        self.newSubactionFrame = ttk.Notebook(self)
        
        self.controlWindow = ttk.Frame(self.newSubactionFrame)
        self.spriteWindow = ttk.Frame(self.newSubactionFrame)
        self.behaviorWindow = ttk.Frame(self.newSubactionFrame)
        self.hitboxWindow = ttk.Frame(self.newSubactionFrame)
        self.articleWindow = ttk.Frame(self.newSubactionFrame)
        
        subactWindows = {'Control': self.controlWindow,
                         'Sprite': self.spriteWindow,
                         'Behavior': self.behaviorWindow,
                         'Hitbox': self.hitboxWindow,
                         'Article': self.articleWindow
                         }
        
        for name,window in subactWindows.iteritems():
            self.newSubactionFrame.add(window,text=name)
            
        subactionLists = {'Control':[],
                          'Sprite':[],
                          'Behavior':[],
                          'Hitbox':[],
                          'Article':[]}
        
        for name,subact in engine.subaction.subActionDict.iteritems():
            if subact.subactGroup in subactWindows.keys():
                shortname = (name[:19] + '..') if len(name) > 22 else name
                button = Button(subactWindows[subact.subactGroup],text=shortname,command=lambda subaction=subact: self.addSubaction(subaction))
                subactionLists[subact.subactGroup].append(button)
                
        for group in subactionLists.values():
            x = 0
            y = 0
            for button in group:
                button.grid(row=y,column=x,sticky=E+W)
                x += 1
                if x > 1:
                    y += 1
                    x = 0
        
        self.subframe = self.newSubactionFrame
        self.subframe.pack(fill=BOTH)
        
    def addSubaction(self,subAction):
        global action
        global frame
        
        groupToAction = {'Current Frame': action.actionsAtFrame[frame],
                         'Set Up': action.setUpActions,
                         'Tear Down': action.tearDownActions,
                         'Transitions': action.stateTransitionActions,
                         'Before Frames': action.actionsBeforeFrame,
                         'After Frames': action.actionsAfterFrame,
                         'Last Frame': action.actionsAtLastFrame}
        group = self.parent.actionSelectorPanel.currentGroup.get()
        if groupToAction.has_key(group) or group.startswith('Cond:'):
            subact = subAction()
            if group.startswith('Cond:'):
                action.conditionalActions[group[6:]].append(subact)
            else: groupToAction[group].append(subact)
            self.root.actionModified()
            self.parent.subactionPanel.addSubactionPanel(subact)
                    
    def onSelect(self,*args):
        self.selected = self.parent.subactionPanel.selected
        self.subframe.pack_forget()
        
        if self.selected:
            if self.selected.propertyFrame:
                self.subframe = self.selected.propertyFrame
                self.subframe.pack(fill=BOTH)
        else:
            self.subframe = self.newSubactionFrame
            self.subframe.pack(fill=BOTH)
            
"""
Scrolling frame, since TKinter doesn't do this for some reason.
Source: http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
"""
class VerticalScrolledFrame(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            
        self.parent = parent
        
        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set,bg="blue")
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return
