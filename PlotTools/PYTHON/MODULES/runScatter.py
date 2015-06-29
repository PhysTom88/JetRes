##
## Script to create scatter plots from trees
##

## import Plotting functions
import PlottingUtils
## import ROOT Functions
import ROOTUtils
## import Python Utils
import PythonUtils
## import config reader, os and sys
import ConfigParser, os, sys
## import command line parser
from optparse import OptionParser

class ScatterPlots(object):

    '''
    ScatterPlots

    Class Will:
        * Create the environment to create scatter plots
        * Save the scatter plots
    '''

    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.debug       = configFileParser.getint('GeneralOptions','debug')
        self.treeFile    = configFileParser.get('GeneralOptions','treeFile')
        self.saveDir     = configFileParser.get('GeneralOptions','saveDir')
        self.saveAs      = configFileParser.get('GeneralOptions','saveAs')
        ## List Files
        self.axisList    = configFileParser.get('ListFiles','axisList')
        self.fileList    = configFileParser.get('ListFiles','fileList')
        self.histoList   = configFileParser.get('ListFiles','histoList')
        self.scatterList = configFileParser.get('ListFiles','scatterlist')
        self.textList    = configFileParser.get('ListFiles','textList')


    def Run(self):

        ## Create lists from configFile info
        l_saveAs = PythonUtils.makeListFromString(self.saveAs, ',')

        ## Check the .list and tree files exist
        l_files = [self.treeFile, self.axisList, self.histoList,
                    self.scatterList, self.textList, self.fileList]
        for file in l_files:
            PythonUtils.doesFileExist(file)

        ## Make the tuples from the list files
        t_axisList    = PythonUtils.makeTupleFromFile(self.axisList,    ',')
        t_fileList    = PythonUtils.makeTupleFromFile(self.fileList,    ',')
        t_histoList   = PythonUtils.makeTupleFromFile(self.histoList,   ',')
        t_scatterList = PythonUtils.makeTupleFromFile(self.scatterList, ',')
        t_textList    = PythonUtils.makeTupleFromFile(self.textList,    ',')

        ## Match the first item in the tuples
        l_tuples = [t_fileList, t_histoList, t_scatterList, t_textList]
        for item in l_tuples:
            PythonUtils.firstItemMatching(t_axisList, item)

        for i in xrange(len(t_scatterList)):
            PlottingUtils.scatterPlot(t_scatterList[i], t_fileList[i], t_histoList[i], 
                                      t_axisList[i], t_textList[i], self.treeFile, 
                                      self.saveDir, l_saveAs)


def main():

    use = '''

    Example:

    python PYTHON/MODULES/runScatter.py --MainConfigFile=ConfigFiles/Scatter/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main config file for creating scatter plots from trees')
    options, args = parser.parse_args()
    if options.MainConfigFile:
        scatterPlots = ScatterPlots(options.MainConfigFile)
        scatterPlots.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
