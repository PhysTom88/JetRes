##
## Script to create a pure MJ sample by subtracting EW from Data MJ
##

## import option parser
from optparse import OptionParser
## Read in config files
import ConfigParser, os, sys, math
## Import some ROOT modules
from ROOT import TH1F, TH1D, TFile
## Personal Python Utils
import PythonUtils
## Personal ROOT Utils
import ROOTUtils

class CreateMJHist(object):

    '''
    CreateMJHist:

    Class Will:
        * Read in config file values
        * loop over Input files
        * create histograms for data, EW and MJ
        * Subtract EW from Data to create MJ sample
    '''

    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.nEvents    = configFileParser.getint('GeneralOptions','nEvents')
        self.outputFile = configFileParser.get('GeneralOptions','outputFile')
        self.samples    = configFileParser.get('GeneralOptions','samples')
        self.selectOn   = configFileParser.get('GeneralOptions','selectOn')
        self.selectBins = configFileParser.get('GeneralOptions','selectBins')
        ## List Files
        self.inputList  = configFileParser.get('ListFiles','inputList')
        self.typeList   = configFileParser.get('ListFiles','typeList')


    def Run(self):

        ## Make lists from the config file options
        l_samples    = PythonUtils.makeListFromString(self.samples, ',')
        t_selectBins = PythonUtils.makeTupleFromString(self.selectBins, ',', '?')

        ## Check the existence of the .list files
        l_listFiles = [self.inputList, self.typeList]
        for file in l_listFiles:
            PythonUtils.doesFileExist(file)

        ## Make the tuples from these files
        t_input = PythonUtils.makeTupleFromFile(self.inputList, ',')
        t_type  = PythonUtils.makeTupleFromFile(self.typeList, ',')

        ## Loop over the input files to create a histogram file
        for i in xrange(len(t_input)):
            dFile, ewFile, treeName, mjDir, dDir, ewDir = t_input[i]
            l_inFiles = [dFile, ewFile]
            for file in l_inFiles:
                PythonUtils.doesFileExist(file)

            for sample in l_samples:
                ## Create the histograms
                d_ewHist = self.createHistograms(t_type, sample, ewDir, 
                                                 self.selectOn, t_selectBins)
                d_dHist  = self.createHistograms(t_type, sample, dDir,
                                                 self.selectOn, t_selectBins)
                d_mjHist = self.createHistograms(t_type, sample, mjDir,
                                                 self.selectOn, t_selectBins)

                ## Fill the histograms
                d_ewHist_f = self.fillHistograms(d_ewHist, t_type, ewFile,
                                                 treeName, sample, ewDir,
                                                 t_selectBins, self.selectOn, self.nEvents)
                d_dHist_f  = self.fillHistograms(d_dHist, t_type, dFile,
                                                 treeName, sample, dDir,
                                                 t_selectBins, self.selectOn, self.nEvents )

                ## Subtract the histograms
                d_mjHist_f = self.subtractHistograms(d_mjHist, d_dHist_f, d_ewHist_f,
                                                     mjDir, dDir, ewDir, sample, 
                                                     self.selectOn, t_selectBins, t_type)

                ## save the histograms
                self.saveHistograms(d_mjHist_f, t_type, self.outputFile, sample,
                                    mjDir, self.selectOn, t_selectBins)
                self.saveHistograms(d_ewHist_f, t_type, self.outputFile, sample,
                                    ewDir, self.selectOn, t_selectBins)
                self.saveHistograms(d_dHist_f, t_type, self.outputFile, sample,
                                    dDir, self.selectOn, t_selectBins)


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
                    if 'crea' not in type:
                        d_hist[location + sName] = TH1F(hName, hName, int(nBins), float(xMin), float(xMax))
                        d_hist[location + sName].SetDirectory(0)
                    else:
                        d_hist[location + sName] = TH1D(hName, hName, int(nBins), float(xMin), float(xMax))
                        d_hist[location + sName].SetDirectory(0)
                d_histType[type] = d_hist
            d_histBinType[select] = d_histType

        return d_histBinType


    def fillHistograms( self, d_histType, t_type, iFile, treeName,
                       sample, baseDir, t_select, selectOn, nEvents ):
        
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


    def subtractHistograms(self, d_mjHist, d_dHist_f, d_ewHist_f, mjDir, dDir, 
                           ewDir, sample, selectOn, t_selectBins, t_type):

        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++')
        PythonUtils.Info('             SUBTRACTING HISTOGRAMS               ')
        PythonUtils.Info('++++++++++++++++++++++++++++++++++++++++++++++++++')
        
        for bin in t_selectBins:
            if bin[0] == 'all':
                select = selectOn + '-' + bin[0]
            else:
                select = selectOn + '-' + bin[0] + '-' + bin[1]

            for i in range(len(t_type)):
                type, typeFile = t_type[i]
                t_typeFile = PythonUtils.makeTupleFromFile(typeFile, ',')
                for j in range(len(t_typeFile)):
                    rBranch, tBranch, sName, sLocation, xMin, xMax, nBuns = t_typeFile[j]
                    mjLocation = mjDir + '/' + sample + '/' + select + '/' + sLocation
                    ewLocation = ewDir + '/' + sample + '/' + select + '/' + sLocation
                    dLocation  = dDir + '/' + sample + '/' + select + '/' + sLocation

                    d_mjHist[select][type][mjLocation + sName] = d_dHist_f[select][type][dLocation + sName].Clone()
                    d_mjHist[select][type][mjLocation + sName].Add(d_ewHist_f[select][type][ewLocation + sName], -1)
                    d_mjHist[select][type][mjLocation + sName] = self.removeNegBins(d_mjHist[select][type][mjLocation + sName])

        return d_mjHist


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
            tValue = getattr(entry, rBranch)
        
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


    def removeNegBins(self, h):

        nBin = h.GetNbinsX()
        for i in xrange(1, nBin, 1):
            cont = h.GetBinContent(i)
            if cont < 0:
                h.SetBinContent(i, 0.0001)

        return h


def main():
    
    use = '''

    Example:

    python PYTHON/MODULES/createMJSample.py --MainConfigFile=ConfigFiles/HistFileMaker/MainConfigFile/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main config file for creating pure QCD sample')
    options, args = parser.parse_args()

    if options.MainConfigFile:
        createMJHist = CreateMJHist(options.MainConfigFile)
        createMJHist.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
