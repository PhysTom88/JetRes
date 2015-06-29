##
## python script to create a beamer document with all the plots
##

## Import config parser, os and sys
import ConfigParser, os, sys
## Import the command line parser
from optparse import OptionParser

class LatexBeamer(object):

    '''
    LatexBeamer

    Class Will:
        * Collate the plots to include
        * Loop over all the plots and create
          a new slide for each plot
        * Save in the form of a beamer
    '''

    def __init__(self, configFile):

        configFileParser = ConfigParser.SafeConfigParser()
        configFileParser.read(configFile)
        ## General Options
        self.debug         = configFileParser.getint('GeneralOptions','debug')
        self.plotDir       = configFileParser.get('GeneralOptions','plotDir')
        self.plotType      = configFileParser.get('GeneralOptions','plotType')
        ## Latex Options
        self.afsArea       = configFileParser.get('LatexOptions','afsArea')
        self.latexLocation = configFileParser.get('LatexOptions','latexLocation')
        self.latexName     = configFileParser.get('LatexOptions','latexName')
        self.title         = configFileParser.get('LatexOptions','title')
        self.author        = configFileParser.get('LatexOptions','author')
        self.institute     = configFileParser.get('LatexOptions','institute')
        self.titleImage    = configFileParser.get('LatexOptions','titleImage')


    def Run(self):

        ## Build the areas from input strings
        latexFile    = self.latexLocation + self.latexName
        plotLocation = self.afsArea + self.plotDir
        titleImLocation = self.afsArea + self.titleImage

        ## Create the latex document
        self.createTitlePage(latexFile, self.title, self.author, self.institute,
                             titleImLocation)
        self.createPlotPages(latexFile, plotLocation, self.plotType)
        self.endLatex(latexFile)

    def createTitlePage(self, latexFile, title, author, institute, titleImage):

        f = open(latexFile, 'w')
        f.write('\documentclass{beamer}\n')
        f.write('\usepackage{graphicx}\n')
        f.write('\usepackage{url}\n')
        f.write('\\beamertemplatenavigationsymbolsempty\n')
        f.write('\useoutertheme{infolines}\n')
        f.write('\usetheme[height=7mm]{Rochester}\n')
        f.write('\usecolortheme[RGB={1,82,137}]{structure}\n')
        f.write('\setbeamertemplate{blocks}[rounded][shadow=True]\n')
        f.write('\\titlegraphic{\includegraphics[scale=0.4]{'+titleImage+'}}\n')
        f.write('\\title{'+title+'}\n')
        f.write('\\author{'+author+'}\n')
        f.write('\date{\\today}\n')
        f.write('\institute{'+institute+'}\n\n')
        f.write('\\begin{document}\n')
        f.write('\maketitle\n')
        f.close()

    
    def createPlotPages(self, latexFile, plotLocation, plotType):

        g = open(latexFile, 'a')
        for root, dir, filenames in os.walk(plotLocation):
            for f in filenames:
                if plotType in f:
                    name = f.replace('_', ' ')
                    plot = os.path.join(root, f)
                    g.write('\n\\begin{frame}\n')
                    g.write('\\frametitle{'+name.strip(plotType)+'}\n')
                    g.write('\\begin{itemize}\n')
                    g.write('\item COMMENT\n')
                    g.write('\end{itemize}\n')
                    g.write('\\begin{center}\n')
                    g.write('\includegraphics[scale = 0.5]{'+plot+'}\n')
                    g.write('\end{center}\n')
                    g.write('\end{frame}\n')
        
        g.close()

    
    def endLatex(self, latexFile):

        f = open(latexFile, 'a')
        f.write('\n\end{document}')
        f.close()


def main():

    use = '''

    Example:

    python LATEX/PYTHON/createLatexBeamer.py --MainConfigFile=ConfigFiles/Latex/MainConfig/MainConfigFile.cfg
    '''

    parser = OptionParser(usage = use)
    parser.add_option('--MainConfigFile', dest='MainConfigFile', default='', type='string', help='Main config file for creating a beamer presentation full of plots!')
    options, args = parser.parse_args()
    if options.MainConfigFile:
        latexBeamer = LatexBeamer(options.MainConfigFile)
        latexBeamer.Run()
    else:
        print '\nERROR: No ConfigFile Found!'
        print use
        sys.exit(1)

if __name__ == '__main__':
    main()
