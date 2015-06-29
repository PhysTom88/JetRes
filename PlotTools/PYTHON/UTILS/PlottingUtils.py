# Collection of Functions to help plot histograms

## We need math and sys
import math, sys, numpy
## For handling trees we need array
from array import array
## We need the following root functions
from ROOT import TLatex, TPad, TList, TH1, TH1F, TH2F, TH1D, TH2D, TFile, TTree, TCanvas, TLegend, SetOwnership, gDirectory, TObject, gStyle, gROOT, TGraph, TMultiGraph, TColor, TAttMarker, TLine, TF1, THStack, TAxis, TStyle, TPaveText, TAttFill, TProfile
## Pythonfunctions
import PythonUtils
## General Root functions
import ROOTUtils

def setupLegend(t_plots, x1, y1, x2, y2, textSize):
    
    l = TLegend(float(x1), float(y1), float(x2), float(y2))
    SetOwnership(l, 0)
    l.SetFillColor(0)
    l.SetBorderSize(0)
    l.SetTextSize(float(textSize))
    for i in reversed(xrange(len(t_plots))):
        if t_plots[i][1]:
            l.AddEntry(t_plots[i][0], t_plots[i][1], t_plots[i][2])

    l.Draw()

def setupTextOnPlot(plotText, t_textSize, t_alignment, t_x,  t_start, t_gap):

    l_plotText = PythonUtils.makeListFromString(plotText, '?')
    t = TLatex()
    t.SetNDC()
    t.SetTextSize(float(t_textSize))
    t.SetTextAlign(int(t_alignment))
    for item in l_plotText:
        t.DrawLatex(float(t_x), float(t_start), item)
        t_start = float(t_start) - float(t_gap)


def setupHistogram():

    '''
    Setting up the Histogram
    '''

def setupAxes(h, xLabel, yLabel, xOffset, yOffset, textSize, xMin, xMax, y_scale):

    h.GetXaxis().SetRangeUser(float(xMin), float(xMax))
    
    h.GetXaxis().SetTitle(xLabel)
    h.GetXaxis().SetTitleOffset(float(xOffset))
    h.GetXaxis().SetTitleSize(float(textSize))
    h.GetXaxis().SetLabelSize(float(textSize))

    h.GetYaxis().SetTitle(yLabel)
    h.GetYaxis().SetTitleOffset(float(yOffset))
    h.GetYaxis().SetTitleSize(float(textSize))
    h.GetYaxis().SetLabelSize(float(textSize))

    yMax = h.GetMaximum() * float(y_scale)
    h.SetMaximum(yMax)


def ATLASStyle():

    '''
    Adding the ATLAS Style to the Plots
    '''

def savePlots(c, saveString, l_saveAs):

    for extension in l_saveAs:
        c.Print(saveString + '.' + extension)

def rebin(h, binWidth):

    xMax  = h.GetXaxis().GetXmax()
    xMin  = h.GetXaxis().GetXmin()
    nBins = h.GetXaxis().GetNbins()

    width = math.fabs(xMax - xMin) / nBins
    factor = 0
    if width:
        factor = float(binWidth) / width

    if factor >= 1 or not binWidth:
        return h.Rebin(int(factor))
    else:
        return h
    
def blindingPlots(h, b_low, b_high):

    nEntries = h.GetNbinsX() + 2
    for i in xrange(0, nEntries, 1):
        if h.GetBinLowEdge(i) >= float(b_low) and h.GetBinLowEdge(i) <= float(b_high):
            h.SetBinContent(i, 0)
            h.SetBinError(i, 0)

    return h

def mergeData(l_data, doBlinding, b_low, b_high):

    h_data = l_data[0].Clone('h_data')
    h_data.Reset()
    h_data.SetTitle('')

    nBins = h_data.GetNbinsX()
    for b in xrange(1, nBins+1, 1):
        bc = 0
        be = 0
        for h in l_data:
            bc += h.GetBinContent(b)
            be += h.GetBinError(b)

        h_data.SetBinContent(b, bc)
        h_data.SetBinError(b, be)

    return h_data

def getStatUncert(h):

    hMC = h.Clone()
    hMC.SetDirectory(0)
    hMC.Reset()
    hMC.SetTitle('')

    for bin in xrange(1, h.GetNbinsX() + 1, 1):
        n = h.GetBinContent(bin)
        e = h.GetBinError(bin)
        hMC.SetBinContent(bin, n)
        hMC.SetBinError(bin, e)

    return hMC


