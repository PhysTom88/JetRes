##
## Script to create histogram file from a tree file
##

## import Config File Parser, os and sys
import ConfigParser, os, sys, math
## import command line parser
from optparse import OptionParser
## Import ROOT Functions
from ROOT import TH1F, TH1D, TFile
## import python functions
import PythonUtils
## import ROOT Utils
import ROOTUtils


class CreateHistFile(object):

    '''
    CreateHistFile:

    Class will:
        * Read in config files
        * Create directory tree in output file
        * Save trees as histograms
    '''


    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.debug      = configFileParser.getint('GeneralOptions','debug')
        self.nEvents    = configFileParser.getint('GeneralOptions','nEvents')
        self.outFile    = configFileParser.get('GeneralOptions','outputFile')
        self.samples    = configFileParser.get('GeneralOptions','samples')
        self.selectOn   = configFileParser.get('GeneralOptions','selectOn')
        self.selectBins = configFileParser.get('GeneralOptions','selectBins')
        ## List Files
        self.inputList  = configFileParser.get('ListFiles','inputFileList')
        self.typeList   = configFileParser.get('ListFiles','typeList')


    def Run(self):
        
        ## Create the lists from the config file
        l_samples = PythonUtils.makeListFromString(self.samples, ',')
        t_select  = PythonUtils.makeTupleFromString(self.selectBins, ',', '?')
        
        ## Check .list Files exist
        l_lFiles = [self.inputList, self.typeList]
        for file in l_lFiles:
            PythonUtils.doesFileExist(file)

        ## Make the tuples from the list files
        t_input = PythonUtils.makeTupleFromFile(self.inputList, ',')
        t_type  = PythonUtils.makeTupleFromFile(self.typeList,  ',')

        for i in range(len(t_input)):
            iFile, treeName, baseDir = t_input[i]
            PythonUtils.doesFileExist(iFile)
            for sample in l_samples:
                d_histType = self.createHistograms(t_type, sample, baseDir, 
                                                    self.selectOn, t_select)
                d_filledHists  = self.fillHistograms(d_histType, t_type, iFile, 
                                                     treeName, sample, baseDir,
                                                     t_select, self.selectOn, self.nEvents)
                self.saveHistograms(d_filledHists, t_type, self.outFile, sample, 
                                    baseDir, self.selectOn, t_select)


    def createHistograms(self, t_type, sample, baseDir, selectOn, t_select):

        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++')
        PythonUtils.Info('       CREATING HISTOGRAMS: ' + baseDir + '       ')
        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++') 
        
        d_histBinType = {}
        for bin in t_select:
            ## Don't have a trailing slash for all - looks messy
            PythonUtils.Info('Creating Histograms for process: ' + baseDir +
                             ' in bin: ' + bin[0] + '-' + bin[1]) 
            if bin[0] == 'all':
                select = selectOn + '-' + bin[0]
            else:
                select = selectOn + '-' + bin[0] + '-' + bin[1]

            d_histType = {}
            for i in range(len(t_type)):
                ## Decalare the list variables
                type, typeFile = t_type[i]
                ## Open typeFile and loop through it
                PythonUtils.doesFileExist(typeFile)
                t_typeFile = PythonUtils.makeTupleFromFile(typeFile, ',')
                d_hist = {}
                for j in range(len(t_typeFile)):
                    rBranch, tBranch, sName, sLocation, xMin, xMax, nBins = t_typeFile[j]
                    hName = 'h_' + baseDir + '_' + sample + '_' + selectOn + bin[0] + '_' + type + '_' + rBranch
                    location = baseDir + '/' + sample + '/' + select + '/' + sLocation
                    if 'crea' in type:
                        d_hist[location + sName] = TH1F(hName, hName, int(nBins), float(xMin), float(xMax))
                        d_hist[location + sName].SetDirectory(0)
                    else:
                        d_hist[location + sName] = TH1D(hName, hName, int(nBins), float(xMin), float(xMax))
                        d_hist[location + sName].SetDirectory(0)

                d_histType[type] = d_hist    
            d_histBinType[select] = d_histType
        
        return d_histBinType


    def fillHistograms(self, d_histType, t_type, iFile, treeName, 
                       sample, baseDir, t_select, selectOn, nEvents):

        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++')
        PythonUtils.Info('       FILLING HISTOGRAMS: ' + baseDir + '       ')
        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++')

        f = TFile(iFile, 'READ')
        t = f.Get(treeName)
        for i, entry in enumerate(t):
            ## Test for the test, train or all samples
            if not PythonUtils.keepEntry(sample, i):
                continue

            ## Run over the number of events: -1 is all
            if nEvents != -1:
                if i == nEvents:
                    break

            ## Loop over the binning
            for bin in t_select:
                ## Don't have a trailing slash for all - looks messy
                if bin[0] == 'all':
                    select = selectOn + '-' + bin[0]
                else:
                    select = selectOn + '-' + bin[0] + '-' + bin[1]
                
                if bin[0] == 'all' or PythonUtils.getSelection(entry, bin[0], bin[1], selectOn):
                    for j in range(len(t_type)):
                        type, typeFile = t_type[j]
                        t_typeFile = PythonUtils.makeTupleFromFile(typeFile, ',')
                        for k in range(len(t_typeFile)):
                            rBranch, tBranch, sName, sLocation, xMin, xMax, nBuns = t_typeFile[k]
                            location = baseDir + '/' + sample + '/' + select + '/' + sLocation
                            ## Setup how the values are filled for different types
                            d_histBinTypeF = self.doFill(d_histType, entry, rBranch, tBranch, 
                                                         select, type, location, sName)
                            
        return d_histBinTypeF


    def saveHistograms(self, d_filledHists, t_type, outFile, sample, baseDir, selectOn, t_select):
        
        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++')
        PythonUtils.Info('       SAVING HISTOGRAMS: ' + baseDir + '       ')
        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++')

        for bin in t_select:
            ## Don't have a trainling slash for all - looks messy
            PythonUtils.Info('Creating Histograms for process: ' + baseDir +
                             ' in bin: ' + bin[0] + '-' + bin[1])
            if bin[0] == 'all':
                select = selectOn + '-' + bin[0]
            else:
                select = selectOn + '-' + bin[0] + '-' + bin[1]
            
            for i in range(len(t_type)):
                type, typeFile = t_type[i]
                t_typeFile = PythonUtils.makeTupleFromFile(typeFile, ',')
                for j in range(len(t_typeFile)):
                    rBranch, tBranch, sName, sLocation, xMin, xMax, nBuns = t_typeFile[j]
                    location = baseDir + '/' + sample + '/' + select + '/' + sLocation
                    ROOTUtils.saveToFile(d_filledHists[select][type][location + sName], outFile, location, sName)

    
    def doFill(self, d_histType, entry, rBranch, tBranch, select, type, location, sName):

        if 'Data' in location and 'GEN' in rBranch:
            rValue = 0
        else:
            rValue = getattr(entry, rBranch)
        
        if 'Data' in location and 'GEN' in tBranch:
            tValue = 0
        else:
            tValue = getattr(entry, tBranch)

        ratio    = 1
        error    = 1
        relErr   = 1
        abRelErr = 1
        if tValue != 0:
            ratio    = rValue / tValue
            error    = tValue - rValue
            relErr   = error / tValue
            abRelErr = math.fabs(relErr)

        if type == 'v':
            d_histType[select][type][location + sName].Fill(rValue)
        elif type == 'vw':
            d_histType[select][type][location + sName].Fill(rValue, entry.eventWeight)
        elif type == 're':
            d_histType[select][type][location + sName].Fill(relErr)
        elif type == 'rew':
            d_histType[select][type][location + sName].Fill(relErr, entry.eventWeight)
        elif type == 'b':
            d_histType[select][type][location + sName].Fill(ratio)
        elif type == 'bw':
            d_histType[select][type][location + sName].Fill(ratio, entry.eventWeight)
        elif type == 'crea':
            d_histType[select][type][location + sName].Fill(abRelErr)
        elif type == 'creaw':
            d_histType[select][type][location + sName].Fill(abRelErr, entry.eventWeight)
        else:
            print '\ntype %s not recognised, exiting...' % (type)
            sys.exit(1)

        return d_histType


def main():

    use = '''

    Example:

    python PYTHON/MODULES/createHistFile.py --MainConfigFile=ConfigFiles/HistFile/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main config File for creating a histogram file from a tree file')

    options, args = parser.parse_args()
    if options.MainConfigFile:
        createHistFile = CreateHistFile(options.MainConfigFile)
        createHistFile.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
