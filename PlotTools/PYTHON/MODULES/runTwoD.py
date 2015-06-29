##
## Script to create 2D plots using stats from 1D plots
##

## Import config File Parser, os and sys options
import ConfigParser, sys, os
## import the command line parser
from optparse import OptionParser
## import python functions
import PythonUtils
## import ROOT Functions
import ROOTUtils
## import the plotting functions
import PlottingUtils

class CreateTwoD(object):

    '''
    CreateTwoD:

    Class Will:
        * Retrieve each histogram
        * Get the required stat from the histogram
        * Create a 2D plot of the stats
    '''

    
    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.debug        = configFileParser.getint('GeneralOptions','debug')
        self.histFile     = configFileParser.get('GeneralOptions','histFile')
        self.saveDir      = configFileParser.get('GeneralOptions','saveDir')
        self.saveAs       = configFileParser.get('GeneralOptions','saveAs')
        ## List Files
        self.axisList     = configFileParser.get('ListFiles','axisList')
        self.fitList      = configFileParser.get('ListFiles','fittingList')
        self.histoList    = configFileParser.get('ListFiles','histoList')
        self.legendList   = configFileParser.get('ListFiles','legendList')
        self.textList     = configFileParser.get('ListFiles','textList')
        self.variableList = configFileParser.get('ListFiles','variableList')

    
    def Run(self):

        ## Create lists from config file options
        l_saveAs = PythonUtils.makeListFromString(self.saveAs, ',')

        ## Check the .list files exist
        l_listFile = [self.axisList, self.fitList, self.histoList, self.legendList,
                      self.textList, self.variableList, self.histFile]
        for file in l_listFile:
            PythonUtils.doesFileExist(file)

        ## Create the tuples from the .list files
        t_axisList   = PythonUtils.makeTupleFromFile(self.axisList,   ',')
        t_fitList    = PythonUtils.makeTupleFromFile(self.fitList,    ',')
        t_histoList  = PythonUtils.makeTupleFromFile(self.histoList,  ',')
        t_legendList = PythonUtils.makeTupleFromFile(self.legendList, ',')
        t_textList   = PythonUtils.makeTupleFromFile(self.textList,   ',')

        ## Math the first titems
        l_tuples = [t_fitList, t_histoList, t_legendList, t_textList]
        for item in l_tuples:
            PythonUtils.firstItemMatching(t_axisList, item)
        
        ## Loop over the variable files to get the relevant info
        for j in xrange(len(t_axisList)):
            f_str, vRebin, vdoNorm, vXMin, vXMax, vFit, vXValue, vYValue = t_fitList[j]

            l_files = []
            f = open(self.variableList, 'r')
            for file in f:
                l_files.append(file.strip())
            
            l_twoD = []
            t_legend = []
            PythonUtils.doesFileExist(l_files[j])
            g = open(l_files[j], 'r')
            for vFile in g:
                PythonUtils.doesFileExist(vFile.strip())
                vFileParser = ConfigParser.SafeConfigParser()
                vFileParser.read(vFile.strip())
                ## Options
                vTitle      = vFileParser.get('Options','title')
                vVariable   = vFileParser.get('Options','variable')
                vColour     = vFileParser.getint('Options','colour')
                vMarker     = vFileParser.getint('Options','marker')
                vMarkerSize = vFileParser.getfloat('Options','markerSize')
                vFitMin     = vFileParser.get('Options','fitMin')
                vFitMax     = vFileParser.get('Options','fitMax')

                ## Create l_statInfo
                l_statInfo = [t_histoList[j][1], t_histoList[j][1], float(vRebin), int(vdoNorm),
                              float(vXMin), float(vXMax), vFitMin, vFitMax]

                getMean = 0
                getRMS  = 0
                getRES  = 0
                if vXValue == 'MEAN':
                    getMean = 1
                elif vXValue == 'RMS':
                    getRMS = 1
                elif vXValue == 'RESOLUTION':
                    getRES = 1
                else:
                    getMean = getRMS = getRES = 0
                l_xOption = [getMean, getRMS, getRES]
                
                getMean = 0
                getRMS  = 0
                getRES  = 0
                if vYValue == 'MEAN':
                    getMean = 1
                elif vYValue == 'RMS':
                    getRMS = 1
                elif vYValue == 'RESOLUTION':
                    getRES = 1
                else:
                    getMean = getRMS = getRES = 0
                l_yOption = [getMean, getRMS, getRES]
                
                ## Get the list of stats
                l_plot =  [ROOTUtils.retrieveHistogram(self.histFile, t_histoList[j][1], vVariable)]
                l_xValue, l_xErr = ROOTUtils.getHistoStat(l_plot, l_statInfo, l_xOption, vFit, vVariable)
                l_yValue, l_yErr = ROOTUtils.getHistoStat(l_plot, l_statInfo, l_yOption, vFit, vVariable)

                ## Get the value we want from the list so we can plot it!
                xValue = -1
                for stat in l_xValue:
                    if stat != -1:
                        xValue = stat

                for stat in l_yValue:
                    if stat != -1:
                        yValue = stat
               
                ## Create a 2D plot and save to a list so can overlay them
                twoDPlot = PlottingUtils.createTwoD(t_histoList[j], xValue, yValue,
                                                    vMarker, vMarkerSize, vColour)
                l_twoD.append(twoDPlot)
                if vTitle:
                    l_legend = [twoDPlot, vTitle, 'p']
                    t_legend.append(l_legend)
            
            ## Overlay our 2D plots onto one canvas
            PlottingUtils.overlayTwoD(l_twoD, t_legend, t_histoList[j], t_legendList[j], 
                                       t_textList[j], t_axisList[j], self.saveDir, l_saveAs)


def main():

    use = '''

    Example:

    python PYTHON/MODULES/runTwoD.py --MainConfigFile=ConfigFiles/TwoD/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main Config File used for creating 2D plots')

    options, args = parser.parse_args()
    if options.MainConfigFile:
        createTwoD = CreateTwoD(options.MainConfigFile)
        createTwoD.Run()
    else:
        print "\nERROR: No ConfigFile Found!"
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
