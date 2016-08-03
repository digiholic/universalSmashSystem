from Tkinter import *
import os
from tkFileDialog import askopenfile, askdirectory
import ttk
import settingsManager

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
        
        self.deleteImage = PhotoImage(file=settingsManager.createPath('sprites/icons/red-x.gif'))
        self.confirmButton = PhotoImage(file=settingsManager.createPath('sprites/icons/green-check.gif'))
        self.deleteButton = Button(self,image=self.deleteImage,command=self.deleteSubaction)
        
        import engine
        if isinstance(data, engine.subaction.SubAction):
            self.propertyFrame = data.getPropertiesPanel(self.root.parent.subactionPropertyPanel)
            self.deleteButton.pack(side=RIGHT)
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

    def deleteSubaction(self,*args):
        action = self.root.getAction()
        print(action)
        print(self.root.group)
        if self.root.group == 'Set Up':
            action.setUpActions.remove(self.subaction)
            print(action.setUpActions)
        
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
                loadFileButton = Button(attribEntry,text='...',command=lambda resultVar=attribVar,fileTuple=vartype: self.pickFile(resultVar,fileTuple))
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
            elif vartype == 'bool':
                attribVar = BooleanVar(self)
                attribVar.set(bool(self.getFromAttrib(obj, prop)))
                attribEntry = Checkbutton(self,variable=attribVar)
            elif vartype == 'sprite':
                attribVar = StringVar(self)
                attribVar.set(self.getFromAttrib(obj, prop))
                attribEntry = OptionMenu(self,attribVar,*self.root.getFighter().sprite.imageLibrary["right"].keys())
                
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
        import settingsManager
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
        self.variableList = {}
        
    def addVariable(self,varType,name):
        var = varType(self)
        self.variableList[name] = var
        
    def getVar(self,name):
        return self.variableList[name]
    
    def initVars(self):
        for (val,var) in self.variableList.iteritems():
            var.set(getattr(self.subaction,val))
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
                
    def variableChanged(self,var,varname,*args):
        setattr(self.subaction, varname, var.get())
        self.root.root.actionModified()    
    
class IfProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        #Create Variables
        self.addVariable(StringVar, 'variable')
        self.addVariable(StringVar, 'source')
        self.addVariable(StringVar, 'function')
        self.addVariable(StringVar, 'ifActions')
        self.addVariable(StringVar, 'elseActions')
        #Value is special, so they need to be made differently
        self.valueVar = StringVar(self)
        self.valueVar.set(subaction.value)
        self.valueTypeVar = StringVar(self)
        self.valueTypeVar.set(type(subaction.value).__name__)
        self.valueVar.trace('w', self.valueChanged)
        self.valueTypeVar.trace('w', self.valueChanged)
        
        variableLabel = Label(self,text="Variable:")
        sourceLabel = Label(self,text="Source:")
        valueLabel = Label(self,text="Value:")
        ifLabel = Label(self,text="Pass:")
        elseLabel = Label(self,text="Fail:")
        
        variableEntry = Entry(self,textvariable=self.getVar('variable'))
        sourceEntry = OptionMenu(self,self.getVar('source'),*['action','fighter'])
        functionEntry = OptionMenu(self,self.getVar('function'),*['==','!=','>','<','>=','<='])
        valueEntry = Entry(self,textvariable=self.valueVar)
        valueTypeEntry = OptionMenu(self,self.valueTypeVar,*['string','int','float','bool'])
        
        conditionals = ['']
        conditionals.extend(root.getAction().conditionalActions.keys())
        ifEntry = OptionMenu(self,self.getVar('ifActions'),*conditionals)
        elseEntry = OptionMenu(self,self.getVar('elseActions'),*conditionals)
        
        self.initVars()
        
        sourceLabel.grid(row=0,column=0,sticky=E)
        sourceEntry.grid(row=0,column=1,columnspan=2,sticky=E+W)
        variableLabel.grid(row=1,column=0,sticky=E)
        variableEntry.grid(row=1,column=1,sticky=E+W)
        functionEntry.grid(row=1,column=2,sticky=E+W)
        valueLabel.grid(row=2,column=0,sticky=E)
        valueEntry.grid(row=2,column=1,sticky=E+W)
        valueTypeEntry.grid(row=2,column=2,sticky=E+W)
        ifLabel.grid(row=3,column=0,sticky=E)
        ifEntry.grid(row=3,column=1,columnspan=2,sticky=E+W)
        elseLabel.grid(row=4,column=0,sticky=E)
        elseEntry.grid(row=4,column=1,columnspan=2,sticky=E+W)
            
    def valueChanged(self,*args):
        value = self.valueVar.get()
        valtype = self.valueTypeVar.get()
        if valtype == 'int': self.subaction.value = int(value)
        elif valtype == 'float': self.subaction.value = float(value)
        elif valtype == 'bool': self.subaction.value = bool(value)
        else: self.subaction.value = value
        self.root.root.actionModified()

class IfButtonProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        #Create Variables
        self.addVariable(StringVar, 'button')
        self.addVariable(BooleanVar, 'held')
        self.addVariable(IntVar, 'bufferTime')
        self.addVariable(StringVar, 'ifActions')
        self.addVariable(StringVar, 'elseActions')
        
        buttonLabel = Label(self,text="Button:")
        bufferLabel = Label(self,text="Buffer:")
        ifLabel = Label(self,text="Pass:")
        elseLabel = Label(self,text="Fail:")
        
        buttonEntry = OptionMenu(self,self.getVar('button'),*['left','right','up','down','attack','jump','special','shield'])
        heldEntry = Checkbutton(self,text="Held?",variable=self.getVar('held'))
        bufferEntry = Spinbox(self,textvariable=self.getVar('bufferTime'),from_=0,to=255)
        
        conditionals = ['']
        conditionals.extend(root.getAction().conditionalActions.keys())
        ifEntry = OptionMenu(self,self.getVar('ifActions'),*conditionals)
        elseEntry = OptionMenu(self,self.getVar('elseActions'),*conditionals)
        
        self.initVars()
        
        buttonLabel.grid(row=0,column=0,sticky=E)
        buttonEntry.grid(row=0,column=1,sticky=E+W)
        heldEntry.grid(row=0,column=2)
        bufferLabel.grid(row=1,column=0,sticky=E)
        bufferEntry.grid(row=1,column=1,columnspan=2,sticky=E+W)
        ifLabel.grid(row=2,column=0,sticky=E)
        ifEntry.grid(row=2,column=1,columnspan=2,sticky=E+W)
        elseLabel.grid(row=3,column=0,sticky=E)
        elseEntry.grid(row=3,column=1,columnspan=2,sticky=E+W)
              
class ChangeSpriteProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
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
        
class ChangeSpeedProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root,subaction)
        
        xSpeedLabel = Label(self,text="X Speed:")
        ySpeedLabel = Label(self,text="Y Speed:")
        
        self.addVariable(IntVar, 'speed_x')
        self.addVariable(IntVar, 'speed_y')
        self.addVariable(BooleanVar, 'xRelative')
        
        self.xUnchanged=BooleanVar(self)
        self.yUnchanged=BooleanVar(self)
        self.xUnchanged.set(not bool(self.subaction.speed_x))
        self.yUnchanged.set(not bool(self.subaction.speed_y))
        self.xUnchanged.trace('w', self.xUnchangedChanged)
        self.yUnchanged.trace('w', self.yUnchangedChanged)
        
        self.xSpeedEntry = Spinbox(self,textvariable=self.getVar('speed_x'),from_=-255,to=255)
        self.xSpeedEntry.config(width=4)
        self.ySpeedEntry = Spinbox(self,textvariable=self.getVar('speed_y'),from_=-255,to=255)
        self.ySpeedEntry.config(width=4)
        
        self.xSpeedRelative = Checkbutton(self,variable=self.getVar('xRelative'),text="Relative?")
        xUnchangedEntry = Checkbutton(self,variable=self.xUnchanged,text="Leave X Unchanged")
        yUnchangedEntry = Checkbutton(self,variable=self.yUnchanged,text="Leave Y Unchanged")
        
        if self.xUnchanged.get():
            self.xSpeedEntry.config(state=DISABLED)
            self.xSpeedRelative.config(state=DISABLED)
        else:
            self.xSpeedEntry.config(state=NORMAL)
            self.xSpeedRelative.config(state=NORMAL)
            
        if self.yUnchanged.get(): self.ySpeedEntry.config(state=DISABLED)
        else: self.ySpeedEntry.config(state=NORMAL)
            
        self.initVars()
        
        xUnchangedEntry.grid(row=0,column=0, columnspan=3)
        xSpeedLabel.grid(row=1,column=0,sticky=E)
        self.xSpeedEntry.grid(row=1,column=1,sticky=E+W)
        self.xSpeedRelative.grid(row=1,column=2)
        yUnchangedEntry.grid(row=2,column=0, columnspan=3)
        ySpeedLabel.grid(row=3,column=0,sticky=E)
        self.ySpeedEntry.grid(row=3,column=1,columnspan=2,sticky=E+W)
    
    def xUnchangedChanged(self,*args): #boy this function's name is silly
        if self.xUnchanged.get():
            self.xSpeedEntry.config(state=DISABLED)
            self.xSpeedRelative.config(state=DISABLED)
            self.getVar('speed_x').set(0)
            self.subaction.speed_x = None
            self.root.root.actionModified()
        else:
            self.xSpeedEntry.config(state=NORMAL)
            self.xSpeedRelative.config(state=NORMAL)
            self.subaction.speed_x = self.getVar('speed_x').get()
            self.root.root.actionModified()
    
    def yUnchangedChanged(self,*args):
        if self.yUnchanged.get():
            self.ySpeedEntry.config(state=DISABLED)
            self.getVar('speed_y').set(0)
            self.subaction.speed_y = None
            self.root.root.actionModified()
        else:
            self.ySpeedEntry.config(state=NORMAL)
            self.subaction.speed_y = self.getVar('speed_y').get()
            self.root.root.actionModified()
            
    def initVars(self):
        for (val,var) in self.variableList.iteritems():
            newval = getattr(self.subaction,val)
            if newval is None: var.set(0)
            else: var.set(newval)
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
    
    def variableChanged(self,var,varname,*args):
        print(var,var.get(),varname)
        if varname == 'speed_x' and self.xUnchanged.get(): return
        if varname == 'speed_y' and self.yUnchanged.get(): return
        setattr(self.subaction, varname, var.get())
        self.root.root.actionModified()
        
class ShiftPositionProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root,subaction)
        
        xSpeedLabel = Label(self,text="New X:")
        ySpeedLabel = Label(self,text="New Y:")
        
        self.addVariable(IntVar, 'new_x')
        self.addVariable(IntVar, 'new_y')
        self.addVariable(BooleanVar, 'xRelative')
        self.addVariable(BooleanVar, 'yRelative')
        
        self.xUnchanged=BooleanVar(self)
        self.yUnchanged=BooleanVar(self)
        self.xUnchanged.set(not bool(self.subaction.speed_x))
        self.yUnchanged.set(not bool(self.subaction.speed_y))
        self.xUnchanged.trace('w', self.xUnchangedChanged)
        self.yUnchanged.trace('w', self.yUnchangedChanged)
        
        self.xSpeedEntry = Spinbox(self,textvariable=self.getVar('new_x'),from_=-255,to=255)
        self.xSpeedEntry.config(width=4)
        self.ySpeedEntry = Spinbox(self,textvariable=self.getVar('new_y'),from_=-255,to=255)
        self.ySpeedEntry.config(width=4)
        
        self.xSpeedRelative = Checkbutton(self,variable=self.getVar('xRelative'),text="Relative?")
        self.ySpeedRelative = Checkbutton(self,variable=self.getVar('yRelative'),text="Relative?")
        xUnchangedEntry = Checkbutton(self,variable=self.xUnchanged,text="Leave X Unchanged")
        yUnchangedEntry = Checkbutton(self,variable=self.yUnchanged,text="Leave Y Unchanged")
        
        if self.xUnchanged.get():
            self.xSpeedEntry.config(state=DISABLED)
            self.xSpeedRelative.config(state=DISABLED)
        else:
            self.xSpeedEntry.config(state=NORMAL)
            self.xSpeedRelative.config(state=NORMAL)
            
        if self.yUnchanged.get():
            self.ySpeedEntry.config(state=DISABLED)
            self.ySpeedRelative.config(state=DISABLED)
        else:
            self.ySpeedEntry.config(state=NORMAL)
            self.ySpeedRelative.config(state=NORMAL)
            
        self.initVars()
        
        xUnchangedEntry.grid(row=0,column=0, columnspan=3)
        xSpeedLabel.grid(row=1,column=0,sticky=E)
        self.xSpeedEntry.grid(row=1,column=1,sticky=E+W)
        self.xSpeedRelative.grid(row=1,column=2)
        yUnchangedEntry.grid(row=2,column=0, columnspan=3)
        ySpeedLabel.grid(row=3,column=0,sticky=E)
        self.ySpeedEntry.grid(row=3,column=1,sticky=E+W)
        self.ySpeedRelative.grid(row=3,column=2)
        
    def xUnchangedChanged(self,*args): #boy this function's name is silly
        if self.xUnchanged.get():
            self.xSpeedEntry.config(state=DISABLED)
            self.xSpeedRelative.config(state=DISABLED)
            self.getVar('speed_x').set(0)
            self.subaction.speed_x = None
            self.root.root.actionModified()
        else:
            self.xSpeedEntry.config(state=NORMAL)
            self.xSpeedRelative.config(state=NORMAL)
            self.subaction.speed_x = self.getVar('speed_x').get()
            self.root.root.actionModified()
    
    def yUnchangedChanged(self,*args):
        if self.yUnchanged.get():
            self.ySpeedEntry.config(state=DISABLED)
            self.ySpeedRelative.config(state=DISABLED)
            self.getVar('speed_y').set(0)
            self.subaction.speed_y = None
            self.root.root.actionModified()
        else:
            self.ySpeedEntry.config(state=NORMAL)
            self.ySpeedRelative.config(state=NORMAL)
            self.subaction.speed_y = self.getVar('speed_y').get()
            self.root.root.actionModified()
            
    def initVars(self):
        for (val,var) in self.variableList.iteritems():
            newval = getattr(self.subaction,val)
            if newval is None: var.set(0)
            else: var.set(newval)
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
    
    def variableChanged(self,var,varname,*args):
        print(var,var.get(),varname)
        if varname == 'speed_x' and self.xUnchanged.get(): return
        if varname == 'speed_y' and self.yUnchanged.get(): return
        setattr(self.subaction, varname, var.get())
        self.root.root.actionModified()

class ShiftSpriteProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root,subaction)
        
        xSpeedLabel = Label(self,text="X Pos:")
        ySpeedLabel = Label(self,text="Y Pos:")
        
        self.addVariable(IntVar, 'new_x')
        self.addVariable(IntVar, 'new_y')
        self.addVariable(BooleanVar, 'xRelative')
        
        self.xUnchanged=BooleanVar(self)
        self.yUnchanged=BooleanVar(self)
        self.xUnchanged.set(not bool(self.subaction.new_x))
        self.yUnchanged.set(not bool(self.subaction.new_y))
        self.xUnchanged.trace('w', self.xUnchangedChanged)
        self.yUnchanged.trace('w', self.yUnchangedChanged)
        
        self.xSpeedEntry = Spinbox(self,textvariable=self.getVar('new_x'),from_=-255,to=255)
        self.xSpeedEntry.config(width=4)
        self.ySpeedEntry = Spinbox(self,textvariable=self.getVar('new_y'),from_=-255,to=255)
        self.ySpeedEntry.config(width=4)
        
        self.xSpeedRelative = Checkbutton(self,variable=self.getVar('xRelative'),text="Relative?")
        xUnchangedEntry = Checkbutton(self,variable=self.xUnchanged,text="Leave X Unchanged")
        yUnchangedEntry = Checkbutton(self,variable=self.yUnchanged,text="Leave Y Unchanged")
        
        if self.xUnchanged.get():
            self.xSpeedEntry.config(state=DISABLED)
            self.xSpeedRelative.config(state=DISABLED)
        else:
            self.xSpeedEntry.config(state=NORMAL)
            self.xSpeedRelative.config(state=NORMAL)
            
        if self.yUnchanged.get(): self.ySpeedEntry.config(state=DISABLED)
        else: self.ySpeedEntry.config(state=NORMAL)
            
        self.initVars()
        
        xUnchangedEntry.grid(row=0,column=0, columnspan=3)
        xSpeedLabel.grid(row=1,column=0,sticky=E)
        self.xSpeedEntry.grid(row=1,column=1,sticky=E+W)
        self.xSpeedRelative.grid(row=1,column=2)
        yUnchangedEntry.grid(row=2,column=0, columnspan=3)
        ySpeedLabel.grid(row=3,column=0,sticky=E)
        self.ySpeedEntry.grid(row=3,column=1,columnspan=2,sticky=E+W)
    
    def xUnchangedChanged(self,*args): #boy this function's name is silly
        if self.xUnchanged.get():
            self.xSpeedEntry.config(state=DISABLED)
            self.xSpeedRelative.config(state=DISABLED)
            self.getVar('new_x').set(0)
            self.subaction.new_x = None
            self.root.root.actionModified()
        else:
            self.xSpeedEntry.config(state=NORMAL)
            self.xSpeedRelative.config(state=NORMAL)
            self.subaction.new_x = self.getVar('new_x').get()
            self.root.root.actionModified()
    
    def yUnchangedChanged(self,*args):
        if self.yUnchanged.get():
            self.ySpeedEntry.config(state=DISABLED)
            self.getVar('new_y').set(0)
            self.subaction.new_y = None
            self.root.root.actionModified()
        else:
            self.ySpeedEntry.config(state=NORMAL)
            self.subaction.new_y = self.getVar('new_y').get()
            self.root.root.actionModified()
            
    def initVars(self):
        for (val,var) in self.variableList.iteritems():
            newval = getattr(self.subaction,val)
            if newval is None: var.set(0)
            else: var.set(newval)
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op))
    
    def variableChanged(self,var,varname,*args):
        print(var,var.get(),varname)
        if varname == 'new_x' and self.xUnchanged.get(): return
        if varname == 'new_y' and self.yUnchanged.get(): return
        setattr(self.subaction, varname, var.get())
        self.root.root.actionModified()
    
class UpdateLandingLagProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        self.addVariable(IntVar, 'newLag')
        self.addVariable(BooleanVar, 'reset')
        
        lagLabel = Label(self,text="New Lag:")
        
        lagEntry = Spinbox(self,textvariable=self.getVar('newLag'),from_=0,to=255)
        resetButton = Checkbutton(self,variable=self.getVar('reset'),text="Reset even if lower?")
        
        self.initVars()
        
        lagLabel.grid(row=0,column=0,sticky=E)
        lagEntry.grid(row=0,column=1,sticky=E+W)
        resetButton.grid(row=1,column=0,columnspan=2)

class ModifyFighterVarProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        self.addVariable(StringVar, 'attr')
        
        attrLabel = Label(self,text="Variable:")
        valueLabel = Label(self,text="Value:")
            
        self.valueVar = StringVar(self)
        self.valueTypeVar = StringVar(self)
        self.valueVar.set(subaction.val)
        self.valueTypeVar.set(type(subaction.value).__name__)
        self.valueVar.trace('w', self.valueChanged)
        self.valueTypeVar.trace('w', self.valueChanged)
        
        attrEntry = Entry(self,textvariable=self.getVar('attr'))
        valueEntry = Entry(self,textvariable=self.valueVar)
        valueTypeEntry = OptionMenu(self,self.valueTypeVar,*['string','int','float','bool'])
        
        self.initVars()
        
        attrLabel.grid(row=0,column=0,sticky=E)
        attrEntry.grid(row=0,column=1,columnspan=2,sticky=E+W)
        valueLabel.grid(row=0,column=0,sticky=E)
        valueEntry.grid(row=0,column=1,sticky=E+W)
        valueTypeEntry.grid(row=0,column=2,sticky=E+W)
        
    def valueChanged(self,*args):
        value = self.valueVar.get()
        valtype = self.valueTypeVar.get()
        if valtype == 'int': self.subaction.value = int(value)
        elif valtype == 'float': self.subaction.value = float(value)
        elif valtype == 'bool': self.subaction.value = bool(value)
        else: self.subaction.val = value
        self.root.root.actionModified()
 
class ChangeFrameProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        self.addVariable(IntVar, 'newFrame')
        self.addVariable(BooleanVar, 'relative')
        
        frameLabel = Label(self,text="Frame:")
        
        frameEntry = Spinbox(self,textvariable=self.getVar('newFrame'),from_=-255,to=255)
        relativeEntry = Checkbutton(self,variable=self.getVar('relative'),text="Relative?")
        
        self.initVars()
        
        frameLabel.grid(row=0,column=0,sticky=E)
        frameEntry.grid(row=0,column=1,sticky=E+W)
        relativeEntry.grid(row=0,column=2)
        
class TransitionProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        self.addVariable(StringVar, 'transition')
        transitionLabel = Label(self,text='Transition State:')
        import engine
        transitionEntry = OptionMenu(self,self.getVar('transition'),*engine.baseActions.stateDict.keys())
        
        self.initVars()
        
        transitionLabel.grid(row=0,column=0,sticky=E)
        transitionEntry.grid(row=0,column=1,sticky=E+W)
        
class ModifyHitboxProperties(BasePropertiesFrame):
    def __init__(self,root,subaction,newHitbox=False):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        import engine
        if root.getAction().hitboxes.has_key(self.subaction.hitboxName):
            self.hitbox = root.getAction().hitboxes[self.subaction.hitboxName]
        else: self.hitbox = engine.hitbox.Hitbox(root.getFighter(),engine.hitbox.HitboxLock())
        self.variableList = []
        
        mainFrame = ttk.Notebook(self)
        propertiesFrame = HitboxPropertiesFrame(self,newHitbox)
        damageFrame = ttk.Frame(mainFrame)
        chargeFrame = ttk.Frame(mainFrame)
        overrideFrame = ttk.Frame(mainFrame)
        autolinkFrame = ttk.Frame(mainFrame)
        funnelFrame = ttk.Frame(mainFrame)
        
        mainFrame.add(propertiesFrame,text="Properties")
        mainFrame.add(damageFrame,text="Damage")
        if isinstance(self.root.getAction(), engine.baseActions.ChargeAttack): mainFrame.add(chargeFrame,text="Charge")
        mainFrame.add(overrideFrame,text="Override")
        if isinstance(self.hitbox, engine.hitbox.AutolinkHitbox): mainFrame.add(autolinkFrame,text="Autolink")
        if isinstance(self.hitbox, engine.hitbox.FunnelHitbox): mainFrame.add(funnelFrame,text="Funnel")
        
        mainFrame.pack()
        
        """""""""""""""""""""""""""
        Build the damage Frame
        """""""""""""""""""""""""""
        damageLabel = Label(damageFrame,text="Damage:")
        bkbLabel = Label(damageFrame,text="Base Knockback:")
        kbgLabel = Label(damageFrame,text="Knockback Growth:")
        trajectoryLabel = Label(damageFrame,text="Trajectory:")
        hitstunLabel = Label(damageFrame,text="Hitstun Multiplier:")
        
        damageVar = DoubleVar(self)
        bkbVar = IntVar(self)
        kbgVar = DoubleVar(self)
        trajectoryVar = IntVar(self)
        hitstunVar = DoubleVar(self)
        
        self.variableList.append((damageVar,'damage'))
        self.variableList.append((bkbVar,'baseKnockback'))
        self.variableList.append((kbgVar,'knockbackGrowth'))
        self.variableList.append((trajectoryVar,'trajectory'))
        self.variableList.append((hitstunVar,'hitstun'))
        
        damageEntry = Spinbox(damageFrame,textvariable=damageVar,from_=0,to=255,increment=0.5,format='%.1f')
        bkbEntry = Spinbox(damageFrame,textvariable=bkbVar,from_=-255,to=255)
        kbgEntry = Spinbox(damageFrame,textvariable=kbgVar,from_=-255,to=255,increment=0.01,format='%.2f')
        trajectoryEntry = Spinbox(damageFrame,textvariable=trajectoryVar,from_=0,to=360)
        hitstunEntry = Spinbox(damageFrame,textvariable=hitstunVar,from_=0,to=255,increment=0.01,format='%.2f')
        
        damageLabel.grid(row=0,column=0,sticky=E)
        damageEntry.grid(row=0,column=1)
        bkbLabel.grid(row=1,column=0,sticky=E)
        bkbEntry.grid(row=1,column=1)
        kbgLabel.grid(row=2,column=0,sticky=E)
        kbgEntry.grid(row=2,column=1)
        trajectoryLabel.grid(row=3,column=0,sticky=E)
        trajectoryEntry.grid(row=3,column=1)
        hitstunLabel.grid(row=4,column=0,sticky=E)
        hitstunEntry.grid(row=4,column=1)
        
        """""""""""""""""""""""""""
        Build the charge Frame
        """""""""""""""""""""""""""
        chargedamageLabel = Label(chargeFrame,text="Damage/charge:")
        chargebkbLabel = Label(chargeFrame,text="Knockback/charge:")
        chargekbgLabel = Label(chargeFrame,text="Growth/charge:")
        
        chargedamageLabel.grid(row=0,column=0,sticky=E)
        chargebkbLabel.grid(row=1,column=0,sticky=E)
        chargekbgLabel.grid(row=2,column=0,sticky=E)
        
        
        """""""""""""""""""""""""""
        Build the override Frame
        """""""""""""""""""""""""""
        
        
        
        #Create the variable tracers
        for (var,val) in self.variableList:
            print(var,val)
            var.set(self.populateHitboxVariable(val))
            var.trace('w',lambda name1, name2, op, variable=var, varname=val: self.variableChanged(variable, varname, name1, name2, op,))
            
    def populateHitboxVariable(self,variable):
        if self.subaction.hitboxVars.has_key(variable):
            return self.subaction.hitboxVars[variable]
        else: return getattr(self.hitbox,variable)
    
    def variableChanged(self,var,varname,*args):
        print(var,varname)
        hitboxVars = {varname: var.get()}
        self.subaction.hitboxVars.update(hitboxVars)
        self.root.root.actionModified()
    