def getRelError(h):

    hC = h.Clone()
    hC.SetDirectory(0)
    hC.Reset()
    hC.SetTitle("")

    for bin in xrange(1, h.GetNbinsX() + 1, 1):
        n = h.GetBinContent(bin)
        e = h.GetBinError(bin)
        if n !=0:
            hC.SetBinContent(bin, 0)
            hC.SetBinError(bin, e / n)
    
    return hC


def getRatio(h_data, h_MC, doBlinding, b_low, b_high):

    h_ratio = h_data.Clone('h_ratio')
    h_ratio.Reset()
    h_ratio.SetTitle("")

    nBins = h_ratio.GetNbinsX()
    for bin in xrange(1, nBins + 1, 1):
        nData = h_data.GetBinContent(bin)
        eData = h_data.GetBinError(bin)
        nMC   = h_MC.GetBinContent(bin)
        eMC   = h_MC.GetBinError(bin)
        if nData > 1e-6 and eData > 1e-6 and nMC > 1e-6:
            nRatio = (nData - nMC) / nMC
            eRatio = eData / nMC

            h_ratio.SetBinContent(bin, nRatio)
            h_ratio.SetBinError(bin, eRatio)
            if int(doBlinding):
                h_ratio = blindingPlots(h_ratio, b_low, b_high)
    
    return h_ratio


