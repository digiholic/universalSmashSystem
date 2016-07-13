from Tkinter import *
import settingsManager
import engine
import os
from tkFileDialog import askopenfile, askdirectory
import ttk

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
        
class ModifyHitboxProperties(BasePropertiesFrame):
    def __init__(self,root,subaction,newHitbox=False):
        BasePropertiesFrame.__init__(self, root, subaction)
        
        self.hitbox = root.getAction().hitboxes[self.subaction.hitboxName]
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
    
    def centerChanged(self,*args):
        print(args)
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