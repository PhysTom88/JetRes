##
## File for storing ROOT functions
##
import math
import PlottingUtils, PythonUtils
import FitUtils
from ROOT import TFile, gDirectory, gROOT, TCanvas, TF1, TObject, TProfile

def retrieveHistogram(inputFile, h_Path, h_Name):

    h_file = TFile(inputFile)
    gDirectory.cd(h_Path)
    h = gDirectory.Get(h_Name)
    h.SetDirectory(0)
    
    return h

def calculateSensitivity(t_plot, l_histo, h_title):

    '''
    Calculate the bin by bin sensitivity for our stacked plots
    '''
    h_st, location, v_rebin, pTVbin = l_histo
    nBins = 0
    for i in xrange(len(t_plot)):
        histogram = PlottingUtils.rebin(t_plot[i][0], float(v_rebin))
        histogram.Scale(float(t_plot[i][3]))
        nBins = histogram.GetXaxis().GetNbins()
    totSen = 0
    totErr = 0
    for bin in range(1, nBins + 1, 1):
        sigNum = 0
        sigErr = 0
        bkgNum = 0
        bkgErr = 0
        totBkg = 0
        totBkgErr = 0
        totSigErr = 0
        for j in range(len(t_plot)):
            histogram = PlottingUtils.rebin(t_plot[j][0], float(v_rebin))
            if t_plot[j][2] == "SIGNAL":
                sigNum += histogram.GetBinContent(bin)
                sigErr += histogram.GetBinError(bin)
            elif t_plot[j][2] == "BACKGROUND":
                bkgNum += histogram.GetBinContent(bin)
                bkgErr += histogram.GetBinError(bin)
            else:
                pass
            
            totBkgErr += bkgErr * bkgErr
            totSigErr += sigErr * sigErr

        if bkgNum > 0:
            sen      = sigNum / (math.sqrt(bkgNum))
            sen_sqrd = sen*sen
            totSen  += sen_sqrd

        if bkgNum > 0 and sigNum > 0:
            senErr = sen * sen * math.sqrt(((2 * sigErr/sigNum)*(2*sigErr/sigNum)) + ((bkgErr/bkgNum)*(bkgErr/bkgNum)))
            totErr += senErr * senErr
    
    sensitivity = math.sqrt(totSen)
    totalErr    = (0.5 * math.sqrt(totErr)) / sensitivity
    return sensitivity, totalErr
            

def getHistoStat(t_plot, l_histoList, l_option, fit, name):

    # if the string is crea then we only return the intergral / nEntries
    h_str, location_suff, v_rebin, doNorm, xMin, xMax, fMin, fMax = l_histoList
    mean  = -1
    eMean = -1
    rms   = -1
    eRMS  = -1
    res   = -1
    eRes  = -1
    if 'crea' in location_suff:
        intergral = t_plot[i][0].Integral()
        entries   = t_plot[i][0].GetEntries()
        return integral / entries
    elif 're' in location_suff and name == 't':
        l_stat = [0, 0, 0]
        l_sErr = [0, 0, 0]
        return l_stat, l_sErr
    elif 'b' in location_suff and name == 't':
        l_stat = [-1, -1, -1]
        l_sErr = [-1, -1, -1]
        if l_option[0]:
            l_stat = [1, -1, -1]
            l_sErr = [0, 0, 0]
        if l_option[1]:
            l_stat = [-1, 0, -1]
            l_sErr = [0, 0, 0]
        if l_option[2]:
            l_stat = [-1, -1, 0]
            l_sErr = [0, 0, 0]
        return l_stat, l_sErr
    else:
        h = PlottingUtils.rebin(t_plot[0], v_rebin)
        h.GetXaxis().SetRangeUser(float(xMin), float(xMax))
        if int(doNorm):
            scale = 1 / h.Integral()
            h.Scale(scale)

        gROOT.SetBatch(1)
        c = TCanvas('c', 'c', 800, 600)
        h.Draw()
        ## Recalculate fMin and fMax for SD values
        if 'SIGMA' in fMin or 'SIGMA' in fMax:
            fMin, fMax = getSigmaFitRange(h, fMin, fMax)
        
        ## Now we add the fit and get the mean, RMS and Resolution
        fh = h
        if fit == 'GAUSS':
            fh.Fit("gaus","Q","")
            fh = fh.GetFunction('gaus')
            fh.Draw('SAME')
        elif fit == 'BUKIN':
            fh = drawBukin(h, float(fMin), float(fMax))
            fh.Draw('SAME')
        
        if fit == 'GAUSS' or fit == 'BUKIN':
            if l_option[0]:
                mean  = fh.GetParameter(1)
                eMean = h.GetMeanError()
            if l_option[1]:
                rms  = fh.GetParameter(2)
                eRMS = h.GetRMSError()
            if l_option[2]:
                res_mean  = fh.GetParameter(1)
                res_eMean = h.GetMeanError()
                res_rms   = fh.GetParameter(2)
                res_eRMS  = h.GetRMSError()
                res       = res_rms / res_mean
                eRes      = res * res * math.sqrt((res_eMean / res_mean) * (res_eMean / res_mean) + (res_eRMS / res_rms) * (res_eRMS / res_rms)) 
        else:
            if l_option[0]:
                mean  = fh.GetMean()
                eMean = h.GetMeanError()

            if l_option[1]:
                rms  = fh.GetRMS()
                eRMS = h.GetRMSError()

            if l_option[2]:
                res_mean  = fh.GetMean()
                res_eMean = h.GetMeanError()
                res_rms   = fh.GetRMS()
                res_eRMS  = h.GetRMSError()
                res       = res_rms / res_mean
                eRes      = res * res * math.sqrt((res_eMean / res_mean) * (res_eMean / res_mean) + (res_eRMS / res_rms) * (res_eRMS / res_rms)) 
                
        l_stat = [mean, rms, res]
        l_err  = [eMean, eRMS, eRes] 
        return l_stat, l_err


