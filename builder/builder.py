import pygame
import settingsManager
import inspect
import sys
import os
import engine.baseActions
import subactionSelector
import xml.etree.ElementTree as ElementTree
from Tkinter import * 
from tkFileDialog import askopenfile
from tkMessageBox import showinfo
from engine.abstractFighter import AbstractFighter
from ScrolledText import ScrolledText


class BuilderWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.width = 640
        self.height = 480
        
        self.wm_title('Legacy Editor')
        self.iconbitmap(settingsManager.createPath('editor.ico'))
        self.geometry('640x480')
        self.config(menu=MenuBar(self))
        
        self.actionPane = ActionPane(self)
        self.viewerPane = ViewerPane(self)
        
        self.viewerPane.grid(row=0,column=0,sticky=N+S+E+W)
        self.actionPane.grid(row=0,column=1,sticky=N+S+E+W)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3, uniform="column")
        self.grid_columnconfigure(1, weight=2, uniform="column")
        
        self.actionPane.actionSelectorPanel.currentAction.trace('w',self.changeAction)
        
        self.fighter = None
        self.fighterFile = None
        self.fighterProperties = None
        self.action = None
        
        self.mainloop()
        
    def loadFighter(self,fighterFile):
        dirname, fname = os.path.split(fighterFile.name)
        if fighterFile.name.endswith('.py'):
            fighter = settingsManager.importFromURI(fighterFile, fighterFile.name, True)
            if hasattr(fighter, 'Fighter'):
                self.fighter = fighter.Fighter(dirname,0)
                showinfo('Advanced mode warning','Legacy Editor cannot edit Advanced Mode (.py) fighter files. The fighter will be opened in read-only mode. Depending on the fighter, there may be inconsistencies with behavior in-game compared to what you view here.')
            else:
                showinfo('Error loading fighter','File does not contain a fighter. Are you sure you are loading the right Python file?')
                return
        else:
            self.fighter = AbstractFighter(dirname,0)
        
        self.fighterFile = fighterFile
        self.fighter.initialize()
        self.fighterProperties = fighterFile.read()
        
        #Load the fighter in the other panels that need it
        self.viewerPane.ViewerPanel.loadFighter(self.fighter)
        self.actionPane.actionSelectorPanel.loadFighter(self.fighter)
        self.actionPane.subactionPanel.loadText(self.fighterProperties)
    
    def getFighterProperties(self):
        if self.fighterProperties:
            return self.fighterProperties
        else:
            return ''
        
    def getFighterAction(self,actionName,getRawXml=False):
        if getRawXml: return self.fighter.actions.actionsXML.find(actionName)
        else: return self.fighter.getAction(actionName)
    
    def changeAction(self,*args):
        newAction = self.actionPane.actionSelectorPanel.currentAction.get()
        if not newAction == 'Fighter Properties':
            self.action = self.getFighterAction(newAction)
            
class MenuBar(Menu):
    def __init__(self,root):
        Menu.__init__(self, root)
        self.root = root
        fileMenu = Menu(self,tearoff=False)
        self.add_cascade(label="File", menu=fileMenu)
        
        fileMenu.add_command(label="New Fighter", command=self.newFighter)
        fileMenu.add_command(label="Load Fighter", command=self.loadFighter)
        fileMenu.add_command(label="Save Fighter", command=self.saveFighter)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.root.destroy)
        
    def newFighter(self):
        pass
    
    def loadFighter(self):
        fighterFile = askopenfile(mode="r",initialdir=settingsManager.createPath('fighters'),filetypes=[('TUSSLE Fighters','*.xml'),('Advanced Fighters', '*.py')])
        self.root.loadFighter(fighterFile)
        
    def saveFighter(self):
        pass
"""
Viewer Pane is the left half of the screen. It contains all of the controls
for viewing the fighter.
"""
class ViewerPane(Frame):
    def __init__(self,root):
        Frame.__init__(self, root)
        self.root = root
        self.NavigatorPanel = NavigatorPanel(self)
        self.ViewerPanel = ViewerPanel(self)
        
        self.ViewerPanel.pack(fill=BOTH,expand=True)
        self.NavigatorPanel.pack(fill=X)
        
