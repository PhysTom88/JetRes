/*
This will contain the main function and will
call the other functions as they are needed
*/

#include <iostream>
#include <string>
#include <map>
#include <vector>
//
#include "ConfigFile.h"
#include "Fitter.h"
//
#include "TFile.h"
#include "TString.h"
#include "TH1D.h"
#include "TCanvas.h"

void usage(char* myprog);
std::map<TString, TH1D*> getHists(std::string& histogram_file_name, std::string& process_list_file, 
                                  std::string& fitting_histogram, std::string& histogram_location,
                                  std::string& selection, std::string& pTV_bin);

TH1D* retrieveHisto(std::string& histogram_file_name, std::string& hist_loc, std::string& fitting_histogram);

int main( int argc, char* argv[]) {

    if (argc != 2) {
        usage(argv[0]);
        return 1;
    }

    std::string configFile(argv[1]);
    
    // Configuration file initialise
    //  1) initialise the variables
    //  2) initialise the funtion
    //  3) Read the configuration file

    std::string histogram_file_name;
    std::string process_list_file;
    std::string selection;
    std::string sf_file_location;
    std::string fitting_histogram;
    std::string histogram_location;
    std::string pTV_bin;
    bool        verbose;

    ConfigFile* config = new ConfigFile(configFile);
    config->readInto(histogram_file_name, "histoFile",     std::string(""));
    config->readInto(process_list_file,   "processFile",   std::string(""));
    config->readInto(selection,           "selection",     std::string(""));
    config->readInto(sf_file_location,    "sfLocation",    std::string(""));
    config->readInto(fitting_histogram,   "fittingHisto",  std::string(""));
    config->readInto(histogram_location,  "histoLocation", std::string(""));
    config->readInto(pTV_bin,             "pTV_bin",       std::string(""));
    config->readInto(verbose,             "verbose",       bool(0));

    if (verbose) {
        std::cout << "histogram_file_name: " << histogram_file_name << std::endl;
        std::cout << "process_list_file: "   << process_list_file   << std::endl; 
        std::cout << "selection: "           << selection           << std::endl; 
        std::cout << "sf_file_location: "    << sf_file_location    << std::endl; 
        std::cout << "fitting_histogram: "   << fitting_histogram   << std::endl; 
        std::cout << "histogram_location: "  << histogram_location  << std::endl; 
        std::cout << "pTV_bin: "             << pTV_bin             << std::endl;
    }
   
    std::map<TString, TH1D*> pro_hist = getHists(histogram_file_name, process_list_file,
                                                 fitting_histogram, histogram_location, 
                                                 selection, pTV_bin);
    
    // Send the map to the doFit function - in Fitter.cxx
    doFitting(pro_hist, sf_file_location, selection);

    // Delete the pointers 
    delete config;

    return 0;
}

std::map<TString, TH1D*> getHists(std::string& histogram_file_name, std::string& process_list_file,
                                  std::string& fitting_histogram, std::string& histogram_location,
                                  std::string& selection, std::string& pTV_bin) {

    // Open the process list file and check it exists
    ifstream process_stream(process_list_file.c_str());
    if (!process_stream.is_open()) {
        std::cout << "ERROR: Process List File: " << process_list_file 
                  << " Could not be opened!"      << std::endl;
        struct INPUT_FILE_OPEN_ERROR{};
        throw INPUT_FILE_OPEN_ERROR();
    }
    
    // Declaration of the map<process, hist> 
    std::map<TString, TH1D*> pro_hist_map;
    
    // loop over the lines and build the map
    std::string process;
    float mc_sf;
    
    while (!process_stream.eof()) {
        process_stream >> process >> mc_sf;
        std::cout << "Process: " << process << " " << "SF: " << mc_sf << std::endl;
        std::string hist_loc = selection + "_0_" + process + "/all/" + pTV_bin + "/" + histogram_location + "/";
        TH1D *hist = retrieveHisto(histogram_file_name, hist_loc, fitting_histogram);
        hist->Scale(mc_sf);
        pro_hist_map[process] = hist;
    }
    process_stream.close();

    return pro_hist_map;
}

TH1D* retrieveHisto(std::string& histogram_file_name, std::string& hist_loc, std::string& fitting_histogram) {

    TFile *f = new TFile(histogram_file_name.c_str(), "READ");
    TH1D *h = (TH1D*)f->Get((hist_loc + fitting_histogram).c_str());

    return h;
}

void usage(char* myprog) {

    std::cout << "Usage: "
              << myprog << " "
              << "<ConfigFile>"
              << std::endl;

    std::cout << "Example: "
              << myprog << " "
              << "../ConfigFiles/MJCreateTemp/FittingFile/2BTag.cfg"
              << std::endl;
}
