##
## Script to calculcate the yields from data and MC 
##

## import Option Parser
from optparse import OptionParser
## Read in Config Files
import ConfigParser, os, sys, math
## Python utils
import PythonUtils
## ROOT Utils
import ROOTUtils

class YieldCalc(object):

    '''
    YieldCalc

    Class Will:
        * Loop over the processes
        * Get each bin content
        * Print the output on screen
        * Save to a .tex file
    '''

    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.inputFile    = configFileParser.get('GeneralOptions','inputFile')
        self.outputFile   = configFileParser.get('GeneralOptions','outputFile')
        self.selectOn     = configFileParser.get('GeneralOptions','selectOn')
        self.selectBins   = configFileParser.get('GeneralOptions','selectBins')
        self.histLocation = configFileParser.get('GeneralOptions','histLocation')
        self.histogram    = configFileParser.get('GeneralOptions','histogram')
        self.plotRange    = configFileParser.get('GeneralOptions','plotRange')
        self.sortList     = configFileParser.getint('GeneralOptions','sortList')
        self.createTex    = configFileParser.getint('GeneralOptions','createTex')
        ## List Files
        self.processList  = configFileParser.get('ListFiles','processList')


    def Run(self):

        ## Make the list from the config file
        l_range  = PythonUtils.makeListFromString(self.plotRange, ',')
        t_select = PythonUtils.makeTupleFromString(self.selectBins, ',','?')
        
        ## Check the input and process files exist
        l_file = [self.processList, self.inputFile]
        for file in l_file:
            PythonUtils.doesFileExist(file)
        
        ## Loop over the ProcessList files
        f = open(self.processList, 'r')
        for line in f:
            if line.startswith('#'):
                continue
            
            l_process = PythonUtils.makeListFromString(line.strip(), ',')
            PythonUtils.doesFileExist(l_process[0])
            t_process = PythonUtils.makeTupleFromFile(l_process[0], ',')
            l_yield = []
            ##ll
            ll_VH = ['VH']
            ll_VV = ['VV']
            ll_top = ['top']
            ll_stop = ['stop']
            ll_Wl = ['W+l']
            ll_Wcl = ['W+cl']
            ll_Whf = ['W+hf']
            ll_Zl = ['Z+l']
            ll_Zcl = ['Z+cl']
            ll_Zhf = ['Z+hf']
            ll_MJe = ['MJe']
            ll_MJm = ['MJm']
            ll_tot = ['Total']
            ll_data = ['Data']
            for bin in t_select:
                if bin[0] == 'all':
                    select = self.selectOn + '-' + bin[0]
                else:
                    select = self.selectOn + '-' + bin[0] + '-' + bin[1]
           
                
                ## nEvents
                nSignal = 0
                nTot    = 0
                nTop    = 0
                nStop   = 0
                nWl     = 0
                nWh     = 0
                nWcl    = 0
                nZl     = 0
                nZh     = 0
                nZcl    = 0
                nVV     = 0
                nMJe    = 0
                nMJm    = 0
                nData   = 0
                ##nEventsErr
                eSignal = 0
                eTot    = 0
                eTop    = 0
                eStop   = 0
                eWl     = 0
                eWh     = 0
                eWcl    = 0
                eZl     = 0
                eZh     = 0
                eZcl    = 0
                eVV     = 0
                eMJe    = 0
                eMJm    = 0
                eData   = 0

                for i in xrange(len(t_process)):
                    process, sLocation, pType, selection, SF = t_process[i]
                    location = sLocation + '/all/' + select + '/' + self.histLocation
                    hist = ROOTUtils.retrieveHistogram(self.inputFile, location, self.histogram)
                    yValue, yErr = ROOTUtils.getYield(hist, l_range[0], l_range[1], t_process[i][4])
                    if pType == "SIGNAL":
                        nTot    += yValue
                        nSignal += yValue
                        eSignal += yErr
                        eTot    += yErr
                    elif pType == "W+H":
                        nTot += yValue
                        nWh  += yValue
                        eWh  += yErr
                        eTot += yErr
                    elif pType == "W+CL":
                        nTot += yValue
                        nWcl += yValue
                        eWcl  += yErr
                        eTot += yErr
                    elif pType == "W+L":
                        nTot += yValue
                        nWl  += yValue
                        eWl  += yErr
                        eTot += yErr
                    elif pType == "Z+H":
                        nTot += yValue
                        nZh  += yValue
                        eZh  += yErr
                        eTot += yErr
                    elif pType == "Z+CL":
                        nTot += yValue
                        nZcl += yValue
                        eZcl  += yErr
                        eTot += yErr
                    elif pType == "Z+L":
                        nTot += yValue
                        nZl  += yValue
                        eZl  += yErr
                        eTot += yErr
                    elif pType == "TOP":
                        nTot += yValue
                        nTop += yValue
                        eTop += yErr
                        eTot += yErr
                    elif pType == "STOP":
                        nTot  += yValue
                        nStop += yValue
                        nStop += yErr
                        eTot  += yErr
                    elif pType == "VV":
                        nTot += yValue
                        nVV  += yValue
                        eVV  += yErr
                        eTot += yErr
                    elif pType == "MJe":
                        nTot  += yValue
                        nMJe  += yValue
                        nMJe  += yErr
                        eTot  += yErr
                    elif pType == "MJm":
                        nTot  += yValue
                        nMJm  += yValue
                        eMJm  += yErr
                        eTot  += yErr
                    elif pType == "DATA":
                        nData += yValue
                        eData += yErr
                    else:
                        PythonUtils.Error('Not a valid selection: ' + t_process[i][2] + '!!!\n')

                
                l_VH =   [nSignal, eSignal]
                ll_VH.append(l_VH)
                l_VV =   [nVV,     eVV]
                ll_VV.append(l_VV)
                l_top =  [nTop,    eTop]
                ll_top.append(l_top)
                l_stop = [nStop,   eStop]
                ll_stop.append(l_stop)
                l_Wl =   [nWl,     eWl]
                ll_Wl.append(l_Wl)
                l_Wcl =  [nWcl,    eWcl]
                ll_Wcl.append(l_Wcl)
                l_Whf =  [nWh,     eWh]
                ll_Whf.append(l_Whf)
                l_Zl =   [nZl,     eZl]
                ll_Zl.append(l_Zl)
                l_Zcl =  [nZcl,    eZcl]
                ll_Zcl.append(l_Zcl)
                l_Zhf =  [nZh,     eZh]
                ll_Zhf.append(l_Zhf)
                l_MJe =  [nMJe,    eMJe]
                ll_MJe.append(l_MJe)
                l_MJm =  [nMJm,    eMJm]
                ll_MJm.append(l_MJm)
                l_tot =  [nTot,    eTot]
                ll_tot.append(l_tot)
                l_data = [nData,   eData]
                ll_data.append(l_data)

            l_yield = [ll_VH, ll_VV, ll_top, ll_stop, ll_Wl, ll_Wcl, ll_Whf, 
                       ll_Zl, ll_Zcl, ll_Zhf, ll_MJe, ll_MJm, ll_tot, ll_data]

            self.printToScreen(l_yield, select + ' ' + t_process[i][3])

            if self.createTex:
                    texFile = self.saveToTex(l_yield, l_process[1], self.outputFile)
                    self.runLatex(self.outputFile, texFile)


    def printToScreen(self, l_yield, evSel):

        print '++++++++++++++++++++++++++++++'
        print 'YIELD'.center(30)
        print evSel.center(30)
        print '++++++++++++++++++++++++++++++'
        print 'SAMPLE       0 - 90      90 - 120      120 - 160    160 - 200    > 200'
        for i in xrange(len(l_yield)):
            print '%-12s %-12s %-12s %-12s %-12s %-12s' % (l_yield[i][0], round(l_yield[i][1][0], 2), round(l_yield[i][2][0], 2), 
                                                           round(l_yield[i][3][0], 2), round(l_yield[i][4][0], 2), round(l_yield[i][5][0], 2)) 
            #print '%-10s %-9s %-8s' % (l_yield[i][0], round(l_yield[i][1], 2), round(l_yield[i][2], 2))

        print '++++++++++++++++++++++++++++++\n'


    def saveToTex(self, l_yield, evSel, texFile):

        file = 'Yields_' + evSel + '.tex'
        f = open(texFile + file, 'w')
        f.write('\documentclass[11pt,landscape]{aastex}\n')
        f.write('\usepackage{pdflscape} \n')
        f.write('\\begin{document}\n')
        f.write('\\begin{landscape} \n')
        f.write('\\begin{tabular}{r|c|c|c|c|c} \n')
        f.write('Sample & $p_{T}^{V} < 90$ GeV & $90 < p_{T}^{V} < 120$ GeV & $120 < p_{T}^{V} 160$ GeV & $160 < p_{T}^{V} < 200$ GeV & $p_{T}^{V} > 200$ GeV \\\ \hline\hline \n')
        for i in xrange(len(l_yield)):
            if l_yield[i][0] == 'Total' or l_yield[i][0] == 'Data':
                f.write('\hline \n')
                f.write(l_yield[i][0] + ' & ' + str(round(l_yield[i][1][0], 2)) + ' $\pm$ ' + str(round(l_yield[i][1][1], 2)) + 
                                        ' & ' + str(round(l_yield[i][2][0], 2)) + ' $\pm$ ' + str(round(l_yield[i][2][1], 2)) +
                                        ' & ' + str(round(l_yield[i][3][0], 2)) + ' $\pm$ ' + str(round(l_yield[i][3][1], 2)) +
                                        ' & ' + str(round(l_yield[i][4][0], 2)) + ' $\pm$ ' + str(round(l_yield[i][4][1], 2)) +
                                        ' & ' + str(round(l_yield[i][5][0], 2)) + ' $\pm$ ' + str(round(l_yield[i][5][1], 2)) + '\\\ \n')
            else:
                f.write(l_yield[i][0] + ' & ' + str(round(l_yield[i][1][0], 2)) + 
                                        ' & ' + str(round(l_yield[i][2][0], 2)) + 
                                        ' & ' + str(round(l_yield[i][3][0], 2)) + 
                                        ' & ' + str(round(l_yield[i][4][0], 2)) + 
                                        ' & ' + str(round(l_yield[i][5][0], 2)) + '\\\ \n' )
        f.write('\hline\hline \n')
        f.write('\end{tabular} \n')
        f.write('\end{landscape} \n')
        f.write('\end{document}\n')
        f.close()
        print '++++++++++++++++++++++++++++++++++++++++'
        print (texFile + file).center(40)
        print '++++++++++++++++++++++++++++++++++++++++\n'

        return file


    def runLatex(self, location, file):

        print location
        cmd =  'cd ' + location + '; '
        cmd += 'ls; '
        cmd += 'pdflatex ' + file + ' > /dev/null; '
        cmd += 'pdflatex ' + file + ' > /dev/null; '
        os.system(cmd)

        print '++++++++++++++++++++++++++++++'
        print 'FILE: ' + location + file + '.pdf Created'
        print '++++++++++++++++++++++++++++++\n'
            

def main():

    use = '''

    Example:

    python PYTHON/MODULES/runYieldCalc.py --MainConfigFile=ConfigFiles/Yields/MainConfigFile/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option("--MainConfigFile", dest="MainConfigFile", default="", type="string", help="Main config file for calculating the yields of our histograms")
    options, args = parser.parse_args()

    if options.MainConfigFile:
        yieldCalc = YieldCalc(options.MainConfigFile)
        yieldCalc.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
