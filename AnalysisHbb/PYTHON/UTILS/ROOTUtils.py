##
## Generic ROOT functions
##

## Import Python functions
import PythonUtils
## Import ROOT functions
from ROOT import TFile, gDirectory, TObject

def saveToFile(h, fileName, directory, name):

    f = TFile(fileName, 'UPDATE')
    path = '/'
    ## Create the directory tree
    for dir in directory.split('/'):
        path += dir + '/'
        if not gDirectory.Get(dir):
            gDirectory.mkdir(dir)
        
        gDirectory.cd(dir)
    ## Now the tree is written, move to the dir
    
    f.cd(path)
    hc = h.Clone()
    hc.Write(name, TObject.kOverwrite)
    f.Close()


