import requests
import os
import sys
import filecmp
import settingsManager

def files(path):
    for file in os.listdir(path):
        if not file.startswith('.'):
            if os.path.isfile(os.path.join(path, file)):
                yield file

def getDirectories(path):
    return [os.path.join(path,x) for x in next(os.walk(path))[1] if x.startswith('.') == False]

def getChangedList():
    changedList = []
    excludeFiles = [settingsManager.createPath('main.exe'),settingsManager.createPath('menu/updater.py'),
                    settingsManager.createPath('w9xopen.exe')]
    excludeDirs = [settingsManager.createPath('tcl')]
    
    base_url = 'https://raw.githubusercontent.com/digiholic/universalSmashSystem/master/'
    base_directory = settingsManager.createPath('')
    
    upcomingDirs = [base_directory]
    
    while len(upcomingDirs) > 0: #for each directory
        directory = upcomingDirs[0]
        l = len(base_directory)
        subdir = directory[l:]
        #print directory
        if directory in excludeDirs:
            print('----------omitting directory '+directory)
        else:
            for filepath in files(directory): #for each file in the directory
                filename = os.path.join(directory,filepath)
                print(filename)
                if filename in excludeFiles:
                    print('----------omitting file '+ filename)
                else:
                    #print os.path.join(base_url,subdir,filepath)
                    r = requests.get(os.path.join(base_url,subdir,filepath))
                    if r.status_code == 200:
                        with open(filename,'r') as f:
                            if f.read() == r.content:
                                pass
                            else:
                                print('-----files differ',filename)
                                changedList.append((os.path.join(base_url,subdir,filepath),filename))
                        
            #after checking all of the files, add subdirectories, then remove itself
            upcomingDirs.extend(getDirectories(directory))
        upcomingDirs.remove(directory)
        #print upcomingDirs
    print(changedList)
    return changedList

def downloadUpdates(changedList):
    for changedfile in changedList:
        print(changedfile)
        r = requests.get(changedfile[0])
        if r.status_code == 200:
            with open(changedfile[1],'w') as f:
                f.seek(0)
                f.write(r.content)
                f.truncate()
                
def main():
    downloadUpdates(getChangedList())
        
if __name__  == '__main__': main()
