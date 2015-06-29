/*
This will call the ROOT function which will do
the fit and get the scale factors
*/ 

#include "Fitter.h"
#include <fstream>

void fitfunction(Int_t &npar, Double_t *gin, Double_t &result, Double_t *par, Int_t iflag);
Int_t ierflg;
TString parnames[2];
Double_t arglist[2];
Double_t vstart[2], step[2];
Double_t amin, edm, errdef;
Int_t nvpar, nparx, icstat;
std::map<TString, TH1D*> map_hist;
Double_t m_SFMJ[2];
Double_t m_SFMC[2];
TMinuit* m_minuit;
double fChiSq;


void doFitting(std::map<TString, TH1D*> pro_hist, std::string sf_file_location, std::string tag) {

    map_hist = pro_hist;
    initMinuit();
    doFit();
    writeFiles(sf_file_location, fChiSq, tag);

}


void writeFiles(std::string sf_file_location, double pf_chiSq,  std::string tag) {
     
    ofstream outFile;
    outFile.open((sf_file_location + tag + ".txt").c_str());
    outFile << "MJ:: \t" << m_SFMJ[0] << "\t+/-\t" << m_SFMJ[1] << std::endl;
    outFile << "MC:: \t" << m_SFMC[0] << "\t+/-\t" << m_SFMC[1] << std::endl;
    outFile << "POST FIT CHISQ:: \t" << pf_chiSq << std::endl;
    outFile.close();

}


void doFit() {

    std::cout << "Fitting the Following: " << std::endl;
    for (int i = 0; i < 2; i++) {
        std::cout << parnames[i] << std::endl;
    }
    m_SFMJ[0] = 0.50; step[0] = 0.1; m_SFMJ[1] = 50.0;
    m_minuit->mnparm(0, parnames[0], m_SFMJ[0], step[0], 0.0,50.0,ierflg);
    m_minuit->mnparm(1, parnames[1], m_SFMC[0], step[1], 0.5,5.0,ierflg);

    for (int i = 0; i < 2; i++) {
        m_minuit->Release(i);
    }
    arglist[0] = 50000;
    arglist[1] = 1.;

    m_minuit->mnexcm("MIGRAD",arglist,2,ierflg);
    m_minuit->mnexcm("HESSE", arglist,1,ierflg);
    m_minuit->mnstat(amin,edm,errdef,nvpar,nparx,icstat);
    m_minuit->mnprin(3,amin);

    gMinuit->GetParameter(0,m_SFMJ[0],m_SFMJ[1]);
    gMinuit->GetParameter(1,m_SFMC[0],m_SFMC[1]);
}

void initMinuit() {

    m_minuit = new TMinuit(2);
    m_minuit->SetFCN(fitfunction);

    ierflg = 0;
    parnames[0] = "MJ SF";
    parnames[1] = "MC SF";

    arglist[0] = 1;
    gMinuit->mnexcm("SET ERR", arglist, 1, ierflg);
    arglist[0] = 50000;
    arglist[1] = 1.;

    for (int i = 0; i < 2; i++) {
        vstart[i] = 1;
        step[i]   = 0.01;
    }

    vstart[0] = 1;
    step[0]   = 0.5;
    for (int i = 0; i < 2; i++) {
        gMinuit->mnparm(i, parnames[i], vstart[i], step[i], -10, 10.0, ierflg);
    }
}


void fitfunction(Int_t &npar, Double_t *gin, Double_t &result, Double_t *par, Int_t iflag) {

    std::map<TString, float> yields;
    std::map<TString, float> yieldsTotal;
    int totBin = 0;
    float delta(0);
    float chisq(0);

    // Get nBins
    Int_t nBins;
    for(std::map<TString, TH1D*>::const_iterator mc(map_hist.begin()); mc!=map_hist.end(); mc++) {
        if ((mc->first).Contains("MJ")) {
            nBins = (mc->second)->GetNbinsX();
        }
    }
    // Loop over the bins to get the yields
    for (int b=1; b < nBins + 1; b++) {
        for (std::map<TString, float>::iterator y(yields.begin()); y != yields.end(); y++) {
            y->second = 0;
        }
        if (map_hist["Data"]->GetBinContent(b) == 0) { continue; }
        totBin++;
        yields["Data"] += map_hist["Data"]->GetBinContent(b);

        for (std::map<TString, TH1D*>::const_iterator ph(map_hist.begin()); ph != map_hist.end(); ph++) {

            // skip signal and if its empty
            if (!ph->second) {continue;}
            if ((ph->first).Contains("WH")) {continue;}
            if ((ph->first).Contains("ZllH")) {continue;}
            yields[ph->first]       = ph->second->GetBinContent(b);
            yieldsTotal[ph->first] += ph->second->GetBinContent(b);
        }

        yields["MJ"] *= par[0];
        delta = yields["Data"];
        for (std::map<TString, float>::iterator y(yields.begin()); y != yields.end(); y++) {
            if ((y->first).Contains("Data")) {continue;}
            if ((y->first).Contains("WH"))   {continue;}
            if ((y->first).Contains("ZllH"))   {continue;}
            if (!(y->first).Contains("MJ")) {
                y->second *= par[1];
            }
            delta -= y->second;
        }

        float chisqLoop = (delta * delta)/yields["Data"];
        chisq += chisqLoop;
    }
    
    result = (double)chisq;
    fChiSq = result/totBin;
}
