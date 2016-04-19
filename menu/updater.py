import requests
import json
import hashlib
import os
import sys
import filecmp
import settingsManager
import githash

from cStringIO import StringIO

from fileinput import filename

def githash(data,size=-1):
    if size == -1:
        size = len(data)
    s = hashlib.sha1()
    s.update("blob %u\0" % size)
    s.update(data)
    return s.hexdigest()

def files(path):
    for file in os.listdir(path):
        if not file.startswith('.'):
            if os.path.isfile(os.path.join(path, file)):
                yield file

def getDirectories(path):
    return [os.path.join(path,x) for x in next(os.walk(path))[1] if x.startswith('.') == False]

class Updater():
    def __init__(self):
        self.changedList = []
        self.base_url = 'https://api.github.com/repos/digiholic/universalSmashSystem/contents/'
        self.upcomingDirs = ['']
        self.currentDirectory = None
        self.json_content = None
        self.done = False
    
    def buildNextList(self):
        if self.currentDirectory:
            self.upcomingDirs.remove(self.currentDirectory)
        
        if self.upcomingDirs:    
            self.currentDirectory = self.upcomingDirs[0]
            r = requests.get(self.base_url+self.currentDirectory)
            self.json_content = json.loads(r.content)
            
            if isinstance(self.json_content, dict) and self.json_content.has_key('documentation_url'):
                return -1
            return 1
        return 0
    
    def update(self):
        if not self.json_content:
            status = self.buildNextList()
            if status == -1:
                self.done = True
                return 'API Access error. Too many connections within 60 minutes. Please wait and try again or update manually.'
            if status == 0:
                self.done = True
                return 'Completed'
            
        obj = self.json_content[0]    
        if obj["type"] == "dir":
            self.upcomingDirs.append(self.currentDirectory+'/'+str(obj['name']))
        else:
            filepath = os.path.join(settingsManager.createPath(self.currentDirectory),obj['name'])
            try:
                with open(filepath,'r') as f:
                    filesha = githash(f.read())
            except:
                #We don't have a local copy of the file
                filesha = ''
            if not filesha == obj['sha']: 
                self.changedList.append(self.currentDirectory+'/'+str(obj['name']))
        
        self.json_content.remove(obj)
        return obj['name']
        

def getChangedList():
    changedList = []
    
    base_url = 'https://api.github.com/repos/digiholic/universalSmashSystem/contents/'
    upcomingDirs = ['']
    
    while upcomingDirs:
        directory = upcomingDirs[0]
        print(directory)
        r = requests.get(base_url+directory)
        json_content = json.loads(r.content)
        if isinstance(json_content, dict) and json_content.has_key('documentation_url'):
            print('API Access error. Too many connections within 60 minutes. Please wait and try again or update manually.')
            return []
        
        for obj in json_content:
            if obj["type"] == "dir":
                upcomingDirs.append(directory+'/'+str(obj['name']))
                
            else:
                filepath = os.path.join(settingsManager.createPath(directory),obj['name'])
                try:
                    with open(filepath,'r') as f:
                        filesha = githash(f.read())
                except:
                    #We don't have a local copy of the file
                    filesha = ''
                if not filesha == obj['sha']: 
                    changedList.append(directory+'/'+str(obj['name']))
        
        upcomingDirs.remove(directory)
    
    return changedList
  
    
def downloadUpdates(changedList):
    base_url = 'https://raw.githubusercontent.com/digiholic/universalSmashSystem/master/'
    base_dir = settingsManager.createPath('')
    
    for changedfile in changedList:
        print(changedfile)
        r = requests.get(base_url + changedfile)
        if r.status_code == 200:
            with open(base_dir+changedfile,'r+') as f:
                if f.read() == r.content:
                    print('files are the same')
                else:
                    pass
                    #f.seek(0)
                    #f.write(r.content)
                    #f.truncate()

