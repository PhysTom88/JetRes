##
## Script for overlaying XH and WH pT reco corrections
##

from ROOT import TFile, TDirectory, TH1, TH1F, TCanvas, TLegend, TLatex, SetOwnership, gDirectory, TObject, gStyle, gROOT, TColor, TAttMarker, TLine, TAxis, TStyle, TAttFill

f = TFile('InputFiles/PtRecoCalib.root')

WH = f.Get('PtCorr_nMu_all')
ZH = f.Get('Correction')

gROOT.SetBatch(1)
c = TCanvas('c', 'c', 800, 600)
gStyle.SetOptStat(0)
c.SetTicks(1,1)

WH.Draw()
WH.SetTitle('')
WH.SetLineColor(868)
WH.SetMarkerColor(868)
WH.SetMarkerStyle(33)
WH.SetMarkerSize(2)

ZH.Draw('SAME')
ZH.SetLineColor(807)
ZH.SetMarkerColor(807)
ZH.SetMarkerStyle(22)
ZH.SetMarkerSize(1.5)

## Setup Axes
WH.GetXaxis().SetRangeUser(20, 280)
WH.SetMaximum(1.23)
WH.SetMinimum(0.97)
WH.GetXaxis().SetTitle('p_{T}^{Reco}')
WH.GetXaxis().SetTitleOffset(0.95)
WH.GetXaxis().SetTitleSize(0.040)
WH.GetXaxis().SetLabelSize(0.040)

WH.GetYaxis().SetTitle('<p_{T}^{Reco}/p_{T}^{Truth}>')
WH.GetYaxis().SetTitleOffset(1.05)
WH.GetYaxis().SetTitleSize(0.040)
WH.GetYaxis().SetLabelSize(0.040)

## Legend Setup
l = TLegend(0.60, 0.77, 0.88, 0.89)
l.SetFillColor(0)
l.SetBorderSize(0)
l.SetTextSize(0.04)
l.AddEntry(WH, 'WH #rightarrow l#nu b#bar{b} p_{T}^{Reco}', 'p')
l.AddEntry(ZH, 'ZH #rightarrow ll b#bar{b} p_{T}^{Reco}', 'p')
l.Draw('SAME')

## Text On Plot
t = TLatex()
t.SetNDC()
t.SetTextSize(0.04)
t.SetTextAlign(13)
t.DrawLatex(0.13, 0.87, '#bf{Simulation}')
t.DrawLatex(0.13, 0.83, '#bf{#it{2 b-Tag; 1l ; p_{T}^{V} inc.}}')

## Line at y = 1
line = TLine(20, 1, 280,1)
line.SetLineWidth(2)
line.SetLineColor(1)
line.SetLineStyle(2)
line.Draw('SAME')

c.Print('Plots/Profile/prof_cw_ZH_WH.pdf')
