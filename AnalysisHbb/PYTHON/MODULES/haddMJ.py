##
## File to hadd the individual MJ files into one MJ file
##

## import option parser
from optparse import OptionParser
## import config reading
import ConfigParser, os, sys
## Python Utis
import PythonUtils
## ROOT
from ROOT import TFile, TTree



class HaddMJ(object):

    '''
    HaddMJ:

    Class Will:
        * Read the config file
        * loop over the different tags
        * collate the files together
        * hadd the files
    '''


    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.splitTag  = configFileParser.getint('GeneralOptions','splitTag')
        self.inputDir  = configFileParser.get('GeneralOptions','inputDir')
        self.outputDir = configFileParser.get('GeneralOptions','outputDir')
        self.tagList   = configFileParser.get('GeneralOptions','tagList')
        self.fileIdent = configFileParser.get('GeneralOptions','fileIdent')
        self.tree      = configFileParser.get('GeneralOptions','tree')

    def Run(self):

        ## Create the lists from configFiles
        l_tags = PythonUtils.makeListFromString(self.tagList, ',')

        if not self.splitTag:
            haddCmd = 'hadd -f ' + self.outputDir + self.fileIdent + '_' + self.tagList + '0_EW_MJ_0.root '
            for root, dir, files in os.walk(self.inputDir):
                for file in files:
                    if 'MJ' in file and 'Data' not in file and '.root' in file:
                        if 'llbb' not in file and 'lv' not in file and 'vv' not in file:
                            print file
                            if self.emptyTree(self.inputDir + file, self.tree):
                                print self.inputDir + file
                                haddCmd += self.inputDir + file + ' '

            print haddCmd
            os.system(haddCmd)
        else: 
            ## loop over the tags and hadd the files
            for tag in l_tags:
                haddCmd = 'hadd -f ' + self.outputDir + self.fileIdent + '_' + tag + '0_EW_MJ_0.root '
                for root, dir, files in os.walk(self.inputDir):
                    for file in files:
                        if tag in file and self.fileIdent in file and 'MJ' in file and 'Data' not in file:
                            if self.emptyTree(self.outputDir + file, self.tree):
                                print self.outputDir + file
                                haddCmd += self.outputDir + file + ' '
               
                print ''
                os.system(haddCmd)

    
    def emptyTree(self, file, tree):

        f = TFile(file, 'READ')
        t = f.Get(tree)
        if t.GetEntries() != 0:
            return True
        else:
            return False


def main():

    use = '''

    Example:

    python PYTHON/MODULES/haddMJ.py --MainConfigFile=ConfigFiles/hadd/MainConfigFile/MainConfigFile.cfg
    '''
    
    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main Config File for hadding MJ files')

    options, args = parser.parse_args()
    if options.MainConfigFile:
        haddMJ = HaddMJ(options.MainConfigFile)
        haddMJ.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)



if __name__ == '__main__':
    main()