"""
Viewer Panel is the actual window that we see the sprite in
"""    
class ViewerPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="gray")
        self.root = root
        
        os.environ['SDL_WINDOWID'] = str(self.winfo_id())
        if sys.platform == "win32":
            os.environ['SDL_VIDEODRIVER'] = 'windib'
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.winfo_width(), self.winfo_height()),pygame.RESIZABLE)
        
        self.root.NavigatorPanel.frame.trace('w',self.changeFrame)
        self.root.root.actionPane.actionSelectorPanel.currentAction.trace('w',self.changeAction)
        self.fighter = None
        self.frame = 0
        self.center = (0,0)
        self.scale = 1.0
        
        self.game_loop()
    
    def game_loop(self):
        
        #TODO figure out that window snap thing that's messing up a lot
        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((self.winfo_width(), self.winfo_height()),pygame.RESIZABLE)
                if self.fighter: self.loadFighter(self.fighter)
        
        self.screen.fill(pygame.Color("pink"))
        
        if self.fighter:
            self.fighter.mask = None #These don't work inside of the builder
            self.fighter.draw(self.screen, self.fighter.rect.topleft, self.scale)
            
        
        pygame.display.flip()
        
        self.after(5, self.game_loop)
    
    def loadFighter(self,fighter):
        self.fighter = fighter
        self.root.root.wm_title('Legacy Editor - '+self.fighter.name)
        self.fighter.rect.centerx = self.screen.get_rect().centerx + self.center[0]
        self.fighter.rect.centery = self.screen.get_rect().centery + self.center[1]
    
    def changeFrame(self,*args):
        self.frame = self.root.NavigatorPanel.frame.get()
        if self.action:
            self.action.frame = 0
            while self.action.frame < self.frame:
                self.action.update(self.fighter)
                
    
    def changeAction(self,*args):
        self.action = self.root.root.action
        if self.action: self.fighter.changeAction(self.action)
    
"""
Navigator Panel contains the controls to step through the action
"""
class NavigatorPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="white",height=50)
        self.root = root
        
        self.frameChangerPanel = Frame(self)
        self.buttonMinus = Button(self.frameChangerPanel, text="-", command=lambda:self.changeFrame(-1),state=DISABLED)
        self.currentFrame = Label(self.frameChangerPanel,text="0/1",state=DISABLED)
        self.buttonPlus = Button(self.frameChangerPanel, text="+", command=lambda:self.changeFrame(1),state=DISABLED)
        
        self.root.root.actionPane.actionSelectorPanel.currentAction.trace('w',self.changeAction)
        self.frame = IntVar(self)
        self.frame.set(0)
        self.action = None
    
        self.frameChangerPanel.pack()
        
        self.buttonMinus.grid(row=0,column=0)
        self.currentFrame.grid(row=0,column=1)
        self.buttonPlus.grid(row=0,column=2)
        
    def changeFrame(self,amt):
        if self.action:
            self.frame.set(self.frame.get() + amt)
            self.currentFrame.config(text=str(self.frame.get())+"/"+str(self.action.lastFrame))
            self.buttonMinus.config(state=NORMAL)
            self.currentFrame.config(state=NORMAL)
            self.buttonPlus.config(state=NORMAL)
            if self.frame.get() == 0:
                self.buttonMinus.config(state=DISABLED)
            if self.frame.get() == self.action.lastFrame:
                self.buttonPlus.config(state=DISABLED)
        else:
            self.buttonMinus.config(state=DISABLED)
            self.currentFrame.config(state=DISABLED)
            self.buttonPlus.config(state=DISABLED)
            
    def changeAction(self,*args):
        self.action = self.root.root.action
        self.frame.set(0)
        self.changeFrame(0)
        
            
"""
Action Pane is the right half of the screen, containing all of the behavior of the character
""" 
class ActionPane(Frame):
    def __init__(self,root):
        Frame.__init__(self,root)
        self.root = root
        self.actionSelectorPanel = ActionSelectorPanel(self)
        self.subactionPanel = SubactionPanel(self)
        self.subactionPropertyPanel = SubactionPropertyPanel(self)
        
        self.actionSelectorPanel.pack(fill=X)
        self.subactionPanel.pack(fill=BOTH,expand=True)
        self.subactionPropertyPanel.pack(fill=X)
        
        
