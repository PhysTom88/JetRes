##
## Script to Calculate the mean, RMS and resolution
##

## Import the Config File parser, os and sys modules
import ConfigParser, os, sys
## import the command line option parser
from optparse import OptionParser
## import python functions
import PythonUtils
## import ROOT funtions
import ROOTUtils
## import NN Functions
import NNUtils


class MeanResRMS(object):

    '''
    MeanResRMS:

    Class will:
        * Read in the configFiles
        * Retrieve the histograms
        * Calculate the stats with or without a fit
        * Rank the values
    '''

    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.debug           = configFileParser.getint('GeneralOptions','debug')
        self.histFile        = configFileParser.get('GeneralOptions','histFile')
        self.doLatex         = configFileParser.getint('GeneralOptions','doLatex')
        self.latexDir        = configFileParser.get('GeneralOptions','latexDir')
        ## List Files
        self.correctionList = configFileParser.get('ListFiles','correctionList')
        self.histoList      = configFileParser.get('ListFiles','histoList')
        self.fittingList    = configFileParser.get('ListFiles','fittingList')
        

    def Run(self):

        ## Check the files in the config file exist
        l_file = [self.histFile, self.correctionList, 
                  self.histoList, self.fittingList]
        for file in l_file:
            PythonUtils.doesFileExist(file)

        ## Add the trailing slash to the end of latexDir
        if not self.latexDir.endswith('/'):
            latexDir = self.latexDir + '/'
            PythonUtils.doesDirExist(latexDir)
        else:
            latexDir = self.latexDir

        ## Make tuples from the list files
        t_histoList =   PythonUtils.makeTupleFromFile(self.histoList, ',')
        t_fittingList = PythonUtils.makeTupleFromFile(self.fittingList, ',')
        
        ## Loop over the files in correctionsList each one is a new run
        l_cFiles = []
        f = open(self.correctionList, 'r')
        for file in f:
            if file.startswith('#'):
                continue
            else:
                l_cFiles.append(file.strip())
       
        for i in xrange(len(l_cFiles)):
            ld_mean = []
            ld_rms  = []
            ld_res  = []
            l_getOption = [int(t_fittingList[i][2]), int(t_fittingList[i][3]), int(t_fittingList[i][4])]
            ## Check the file in the list exists
            PythonUtils.doesFileExist(l_cFiles[i])
            t_corrList = PythonUtils.makeTupleFromFile(l_cFiles[i], ',')
            d_meanResRMS = {}
            tagType = ''
            for j in xrange(len(t_corrList)):
                h_location = t_corrList[j][1] + t_histoList[i][1]
                t_histoList[i].append(t_corrList[j][3])
                t_histoList[i].append(t_corrList[j][4])
                l_hist = [t_histoList[i][0], t_histoList[i][1], t_histoList[i][2], 
                          t_histoList[i][3], t_histoList[i][4], t_histoList[i][5], 
                          t_corrList[j][3], t_corrList[j][4]]
                
                pTVBin = t_histoList[i][6]
                tagType = t_histoList[i][7]
                l_h = [ROOTUtils.retrieveHistogram(self.histFile, 
                       h_location, t_corrList[j][2])]
                
                d_meanResRMS[t_corrList[j][0]] = ROOTUtils.getHistoStat(l_h, l_hist, l_getOption, 
                                                                        t_fittingList[i][5], t_corrList[j][0])


            ## We now have all the info to calculate the stats from the plots!

            d_mean = {}
            d_RMS  = {}
            d_res  = {}
            getMean, getRMS, getResolution = l_getOption
            compareTo = t_fittingList[i][1]
            fit = t_fittingList[i][5]
            l_corrName = []
            for k, v in d_meanResRMS.iteritems():
                l_corrName.append(k)
                if getMean:
                    d_mean[k] = [v[0][0], v[1][0]]
                if getRMS:
                    d_RMS[k]  = [v[0][1], v[1][1]]
                if getResolution:
                    d_res[k]  = [v[0][2], v[1][2]]

            ld_mean.append([t_histoList[i][0], d_mean])
            ld_rms.append([t_histoList[i][0], d_RMS])
            ld_res.append([t_histoList[i][0], d_res])
            t_mRr = []
            if getMean:
                t_mRr.append(PythonUtils.rankByValue(ld_mean, compareTo,
                                                     fit + ' Mean'))
            if getRMS:
                t_mRr.append(PythonUtils.rankByValue(ld_rms, compareTo,
                                                     fit + ' RMS'))
            if getResolution:
                t_mRr.append(PythonUtils.rankByValue(ld_res, compareTo,
                                                     fit + ' Resolution'))

            if self.doLatex:
                latex = self.writeLatex(t_mRr, l_corrName, pTVBin, t_histoList[i][0], latexDir, getMean, getRMS, getResolution)
                PythonUtils.runLatex(latex, latexDir)


    def writeLatex(self, t_mRr, l_corrName, pTVBin, texFile, lDir, gMean, gRMS, gRes):

        ## We want the corrections to appear in order
        l_corrName.sort()
        texName = lDir + texFile + '.tex'

        # Write the table for the mean, rms and res for the 
        # different jet corrections
        f = open(texName, 'w')
        f.write('\documentclass[11pt, landscape]{aastex} \n')
        f.write('\\begin{document}\n')
        f.write('\\begin{center}\n')

        f.write('\\begin{tabular}{r')
        if gMean:
            f.write('|c')
        if gRMS:
            f.write('|c')
        if gRes:
            f.write('|c')
        f.write('} \n')
        
        f.write('Correction ')
        if gMean:
            f.write('& Mean ')
        if gRMS:
            f.write('& RMS ')
        if gRes:
            f.write('& Resolution ')
        f.write('\\\ \hline\hline \n')

        for corr in l_corrName:
            f.write(corr)
            for i in xrange(len(t_mRr)):
                for j in xrange(len(t_mRr[i])):
                    t_sort = tuple(sorted(t_mRr[i][j], key = lambda item: item[0]))
                    for k in xrange(len(t_sort)):
                        if t_sort[k][0] == corr:
                            f.write(' & ' + str(round(t_sort[k][1], 5)) + ' $\pm$ ' + str(round(t_sort[k][2], 5)))
                
            f.write(' \\\ \n')

        f.write('\hline\n')
        f.write('\end{tabular} \n')
        f.write('\end{center}\n')
        f.write('\end{document}\n')
        f.close()

        PythonUtils.Info('FILE: ' + texName + ' Written')

        return texFile

def main():

    use = '''
    
    Example:

    python PYTHON/MODULES/runMeanResRMS.py --MainConfigFile=ConfigFiles/MeanResRMS/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main configFile used for geting the mean, RMS and res')

    options, args = parser.parse_args()
    if options.MainConfigFile:
        meanResRMS = MeanResRMS(options.MainConfigFile)
        meanResRMS.Run()
    else:
        print '\nERROR: No Config File Found!'
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
