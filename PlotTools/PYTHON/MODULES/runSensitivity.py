## 
## Script to calculate the sensitivity
##

## ROOT Functions
import ROOTUtils
## Python Functions
import PythonUtils
## ConfigFile parser and other python
import ConfigParser, sys, os
## Parsing Command Line Options
from optparse import OptionParser


class SensitivityCalculation(object):

    '''
    Class Will:
        * Read in ConfigFile
        * Calculate Sensitivity
        * Rank Sensitivity
    '''

    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.debug       = configFileParser.getint('GeneralOptions','debug')
        self.histFile    = configFileParser.get('GeneralOptions','histFile')
        self.doLatex     = configFileParser.getint('GeneralOptions','doLatex')
        self.latexDir    = configFileParser.get('GeneralOptions','latexDir')
        ## List Files
        self.processList = configFileParser.get('ListFiles','processList')
        self.histoList   = configFileParser.get('ListFiles','histoList')
        self.corrList    = configFileParser.get('ListFiles','corrList')

    
    def Run(self):

        ## Add the trailing slash to the end of latexDir
        if not self.latexDir.endswith('/'):
            latexDir = self.latexDir + '/'
            PythonUtils.doesDirExist(latexDir)
        else:
            latexDir = self.latexDir

        ## Check the .list files exist
        l_fList = [self.processList, self.histoList, 
                   self.corrList, self.histFile]
        for file in l_fList:
            PythonUtils.doesFileExist(file)

        ## Make the lists from the list files
        t_histoList = PythonUtils.makeTupleFromFile(self.histoList,   ',')
        t_corrList  = PythonUtils.makeTupleFromFile(self.corrList,    ',')
        t_pList     = PythonUtils.makeTupleFromFile(self.processList, ',')

        ## Create the variable name dictionary
        compTo = ''
        d_nameVar = {}
        for i in xrange(len(t_corrList)):
            d_nameVar[t_corrList[i][0]] = t_corrList[i][1]
            if t_corrList[i][2] == '1':
                compTo = t_corrList[i][0]

        ## Construct the list of processes for each region
        
        
        l_pFiles = []
        f = open(self.processList, 'r')
        for line in f:
            if not line.startswith('#'):
                l_pFiles.append(line.strip())

        for i in xrange(len(t_pList)):
            pFile, tagType = t_pList[i]
            PythonUtils.doesFileExist(pFile)
            t_processList = PythonUtils.makeTupleFromFile(pFile, ',')
            ld_sens = []
            l_pTV = []
            option = ''
            for k in xrange(len(t_histoList)):
                l_pTV.append(t_histoList[k][3])
                d_sens = {}
                l_corrName = []
#                option = t_histoList[k][2]
                for name, title in d_nameVar.iteritems():
                    t_h = []
                    l_corrName.append(name)
                    for j in xrange(len(t_processList)):
                        option = t_processList[j][0]
                        hLocation = t_processList[j][1] + t_histoList[k][1]
                        t_h.append([ROOTUtils.retrieveHistogram(self.histFile, hLocation, title), t_processList[j][0], t_processList[j][2], t_processList[j][3]])
                    
                    sens, sensErr = ROOTUtils.calculateSensitivity(t_h, t_histoList[k], name)
                    
                    d_sens[name] = [sens, sensErr] 
                    d_sens[name] = ROOTUtils.calculateSensitivity(t_h, t_histoList[k], name) 

                l_sens = [t_histoList[k][0] + ' ' + tagType, d_sens]
                ld_sens.append(l_sens)
            
            t_sens = PythonUtils.rankByValue(ld_sens, compTo, 'SENSITIVITY')
            if self.doLatex:
                latex = self.writeLatex(t_sens, l_corrName, l_pTV, 
                                'Sensitivity_' + tagType + '_' + option, latexDir)
                PythonUtils.runLatex(latex, latexDir)

        
    def writeLatex(self, t_sens, l_corrName, l_pTV, texFile, latexDir):

        ## Want the corrections to appear in order
        l_corrName.sort()
        texName = latexDir + texFile + '.tex'

        ## Create the latex table for the number of corrections 
        ## and also the number of bins
        f = open(texName, 'w')
        f.write('\documentclass[11pt, landscape]{aastex} \n')
        f.write('\usepackage{pdflscape} \n')
        f.write('\\begin{document}\n')
        f.write('\\footnotesize \n')
        f.write('\\begin{landscape} \n')
        f.write('\\begin{tabular}{r' + len(l_pTV) * '|c' + '}\n')
        f.write('Correction')
        for bin in l_pTV:
            f.write(' & ' + bin)

        f.write(' \\\ \hline\hline \n')

        for corr in l_corrName:
            f.write(corr)
            for i in xrange(len(t_sens)):
                t_sort = tuple(sorted(t_sens[i], key = lambda item: item[0]))
                for j in xrange(len(t_sort)):
                    if t_sort[j][0] == corr:
                        f.write(' & ' + str(round(t_sort[j][1], 3)) + ' $\pm$ ' + str(round(t_sort[j][2], 3)))

            f.write(' \\\ \n')

        f.write('\hline\n')
        f.write('\end{tabular} \n')
        f.write('\end{landscape} \n')
        f.write('\end{document}\n')
        f.close()

        PythonUtils.Info('FILE: ' + texName + ' Written')

        return texFile


def main():

    use = '''

    Example:

    python PYTHON/MODULES/runSensitivity.py --MainConfigFile=ConfigFiles/Sensitivity/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option("--MainConfigFile", dest="MainConfigFile", default="", type="string", help="Main config file used for the sensitivity calculation")

    options, args = parser.parse_args()
    if options.MainConfigFile:
        sensCalc = SensitivityCalculation(options.MainConfigFile)
        sensCalc.Run()
    else:
        print "\nERROR: No Config File Found!"
        print use
        sys.exit(1)

if __name__ == '__main__':
    main()