"""
Action Selector Panel has the dropdowns to change the currently viewed action and group
"""
class ActionSelectorPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="purple", height=50)
        self.root = root
        
        self.currentAction = StringVar(self)
        self.currentAction.set("Fighter Properties")
        self.currentAction.trace('w', self.changeAction)
        
        self.currentGroup = StringVar(self)
        self.currentGroup.set("SetUp")
        
        
        self.actList = ['Fighter Properties']
        self.defaultGroupList = ["Properties","Set Up","Tear Down","Transitions","Before Frames","After Frames","Last Frame"] 
        self.groupList = self.defaultGroupList[:] #have to do this to copy be value instead of reference
        
        self.action = OptionMenu(self,self.currentAction,*self.actList)
        self.group = OptionMenu(self,self.currentGroup,*self.groupList)
        
    def loadFighter(self,fighter):
        self.actList = ["Fighter Properties"]
        
        if isinstance(fighter.actions, engine.actionLoader.ActionLoader):
            self.actList.extend(fighter.actions.getAllActions())
        else:
            for name,_ in inspect.getmembers(fighter.actions, inspect.isclass):
                self.actList.append(name)
        self.refreshDropdowns()
        self.currentAction.set('Fighter Properties')
        
    def changeAction(self,*args):
        if self.currentAction.get() == 'Fighter Properties':
            self.group.pack_forget()
        else:
            self.groupList = self.defaultGroupList[:]
            action = self.root.root.fighter.getAction(self.currentAction.get())
            if action:
                for i in range(0,action.lastFrame):
                    self.groupList.append('Frame '+str(i))
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
"""
Subaction Panel shows the subactions in the current group
"""
class SubactionPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="white")
        self.root = root
        
        #Create scrollbars and textfield
        self.textfield = Text(self,wrap=NONE)
        self.xscrollbar = Scrollbar(self.textfield, orient=HORIZONTAL, command=self.textfield.xview)
        self.yscrollbar = Scrollbar(self.textfield, orient=VERTICAL, command=self.textfield.yview)
        self.textfield.configure(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        
        self.subActionList = []
        
        self.showTextField()
        
        self.selected = None
        
        #The event listeners from the dropdowns in the selector panel
        self.root.actionSelectorPanel.currentAction.trace('w',self.actionChanged)
        self.root.actionSelectorPanel.currentGroup.trace('w',self.groupChanged)
        
        self.action = None
        self.group = None
        
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
        
    def actionChanged(self,*args):
        newAction = self.root.actionSelectorPanel.currentAction.get()
        self.clearSubActList()
        
        if newAction == 'Fighter Properties':
            self.showTextField()
            self.loadText(self.root.root.getFighterProperties())
        else:
            self.action = self.root.root.getFighterAction(newAction)
            self.showTextField()
            if isinstance(self.action,engine.action.DynamicAction):
                node = self.root.root.getFighterAction(newAction,True)
                self.loadText(ElementTree.tostring(node))
            else:
                self.loadText('Advanced action from '+str(self.root.root.fighter.actions))
            #self.showSubactionList()
    
    def clearSubActList(self):
        for subAct in self.subActionList:
            subAct.destroy()
        self.subActionList = []
        
    def groupChanged(self,*args):
        self.group = self.root.actionSelectorPanel.currentGroup.get()
        newAction = self.root.actionSelectorPanel.currentAction.get()
        
        if isinstance(self.action,engine.action.DynamicAction):
            self.clearSubActList()
            node = self.root.root.getFighterAction(newAction,True)
            if self.group == 'Set Up':
                for subact in self.action.setUpActions:
                    self.subActionList.append(subactionSelector.SubactionSelector(self,subact))
                #try: self.loadText(ElementTree.tostring(node.find('setUp')))
                #except: self.loadText('')
            elif self.group == 'Tear Down':
                for subact in self.action.tearDownActions:
                    self.subActionList.append(self.SubactionSelector(self,subact))
                #try: self.loadText(ElementTree.tostring(node.find('tearDown')))
                #except: self.loadText('')
            elif self.group == 'Transitions':
                for subact in self.action.stateTransitionActions:
                    self.subActionList.append(self.SubactionSelector(self,subact))
                #try: self.loadText(ElementTree.tostring(node.find('transitions')))
                #except: self.loadText('')
            elif self.group == 'Before Frames':
                for subact in self.action.actionsBeforeFrame:
                    self.subActionList.append(self.SubactionSelector(self,subact))
                #for target in node.findall("frame"):
                #    self.loadText('')
                #    if target.attrib['number'] == 'before':
                #        self.loadText(ElementTree.tostring(target))
            elif self.group == 'After Frames':
                for subact in self.action.actionsAfterFrame:
                    self.subActionList.append(self.SubactionSelector(self,subact))
                #self.loadText('')
                #for target in node.findall("frame"):
                #    if target.attrib['number'] == 'after':
                #        self.loadText(ElementTree.tostring(target))
            elif self.group == 'Last Frame':
                for subact in self.action.actionsAtLastFrame:
                    self.subActionList.append(self.SubactionSelector(self,subact))
                #self.loadText('')
                #for target in node.findall("frame"):
                #    if target.attrib['number'] == 'last':
                #        self.loadText(ElementTree.tostring(target))
            elif not self.group == 'Properties': #It's a numbered frame
                frameNo = int(self.group[6:])
                for subact in self.action.actionsAtFrame[frameNo]:
                    self.subActionList.append(self.SubactionSelector(self,subact))
                #self.loadText('')
                #for target in node.findall("frame"):
                #    if target.attrib['number'] == frameNo:
                #        self.loadText(ElementTree.tostring(target))
            self.showSubactionList()
            if self.group == 'Properties':
                self.loadText(ElementTree.tostring(node))
                self.showTextField()
        else:
            self.loadText('Advanced action from '+str(self.root.root.fighter.actions))
        
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
        
"""
Subaction Property Panel has the options for creating a subaction
"""
class SubactionPropertyPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="red",height=200)
        
        
if __name__ == '__main__': 
    BuilderWindow()