def stackHistograms(t_plots, t_processList, l_histoList, l_legendList, l_textList, l_axisList, saveAs,l_ratioList,  saveString, tagText):

    ''' 
    PURPOSE:

    Function to create stacked plots and save them to the local disk.
    This function will:
        * Create a stacked plot
        * Create a ratio plot
        * Allow for Blinding
        * Save the canvas as requested
    '''
    # Release the variables from the lists
    h_st, location_suf, name, c_x, c_y, v_rebin, xMin, xMax, doBlinding, b_low, b_high = l_histoList
    l_st, l_x1, l_y1, l_x2, l_y2, l_textSize = l_legendList
    t_st, plotText, t_textSize, t_alignment, t_start, t_gap, t_x = l_textList
    a_st, xLabel, yLabel, xOffset, yOffset, a_labelSize, a_textSize, y_scale = l_axisList
    r_st, doRatio, r_yLabel, r_xOffset, r_yOffset, r_labelSize, r_textSize = l_ratioList
    len_plots = len(t_plots)

    plotText = plotText + tagText
    
    l_overlay = []
    l_data    = []
    sh        = THStack('sh', '')
    t_legend = []
    listMC = TList()
    for i in xrange(len_plots):
        process, location_pre, v_colour, v_scale, ovack, sigrouta, l_marker, sel = t_processList[i]
        histogram = rebin(t_plots[i][0], v_rebin)
        histogram.Scale(float(v_scale))
        histogram.SetLineWidth(1)
        histogram.SetLineColor(int(v_colour))
        l_legendLine = [t_plots[i][0], process, l_marker]
        t_legend.append(l_legendLine)
        
        if sigrouta == "DATA" and int(doBlinding):
            histogram = blindingPlots(histogram, b_low, b_high)
        if ovack == "STACK":
            if sigrouta == "BACKGROUND":
                listMC.Add(histogram)
            histogram.SetFillColor(int(v_colour))
            sh.Add(histogram)
        elif ovack == "OVERLAY" and sigrouta != "DATA":
            l_overlay.append(histogram)
        elif ovack == "OVERLAY" and sigrouta == "DATA":
            histogram.SetMarkerStyle(8)
            histogram.SetMarkerColor(1)
            l_data.append(histogram)
        else:
            print "\n%s or %s are not a valid options" % (sigrouta, ovack)
            sys.exit(1)
    mergeMC = histogram.Clone('mergeMC')
    mergeMC.Reset()
    mergeMC.Merge(listMC)

    gROOT.SetBatch(1)
    c = TCanvas('c', 'c', int(c_x), int(c_y))
    gStyle.SetOptStat(0)
    if int(doRatio):
        m_Pad = TPad('m_pad', 'm_pad', 0, 0.30, 1, 1)
        r_Pad = TPad('r_pad', 'r_pad', 0, 0, 1, 0.30)
        m_Pad.Draw()
        r_Pad.Draw()
        m_Pad.SetTopMargin(0.05)
        m_Pad.SetBottomMargin(0.01)
        r_Pad.SetTopMargin(0)
        r_Pad.SetBottomMargin(0.3)
        m_Pad.cd()
        m_Pad.SetTicks(1)
        m_Pad.Update()
    else:
        c.SetTicks(1)
        c.Update
    
    # Draw our plots we defined earlier. First the stacked plot, then any overlaid plots and finally data
    sh.Draw()
    if l_overlay:
        for i in xrange(len(l_overlay)):
            l_overlay[i].Draw('hist same')
    h_MCerr = getStatUncert(mergeMC)
    h_MCerr.SetMarkerSize(0)
    h_MCerr.SetFillColor(921)
    h_MCerr.SetFillStyle(3344)
    h_MCerr.Draw('e2s same')
    t_legend.append([h_MCerr, 'Stat Uncert.', 'f']) 

    if l_data:
        h_data = mergeData(l_data, doBlinding, b_low, b_high)
        h_data.Draw('epsames')
    
    ## Next up is to add the styling:
    ## 1, Axis labels
    ## 2. Text on the plot
    ## 3. Legend
    if not int(doRatio):
        setupAxes(sh, xLabel, yLabel, xOffset, 0.8, a_textSize, xMin, xMax, y_scale)
    else:
        sh.SetMinimum(0.001)
        setupAxes(sh, "", yLabel, -999, yOffset, a_textSize, xMin, xMax, y_scale)

    setupLegend(t_legend, l_x1, l_y1, l_x2, l_y2, l_textSize)
    setupTextOnPlot(plotText, t_textSize, t_alignment, t_x, t_start, t_gap)
    
    if int(doRatio):
        r_Pad.cd()
        r_Pad.SetTicks(1)
        r_Pad.Update()
        l_mc   = TList()
        l_data = TList()
        for i in xrange(len_plots):
            l_histogram = rebin(t_plots[i][0], v_rebin)
            process, location_pre, v_colour, v_scale, ovack, sigrouta, l_marker, tag = t_processList[i] 
            if sigrouta == "SIGNAL":
                l_mc.Add(l_histogram)
            elif sigrouta == "BACKGROUND":
                l_mc.Add(l_histogram)
            elif sigrouta == "DATA":
                l_data.Add(l_histogram)
            elif sigrouta == "OVERLAY":
                pass
            else:
                print "\nOption %s not available" % (sigrouta)

        mh_MC = l_histogram.Clone('mh_MC')
        mh_MC.Merge(l_mc)

        h_statMC = getRelError(mh_MC)
        h_statMC.SetMarkerSize(0)
        h_statMC.SetFillColor(921)
        h_statMC.SetFillStyle(3344)
        h_statMC.Draw('e2s')
        setupAxes(h_statMC, xLabel, r_yLabel, r_xOffset, r_yOffset, r_textSize, xMin, xMax, 1)
        h_statMC.GetYaxis().SetRangeUser(-0.38, 0.38)
       
        mh_data = l_histogram.Clone('mh_data')
        mh_data.Merge(l_data)
        h_dataMC = getRatio(mh_data, mh_MC, doBlinding, b_low, b_high)
        h_dataMC.Draw('epsames')
 
        h_line = TLine(float(xMin), 0, float(xMax), 0)
        h_line.SetLineWidth(2)
        h_line.SetLineColor(1)
        h_line.SetLineStyle(2)
        h_line.Draw('same')
    
    savePlots(c, saveString, saveAs)

