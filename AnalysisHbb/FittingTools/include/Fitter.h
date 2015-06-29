#ifndef FITTER_H
#define FITTER_H

//c++
#include <iostream>
#include <string>
#include <map>
//
#include "TFile.h"
#include "TString.h"
#include "TH1D.h"
#include "TMinuit.h"

void doFitting(std::map<TString, TH1D*> pro_hist, std::string sf_file_location, std::string tag);
void initMinuit();
void doFit();
void writeFiles(std::string sf_file_location, double pf_chiSq, std::string tag);

#endif
