################################
#
# Use this to run the different 
# parts of the analysis Tools
# 
# Author: Tom Ravenscroft
#
################################

function writeUsage()
{
cat <<EOD
Script to run the options for Analysis Tools

Usage: runAnalysisTools.sh [options]

        --doStacking
        --doOverlay
        --doTwoD
        --dodoMeanRMSRes
        --doSensitivity

Author: Tom Ravenscroft

EOD
}

function runningExample()
{

cat <<EOF
    
    Example of running the script.

    Consult the respective configuration files for the
    details of each module

    ===== Example for Running =====
    ./runAnalysisTools.sh --doStacking yes --doOverlay yes --doTwoD yes --doMeanRMSRes yes --doSensitivity yes

    Change the yes to no for not doing that option

EOF
}

function parseOptions()
{
    while [ $# -ne 0 ]; do
        case $1 in
            --doStacking) shift; doStacking=$1; shift;;
            --doOverlay) shift; doOverlay=$1; shift;;
            --doTwoD) shift; doTwoD=$1; shift;;
            --doMeanRMSRes) shift; doMeanRMSRes=$1; shift;;
            --doSensitivity) shift; doSensitivity=$1; shift;;
            -h|--h*) writeUsage; runningExample; kill -INT $$;;
            *) echo -e "Bad Option $1, use -h for help"; kill -INT $$;;
        esac
    done
}
# Set script variables
doStacking=default
doOverlay=default
doTwoD=default
doMeanRMSRes=default
doSensitivity=default
parseOptions $*

cat <<EOF
#############################
##
##    SETUP PYTHON PATH
##
#############################
PYTHONPATH=$PYTHONPATH:${PWD}/PYTHON/UTILS:${PWD}/PYTHON/MODULES
EOF
export PYTHONPATH=$PYTHONPATH:${PWD}/PYTHON/UTILS:${PWD}/PYTHON/MODULES

#########################
##
## RUN STACKING
##
#########################
if [[ ${doStacking} == "yes" ]]; then
    echo ""
    echo "          CREATE STACKED PLOTS           "
    echo "========================================="
    python PYTHON/MODULES/runStacking.py --MainConfigFile=ConfigFiles/Stacking/MainConfig/MainConfigFile.cfg
fi

#########################
##
## RUN OVERLAY
##
#########################
if [[ ${doOverlay} == "yes" ]]; then
    echo ""
    echo "         CREATE OVERLAID PLOTS           "
    echo "========================================="
    python PYTHON/MODULES/runOverlayPlots.py --MainConfigFile=ConfigFiles/Overlay/MainConfig/MainConfigFile.cfg
fi

#########################
##
## RUN TWO D
##
#########################
if [[ ${doTwoD} == "yes" ]]; then
    echo ""
    echo "           CREATE TWO D PLOTS            "
    echo "========================================="
    python PYTHON/MODULES/runTwoD.py --MainConfigFile=ConfigFiles/TwoD/MainConfig/MainConfigFile.cfg
fi

#########################
##
## RUN MEAN RMS RES
##
#########################
if [[ ${doMeanRMSRes} == "yes" ]]; then
    echo ""
    echo "   CALCULATE MEAN RMS AND RESOLUTION    "
    echo "========================================"
    python PYTHON/MODULES/runMeanResRMS.py --MainConfigFile=ConfigFiles/MeanResRMS/MainConfig/MainConfigFile.cfg
fi

#########################
##
## RUN SENSITIVITY
##
#########################
if [[ ${doSensitivity} == "yes" ]]; then
    echo ""
    echo "          CALCULATE SENSITIVITY       "
    echo "======================================"
    python PYTHON/MODULES/runSensitivity.py --MainConfigFile=ConfigFiles/Sensitivity/MainConfig/MainConfigFile.cfg
fi