def overlayHistograms(t_plots, t_overlayList, l_histo, l_legend, l_text, l_axis,
                      l_saveAs, s_save):

    '''
    PURPOSE:

    This Function will:
        * Rebin and alter histograms
        * Apply a fit to the histograms
        * Plot them all on the same canvas
        * Add the aesthetic features
    '''
    # Declare the variables from our lists
    h_str, location_suf, c_x, c_y, drawGrid, v_rebin, xMin, xMax, fit, doNorm = l_histo
    l_str, l_x1, l_y1, l_x2, l_y2, l_textSize = l_legend
    t_str, plotText, t_textSize, t_alignment, t_start, t_gap, t_x = l_text
    a_str, xLabel, yLabel, xOffset, yOffset, a_labelSize, a_textSize, y_scale = l_axis
    
    # Setup the canvas before filling
    gROOT.SetBatch(1)
    c = TCanvas('c', 'c', int(c_x), int(c_y))
    gStyle.SetOptStat(0)
    c.SetTickx(1)
    c.SetTicky(1)
    if int(drawGrid):
        c.SetGridx(1)
        c.SetGridy(1)
    c.Update()

    t_legend = []
    for i in xrange(len(t_plots)):
        f_min = t_overlayList[i][5]
        f_max = t_overlayList[i][6]
        colour = int(t_overlayList[i][3])
        h = rebin(t_plots[i][0], float(v_rebin))
        h.SetLineWidth(1)
        h.SetLineColor(colour)
        l_legendLine = [t_plots[i][0], t_overlayList[i][0], t_overlayList[i][4]]
        t_legend.append(l_legendLine)
        
        ## Get the numerical range for SD ranges
        if 'SIGMA' in str(f_min) or 'SIGMA' in str(f_max):
            f_min, f_max = ROOTUtils.getSigmaFitRange(h, f_min, f_max)
        
        if int(doNorm):
            scale = 1 / h.Integral()
            h.Scale(scale)

        if i == 0:
            h.Draw()
            h.SetTitle('')
            setupAxes(h, xLabel, yLabel, xOffset, yOffset, 
                      a_textSize, xMin, xMax, y_scale)
        else:
            h.GetXaxis().SetRangeUser(float(xMin), float(xMax))
            h.Draw('HIST SAME')

        if fit == 'BUKIN':
            fh = ROOTUtils.drawBukin(h, f_min, f_max)
            fh.SetLineColor(colour)
            fh.Draw('HISTSAME')
    
    setupLegend(t_legend, l_x1, l_y1, l_x2, l_y2, l_textSize)
    setupTextOnPlot(plotText, t_textSize, t_alignment, t_x, t_start, t_gap)
    savePlots(c, s_save, l_saveAs)

def createTwoD(l_histo, xValue, yValue, vMarker, vMarkerSize, vColour):

    '''Objective:
         * Create a 2D plot using an x and y value
         * Return the plot
    '''

    ## Splitting the histo list
    h_st, location, c_x, c_y, xMin, xMax, yMin, yMax, nBins = l_histo

    ## Define the 2D plot
    h_2d = TH2D('h_2d','', int(nBins), float(xMin), float(xMax), 
                 int(nBins), float(yMin), float(yMax))
    h_2d.Fill(float(xValue), float(yValue))
    h_2d.SetMarkerStyle(vMarker)
    if vMarkerSize != -1:
        h_2d.SetMarkerSize(vMarkerSize)
    h_2d.SetMarkerColor(vColour)
    h_2d.SetDirectory(0)

    return h_2d


def overlayTwoD(l_plots, t_legend, l_histo, l_legend, l_text,
                l_axis, saveDir, l_saveAs):

    ## De-list the list objects:
    a_str, xLabel, yLabel, xOffset, yOffset, a_labelSize, a_textSize = l_axis
    h_str, h_location, c_x, c_y, xMin, xMax, yMin, yMax, nBins = l_histo
    l_str, l_x1, l_y1, l_x2, l_y2, l_textSize = l_legend
    t_str, plotText, t_textSize, t_alignment, t_start, t_gap, t_x = l_text

    ## Setup the canvas
    gROOT.SetBatch(1)
    c = TCanvas('c', 'c', int(c_x), int(c_y))
    gStyle.SetOptStat(0)
    c.SetGrid(1,1)
    c.SetTicks(1,1)
    c.Update()

    for i in xrange(len(l_plots)):
        if i == 0:
            l_plots[i].Draw()
            setupAxes(l_plots[i], xLabel, yLabel, xOffset, yOffset,
                      a_textSize, xMin, xMax, 1)
        else:
            l_plots[i].Draw('SAME p')

    setupLegend(t_legend, l_x1, l_y1, l_x2, l_y2, l_textSize)
    setupTextOnPlot(plotText, t_textSize, t_alignment, t_x, t_start, t_gap)
    savePlots(c, saveDir + h_str, l_saveAs)


