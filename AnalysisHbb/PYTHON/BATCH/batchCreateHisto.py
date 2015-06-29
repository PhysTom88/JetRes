##
## Script to submit jobs to create histogram Files
##

## Config Parser, os and sys
import ConfigParser, os, sys
## option parser
from optparse import OptionParser
## import my modules
import PythonUtils

class BatchSubmission(object):

    '''
    BatchSubmission:

    Class will:
        * Read in main config file
        * Loop over processes
        * Loop over variables to fill
        * Submit one job per variable per process
    '''

    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.processDir = configFileParser.get('GeneralOptions','processDir')
        self.typeDir = configFileParser.get('GeneralOptions','typeDir')
        self.mainDir = configFileParser.get('GeneralOptions','mainDir')
        self.nEvents = configFileParser.get('GeneralOptions','nEvents')
        self.outDir = configFileParser.get('GeneralOptions','outputDir')
        self.samples = configFileParser.get('GeneralOptions','samples')
        self.selectOn = configFileParser.get('GeneralOptions','selectOn')
        self.selectBins = configFileParser.get('GeneralOptions','selectBins')
        ## List Files
        self.processList = configFileParser.get('ListFiles','processList')
        self.typeList = configFileParser.get('ListFiles','typeList')
        ## Batch Options
        self.queue = configFileParser.get('BatchOptions','queue')
        self.email = configFileParser.get('BatchOptions','email')
        self.cmdLocation = configFileParser.get('BatchOptions','cmdLocation')
        self.trunkLocation = configFileParser.get('BatchOptions','trunkLocation')


    def Run(self):
        
        ##
        ## Check our files exist
        ##
        l_files = [self.processList, self.typeList]
        for file in l_files:
            PythonUtils.doesFileExist(file)
        ##
        ## Make lists from the file contents
        ##
        l_process = PythonUtils.makeListFromFile(self.processList)
        l_type    = PythonUtils.makeListFromFile(self.typeList)

        l_bSub = []
        count = 0
        for process in l_process:
            for type in l_type:
                bMainCfg = self.createConfigs(self.processDir, self.typeDir, self.mainDir, self.nEvents,
                                              self.outDir, self.samples, self.selectOn, self.selectBins,
                                               count, process.strip(), type.strip())
                bSub = self.createBatchSub(bMainCfg, self.cmdLocation, self.trunkLocation, count)
                l_bSub.append(bSub)
                count += 1

        self.submission(l_bSub, self.queue, self.email)


    def createConfigs(self, processDir, typeDir, mainDir, nEvents, outDir, samples, selectOn,
                      selectBins, count, process, type):

        pFile = processDir + str(count) + '.list'
        f = open(pFile, 'w')
        f.write(process)
        f.close()

        tFile = typeDir + str(count) + '.list'
        g = open(tFile, 'w')
        g.write(type)
        g.close()

        cFile = mainDir + str(count) + '.cfg'
        h = open(cFile, 'w')
        h.write('[GeneralOptions]\n')
        h.write('debug=0\n')
        h.write('outputFile=' + outDir + str(count) + '.root\n')
        h.write('nEvents=' + nEvents + '\n')
        h.write('samples=' + samples + '\n')
        h.write('selectOn=' + selectOn + '\n')
        h.write('selectBins=' + selectBins + '\n')
        h.write('[ListFiles]\n')
        h.write('inputList=' + pFile + '\n')
        h.write('typeList=' + tFile + '\n')
        h.close()

        return cFile

    def createBatchSub(self, bMainCfg, cmdLocation, trunkLocation, count):

        bSub = cmdLocation + str(count) + '.txt'
        f = open(bSub, 'w')
        f.write('cd ' + trunkLocation + ';')
        f.write('source ENV.sh;')
        f.write('python PYTHON/MODULES/createMJSample.py --MainConfigFile=' + bMainCfg + ';')
        f.close()

        return bSub
   

    def submission(self, l_bSub, queue, email):

        for i in xrange(len(l_bSub)):
            subCmd = 'qsub -N MultiJet_' + str(i) + ' -q ' + queue + ' -M ' + email + ' -S /bin/bash ' + str(l_bSub[i])
            print subCmd
            os.system(subCmd)

def main():

    use = '''

    Example:

    python PYTHON/BATCH/batchCreateHisto.py --MainConfigFile=ConfigFiles/Batch/MainConfigFile/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main Config File for producing Histo files on the batch')
    option, args = parser.parse_args()

    if option.MainConfigFile:
        batchSub = BatchSubmission(option.MainConfigFile)
        batchSub.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)


if __name__ == '__main__':
    main()