def main():
    changedList = getChangedList()
    print(changedList)
    changedList = ['/controller_test.py', '/full Pack 2025.ttf', '/rexlia rg.ttf', '/setup.py', '/spriteManager.py', '/builder/__init__.py', '/builder/builder.py', '/engine/__init__.py', '/engine/abstractFighter.py', '/engine/action.py', '/engine/article.py', '/engine/baseActions.py', '/engine/basicFighter.py', '/engine/controller.py', '/engine/cpuPlayer.py', '/engine/hitbox.py', '/engine/stage.py', '/engine/subaction.py', '/engine/vector2D.py', '/fighters/__init__.py', '/menu/__init__.py', '/menu/css.py', '/menu/mainMenu.py', '/menu/sss.py', '/menu/updater.py', '/music/Character Lobby.ogg', '/music/Laszlo - Imaginary Friends.ogg', '/music/The Void - Lost Language (Original Edit).ogg', '/settings/gamepads.ini', '/settings/settings.ini', '/sfx/selectL.wav', '/sfx/selectR.wav', '/sprites/bottomshutter_wip.png', '/sprites/circlepuff.png', '/sprites/cssbar_shadow.png', '/sprites/default_franchise_icon.png', '/sprites/exit_button.png', '/sprites/guisheet.png', '/sprites/halfcirclepuff.png', '/sprites/icon_unknown.png', '/sprites/joyTest.png', '/sprites/logo-bluebg-square.png', '/sprites/logo-bluebg.png', '/sprites/logo-wip.png', '/sprites/melee_shield.png', '/sprites/menu_button.png', '/sprites/modules_button.png', '/sprites/options_button.png', '/sprites/shield_bubble.png', '/sprites/star.png', '/sprites/topshutter_wip.png', '/sprites/tussle_button.png', '/stages/__init__.py', '/fighters/hitboxie/__init__.py', '/fighters/hitboxie/actions.txt~', '/fighters/hitboxie/fighter.py', '/fighters/hitboxie/franchise_icon.png', '/fighters/hitboxie/hitboxie.py', '/fighters/hitboxie/hitboxie_actions.py', '/fighters/sandbag/__init__.py', '/fighters/sandbag/fighter.py', '/fighters/sandbag/sandbag_actions.py', '/settings/rules/custom.ini', '/settings/rules/default.ini', '/stages/arena/__init__.py', '/stages/arena/stage.py', '/stages/arena_moving_platform/__init__.py', '/stages/arena_moving_platform/stage.py', '/stages/training_stage/__init__.py', '/stages/training_stage/stage.py', '/stages/treehouse/__init__.py', '/stages/treehouse/stage.py', '/stages/true_arena/__init__.py', '/stages/true_arena/stage.py', '/fighters/hitboxie/sprites/hitboxie_airjump.png', '/fighters/hitboxie/sprites/hitboxie_bair.png', '/fighters/hitboxie/sprites/hitboxie_bthrow.png', '/fighters/hitboxie/sprites/hitboxie_dair.png', '/fighters/hitboxie/sprites/hitboxie_dsmash.png', '/fighters/hitboxie/sprites/hitboxie_dtilt.png', '/fighters/hitboxie/sprites/hitboxie_fair.png', '/fighters/hitboxie/sprites/hitboxie_fsmash.png', '/fighters/hitboxie/sprites/hitboxie_getup.png', '/fighters/hitboxie/sprites/hitboxie_idle.png', '/fighters/hitboxie/sprites/hitboxie_jump.png', '/fighters/hitboxie/sprites/hitboxie_land.png', '/fighters/hitboxie/sprites/hitboxie_nair.png', '/fighters/hitboxie/sprites/hitboxie_neutral.png', '/fighters/hitboxie/sprites/hitboxie_nspecial.png', '/fighters/hitboxie/sprites/hitboxie_pivot.png', '/fighters/hitboxie/sprites/hitboxie_run.png', '/fighters/hitboxie/sprites/hitboxie_uair.png', '/fighters/hitboxie/sprites/hitboxie_usmash.png', '/fighters/hitboxie/sprites/hitboxie_utilt.png', '/fighters/hitboxie/sprites/icon_hitboxie.png', '/fighters/hitboxie/sprites/shield-bubble.png', '/fighters/sandbag/sprites/icon_sandbag.png', '/fighters/sandbag/sprites/sandbag.png', '/stages/arena/music/Autumn Warriors.ogg', '/stages/arena/music/Laszlo - Fall To Light.ogg', '/stages/arena/sprites/ArenaBack.png', '/stages/arena/sprites/ArenaFront.png', '/stages/arena/sprites/ArenaPlatBackL.png', '/stages/arena/sprites/ArenaPlatBackM.png', '/stages/arena/sprites/ArenaPlatBackR.png', '/stages/arena/sprites/ArenaPlatFrontL.png', '/stages/arena/sprites/ArenaPlatFrontM.png', '/stages/arena/sprites/ArenaPlatFrontR.png', '/stages/arena/sprites/icon_arena.png', '/stages/arena_moving_platform/music/Autumn Warriors.ogg', '/stages/arena_moving_platform/music/Laszlo - Fall To Light.ogg', '/stages/arena_moving_platform/sprites/ArenaBack.png', '/stages/arena_moving_platform/sprites/ArenaFront.png', '/stages/arena_moving_platform/sprites/ArenaPlatBackL.png', '/stages/arena_moving_platform/sprites/ArenaPlatBackM.png', '/stages/arena_moving_platform/sprites/ArenaPlatBackR.png', '/stages/arena_moving_platform/sprites/ArenaPlatFrontL.png', '/stages/arena_moving_platform/sprites/ArenaPlatFrontM.png', '/stages/arena_moving_platform/sprites/ArenaPlatFrontR.png', '/stages/arena_moving_platform/sprites/icon_arena.png', '/stages/training_stage/music/Character Lobby.ogg', '/stages/training_stage/sprites/icon_training_stage.png', '/stages/training_stage/sprites/training_stage_bg.png', '/stages/treehouse/music/Autumn Warriors.ogg', '/stages/treehouse/music/Laszlo - Fall To Light.ogg', '/stages/treehouse/sprites/TreeHouseBack.png', '/stages/treehouse/sprites/TreeHouseFront.png', '/stages/treehouse/sprites/icon_treehouse.png', '/stages/true_arena/music/Autumn Warriors.ogg', '/stages/true_arena/music/Laszlo - Fall To Light.ogg', '/stages/true_arena/sprites/TAscroll1.png', '/stages/true_arena/sprites/TAscroll2.png', '/stages/true_arena/sprites/TAscroll3.png', '/stages/true_arena/sprites/TAscroll4.png', '/stages/true_arena/sprites/TrueArenaBack.png', '/stages/true_arena/sprites/TrueArenaFront.png', '/stages/true_arena/sprites/icon_true_arena.png', '/fighters/hitboxie/sprites/articles/hitboxie_projectile.png', '/fighters/hitboxie/sprites/articles/hitboxie_shine.png']
    downloadUpdates(changedList)
        
if __name__  == '__main__': main()