def scatterPlot(l_scatter, l_file, l_histo, l_axis, 
                l_text, treeFile, saveDir, l_saveAs):

    ## De construct the list objects
    f_str, doSave, outputFile, directory, name = l_file
    s_str, tree, xBranch, yBranch, option = l_scatter
    h_str, c_x, c_y, xMin, xMax, yMin, yMax, nBins = l_histo
    a_str, xLabel, yLabel, xOffset, yOffset, a_labelSize, a_textSize = l_axis
    t_str, plotText, t_textSize, t_alignment, t_start, t_gap, t_x = l_text

    ## Read the tree
    f = TFile(treeFile, 'READ')
    t = f.Get(tree)

    v1 = array('d', [0])
    v2 = array('d', [0])

    t.SetBranchAddress(xBranch, v1)
    t.SetBranchAddress(yBranch, v2)

    ## Setup the canvas and fill it!
    gROOT.SetBatch(1)
    c = TCanvas('c', 'c', int(c_x), int(c_y))
    c.SetTicks(1,1)
    gStyle.SetOptStat(0)
    hs = TH2D('hs', '', int(nBins), float(xMin), float(xMax), 
              int(nBins), float(yMin), float(yMax))

    for i in range(0, t.GetEntries(), 1):
        t.GetEntry(i)
        x = v1[0]
        y = v2[0]
        hs.Fill(x,y)

    if int(doSave):
        hs.Draw()
        setupAxes(hs, xLabel, yLabel, xOffset, yOffset,
                  a_textSize, xMin, xMax, 1)
        ROOTUtils.saveToFile(hs, outputFile, directory, name)

    hs.Draw(option)
    setupAxes(hs, xLabel, yLabel, xOffset, yOffset,
              a_textSize, xMin, xMax, 1)
    
    setupTextOnPlot(plotText, t_textSize, t_alignment, t_x, t_start, t_gap)
    savePlots(c, saveDir + h_str, l_saveAs)


def overlayProfile(l_plot, l_legend,  l_histo, l_legendInfo, l_text, l_axis, sName, l_saveAs, tAdd):

    
    ## Destruct the lists
    a_str, xLabel, yLabel, xOffset, yOffset, a_labelSize, a_textSize = l_axis
    l_str, l_x1, l_y1, l_x2, l_y2, l_textSize = l_legendInfo
    t_str, plotText, t_textSize, t_alignment, t_start, t_gap, t_x = l_text
    h_str, tFile, c_x, c_y, xMin, xMax, yMin, yMax, nBins = l_histo
    
    ## Add the plot specific text to the other text
    plotText += tAdd

    PythonUtils.Info('      OVERLAYING PROFILES: ' + h_str + '          ')

    ## Setup the Canvas
    gROOT.SetBatch(1)
    c = TCanvas('c', 'c', int(c_x), int(c_y))
    c.SetTicks(1, 1)
    c.SetGrid(1, 1)
    c.SetLogx(1)
    gStyle.SetOptStat(0)

    for i in xrange(len(l_plot)):
        if i == 0:
            l_plot[i].Draw()
            setupAxes(l_plot[i], xLabel, yLabel, xOffset, yOffset,
                      a_textSize, xMin, xMax, 1)
            l_plot[i].GetXaxis().SetRange(20, 1200)
        else:
            l_plot[i].Draw('SAME eps')
    setupLegend(l_legend, l_x1, l_y1, l_x2, l_y2, l_textSize)
    setupTextOnPlot(plotText, t_textSize, t_alignment, t_x, t_start, t_gap)
    savePlots(c, sName, l_saveAs)


def fillProfile(d_profile, t_corrList, tName, l_histo, t_select):

    t_profile = []
    t_legend = []
    h_str, tFile, c_x, x_y, xMin, xMax, yMin, yMax, nBins = l_histo
    PythonUtils.Info('       FILLING HISTOGRAMS: ' + h_str +    '       ')
    
    f = TFile(tFile, 'READ')
    t = f.Get(tName)
    for i, entry in enumerate(t):

        if i%10000 == 0:
            PythonUtils.Info('Filling Event Number: ' + str(i)) 

        l_bin = []
        for bin in t_select:
            for i in range(len(t_corrList)):
                cName, xBranch, yBranch, sBranch, cColour, cMarker, mSize = t_corrList[i]
                if bin[0] == 'all' or PythonUtils.getSelection(entry, bin[0], bin[1], sBranch):
                    dName = h_str + '_' + bin[0] + '_' + bin[1] + '_' + t_corrList[i][0]
                    xValue = getattr(entry, xBranch)
                    yValue = getattr(entry, yBranch)
                    d_profile[bin[0] + bin[1]][dName].Fill(xValue, yValue)

    for bin in t_select:
        l_bin = []
        l_legend = []
        for i in range(len(t_corrList)):
            cName, xBranch, yBranch, sBranch, cColour, cMarker, mSize = t_corrList[i]
            dName = h_str + '_' + bin[0] + '_' + bin[1] + '_' + t_corrList[i][0]
            
            d_profile[bin[0] + bin[1]][dName].GetYaxis().SetRangeUser(float(yMin), float(yMax))
            d_profile[bin[0] + bin[1]][dName].GetXaxis().SetRangeUser(float(xMin), float(xMax))
            d_profile[bin[0] + bin[1]][dName].SetMarkerStyle(int(cMarker))
            d_profile[bin[0] + bin[1]][dName].SetMarkerColor(int(cColour))
            d_profile[bin[0] + bin[1]][dName].SetLineColor(int(cColour))
            d_profile[bin[0] + bin[1]][dName].SetTitle('')
            if int(mSize) != -1:
                d_profile[bin[0] + bin[1]][dName].SetMarkerSize(int(mSize))
            
            l_legend.append([d_profile[bin[0] + bin[1]][dName], cName, 'p'])
            l_bin.append(d_profile[bin[0] + bin[1]][dName])

        t_legend.append(l_legend)
        t_profile.append(l_bin)
    
    return t_profile, t_legend


