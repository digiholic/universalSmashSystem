from Tkinter import *
import settingsManager
import engine
import os
from tkFileDialog import askopenfile, askdirectory

class SubactionSelector(Label):
    def __init__(self,root,data,name=''):
        self.displayName = StringVar()
        self.displayName.set(name)
        Label.__init__(self, root.interior, textvariable=self.displayName, bg="white", anchor=W)
        self.root = root.parent
        
        self.subaction = None
        self.property = None
        
        self.propertyFrame = None
        
        self.data = data
        
        if isinstance(data, engine.subaction.SubAction):
            self.propertyFrame = data.getPropertiesPanel(self.root.parent.subactionPropertyPanel)
        else:
            self.propertyFrame = ChangeAttributeFrame(self.root.parent.subactionPropertyPanel,data)
            
        self.selected = False
        self.bind("<Button-1>", self.onclick)
        
    def onclick(self,*args):
        if self.selected:
            self.unselect()
        else:
            self.select()
        if not self.root.selected:
            self.root.selectedString.set('')
    
    def select(self):
        self.selected = True
        self.config(bg="lightblue")
        if self.root.selected:
            self.root.selected.unselect()
        self.root.selected = self
        if self.data:
            self.root.selectedString.set(str(self.data))
            
    def unselect(self):
        self.selected = False
        self.config(bg="white")
        self.root.selected = None
        
    def updateName(self,string=None):
        if string: self.displayName.set(string)
        else: self.displayName.set(self.data.getDisplayName())

class ChangeAttributeFrame(Frame):
    def __init__(self,root,attribSet):
        Frame.__init__(self,root,height=root.winfo_height())
        self.root = root
        
        self.data = []
        #attrib is in the form ('name','type',object,property)
        currentRow = 0
        for attrib in attribSet:
            name, vartype, obj, prop = attrib
            attribLabel = Label(self,text=name+':')
            if isinstance(vartype, tuple): #It's a file, and we have to unpack more stuff
                fileType,extensions = vartype
                attribVar = StringVar(self)
                attribVar.set(str(self.getFromAttrib(obj, prop)))
                attribEntry = Frame(self)
                
                fileName = Entry(attribEntry,textvariable=attribVar,state=DISABLED)
                loadFileButton = Button(attribEntry,text='...',command=lambda: self.pickFile(attribVar, vartype))
                fileName.pack(side=LEFT,fill=X)
                loadFileButton.pack(side=RIGHT)
                
            if vartype == 'string':
                attribVar = StringVar(self)
                attribVar.set(str(self.getFromAttrib(obj, prop)))
                attribEntry = Entry(self,textvariable=attribVar)
            elif vartype == 'int':
                attribVar = IntVar(self)
                attribVar.set(int(self.getFromAttrib(obj, prop)))
                attribEntry = Spinbox(self,from_=-255,to=255,textvariable=attribVar)
            elif vartype == 'float':
                attribVar = DoubleVar(self)
                attribVar.set(float(self.getFromAttrib(obj, prop)))
                attribEntry = Spinbox(self,from_=-255,to=255,textvariable=attribVar,increment=0.01,format='%.2f')
            attribLabel.grid(row=currentRow,column=0)
            attribEntry.grid(row=currentRow,column=1)
            self.data.append((attrib,attribVar))
            currentRow += 1
        
        confirmButton = Button(self,text="confirm",command=self.saveData)
        confirmButton.grid(row=currentRow,columnspan=2)
        
    def saveData(self,*args):
        for data in self.data:
            _, vartype, obj, prop = data[0]
            val = data[1].get()
            #Cast it to the proper type
            if vartype == 'string': val = str(val)
            elif vartype == 'int': val = int(val)
            elif vartype == 'float': val = float(val)
            elif vartype == 'bool': val = bool(val)
            
            self.setFromAttrib(obj, prop, val)
            
    def getFromAttrib(self,obj,prop):
        if isinstance(obj, dict):
            return obj[prop]
        else:
            return getattr(obj, prop)
    
    def setFromAttrib(self,obj,prop,val):
        if isinstance(obj, dict):
            obj[prop] = val
        else:
            setattr(obj, prop, val)
    
    def pickFile(self,resultVar,fileTuple):
        filetype,extensions = fileTuple
        if filetype == 'file':
            loadedFile = askopenfile(mode="r",
                               initialdir=settingsManager.createPath('fighters'),
                               filetypes=extensions)
        elif filetype == 'dir':
            loadedFile = askdirectory(mode="r",
                               initialdir=settingsManager.createPath())
        res = os.path.relpath(loadedFile.name,os.path.dirname(self.root.root.fighterFile.name))
        resultVar.set(res)
        
