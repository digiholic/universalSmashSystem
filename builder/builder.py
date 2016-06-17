import pygame
import settingsManager
import inspect
import sys
import os
import engine.baseActions
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
        
        self.viewerPane = ViewerPane(self)
        self.actionPane = ActionPane(self)
        
        self.viewerPane.grid(row=0,column=0,sticky=N+S+E+W)
        self.actionPane.grid(row=0,column=1,sticky=N+S+E+W)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3, uniform="column")
        self.grid_columnconfigure(1, weight=2, uniform="column")
        
        self.fighter = None
        
        self.mainloop()
        
    def loadFighter(self,fighterFile):
        dirname, fname = os.path.split(fighterFile.name)
        if fighterFile.name.endswith('.py'):
            fighter = settingsManager.importFromURI(fighterFile, fighterFile.name, True)
            self.fighter = fighter.Fighter(dirname,0)
        else:
            self.fighter = AbstractFighter(dirname,0)
        
        self.fighter.initialize()
        self.viewerPane.ViewerPanel.loadFighter(self.fighter)
        
        #Load the fighter.xml in the side pane
        self.actionPane.subactionPanel.loadText(fighterFile.read())
        
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
        if fighterFile.name.endswith('.py'):
            showinfo('Advanced mode warning','Legacy Editor cannot edit Advanced Mode (.py) fighter files. The fighter will be opened in read-only mode. Depending on the fighter, there may be inconsistencies with behavior in-game compared to what you view here.')
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
        self.ViewerPanel = ViewerPanel(self)
        self.NavigatorPanel = NavigatorPanel(self)
        
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
        
        self.fighter = None
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
            self.fighter.draw(self.screen, self.fighter.rect.topleft, self.scale)
        
        pygame.display.flip()
        
        self.after(5, self.game_loop)
    
    def loadFighter(self,fighter):
        self.fighter = fighter
        self.root.root.wm_title('Legacy Editor - '+self.fighter.name)
        self.fighter.rect.centerx = self.screen.get_rect().centerx + self.center[0]
        self.fighter.rect.centery = self.screen.get_rect().centery + self.center[1]
            
"""
Navigator Panel contains the controls to step through the action
"""
class NavigatorPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="white",height=50)

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
        
        currentAction = StringVar(self)
        currentAction.set("Fighter Properties")
        actList = []
        for name,_ in inspect.getmembers(engine.baseActions, inspect.isclass):
            actList.append(name)
        
        action = OptionMenu(self,currentAction,*actList)
        action.config(width=15)
        
        currentGroup = StringVar(self)
        currentGroup.set("SetUp")
        groupList = ["SetUp","TearDown","Transitions","Before Frames","After Frames","Last Frame"]
        group = OptionMenu(self,currentGroup,*groupList)
        group.config(width=15)
        
        action.pack(side=LEFT)
        group.pack(side=LEFT)

"""
Subaction Panel shows the subactions in the current group
"""
class SubactionPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="blue")
        self.root = root
        
        self.textfield = Text(self,wrap=NONE)
        
        self.xscrollbar = Scrollbar(self.textfield, orient=HORIZONTAL, command=self.textfield.xview)
        self.yscrollbar = Scrollbar(self.textfield, orient=VERTICAL, command=self.textfield.yview)
        
        self.textfield.configure(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        
        self.textfield.pack(fill=BOTH,expand=True)
        self.yscrollbar.pack(side=RIGHT, fill=Y)
        self.xscrollbar.pack(side=BOTTOM, fill=X)
        
    def loadText(self,text):
        act = self.xmlToActions(text)
        self.textfield.insert(INSERT, act)
    
    def xmlToActions(self,xml):
        root = ElementTree.fromstring(xml)
        text = ""
        for child in list(root):
            text += child.tag+': '
            if len(list(child)) > 0: #It has child nodes
                if len(child.attrib) > 0: #if it has attributes
                    text += '('
                    for name,atr in child.attrib.iteritems():
                        text+=name+': '+str(atr)
                        text+=','
                    text = text[:-1] #chop off the last comma
                    text += ')'
                text += '\n'
                for subchild in child:
                    text += '  '+subchild.tag+': '
                    text += subchild.text if subchild.text is not None else '' 
                    if len(subchild.attrib) > 0: #if it has attributes
                        text += '('
                        for name,atr in subchild.attrib.iteritems():
                            text+=name+': '+str(atr)
                            text+=','
                        text = text[:-1] #chop off the last comma
                        text += ')'
                    text += '\n'
            else:
                text += child.text if child.text is not None else ''
                if len(child.attrib) > 0: #if it has attributes
                    text += '('
                    for name,atr in child.attrib.iteritems():
                        text+=name+': '+str(atr)
                        text+=','
                    text = text[:-1] #chop off the last comma
                    text += ')'
                text += '\n'
        return text
"""
Subaction Property Panel has the options for creating a subaction
"""
class SubactionPropertyPanel(Frame):
    def __init__(self,root):
        Frame.__init__(self,root, bg="red",height=200)
        
        
if __name__ == '__main__': 
    BuilderWindow()
    """
    root = Tk()
    root.geometry('640x480')
    
    #Begin defining left frame areas
    leftFrame = Frame(root)
    
    grayPanel = Frame(leftFrame,bg="gray")
    whitePanel = Frame(leftFrame,bg="white", height=50)
    grayPanel.pack(expand=True,fill=BOTH)
    whitePanel.pack(fill=X)
    
    #Begin defining right frame areas
    rightFrame = Frame(root)
    
    purplePanel = Frame(rightFrame,bg="purple", height=50)
    bluePanel = Frame(rightFrame,bg="blue")
    redPanel = Frame(rightFrame,bg="red", height=100)
    
    purplePanel.pack(fill=X)
    bluePanel.pack(expand=True,fill=BOTH)
    redPanel.pack(fill=X)
    
    #create the options dropdown for purple
    currentOption = StringVar(purplePanel)
    currentOption.set("None")
    optList = ["None","Some incredibly long string that breaks everything"]
    options = OptionMenu(purplePanel,currentOption,*optList)
    options.pack(side=LEFT)
    
    
    leftFrame.grid(row=0,column=0,sticky=N+S+E+W)
    rightFrame.grid(row=0,column=1,sticky=N+S+E+W)
    
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=3)
    root.grid_columnconfigure(1, weight=2)
    
    root.mainloop()
    """