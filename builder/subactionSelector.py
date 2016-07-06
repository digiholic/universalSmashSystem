from Tkinter import *

class SubactionSelector(Label):
    def __init__(self,root,subaction):
        Label.__init__(self, root, text=subaction.getDisplayName(), bg="white", anchor=W)
        self.root = root
        
        self.subaction = subaction
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
        self.root.selectedString.set(str(self.subaction))
    
    def unselect(self):
        self.selected = False
        self.config(bg="white")
        self.root.selected = None

class BasePropertiesFrame(Frame):
    def __init__(self,root,subaction):
        Frame.__init__(self, root, height=root.winfo_height())
        self.root = root
        self.subaction = subaction
        self.changed = False
        
    def addConfirmCancel(self):
        confirmButton = Button(self,text="Confirm")
        cancelButton = Button(self,text="Cancel")
        confirmButton.pack(side="left")
        cancelButton.pack(side="left")
        
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
        print(self.spriteChoice.get())
        self.subaction.sprite = self.spriteChoice.get()
        self.root.root.actionModified()
        
class ChangeSubimageProperties(BasePropertiesFrame):
    def __init__(self,root,subaction):
        BasePropertiesFrame.__init__(self, root,subaction)
        
        subimageLabel = Label(self,text="Subimage:")
        subimageValue = IntVar(self)
        
        if root.getAction():
            subimageSpinner = Spinbox(self,from_=0,to=root.getAction().lastFrame,textvariable=subimageValue)
            
        subimageLabel.grid(row=0,column=0)
        subimageSpinner.grid(row=0,column=1)
    
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