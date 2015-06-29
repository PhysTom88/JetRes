# Python script for stacking plots
# Tom Ravenscroft

## Import Plotting functions
import PlottingUtils
## Import ROOT Functions
import ROOTUtils
## Python Functions
import PythonUtils
## Neural Networks
import NNUtils
## Import Config file parser, os and sys
import ConfigParser, sys, os
## Import option parser functions
from optparse import OptionParser

class CreateStackedPlots(object):

    '''
    CreateStackedPlots:

    Class Will:
        * Loop over the contents of Processes list
        * retrieve the histograms from the file
        * Create stacked plots from these histograms
    '''
    def __init__(self, t_histoList, t_legendList, t_textList, t_axisList, t_ratioList, histFile, l_saveAs, saveDir, doStacking):
        
        self.t_histoList  = t_histoList
        self.t_legendList = t_legendList
        self.t_textList   = t_textList
        self.t_axisList   = t_axisList
        self.t_ratioList  = t_ratioList
        self.histFile     = histFile
        self.l_saveAs     = l_saveAs
        self.saveDir      = saveDir
        self.doStacking   = doStacking


    def Run(self, processList):
    
        len_histoList   = len(self.t_histoList)
        t_tagList = PythonUtils.makeTupleFromFile(processList, ',')

        l_files = []
        f = open(processList, 'r')
        for file in f:
            l_files.append(file.strip())
            
        for i in xrange(len(t_tagList)):
            pFile, tagText = t_tagList[i]
            PythonUtils.doesFileExist(pFile)
            t_processList = PythonUtils.makeTupleFromFile(pFile, ',')

            for j in xrange(len(self.t_histoList)):
                t_plot = []
                name = self.t_histoList[j][2]
                for k in xrange(len(t_processList)):
                    histoLocation = t_processList[k][1] + self.t_histoList[j][1]
                    t_plot.append([ROOTUtils.retrieveHistogram(self.histFile, histoLocation, name)])

                saveString = self.saveDir + self.t_histoList[j][0] + '_'  + t_processList[k][7]
                PlottingUtils.stackHistograms(t_plot, t_processList, self.t_histoList[j],
                                              self.t_legendList[j], self.t_textList[j],
                                              self.t_axisList[j], self.l_saveAs, 
                                              self.t_ratioList[j], saveString, tagText)


def main():
    
    use = '''

    Example:

    python PYTHON/MODULES/runStacking.py --MainConfigFile=ConfigFiles/Stacking/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option("--MainConfigFile", dest="MainConfigFile", default="", type="string", help="Main Configuration File used for stacking")
    options, args = parser.parse_args()
    if options.MainConfigFile:
        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(options.MainConfigFile)
        ## General Options
        debug       = configFileParser.getint('GeneralOptions','debug')
        doStacking  = configFileParser.getint('GeneralOptions','doStacking')
        histFile    = configFileParser.get('GeneralOptions','histFile')
        saveDir     = configFileParser.get('GeneralOptions','saveDir')
        saveAs      = configFileParser.get('GeneralOptions','saveAs')
        ## List Files
        processList = configFileParser.get('ListFiles','processList')
        histoList   = configFileParser.get('ListFiles','histoList')
        legendList  = configFileParser.get('ListFiles','legendList')
        textList    = configFileParser.get('ListFiles','textList')
        axisList    = configFileParser.get('ListFiles','axisList')
        ratioList   = configFileParser.get('ListFiles','ratioList')
    else:
        print "\nERROR: No ConfigFile"
        print use
        sys.exit(1)

    ## Make Lists, dicts and tuples from Main Config File
    l_saveAs      = PythonUtils.makeListFromString(saveAs, ',')
    
    ## Make sure our .list files do existi
    PythonUtils.doesDirExist(saveDir)
    PythonUtils.doesFileExist(histFile)
    PythonUtils.doesFileExist(processList)
    PythonUtils.doesFileExist(histoList)
    PythonUtils.doesFileExist(legendList)
    PythonUtils.doesFileExist(textList)
    PythonUtils.doesFileExist(axisList)
    PythonUtils.doesFileExist(ratioList)
    

    ## Make the Tuples and Lists from the .list files
    t_histoList   = PythonUtils.makeTupleFromFile(histoList,   ',')
    t_legendList  = PythonUtils.makeTupleFromFile(legendList,  ',')
    t_textList    = PythonUtils.makeTupleFromFile(textList,    ',')
    t_axisList    = PythonUtils.makeTupleFromFile(axisList,    ',')
    t_ratioList   = PythonUtils.makeTupleFromFile(ratioList,   ',')
    ## Match the first item to make sure theyre compatible
    PythonUtils.firstItemMatching(t_histoList, t_legendList)
    PythonUtils.firstItemMatching(t_histoList, t_textList)
    PythonUtils.firstItemMatching(t_histoList, t_axisList)
    PythonUtils.firstItemMatching(t_histoList, t_ratioList)

    ## Loops over the contents of processList
    createStackedPlots = CreateStackedPlots(t_histoList, t_legendList, t_textList, t_axisList, 
                                            t_ratioList, histFile, l_saveAs, saveDir, doStacking)
    createStackedPlots.Run(processList)

if __name__ == "__main__":
    main()