class BasePropertiesFrame(Frame):
    def __init__(self,root,subaction):
        Frame.__init__(self, root, height=root.winfo_height())
        self.root = root
        self.subaction = subaction
        self.changed = False
                
class ChangeSpriteProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root,subaction)
        
        spriteLabel = Label(self,text="Sprite:")
        self.spriteChoice = StringVar(self)
        self.spriteChoice.set(self.subaction.sprite)
        
        spriteVals = ['No Sprites found']
        if root.getFighter():
            spriteVals = root.getFighter().sprite.imageLibrary["right"].keys()
            
        sprites = OptionMenu(self,self.spriteChoice,*spriteVals)
        sprites.config(width=18)
        spriteLabel.grid(row=0,column=0)
        sprites.grid(row=0,column=1)
        self.spriteChoice.trace('w', self.changeActionSprite)
        
    def changeActionSprite(self,*args):
        self.subaction.sprite = self.spriteChoice.get()
        self.root.root.actionModified()
        
class ChangeSubimageProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root,subaction)
        
        subimageLabel = Label(self,text="Subimage:")
        self.subimageValue = IntVar(self)
        self.subimageValue.set(self.subaction.index)
        
        if root.getAction():
            subimageSpinner = Spinbox(self,from_=0,to=root.getFighter().sprite.currentAnimLength()-1,textvariable=self.subimageValue)
            
        subimageLabel.grid(row=0,column=0)
        subimageSpinner.grid(row=0,column=1)
        
        self.subimageValue.trace('w',self.changeSubimageValue)
        
    def changeSubimageValue(self,*args):
        self.subaction.index = self.subimageValue.get()
        self.root.root.actionModified()
        
class ChangePreferredSpeedProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root,subaction)
        
        xSpeedLabel = Label(self,text="Preferred X Speed:")
        ySpeedLabel = Label(self,text="Preferred Y Speed:")
        xSpeedRelative = Checkbutton(self,text="Relative?")
        
        xSpeedVariable = IntVar(self)
        xSpeedField = Spinbox(self,textvariable=xSpeedVariable)
        xSpeedField.config(width=5)
        
        ySpeedVariable = IntVar(self)
        ySpeedField = Spinbox(self,textvariable=ySpeedVariable)
        ySpeedField.config(width=5)
        
        xSpeedLabel.grid(row=0,column=0)
        xSpeedField.grid(row=0,column=1)
        xSpeedRelative.grid(row=0,column=3)
        
        ySpeedLabel.grid(row=1,column=0)
        ySpeedField.grid(row=1,column=1)
        
class ChangeSpeedProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self,root,subaction)
        
        xSpeedLabel = Label(self,text="X Speed:")
        ySpeedLabel = Label(self,text="Y Speed:")
        xSpeedRelative = Checkbutton(self,text="Relative?")
        
        xSpeedVariable = IntVar(self)
        xSpeedField = Spinbox(self,textvariable=xSpeedVariable)
        xSpeedField.config(width=5)
        
        ySpeedVariable = IntVar(self)
        ySpeedField = Spinbox(self,textvariable=ySpeedVariable)
        ySpeedField.config(width=5)
        
        xSpeedLabel.grid(row=0,column=0)
        xSpeedField.grid(row=0,column=1)
        xSpeedRelative.grid(row=0,column=3)
        
        ySpeedLabel.grid(row=1,column=0)
        ySpeedField.grid(row=1,column=1)  