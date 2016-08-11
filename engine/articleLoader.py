import os
import xml.etree.ElementTree as ElementTree
import engine.subaction as subaction
import engine.article as article
import settingsManager
from ast import literal_eval as make_tuple

class ArticleLoader():
    def __init__(self,owner):
        self.owner = owner
        self.baseDir = owner.baseDir
        xmlPath = owner.article_loader_path
        self.articlePath = owner.article_path
        if xmlPath:
            self.articlesXMLpath = os.path.join(self.baseDir,xmlPath)
            self.articlesXMLFull = ElementTree.parse(self.articlesXMLpath)
            self.articlesXML = self.articlesXMLFull.getroot()
        
    """
    Returns True if the XML data has the article of the given name.
    """
    def hasArticle(self,articleName):
        if self.articlesXML.find(articleName) is None:
            return False
        return True
    
    """
    Get a list of all articles in the XML data
    """
    def getAllArticles(self):
        ret = []
        for item in list(self.articlesXML):
            ret.append(item.tag)
        return ret
    
    """
    Save all articles to disk, defaults to original location
    """
    def saveArticles(self,path=None):
        if not path: path = self.articlesXMLpath
        self.articlesXMLFull.write(path)
        
    """
    Save a given article into the XML over the given name
    """
    def modifyArticle(self,articleName,newArticle):
        pass
    
    """
    Creates a DynamicArticle from the given XML object
    """
    def loadArticle(self,articleName):
        articleXML = self.articlesXML.find(articleName)
        
        #Check if it's a Python article
        if articleXML is not None and articleXML.find('loadCodeAction') is not None:
            fileName = articleXML.find('loadCodeAction').find('file').text
            articleName = articleXML.find('loadCodeAction').find('action').text
            newaction = settingsManager.importFromURI(os.path.join(self.baseDir,fileName), fileName)
            return getattr(newaction, articleName)()
    
        #Get the action variables
        length = int(self.loadNodeWithDefault(articleXML, 'length', 1))
        spriteName = self.loadNodeWithDefault(articleXML, 'sprite', None)
        spriteRate = int(self.loadNodeWithDefault(articleXML, 'spriteRate', 1))
        imgWidth = int(self.loadNodeWithDefault(articleXML, 'imgWidth', 0))
        drawDepth = int(self.loadNodeWithDefault(articleXML, 'drawDepth', 1))
        originPoint = make_tuple(self.loadNodeWithDefault(articleXML, 'originPoint', (0,0)))
        facingDirection = int(self.loadNodeWithDefault(articleXML, 'facingDirection', 0))
        
        #Load the SetUp subactions
        setUpActions = []
        if articleXML.find('setUp') is not None:
            for subact in articleXML.find('setUp'):
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    setUpActions.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                    
        #Load the tearDown subactions
        tearDownActions = []
        if articleXML.find('tearDown') is not None:
            for subact in articleXML.find('tearDown'):
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    tearDownActions.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
        
        actionsOnClank = []
        if articleXML.find('onClank') is not None:
            for subact in articleXML.find('onClank'):
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    actionsOnClank.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
        
        #Load all of the frames
        frames = articleXML.findall('frame')
        subactionsBeforeFrame = []
        subactionsAfterFrame = []
        subactionsAtLastFrame = []
        
        for frame in frames:
            if frame.attrib['number'] == 'before':
                for subact in frame:
                    if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                        subactionsBeforeFrame.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            if frame.attrib['number'] == 'after':
                for subact in frame:
                    if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                        subactionsAfterFrame.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            if frame.attrib['number'] == 'last':
                for subact in frame:
                    if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                        subactionsAtLastFrame.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            
        subactionsAtFrame = []
                        
        #Iterate through every frame possible (not just the ones defined)
        for frameNo in range(0,length+1):
            sublist = []
            if frames:
                for frame in frames:
                    if frame.attrib['number'] == str(frameNo): #If this frame matches the number we're on
                        for subact in frame:
                            if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                                sublist.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                                
                        frames.remove(frame) #Done with this one
                         
            subactionsAtFrame.append(sublist) #Put the list in, whether it's empty or not
        
        conditionalActions = dict()
        conds = articleXML.findall('conditional')
        for cond in conds:
            conditionalList = []
            for subact in cond:
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    conditionalList.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
            conditionalActions[cond.attrib['name']] = conditionalList
         
        #Create and populate the Dynamic Action
        dynArticle = article.DynamicArticle(self.owner, os.path.join(self.articlePath,spriteName),
                                            imgWidth, originPoint, length, spriteRate, facingDirection,
                                            drawDepth)
        
        dynArticle.actionsBeforeFrame = subactionsBeforeFrame
        dynArticle.actionsAtFrame = subactionsAtFrame
        dynArticle.actionsAfterFrame = subactionsAfterFrame
        dynArticle.actionsAtLastFrame = subactionsAtLastFrame
        dynArticle.setUpActions = setUpActions
        dynArticle.tearDownActions = tearDownActions
        dynArticle.actionsOnClank = actionsOnClank
        dynArticle.conditionalActions = conditionalActions
        if spriteName: dynArticle.spriteName = spriteName
        if spriteRate: dynArticle.baseSpriteRate = spriteRate
        
        return dynArticle
    
    """
    Helper method to load a node from XML, and default it to something if the node is not there.
    """
    @staticmethod
    def loadNodeWithDefault(node,subnode,default):
        if node is not None:
            if node.find(subnode) is not None:
                return node.find(subnode).text
            else:
                return default
        else:
            return default