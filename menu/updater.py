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
                path = settingsManager.createPath(directory+'/'+str(obj['name']))
                filesha = githash(path, os.path.getsize(path))
                
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
    
    print changedList 
    return changedList
  
    
def downloadUpdates(changedList):
    base_url = 'https://raw.githubusercontent.com/digiholic/universalSmashSystem/master/'
    base_dir = settingsManager.createPath('')
    
    for changedfile in changedList:
        print(changedfile)
        r = requests.get(base_url + changedfile)
        if r.status_code == 200:
            with open(base_dir+changedfile,'rw') as f:
                if f.read() == r.content():
                    print('files are the same')
                else:
                    pass
                    #f.seek(0)
                    #f.write(r.content)
                    #f.truncate()

def main():
    changedList = getChangedList()
    print(changedList)
    downloadUpdates(changedList)
        
if __name__  == '__main__': main()
