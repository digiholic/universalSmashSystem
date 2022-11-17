from engine.subaction import *

class deactivateArticle(SubAction):
    subact_group = 'Article'
    fields = [NodeMap('name','string','deactivateArticle','')
              ]
    
    def __init__(self,_name=''):
        SubAction.__init__(self)
        self.name = _name
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.name in _action.articles:
            _action.articles[self.name].deactivate()
    
    def getDisplayName(self):
        return 'Deactivate Article: ' + self.name
