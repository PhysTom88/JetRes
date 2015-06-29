## Python script for overlaying plots
## Tom Ravenscroft

## import the plotting functions
import PlottingUtils
## import the root functions
import ROOTUtils
## import useful python functions
import PythonUtils
## import config file, sys and os modules
import ConfigParser, sys, os
## Import command line parser
from optparse import OptionParser

class OverlayPlots(object):

    '''
    OverlayPlots:

    Class Will:
        * Make sure the list files exist
        * Retrieve the histograms
        * create overlaid plots
    '''
    
    def __init__(self, configFile):
        
        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        # General Options
        self.debug        = configFileParser.getint('GeneralOptions','debug')
        self.histFile     = configFileParser.get('GeneralOptions','histFile')
        self.saveDir      = configFileParser.get('GeneralOptions','saveDir')
        self.saveAs       = configFileParser.get('GeneralOptions','saveAs')
        # List Files
        self.axisList     = configFileParser.get('ListFiles','axisList')
        self.histoList    = configFileParser.get('ListFiles','histoList')
        self.legendList   = configFileParser.get('ListFiles','legendList')
        self.overlayList  = configFileParser.get('ListFiles','overlayList')
        self.textList     = configFileParser.get('ListFiles','textList')


    def Run(self):

        # Create lists from config file info
        l_saveAs = PythonUtils.makeListFromString(self.saveAs, ',')

        ## Check the .list files exist!
        l_listFile = [self.axisList, self.histoList, self.legendList,
                      self.overlayList, self.textList, self.histFile]
        for file in l_listFile:
            PythonUtils.doesFileExist(file)

        ## Make the tuples from the input files
        t_axisList   = PythonUtils.makeTupleFromFile(self.axisList,   ',')
        t_histoList  = PythonUtils.makeTupleFromFile(self.histoList,  ',')
        t_legendList = PythonUtils.makeTupleFromFile(self.legendList, ',')
        t_textList   = PythonUtils.makeTupleFromFile(self.textList,   ',')

        ## match the first item to make sure they're compatible
        l_tuples = [t_histoList, t_legendList, t_textList]
        for item in l_tuples:
            PythonUtils.firstItemMatching(t_axisList, item)

        l_files = []
        f = open(self.overlayList, 'r')
        for line in f:
            if line.startswith('#'):
                continue
            else:
                l_files.append(line.strip())

        for i in xrange(len(l_files)):
            PythonUtils.doesFileExist(l_files[i])
            t_overlayList = PythonUtils.makeTupleFromFile(l_files[i], ',')
            t_plots = []
            for j in xrange(len(t_overlayList)):
                histoLocation = t_overlayList[j][1] + t_histoList[i][1]
                t_plots.append([ROOTUtils.retrieveHistogram(self.histFile, histoLocation, t_overlayList[j][2])])

            saveString = self.saveDir + t_histoList[i][0]
            PlottingUtils.overlayHistograms(t_plots, t_overlayList, t_histoList[i],
                                            t_legendList[i], t_textList[i], t_axisList[i],
                                            l_saveAs, saveString)

        
def main():

    use = '''
    
    Example:

    python PYTHON/MODULES/runOverlayPlots.py --MainConfigFile=ConfigFiles/Overlay/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main Configuration file used for overlaying')
    options, args = parser.parse_args()
    if options.MainConfigFile:
        overlayPlots = OverlayPlots(options.MainConfigFile)
        overlayPlots.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
