##
## File for storing ROOT functions
##
from ROOT import TFile, gDirectory, Double

def retrieveHistogram(inputFile, h_Path, h_Name):

    h_file = TFile(inputFile)
    gDirectory.cd(h_Path)
    h = gDirectory.Get(h_Name)
    h.SetDirectory(0)
    
    return h


def getYield(h, min, max, sf):

    xMin = h.FindBin(float(min))
    xMax = h.FindBin(float(max))
    yErr = Double(0.0)
    y = h.IntegralAndError(xMin, xMax, yErr) * float(sf)
    
    return y, yErr
