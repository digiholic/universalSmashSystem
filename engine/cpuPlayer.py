import engine.baseActions as baseActions

class CPUplayer():
    def __init__(self):
        self.mode = 'duckling'
        self.keysHeld = []
        self.jump_last_frame = 0
    
    def loadGameState(self,fighter,stage,players):
        self.fighter = fighter
        self.gameState = stage
        self.players = players
        
    def getDistanceTo(self,target):
        sx,sy = self.fighter.rect.center
        tx,ty = target.rect.center
        
        return (tx - sx, ty - sy)
    
    def pressButton(self,button):
        if not button in self.keysHeld:
            self.fighter.keyPressed(button)
            self.keysHeld.append(button)
    
    def releaseButton(self,button):
        if button in self.keysHeld:
            self.fighter.keyReleased(button)
            self.keysHeld.remove(button)
            
    
    def update(self):
        """
        These modes will determine the current state of the player. Right now,
        the only mode is 'duckling' mode, where the AI will follow the player.
        """
        if self.mode == 'duckling':
            dx, dy = self.getDistanceTo(self.players[0])
            if dx < 0 and abs(dx)>abs(dy)//2:
                self.pressButton('left')
            else:
                self.releaseButton('left')
                
            if dx > 0 and abs(dx)>abs(dy)//2:
                self.pressButton('right')
            else:
                self.releaseButton('right')

            if dy < 0 and abs(dy)>abs(dx)//2 and self.jump_last_frame > 8 and self.fighter.change_y>=-1:
                self.pressButton('jump')
                self.jump_last_frame = 0
            else:
                self.releaseButton('jump')
                self.jump_last_frame += 1

            if dy > 0 and abs(dy)>abs(dx)//2 and self.fighter.grounded and not isinstance(self.fighter.current_action, baseActions.Crouch):
                self.pressButton('down')
            else:
                self.releaseButton('down')
