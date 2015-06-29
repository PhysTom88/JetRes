## 
## Python script to create a 2D profile
##

## Import the config file parser, os and sys modules
import ConfigParser, os, sys
## Import the ability to parse command line options
from optparse import OptionParser
## ROOT functions we will use
from ROOT import TH1F, TH1D, TFile
## Import Custom Python Funtions
import PythonUtils
## Import Custom ROOT Tools
import ROOTUtils
## Import custom Plotting Functions
import PlottingUtils


class CreateProfile(object):

    '''
    CreateProfile

    Class Will:
        * Create histogram file for jet energy values
        * Retrieve the histograms mean, rms
        * Create a 2D histogram with these values
    '''


    def __init__(self, configFile, doProfile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.outHist      = configFileParser.get('GeneralOptions','outHist')
        self.nEvents      = configFileParser.getint('GeneralOptions','nEvents')
        self.selectOn     = configFileParser.get('GeneralOptions','selectOn')
        self.selectBins   = configFileParser.get('GeneralOptions','selectBins')
        self.muBins       = configFileParser.get('GeneralOptions','muBins')
        ## List Files
        self.variableList = configFileParser.get('ListFiles','variableList')
        self.treeList     = configFileParser.get('ListFiles','treeList')
        ## Config Files
        self.profCfg      = configFileParser.get('ConfigFiles','profileConfig')

        if doProfile:
            configFileParser.read(self.profCfg)
            ## GeneralOptions
            self.inFile      = configFileParser.get('GeneralOptions','inputFile')
            self.plotDir     = configFileParser.get('GeneralOptions','saveDir')
            self.plotType    = configFileParser.get('GeneralOptions','saveType')
            ## ListFiles
            self.axisList    = configFileParser.get('ListFiles','axisList')
            self.histoList   = configFileParser.get('ListFiles','histogramList')
            self.legendList  = configFileParser.get('ListFiles','legendList')
            self.textList    = configFileParser.get('ListFiles','textList')
            self.varList     = configFileParser.get('ListFiles','variableList')

    def Run(self, doProfile, createFile):

        ## Create the lists from the main configFile
        t_select = PythonUtils.makeTupleFromString(self.selectBins, ',', '?')
        t_muon   = PythonUtils.makeTupleFromString(self.muBins,     ',', '?')

        if createFile:
            PythonUtils.Info('Creating Histogram File for Profile Plots')
            ## Check the list files exist
            l_fList = [self.variableList, self.treeList]
            for f in l_fList:
                PythonUtils.doesFileExist(f)

            ## Make the lists from the list files
            t_var  = PythonUtils.makeTupleFromFile(self.variableList, ',')
            t_tree = PythonUtils.makeTupleFromFile(self.treeList, ',')

            for i in xrange(len(t_tree)):
                tFile, tName, sDir = t_tree[i]
                PythonUtils.doesFileExist(tFile)

                d_histType    = self.createHistograms(t_var, sDir, tFile, t_muon, 
                                                      self.selectOn, t_select)
                d_filledHists = self.fillHistograms(d_histType, t_var, tFile, tName, sDir, t_muon,
                                                    t_select, self.selectOn, self.nEvents)
                self.saveHistograms(d_filledHists, t_var, self.outHist, 
                                    sDir, t_muon, self.selectOn, t_select)

        if doProfile:
            PythonUtils.Info("Creating Profile Plots!")

            ## Create the Lists from profile cfg
            l_saveAs = PythonUtils.makeListFromString(self.plotType, ',')

            ## Check the list files exist
            l_pList = [self.axisList, self.histoList, self.legendList, 
                       self.textList, self.varList, self.inFile]

            for f in l_pList:
                PythonUtils.doesFileExist(f)

            ## Create the list of lists from each list file
            t_axisList    = PythonUtils.makeTupleFromFile(self.axisList,    ',')
            t_histoList   = PythonUtils.makeTupleFromFile(self.histoList,   ',')
            t_legendList  = PythonUtils.makeTupleFromFile(self.legendList,  ',')
            t_textList    = PythonUtils.makeTupleFromFile(self.textList,    ',')
            
            ## Check teh first Item matches:
            l_tList = [t_histoList, t_legendList, t_textList]
            for l in l_tList:
                PythonUtils.firstItemMatching(l, t_axisList)

            ## Add the var list files to a list
            l_varList = []
            f = open(self.varList, 'r')
            for line in f:
                if line.startswith('#'):
                    continue
                else:
                    l_varList.append(line)
            
            for i in xrange(len(l_varList)):
                PythonUtils.doesFileExist(l_varList[i].strip())
                t_varList = PythonUtils.makeTupleFromFile(l_varList[i].strip(), ',')
                l_prof = []
                t_legend = []
                for j in xrange(len(t_varList)):
                    d_pTMean = {}
                    l_err = []
                    for bin in t_select:
                        if bin[0] == 'all' or bin[1] == 'Inf': 
                            continue
                        if bin[1]:
                            select = self.selectOn + '-' + bin[0] + '-' + bin[1]
                        else:
                            select = self.selectOn + '-' + bin[0]
                        
                        location = t_varList[j][2] + '/' + t_varList[j][6] + '/' + select + '/' + t_varList[j][7]
                        pTbin = float(bin[0]) + (float(bin[1]) - float(bin[0])) / 2
                        pTMean = ROOTUtils.retrieveHistogram(self.inFile, location, t_varList[j][1]).GetMean()
                        pTMeanErr = ROOTUtils.retrieveHistogram(self.inFile, location, t_varList[j][1]).GetMeanError()
                        l_err.append(pTMeanErr)
                        d_pTMean[pTbin] = pTMean

                    h_prof, l_legend= PlottingUtils.twoDprofile(d_pTMean, t_histoList[i], t_varList[j], l_err)
                    l_prof.append(h_prof)
                    t_legend.append(l_legend)

                saveString = self.plotDir + t_histoList[i][0] 
                PlottingUtils.overlayProfile(l_prof, t_axisList[i], t_histoList[i], t_legendList[i], t_textList[i], t_legend, l_saveAs, saveString)


    def createHistograms(self, t_var, sDir, tFile, t_muon, selectOn, t_select):

        PythonUtils.Info('Creating Histograms: ' + sDir + ' For: ' + tFile)
        
        d_hMuBinType = {}
        for sMu in t_muon:
            b_mu = 'nMu_' + sMu[0] + sMu[1]

            d_hBinType = {}
            for bin in t_select:
                if bin[1]:
                    select = selectOn + '-' + bin[0] + '-' + bin[1]
                else:
                    select = selectOn + '-' + bin[0]

                d_hType = {}
                for i in xrange(len(t_var)):
                    rBranch, tBranch, sName, sLoc, xMin, xMax, nBins = t_var[i]
                    hName = 'h_' + sDir.replace('/', '_') + '_' + selectOn + '_' + bin[0] + '_' + rBranch
                    location = sDir + '/' + b_mu + '/' + select + '/' + sLoc
                    
                    d_hType[location + sName] = TH1F(hName, hName, int(nBins), float(xMin), float(xMax))
                    d_hType[location + sName].SetDirectory(0)

                d_hBinType[select] = d_hType

            d_hMuBinType[b_mu] = d_hBinType

        return d_hMuBinType


    def fillHistograms(self, d_histType, t_var, tFile, tName, sDir, t_muon, t_select, selectOn, nEvents):

        PythonUtils.Info('Filling Histograms: ' + tFile)

        f = TFile(tFile, 'READ')
        t = f.Get(tName)
        for i, entry in enumerate(t):

            ## only run over nEvents
            if nEvents != -1:
                if i == nEvents:
                    break
            for sMu in t_muon:
                b_mu = 'nMu_' + sMu[0] + sMu[1]

                for bin in t_select:
                    if bin[1]:
                        select = selectOn + '-' + bin[0] + '-' + bin[1]
                    else:
                        select = selectOn + '-' + bin[0]
                    
                    for j in xrange(len(t_var)):
                        rBranch, tBranch, sName, sLoc, xMin, xMax, nBins = t_var[j]
                        bSelect = ''
                        if selectOn == 'TRUTH':
                            bSelect = tBranch
                        elif selectOn == 'RECO':
                            bSelect = rBranch
                        else:
                            PythonUtils.Error('Option Not available')
                        if sMu[0] == 'all' or PythonUtils.getSelection(entry, sMu[0], sMu[1], 'hasMuon'):
                            if bin[0] == 'all' or PythonUtils.getSelection(entry, bin[0], bin[1], bSelect):
                                location = sDir + '/' + b_mu + '/' + select + '/' + sLoc
                                rValue = getattr(entry, rBranch)
                                tValue = getattr(entry, tBranch)
                                if 'cw' in location:
                                    d_histType[b_mu][select][location + sName].Fill(tValue/rValue, entry.eventWeight)
                                elif 'bw' in location:
                                    d_histType[b_mu][select][location + sName].Fill(rValue/tValue, entry.eventWeight)
                                elif 'vw' in location:
                                    d_histType[b_mu][select][location + sName].Fill(rValue, entry.eventWeight)
                                else:
                                    PythonUtils.Error('Histogram Type not recognised!')

        return d_histType


    def saveHistograms(self, d_filledHists, t_var, outFile, sDir, t_muon, selectOn, t_select):

        PythonUtils.Info('Saving Histograms: ' + outFile)
        
        for sMu in t_muon:
            b_mu = 'nMu_' + sMu[0] + sMu[1]

            for bin in t_select:
                if bin[1]:
                    select = selectOn + '-' + bin[0] + '-' + bin[1]
                else:
                    select = selectOn + '-' + bin[0]
                
                PythonUtils.Info('Saving Histograms for: ' + selectOn + ' In bin range: ' 
                                 + bin[0] + ' - ' + bin[1])
                for i in xrange(len(t_var)):
                    rBranch, tBranch, sName, sLocation, xMin, xMax, nBins = t_var[i]
                    location = sDir + '/' + b_mu + '/' + select + '/' + sLocation
                    ROOTUtils.saveToFile(d_filledHists[b_mu][select][location + sName], outFile, location, sName)


def main():

    use = '''

    Example:

    python PYTHON/MODULES/runProfile.py --MainConfigFile=ConfigFiles/Profile/MainConfigFile/MainConfigFile.cfg --doProfile=0 --createFile=0
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', 
                      type='string', help='Main config file for creating profile plots')
    parser.add_option('--doProfile', dest='doProfile', default=0,
                      type='int', help='Create the 2D profile plots ')
    parser.add_option('--createFile', dest='createFile', default=0,
                      type='int', help='Create the histogram for the pT bins')

    options, args = parser.parse_args()
    if options.MainConfigFile:
        createProfile = CreateProfile(options.MainConfigFile, options.doProfile)
        createProfile.Run(options.doProfile, options.createFile)
    else:
        PythonUtils.Error('Configuration File NOT Found!!')
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
