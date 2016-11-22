from engine.subaction import *

class loadArticle(SubAction):
    subact_group = 'Article'
    fields = [NodeMap('article','string','loadArticle',None),
              NodeMap('name','string','loadArticle|name','')
              ]
    
    def __init__(self,_article=None,_name=''):
        SubAction.__init__(self)
        self.article = _article
        self.name = _name
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.article:
            _action.articles[self.name] = _actor.loadArticle(self.article)
    
    def getDisplayName(self):
        return 'Load Article: ' + self.name
