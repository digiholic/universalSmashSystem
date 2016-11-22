from engine.subaction import *

class changeECB(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('size','tuple','changeECB>size',(0,0)),
              NodeMap('offset','tuple','changeECB>offset',(0,0))
              ]
    
    def __init__(self,_size=[0,0],_ecbOffset=[0,0]):
        SubAction.__init__(self)
        self.size = _size
        self.offset = _ecbOffset
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _action.ecb_size = self.size
        _action.ecb_offset = self.offset
    
    def getDisplayName(self):
        return 'Modify Fighter Collision Box'
    
    @staticmethod
    def customBuildFromXml(_node):
        size = [0,0]
        ecb_offset = [0,0]
        if _node.find('size') is not None:
            size = map(int, _node.find('size').text.split(','))
        if _node.find('offset') is not None:
            ecb_offset = map(int, _node.find('offset').text.split(','))
        return changeECB(size,ecb_offset)
