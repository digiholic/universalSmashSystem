import requests
import json
import hashlib
import os
import settingsManager
import threading
import sys
import urllib
import glob
import shutil
import zipfile

def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f), 
                                    os.path.join(dest, f), 
                                    ignore)
    else:
        shutil.copyfile(src, dest)
        
def main():
    print('Downloading Update from HEAD...')
    #Need the cert to access github
    os.environ["REQUESTS_CA_BUNDLE"] = os.path.join(os.getcwd(), "cacert.pem")
    
    #Get the Zipfile from Github
    base_url='https://github.com/digiholic/universalSmashSystem/archive/master.zip'
    page = urllib.urlopen(base_url)
    
    #Download the zipfile
    downloader = urllib.URLopener()
    downloader.retrieve(page.geturl(), settingsManager.createPath('update.zip'))
    
    #Extract it
    updatezip = zipfile.ZipFile(settingsManager.createPath('update.zip'))
    updatezip.extractall('tmp')
    
    print('Copying files into game directory...')
    #Copy the files upward, then remove the tmp files
    tmp_path = settingsManager.createPath('tmp'+os.sep+'universalSmashSystem-master'+os.sep)
    recursive_overwrite(tmp_path, settingsManager.createPath(''))
    shutil.rmtree(tmp_path)
    os.remove(settingsManager.createPath('update.zip'))
    
    print('Done!')
if __name__ == '__main__': main()