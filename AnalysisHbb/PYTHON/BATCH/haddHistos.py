##
## Python script to hadd the histogram files after the batch run
##

## import option parser
from optparse import OptionParser
## import os and sys
import os, sys

def main():

    use = '''

    Example:

    python PYTHON/BATCH/haddHistos.py --histoDir=OutputFiles/Batch/ --outFile=OutputFiles/histos.root
    '''

    parser = OptionParser(usage = use)
    parser.add_option("--histoDir", dest="histoDir", default="", type="string", help="Directory containing histogram files to hadd")
    parser.add_option("--outFile", dest="outFile", default="", type="string", help="Output file name and directory")
    options, args = parser.parse_args()

    histoDir = options.histoDir
    outFile  = options.outFile


    haddCmd = 'hadd -f ' + outFile
    for root, dir, files in os.walk(histoDir):
        for file in files:
            if file.endswith('.root'):
                haddCmd += ' ' + histoDir + file
    
    os.system(haddCmd)

if __name__ == '__main__':
    main()
