import os
import xml.etree.ElementTree as ElementTree
import engine.subaction as subaction
import engine.article as article
import settingsManager
from ast import literal_eval as make_tuple

class ArticleLoader():
    def __init__(self,_owner):
        self.owner = _owner
        self.base_dir = _owner.base_dir
        xml_path = _owner.article_loader_path
        self.article_path = _owner.article_path
        if xml_path:
            self.articles_xml_path = os.path.join(self.base_dir,xml_path)
            self.articles_xml_full = ElementTree.parse(self.articles_xml_path)
            self.articles_xml = self.articles_xml_full.getroot()
        
    """
    Returns True if the XML data has the article of the given name.
    """
    def hasArticle(self,_articleName):
        if self.articles_xml.find(_articleName) is None:
            return False
        return True
    
    """
    Get a list of all articles in the XML data
    """
    def getAllArticles(self):
        ret = []
        for item in list(self.articles_xml):
            ret.append(item.tag)
        return ret
    
    """
    Save all articles to disk, defaults to original location
    """
    def saveArticles(self,_path=None):
        if not _path: _path = self.articles_xml_path
        self.articles_xml_full.write(_path)
        
    """
    Save a given article into the XML over the given name
    """
    def modifyArticle(self,_articleName,_newArticle):
        pass
    
    """
    Creates a DynamicArticle from the given XML object
    """
    def loadArticle(self,_articleName):
        article_xml = self.articles_xml.find(_articleName)
        
        #Check if it's a Python article
        if article_xml is not None and article_xml.find('loadCodeAction') is not None:
            file_name = article_xml.find('loadCodeAction').find('file').text
            article_name = article_xml.find('loadCodeAction').find('action').text
            new_action = settingsManager.importFromURI(os.path.join(self.base_dir,file_name), file_name)
            return getattr(new_action, article_name)()
    
        #Get the action variables
        length = int(self.loadNodeWithDefault(article_xml, 'length', 1))
        sprite_name = self.loadNodeWithDefault(article_xml, 'sprite', None)
        sprite_rate = int(self.loadNodeWithDefault(article_xml, 'sprite_rate', 1))
        img_width = int(self.loadNodeWithDefault(article_xml, 'img_width', 0))
        draw_depth = int(self.loadNodeWithDefault(article_xml, 'draw_depth', 1))
        origin_point = make_tuple(self.loadNodeWithDefault(article_xml, 'origin_point', '(0,0)'))
        facing_direction = int(self.loadNodeWithDefault(article_xml, 'facing_direction', 0))
        
        #Load the SetUp subactions
        set_up_actions = []
        if article_xml.find('setUp') is not None:
            for subact in article_xml.find('setUp'):
                if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    set_up_actions.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
                    
        #Load the tearDown subactions
        tear_down_actions = []
        if article_xml.find('tearDown') is not None:
            for subact in article_xml.find('tearDown'):
                if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    tear_down_actions.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
        
        actions_on_clank = []
        if article_xml.find('onClank') is not None:
            for subact in article_xml.find('onClank'):
                if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    actions_on_clank.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
        
        #Load all of the frames
        frames = article_xml.findall('frame')
        subactions_before_frame = []
        subactions_after_frame = []
        subactions_at_last_frame = []
        
        for frame in frames:
            if frame.attrib['number'] == 'before':
                for subact in frame:
                    if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        subactions_before_frame.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
            if frame.attrib['number'] == 'after':
                for subact in frame:
                    if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        subactions_after_frame.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            if frame.attrib['number'] == 'last':
                for subact in frame:
                    if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        subactions_at_last_frame.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            
        subactions_at_frame = []
                        
        #Iterate through every frame possible (not just the ones defined)
        for frame_number in range(0,length+1):
            sublist = []
            if frames:
                for frame in frames:
                    if frame.attrib['number'] == str(frame_number): #If this frame matches the number we're on
                        for subact in frame:
                            if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                                sublist.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
                                
                        frames.remove(frame) #Done with this one
                         
            subactions_at_frame.append(sublist) #Put the list in, whether it's empty or not
        
        conditional_actions = dict()
        conds = article_xml.findall('conditional')
        for cond in conds:
            conditional_list = []
            for subact in cond:
                if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    conditional_list.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
            conditional_actions[cond.attrib['name']] = conditional_list
         
         
        collision_actions = dict()
        collisions = article_xml.findall('collision')
        for col in collisions:
            collision_list = []
            for subact in col:
                if subaction.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    collision_list.append(subaction.subaction_dict[subact.tag].buildFromXml(subact))
            collision_actions[col.attrib['other']] = collision_list
        
        #Create and populate the Dynamic Action
        dyn_article = article.DynamicArticle(self.owner, os.path.join(self.article_path,sprite_name),
                                             img_width, origin_point, length, sprite_rate, facing_direction,
                                             draw_depth)
        
        dyn_article.actions_before_frame = subactions_before_frame
        dyn_article.actions_at_frame = subactions_at_frame
        dyn_article.actions_after_frame = subactions_after_frame
        dyn_article.actions_at_last_frame = subactions_at_last_frame
        dyn_article.set_up_actions = set_up_actions
        dyn_article.tear_down_actions = tear_down_actions
        dyn_article.actions_on_clank = actions_on_clank
        dyn_article.conditional_actions = conditional_actions
        dyn_article.collision_actions = collision_actions
        if sprite_name: dyn_article.sprite_name = sprite_name
        if sprite_rate: dyn_article.base_sprite_rate = sprite_rate
        
        return dyn_article
    
    """
    Helper method to load a node from XML, and default it to something if the node is not there.
    """
    @staticmethod
    def loadNodeWithDefault(_node,_subnode,_default):
        if _node is not None:
            if _node.find(_subnode) is not None:
                return _node.find(_subnode).text
            else:
                return _default
        else:
            return _default
