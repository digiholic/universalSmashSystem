from Tkinter import *
from builderWindow import BuilderPanel
import dataSelector


class dataPanel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        
        # A list of dataLines to draw
        self.data_list = []
        
        self.scroll_frame = VerticalScrolledFrame(self,bg="blue")
        self.scroll_frame.config(width=self.winfo_width())
        
        self.selected_string = StringVar(self)
        self.selected = None
        
    def loadDataList(self):
        self.scroll_frame.pack(fill=BOTH,expand=TRUE)
        for data in self.data_list:
            data.pack(fill=X) #the data line will hide itself if it's not expanded
            

class FighterPropertiesPanel(dataPanel):
    pass
    
class Subaction_panel(BuilderPanel):
    def __init__(self,_parent,_root):
        BuilderPanel.__init__(self, _parent, _root)
        self.config(bg="blue")
        
        self.parent.action_selector_panel.current_action.trace('w',self.changeActionDropdown)
        self.parent.action_selector_panel.current_group.trace('w',self.groupChanged)
        
        self.subaction_list = []
        self.current_frame_subacts = []
        
        self.scroll_frame = VerticalScrolledFrame(self,bg="blue")
        self.scroll_frame.config(width=self.winfo_width())
        
        self.text_field = Text(self,wrap=NONE)
        self.x_scroll_bar = Scrollbar(self.text_field, orient=HORIZONTAL, command=self.text_field.xview)
        self.y_scroll_bar = Scrollbar(self.text_field, orient=VERTICAL, command=self.text_field.yview)
        self.text_field.configure(xscrollcommand=self.x_scroll_bar.set, yscrollcommand=self.y_scroll_bar.set)
        
        self.text_field.pack(fill=BOTH,expand=TRUE)
        self.y_scroll_bar.pack(side=RIGHT, fill=Y)
        self.x_scroll_bar.pack(side=BOTTOM, fill=X)
        
        self.selected_string = StringVar(self)
        self.selected = None
    
    
    """
    When displaying a modifiable subaction list instead of text,
    switch to the list.
    """
    def showSubactionList(self):
        #Show subaction selector
        self.text_field.pack_forget()
        self.y_scroll_bar.pack_forget()
        self.x_scroll_bar.pack_forget()
        
        self.scroll_frame.pack(fill=BOTH,expand=TRUE)
        for subact in self.subaction_list:
            subact.pack(fill=X)
    
    def clearSubActList(self):
        self.scroll_frame.pack_forget()
        
        for subact in self.subaction_list:
            subact.destroy()
        self.subaction_list = []
    
    def changeActionDropdown(self, *_args):
        global fighter
        
        self.unselect()
            
        new_action = self.parent.action_selector_panel.current_action.get()
        if new_action == 'Fighter Properties':
            self.parent.action_selector_panel.current_group.set('Fighter')
        else:
            self.text_field.delete("1.0", END)
            self.text_field.insert(INSERT, str(action))
    
    def refreshSubactionNames(self):
        for subact in self.subaction_list:
            subact.updateName()
            
    def groupChanged(self,*_args):
        global fighter
        global action
            
        self.group = self.parent.action_selector_panel.current_group.get()
        new_action = self.parent.action_selector_panel.current_action.get()
        
        self.unselect()
            
        self.clearSubActList()
        if self.group == "Fighter":
            name_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'name', 'Name', 'string')
            icon_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'franchise_icon_path', 'Icon', 'image')
            css_icon_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'css_icon_path', 'CSS Icon', 'image')
            scale_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter.sprite, 'scale', 'Scale', 'float')
            sprite_directory_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'sprite_directory', 'Sprite Directory', 'dir')
            sprite_prefix_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'sprite_prefix', 'Sprite Prefix', 'string')
            sprite_width_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'sprite_width', 'Sprite Width', 'int')
            default_sprite_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'default_sprite', 'Default Sprite', 'string')
            article_path_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'article_path', 'Article Path', 'dir')
            actions_panel = subactionSelector.PropertySelector(self.scroll_frame, fighter, 'action_file', 'Actions File', 'module')
            
            self.subaction_list.append(name_panel)
            self.subaction_list.append(icon_panel)
            self.subaction_list.append(css_icon_panel)
            self.subaction_list.append(scale_panel)
            self.subaction_list.append(sprite_directory_panel)
            self.subaction_list.append(sprite_prefix_panel)
            self.subaction_list.append(sprite_width_panel)
            self.subaction_list.append(default_sprite_panel)
            self.subaction_list.append(article_path_panel)
            self.subaction_list.append(actions_panel)
            
            self.showSubactionList()
        elif self.group == 'Attributes':
            for tag,val in fighter.var.iteritems():
                panel = subactionSelector.SubactionSelector(self.scroll_frame,[(tag,type(val).__name__,fighter.var,tag)],tag+': '+str(val))
                self.subaction_list.append(panel)
            
            self.showSubactionList()
        elif isinstance(action,engine.action.Action):
            subact_group = []
            if self.group == 'Set Up':
                subact_group = action.set_up_actions
            elif self.group == 'Tear Down':
                subact_group = action.tear_down_actions
            elif self.group == 'Transitions':
                subact_group = action.state_transition_actions
            elif self.group == 'Before Frames':
                subact_group = action.actions_before_frame
            elif self.group == 'After Frames':
                subact_group = action.actions_after_frame
            elif self.group == 'Last Frame':
                subact_group = action.actions_at_last_frame
            elif self.group == 'Current Frame':
                subact_group = self.current_frame_subacts
            elif self.group.startswith('Cond:'):
                subact_group = action.conditional_actions[self.group[6:]]
            
            for subact in subact_group:
                selector = subactionSelector.SubactionSelector(self.scroll_frame,subact)
                selector.subaction = subact
                selector.updateName()
                self.subaction_list.append(selector)
            
            
            self.showSubactionList()
            if self.group == 'Properties':
                pass
                """
                length_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Length','int',action,'last_frame')],'Length: '+str(action.last_frame))
                sprite_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Sprite','sprite',action,'sprite_name')],'Sprite Name: '+str(action.sprite_name))
                sprite_rate_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Sprite Rate','int',action,'sprite_rate')],'Sprite Rate: '+str(action.sprite_rate))
                loop_panel = subactionSelector.SubactionSelector(self.scroll_frame,[('Loop','bool',action,'loop')],'Loop:'+str(action.loop))
                
                self.subaction_list.append(length_panel)
                self.subaction_list.append(sprite_panel)
                self.subaction_list.append(sprite_rate_panel)
                self.subaction_list.append(loop_panel)
                
                self.showSubactionList()
                #node = self.root.getFighterAction(new_action,True)
                #self.loadText(ElementTree.tostring(node))
                #self.showTextField()
                """
                
        else:
            self.loadText('Advanced action from '+str(fighter.actions))
    
    def addSubactionPanel(self,_subact):
        selector = subactionSelector.SubactionSelector(self.scroll_frame,_subact)
        selector.updateName()
        self.subaction_list.append(selector)
        selector.pack(fill=X)
        
    def changeFrame(self, *_args):
        global frame
        
        self.unselect()
        
        self.current_frame_subacts = []
        for subact in action.actions_at_frame[frame]:
            self.current_frame_subacts.append(subact)
        if self.parent.action_selector_panel.current_group.get() == 'Current Frame':
            self.clearSubActList()
            for subact in self.current_frame_subacts:
                selector = subactionSelector.SubactionSelector(self.scroll_frame,subact)
                selector.subaction = subact
                selector.updateName()
                self.subaction_list.append(selector)
            self.showSubactionList()
            
    
    def unselect(self):
        if self.selected:
            self.selected.unselect()
            self.selected_string.set('')
            
"""
Scrolling frame, since TKinter doesn't do this for some reason.
Source: http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
"""
class VerticalScrolledFrame(Frame):
    def __init__(self, _parent, *_args, **_kw):
        Frame.__init__(self, _parent, *_args, **_kw)            
        self.parent = _parent
        
        # create a canvas object and a vertical scrollbar for scrolling it
        v_scroll_bar = Scrollbar(self, orient=VERTICAL)
        v_scroll_bar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=v_scroll_bar.set,bg="blue")
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        v_scroll_bar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(_event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(_event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return