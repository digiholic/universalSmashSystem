from engine.subaction import *

class executeCode(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('codeString', 'string', 'exec', ''),
              NodeMap('scope', 'string', 'exec|scope', 'action')]
    
    def __init__(self):
        SubAction.__init__(self)
        self.codeString = ''
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.scope == 'action':
            working_locals = {field: getattr(_action, field) for field in dir(_action)}
        elif self.scope == 'actor':
            if hasattr(_actor, 'owner'):
                working_locals = {field: getattr(_actor.owner, field) for field in dir(_actor.owner)}
            else:
                working_locals = {field: getattr(_actor, field) for field in dir(_actor)}
        elif self.scope == 'object':
            working_locals = {field: getattr(_actor, field) for field in dir(_actor)}
        elif self.scope == 'article' and hasattr(_actor, 'owner'):
            working_locals = {field: getattr(_actor, field) for field in dir(_actor)}
        elif self.scope == 'global':
            working_locals = globals()
        elif self.scope == 'battle':
            working_locals = {field: getattr(_actor.game_state, field) for field in dir(_actor.game_state)}
        elif self.scope == 'local':
            working_locals = locals()
        else:
            print(self.scope + " is not a valid scope")
            return None
        exec self.codeString in globals(), working_locals

    def getDisplayName(self):
        return 'Execute ' + self.codeString + ' in the ' + self.scope + ' scope'