def drawBukin(h, min, max):

    mean   = h.GetMean()
    RMS    = h.GetRMS()
    height = h.GetMaximum()

    f = TF1('bukin', FitUtils.Bukin(), float(min), float(max), 8)
    f.SetParName(0, 'height')
    f.SetParName(1, 'mean')
    f.SetParName(2, 'width')
    f.SetParName(3, 'asymmetry')
    f.SetParName(4, 'size of lower tail')
    f.SetParName(5, 'size of upper tail')

    f.SetParameter(0, float(height))
    f.SetParameter(1, float(mean))
    f.SetParameter(2, float(RMS))
    f.SetParameter(3, -0.2)
    f.SetParameter(4, 0.2)
    f.SetParameter(5, 0.001)
    h.Fit('bukin', 'Q', 'histsame', float(min), float(max))
    bh = h.GetFunction('bukin')

    return bh

def getSigmaFitRange(h, fMin, fMax):

    mean = h.GetMean()
    RMS  = h.GetRMS()
    vMin = fMin.strip(' SIGMA')
    vMax = fMax.strip(' SIGMA')
    nfMin = mean - (float(vMin) * RMS)
    nfMax = mean + (float(vMax) * RMS)

    return nfMin, nfMax


def saveToFile(h, fileName, directory, name):

    f = TFile(fileName, 'UPDATE')
    path = '/'
    ## Create the directory tree
    for dir in directory.split('/'):
        path += dir + '/'
        if not gDirectory.Get(dir):
            gDirectory.mkdir(dir)

        gDirectory.cd(dir)
    ## Now the tree is written, move to the dir
    f.cd(path)
    hc = h.Clone()
    hc.Write(name, TObject.kOverwrite)
    f.Close()


def createProfile(t_corrList, t_select, l_histoList, nBins, dBins):

    d_profileBin = {}
    h_str, tFile, c_x, c_y, xMin, xMax, yMin, yMax, varBins = l_histoList
    PythonUtils.Info('       CREATING PROFILES: ' + h_str + '           ')
    for bin in t_select:
        PythonUtils.Info('Creating Profiles: ' + h_str + 
                         ' in bin: ' + bin[0] + ' -> ' + bin[1])
        d_profile = {}
        for i in range(len(t_corrList)):
            dName = h_str + '_' + bin[0] + '_' + bin[1] + '_' + t_corrList[i][0]
            d_profile[dName] = TProfile(dName, dName, int(nBins), dBins, 
                                        float(yMin), float(yMax))

        d_profileBin[bin[0] + bin[1]] = d_profile

    return d_profileBin
