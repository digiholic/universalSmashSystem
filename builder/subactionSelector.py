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
    
    def select(self):
        self.selected = True
        self.config(bg="lightblue")
        if self.root.selected:
            self.root.selected.unselect()
        self.root.selected = self
    
    def unselect(self):
        self.selected = False
        self.config(bg="white")
        self.root.selected = None