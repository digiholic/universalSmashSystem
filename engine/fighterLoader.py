import settingsManager
import xml.etree.ElementTree as ElementTree
import pygame

class Loader():
    def __init__(self,path):
        self.tree = ElementTree.parse(path)
        self.root = self.tree.getroot()
        
        varDict = {}
        for stat in self.root.find('stats'):
            varDict[stat.tag] = float(stat.text)
        
        colorPalettes = []
        for colorPalette in self.root.findall('colorPalette'):
            colorDict = {}
            for colorMap in colorPalette.findall('colorMap'):
                fromColor = pygame.Color(colorMap.attrib['fromColor'])
                toColor = pygame.Color(colorMap.attrib['toColor'])
                colorDict[(fromColor.r, fromColor.g, fromColor.b)] = (toColor.r, toColor.g, toColor.b)
            
            colorPalettes.append(colorDict)
        
        print colorPalettes
    
    def getData(self,element):
        ret = []
        for e in self.root.findall(element):
            ret.append(e.text)
            
        if len(ret) == 1:
            return ret[0]
        else:
            return ret
    
                
def main():
    Loader(settingsManager.createPath('fighters/hitboxie/fighter.xml'))
    
if __name__=='__main__': main()