##
## Neural Network Utilities
##
import PythonUtils

def appendNN(d, NNList, l_Append):

    l_NN = NeuralNetwork.getListNN(NNList, debug=False)
    for d_NN in l_NN:
        for value in l_Append:
            NNname = d_NN[d_NN.keys()[0]][1]
            d[NNname + value] = NNname + value

    return d

def getNNInfo(NNListFile, name):

    '''
    Get the neural network information
    '''
    NNNameRaw   = name[0:-1]
    ListNN      = getListNN(NNListFile)
    NNDict      = getNNDict(ListNN, NNNameRaw)
    NNObject    = NNDict[NNDict.keys()[0]]
    NNTrainInfo = stringNN(NNObject, 'c') 

    return NNTrainInfo

def getListNN(file):

    '''
    Get NN List
    '''
    fileList = open(file, 'r')
    result = []
    for f in fileList:
        NNOptionParser = ConfigParser.SafeConfigParser()
        NNOptionParser.read(f.strip())
        # NNOptions
        initialNumber             = NNOptionParser.getint('NNOptions','initialNumber')
        randomNumberVariations    = NNOptionParser.getint('NNOptions','randomNumberVariations')
        neuronActivationFunctions = NNOptionParser.get('NNOptions','neuronActivationFunctions')
        learningMethods           = NNOptionParser.get('NNOptions','learningMethods')
        inputLayers               = NNOptionParser.get('NNOptions','inputLayers')
        hiddenLayers              = NNOptionParser.get('NNOptions','hiddenLayers')
        outputLayers              = NNOptionParser.get('NNOptions','outputLayers')
        epochInfo                 = NNOptionParser.get('NNOptions','epochInfo')
        useDefaults               = NNOptionParser.get('NNOptions','useDefaults')
        # GeneralOptions
        doInputCombinations       = NNOptionParser.getint('GeneralOptions','doInputCombinations')
        inputComboLength          = NNOptionParser.getint('GeneralOptions','inputComboLength')
        doOutputCombinations      = NNOptionParser.getint('GeneralOptions','doOutputCombinations')
        outputComboLength         = NNOptionParser.getint('GeneralOptions','outputComboLength')
        # Create the lists and dicts for training
        activationFunctionList = PythonUtils.makeListFromString(neuronActivationFunctions, ',')
        learningMethodList     = PythonUtils.makeListFromString(learningMethods, ',')
        inputLayerList         = PythonUtils.makeListFromString(inputLayers, ',')
        outputLayerList        = PythonUtils.makeListFromString(outputLayers, ',')
        epochDict              = PythonUtils.makeDictFromString(epochInfo, ':', ',')

        result = result + getResult(initialNumber, randomNumberVariations, activationFunctionList, 
                                    learningMethodList,  inputLayersList,outputLayersList, 
                                    hiddenLayers, epochDict , useDefaults)

def getNNDict(l_NN, name):

    '''
    Get NN dict
    '''
    for dict in l_NN:
        NNname=NNdict[NNdict.keys()[0]][1]
        if NNname == name:
            return dict

def stringNN(object, option):

    '''
    Get training Info
    '''
    if option == 'c':
        result = '%-7s %-7s %-4s %-100s %-10s' % (NN[4], NN[5], str(NN[6]), NN[7], NN[9])

    return result

def getResult(initialNumber, randomNumberVariations, neuronActivationFunctions, learningMethods,
              inputLayers, outputLayers, hiddenLayers, epochDict, useDefaults):

    '''
    Get the result to parse back
    '''
    l_NN = []
    counter = initialNumber - 1
    for function in neuronActivationFunctions:
        for method in learningMethods:
            for iLayer in inputLayers:
                for oLayer in outputLayers:
                    for i in xrange(randomNumberVariations):
                        counter += 1
                        d_treeNN = {}
                        for tree in epochDict:
                            NN = ['NN', 'n' + str(counter), tree, function, method, epochDict[tree], 
                                   PythonUtils.updateListVars('r', iLayer, ''), hiddenLayers, 
                                   oLayer, useDefaults]
                            d_treeNN[tree] = NN
                        l_NN.append(d_treeNN)

    return l_NN