def twoDprofile(d_ptMean, l_histo, l_corr, l_err):

    hString,c_x, c_y, yMin, yMax, hBins, saveFile = l_histo
    cName, cVar, cDir, cColor, cMarker, cSize, cMu, cDir = l_corr
    l_bin = []
    for bin in hBins.split(';'):
        l_bin.append(float(bin))

    arrBin = numpy.asarray(l_bin)
    h_prof = TH1D('h_prof', cMu, len(l_bin) - 1, arrBin)
    gROOT.SetBatch(1) 
    c = TCanvas('c', 'c', int(c_x), int(c_y))
    gStyle.SetOptStat(0)

    for k, v in d_ptMean.iteritems():
        h_prof.Fill(float(k), float(v))
    
    for b in xrange(0, len(l_bin)):
        h_prof.SetBinError(b, l_err[b])

    h_prof.SetMarkerColor(int(cColor))
    h_prof.SetLineColor(int(cColor))
    h_prof.SetMarkerStyle(int(cMarker))
    if cSize != int(-1):
        h_prof.SetMarkerSize(float(cSize))
    
    h_prof.Draw('eps')
    h_prof.SetDirectory(0)

    if saveFile != '':
        ROOTUtils.saveToFile(h_prof, saveFile, '', 'PtCorr_' + cMu)

    l_legend = [h_prof, cName, 'p']

    return h_prof, l_legend

def overlayProfile(l_prof, l_axis, l_histo, l_legend, l_text, l_legInfo, saveAs, saveString):
    
    aString, xLabel, yLabel, xOffset, yOffset, aLabSize, aTextSize = l_axis
    hString, c_x, c_y, yMin, yMax, hBins, hFile = l_histo
    lString, l_x1, l_y1, l_x2, l_y2, l_textSize = l_legend
    t_str, plotText, t_textSize, t_alignment, t_start, t_gap, t_x = l_text

    l_bins = PythonUtils.makeListFromString(hBins, ';')

    gROOT.SetBatch(1)
    c = TCanvas('c', 'c', int(c_x), int(c_y))
    gStyle.SetOptStat(0)
    c.SetTicks(1, 1)

    for i in xrange(len(l_prof)):
        if i == 0:
            l_prof[i].Draw('eps')
            setupAxes(l_prof[i], xLabel, yLabel, xOffset, yOffset,
                      aTextSize, l_bins[0], l_bins[len(l_bins) -1], 1)
            l_prof[i].SetMinimum(float(yMin))
            l_prof[i].SetMaximum(float(yMax))
            l_prof[i].SetTitle('')
            hLine = TLine(l_prof[i].GetXaxis().GetXmin(), 1, l_prof[i].GetXaxis().GetXmax(), 1)
            hLine.SetLineWidth(2)
            hLine.SetLineColor(1)
            hLine.SetLineStyle(2)
            hLine.Draw('same')
        else:
            l_prof[i].Draw('eps same')

    setupTextOnPlot(plotText, t_textSize, t_alignment, t_x, t_start, t_gap)
    setupLegend(l_legInfo, l_x1, l_y1, l_x2, l_y2, l_textSize)
    savePlots(c, saveString, saveAs)