"""""""""""""""""""""""""""
Build the properties Frame
"""""""""""""""""""""""""""
class HitboxPropertiesFrame(ttk.Frame):
    def __init__(self, parent, newHitbox=False):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        
        self.subaction = parent.subaction
        self.hitbox = parent.hitbox
        
        nameLabel = Label(self,text="Hitbox Name:")
        typeLabel = Label(self,text="Type:")
        centerLabel = Label(self,text="Center:")
        sizeLabel = Label(self,text="Size:")
        lockLabel = Label(self,text="Lock:")
        
        self.hitboxName = StringVar(self)
        self.hitboxType = StringVar(self)
        self.hitboxLock = StringVar(self)
        self.centerX = IntVar(self)
        self.centerY = IntVar(self)
        self.sizeX = IntVar(self)
        self.sizeY = IntVar(self)
        
        self.hitboxName.set(self.subaction.hitboxName)
        self.hitboxType.set(self.hitbox.hitboxType)
        self.hitboxLock.set(self.hitbox.hitbox_lock.lockName)
        
        self.name = self.hitboxName.get()
        
        center = self.populateHitboxVariable('center')
        self.centerX.set(center[0])
        self.centerY.set(center[1])
        size = self.populateHitboxVariable('size')
        self.sizeX.set(size[0])
        self.sizeY.set(size[1])
        
        if newHitbox:
            hitboxTypes = ['damage','sakurai','autolink','funnel','grab','reflector']
            
            nameEntry = Entry(self,textvariable=self.hitboxName)
            typeEntry = OptionMenu(self,self.hitboxType,*hitboxTypes)
            lockEntry = Entry(self,textvariable=self.hitboxLock)
        else:
            hitboxVals = ['No Hitboxes found']
            if parent.root.getAction():
                hitboxVals = parent.root.getAction().hitboxes.keys()
                
            nameEntry = OptionMenu(self,self.hitboxName,*hitboxVals)
            typeEntry = Entry(self,textvariable=self.hitboxType,state=DISABLED)
            lockEntry = Entry(self,textvariable=self.hitboxLock,state=DISABLED)
        
        self.hitboxName.trace('w',self.nameChanged)
        self.hitboxType.trace('w',self.typeChanged)
        self.hitboxLock.trace('w',self.lockChanged)
        
        centerXEntry = Spinbox(self,from_=-255,to=255,textvariable=self.centerX,width=4)
        centerYEntry = Spinbox(self,from_=-255,to=255,textvariable=self.centerY,width=4)
        sizeXEntry = Spinbox(self,from_=-255,to=255,textvariable=self.sizeX,width=4)
        sizeYEntry = Spinbox(self,from_=-255,to=255,textvariable=self.sizeY,width=4)
        
        self.centerX.trace('w',self.centerChanged)
        self.centerY.trace('w',self.centerChanged)
        self.sizeX.trace('w',self.sizeChanged)
        self.sizeY.trace('w',self.sizeChanged)
        
        nameLabel.grid(row=0,column=0,sticky=E)
        nameEntry.grid(row=0,column=1,columnspan=2,sticky=E+W)
        typeLabel.grid(row=1,column=0,sticky=E)
        typeEntry.grid(row=1,column=1,columnspan=2,sticky=E+W)
        lockLabel.grid(row=2,column=0,sticky=E)
        lockEntry.grid(row=2,column=1,columnspan=2,sticky=E+W)
        centerLabel.grid(row=3,column=0,sticky=E)
        centerXEntry.grid(row=3,column=1)
        centerYEntry.grid(row=3,column=2)
        sizeLabel.grid(row=4,column=0,sticky=E)
        sizeXEntry.grid(row=4,column=1)
        sizeYEntry.grid(row=4,column=2)
    
    def nameChanged(self,*args):
        oldName = self.name
        newName = self.hitboxName.get()
        self.name = newName
        self.subaction.hitboxName = newName
        
        #we need something in the action so that we can select it from a dropdown later
        if not self.parent.root.getAction().hitboxes.has_key(newName): #Set our working Hitbox to the action
            self.parent.root.getAction().hitboxes[newName] = self.hitbox
        if self.parent.root.getAction().hitboxes.has_key(oldName): #Set it to the Old one if it exists
            self.parent.root.getAction().hitboxes[newName] = self.parent.root.getAction().hitboxes[oldName]
            del(self.parent.root.getAction().hitboxes[oldName])
        self.parent.root.root.actionModified()
        
    def typeChanged(self,*args):
        newType = self.hitboxType.get()
        self.subaction.hitboxType = newType
        self.parent.root.root.actionModified()
        
    def lockChanged(self,*args):
        newLock = self.hitboxLock.get()
        self.subaction.hitboxLock = newLock
        self.parent.root.root.actionModified()
        
    def centerChanged(self,*args):
        center = (self.centerX.get(),self.centerY.get())
        hitboxVars = {"center": center}
        self.subaction.hitboxVars.update(hitboxVars)
        self.parent.root.root.actionModified()
        
    def sizeChanged(self,*args):
        size = (self.sizeX.get(),self.sizeY.get())
        hitboxVars = {"size": size}
        self.subaction.hitboxVars.update(hitboxVars)
        self.parent.root.root.actionModified()
        
    def populateHitboxVariable(self,variable):
        if self.subaction.hitboxVars.has_key(variable):
            return self.subaction.hitboxVars[variable]
        else: return getattr(self.hitbox,variable)
        
class UpdateHitboxProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        self.addVariable(StringVar, 'hitboxName')
        
        hitboxVals = ['No Hitboxes found']
        if root.getAction():
            hitboxVals = root.getAction().hitboxes.keys()
        
        hitboxLabel = Label(self,text="Hitbox:")
        hitboxEntry = OptionMenu(self,self.getVar('hitboxName'),*hitboxVals)
        
        self.initVars()
        
        hitboxLabel.grid(row=0,column=0,sticky=E)
        hitboxEntry.grid(row=0,column=1,sticky=E+W)
