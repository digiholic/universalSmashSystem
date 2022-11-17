from engine.subaction import *

class ifButton(SubAction):
    subact_group = 'Control'
    
    def __init__(self,_button='',_check='keyBuffered',_bufferFrom=0,_bufferTo=0,_threshold=0.1,_ifActions='',_elseActions='',_beyondAction=False):
        SubAction.__init__(self)
        self.button = _button
        self.check = _check
        self.buffer_from = _bufferFrom
        self.buffer_to = _bufferTo
        self.threshold = _threshold
        self.if_actions = _ifActions
        self.else_actions = _elseActions
        self.beyond_action = _beyondAction
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.button == '': return
        if self.button == 'forward': 
            key, invkey = _actor.getForwardBackwardKeys()
            working_button = key
        elif self.button == 'backward':
            key, invkey = _actor.getForwardBackwardKeys()
            working_button = invkey
        else:
            working_button = self.button

        if self.beyond_action:
            working_from = self.buffer_from
        else:
            working_from = max(min(_actor.last_input_frame, self.buffer_from), 1)
        
        if self.check == 'keysContain':
            cond = _actor.keysContain(working_button, self.threshold)
        elif self.check == 'keyBuffered':
            cond = _actor.keyBuffered(working_button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyTapped':
            cond = _actor.keyTapped(working_button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyHeld':
            cond = _actor.keyHeld(working_button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyUp':
            cond = _actor.keyUp(working_button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyReinput':
            cond = _actor.keyReinput(working_button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyIdle':
            cond = _actor.keyIdle(working_button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'smash':
            cond = _actor.checkSmash(working_button)
        elif self.check == 'tap':
            cond = _actor.checkTap(working_button)
        else:
            return

        if cond:
            if self.if_actions and self.if_actions in _action.events:
                for act in _action.events[self.if_actions]:
                    act.execute(_action,_actor)
        else:
            if self.else_actions and self.else_actions in _action.events:
                for act in _action.events[self.else_actions]:
                    act.execute(_action,_actor)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.IfButtonProperties(_root,self)
    
    def getDisplayName(self):
        if self.check == 'keysContain':
            pressed_text = 'is pressed to a depth of at least ' + str(self.threshold)
        elif self.check == 'keyBuffered':
            pressed_text = 'was pressed to a depth of at least ' + str(self.threshold) + ' between frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyTapped':
            pressed_text = 'was tapped to a depth of at least ' + str(self.threshold) + ' within frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyHeld':
            pressed_text = 'was held to a depth of at least ' + str(self.threshold) + ' through frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyUp':
            pressed_text = 'was released from a depth of at least ' + str(self.threshold) + ' between frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyReinput':
            pressed_text = 'was released and reinput from a depth of at least ' + str(self.threshold) + ' within frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyIdle':
            pressed_text = 'was released from a depth of at least ' + str(self.threshold) + ' through frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'smash':
            pressed_text = 'was smashed'
        elif self.check == 'tap':
            pressed_text = 'was tapped'
        else:
            return 'Unknown check type: ' + self.check

        if self.beyond_action:
            pressed_text += ':'
        else:
            pressed_text += ' during this action:'
            
        return 'If '+self.button+' '+pressed_text+self.if_actions
    
    def getXmlElement(self):
        elem = ElementTree.Element('ifButton')
        
        button_elem = ElementTree.Element('button')
        
        check_elem = ElementTree.Element('check')
        check_elem.text = self.check
        elem.append(check_elem)
        
        from_elem = ElementTree.Element('from')
        from_elem.text = str(self.buffer_from)
        if self.beyond_action: from_elem.attrib['beyondAction'] = 'True'
        elem.append(from_elem)
        
        to_elem = ElementTree.Element('to')
        to_elem.text = str(self.buffer_to)
        elem.append(to_elem)
        
        threshold_elem = ElementTree.Element('threshold')
        threshold_elem.text = str(self.threshold)
        elem.append(threshold_elem)
        
        if self.if_actions:
            pass_elem = ElementTree.Element('pass')
            pass_elem.text = self.if_actions
            elem.append(pass_elem)
        if self.else_actions:
            fail_elem = ElementTree.Element('fail')
            fail_elem.text = self.else_actions
            elem.append(fail_elem)
        
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        button = _node.find('button')
        if 'check' in button.attrib:
            check = button.attrib['check']
        else: check = 'keyBuffered'
        button = button.text
        buffer_from = int(loadNodeWithDefault(_node, 'from', 1))
        buffer_to = int(loadNodeWithDefault(_node, 'to', 0))
        threshold = float(loadNodeWithDefault(_node, 'threshold', 0.1))
        
        if_actions = loadNodeWithDefault(_node, 'pass', None)
        else_actions = loadNodeWithDefault(_node, 'fail', None)
        
        return ifButton(button, check, buffer_from, buffer_to, threshold, if_actions, else_actions, 'beyondAction' in _node.attrib)
