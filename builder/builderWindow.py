import os
import pygame
import settingsManager
import inspect
import engine.abstractFighter
import subactionSelector
import xml.etree.ElementTree as ElementTree
from Tkinter import *
from tkFileDialog import askopenfile
from tkMessageBox import showinfo

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
        self.iconbitmap(settingsManager.createPath('editor.ico'))
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
        self.viewerPane.viewerPanel.reloadFrame()
        print(changedActions)
                
    def getFighterAction(self,actionName,getRawXml=False):
        global fighter
        if getRawXml: return fighter.actions.actionsXML.find(actionName)
        else: return fighter.getAction(actionName)
    
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
        fileMenu = Menu(self,tearoff=False)
        actionMenu = Menu(self,tearoff=False)
        self.add_cascade(label="File", menu=fileMenu)
        self.add_cascade(label="Action", menu=actionMenu, state=DISABLED)
        
        fileMenu.add_command(label="New Fighter", command=self.newFighter)
        fileMenu.add_command(label="Load Fighter", command=self.loadFighter)
        fileMenu.add_command(label="Save Fighter", command=self.saveFighter)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.root.destroy)
        
        actionMenu.add_command(label="Add Action", command=self.addAction)
        actionMenu.add_command(label="Save Action", command=self.saveAction)
        actionMenu.add_command(label="Delete Action", command=self.deleteAction)
        
        self.root.fighterString.trace('w',self.changeFighter)
        self.root.actionString.trace('w',self.changeAction)
        self.root.frame.trace('w',self.changeFrame)
        
    def newFighter(self):
        pass
    
    def loadFighter(self):
        fighterFile = askopenfile(mode="r",initialdir=settingsManager.createPath('fighters'),filetypes=[('TUSSLE Fighters','*.xml'),('Advanced Fighters', '*.py')])
        self.root.fighterFile = fighterFile
        self.root.fighterProperties = fighterFile.read()
        self.root.fighterString.set(fighterFile.name)
        
    def saveFighter(self):
        global fighter
        global action
        global changedActions
        
        for actName, newAction in changedActions.iteritems():
            fighter.actions.modifyAction(actName, newAction) 
        fighter.actions.saveActions()

    def addAction(self):
        pass
    
    def saveAction(self):
        pass
    
    def deleteAction(self):
        pass
    
    def changeFighter(self,*args):
        pass
    
    def changeAction(self,*args):
        global action
        if action:
            self.entryconfig("Action", state=NORMAL)
    
    def changeFrame(self,*args):
        pass
    
class LeftPane(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.viewerPanel = ViewerPanel(self,root)
        self.navigatorPanel = NavigatorPanel(self,root)
        
        self.viewerPanel.pack(fill=BOTH,expand=True)
        self.navigatorPanel.pack(fill=X)
        
class ViewerPanel(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.config(bg="pink")
        #Create Pygame Panel
        os.environ['SDL_WINDOWID'] = str(self.winfo_id())
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
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
        self.subactionPanel.pack(fill=BOTH,expand=True)
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
        self.defaultGroupList = ["Properties","Set Up","Tear Down","Transitions","Before Frames","After Frames","Last Frame","Current Frame"] 
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
        else:
            self.root.actionString.set(self.currentAction.get())
            
            self.groupList = self.defaultGroupList[:]
            if action:
                for group in action.conditionalActions.keys():
                    self.groupList.append('Cond: '+ group)
            self.refreshDropdowns()
            self.currentGroup.set('Properties')
    
    def refreshDropdowns(self):
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
        
        self.textfield = Text(self,wrap=NONE)
        self.xscrollbar = Scrollbar(self.textfield, orient=HORIZONTAL, command=self.textfield.xview)
        self.yscrollbar = Scrollbar(self.textfield, orient=VERTICAL, command=self.textfield.yview)
        self.textfield.configure(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        
        self.textfield.pack(fill=BOTH,expand=True)
        self.yscrollbar.pack(side=RIGHT, fill=Y)
        self.xscrollbar.pack(side=BOTTOM, fill=X)
        
        self.selectedString = StringVar(self)
        self.selected = None
    
    """
    When displaying text instead of a modifiable subaction list,
    switch to the textField.
    """
    def showTextField(self):
        self.textfield.pack(fill=BOTH,expand=True)
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
        
        for subAct in self.subActionList:
            print(subAct)
            subAct.pack(fill=X)
    
    def clearSubActList(self):
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
        self.selected = None
        newAction = self.parent.actionSelectorPanel.currentAction.get()
        if newAction == 'Fighter Properties':
            self.textfield.delete("1.0", END)
            self.textfield.insert(INSERT, self.root.fighterProperties)
        else:
            self.textfield.delete("1.0", END)
            self.textfield.insert(INSERT, str(action))
    
    def groupChanged(self,*args):
        global fighter
        global action
        
        self.selected = None
        self.group = self.parent.actionSelectorPanel.currentGroup.get()
        newAction = self.parent.actionSelectorPanel.currentAction.get()
        
        if isinstance(action,engine.action.DynamicAction):
            self.clearSubActList()
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
                subActGroup = action.conditionalActions[self.group]
            
            for subact in subActGroup:
                self.subActionList.append(subactionSelector.SubactionSelector(self,subact))
            
            self.showSubactionList()
            if self.group == 'Properties':
                node = self.root.getFighterAction(newAction,True)
                self.loadText(ElementTree.tostring(node))
                self.showTextField()
        else:
            self.loadText('Advanced action from '+str(fighter.actions))
        
    def changeFrame(self, *args):
        global frame
        
        self.currentFrameSubacts = []
        for subact in action.actionsAtFrame[frame]:
            self.currentFrameSubacts.append(subact)
        if self.parent.actionSelectorPanel.currentGroup.get() == 'Current Frame':
            self.clearSubActList()
            for subact in self.currentFrameSubacts:
                self.subActionList.append(subactionSelector.SubactionSelector(self,subact))
            self.showSubactionList()
            
        
class PropertiesPanel(BuilderPanel):
    def __init__(self,parent,root):
        BuilderPanel.__init__(self, parent, root)
        self.config(bg="red",height=200)
        self.selected = None
        self.subframe = Frame(self)
        self.parent.subactionPanel.selectedString.trace('w',self.onSelect)
        self.subframe.pack(fill=BOTH)
        
    def onSelect(self,*args):
        self.selected = self.parent.subactionPanel.selected
        rowNo = 0
        self.subframe.destroy()
        print('subframe',self.subframe)

        if self.selected:
            print(self.selected.subaction)
            """
            for key,value in self.selected.subaction.variableMap.iteritems():
                newLabel = Label(self,text=key)
                #TODO: Case statement on value
                newValue = Label(self,text=str(getattr(self.selected.subaction,key)))
                newLabel.grid(row=rowNo,column=0)
                newValue.grid(row=rowNo,column=1)
                rowNo += 1
            """
            self.subframe = self.selected.subaction.getPropertiesPanel(self)
            self.subframe.pack(fill=BOTH)
if __name__=='__main__': MainFrame()