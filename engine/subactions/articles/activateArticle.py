from engine.subaction import *

class activateArticle(SubAction):
    subact_group = 'Article'
    fields = [NodeMap('name','string','activateArticle','')
              ]
    
    def __init__(self,_name=''):
        SubAction.__init__(self)
        self.name = _name
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.articles.has_key(self.name):
            _action.articles[self.name].activate()
        
    def getDisplayName(self):
        return 'Activate Article: ' + self.name
