##
## module for storing generic Python Functions
##
import os, sys, operator

def makeListFromString(string, delim):

    l = []
    for item in string.split(delim):
        l.append(item)

    return l

def makeListFromFloat(fl, delim):

    l = []
    for item in fl.split(delim):
        l.append(float(item))

    return l


def makeTupleFromFile(file, delim):

    f = open(file, 'r')
    t = []
    for line in f:
        if not line.startswith('#'):
            item = [x.strip() for x in line.split(delim)]
            t.append(item)

    return t

def makeDictFromString(string, kv_delim, i_delim):

    d = {}
    for name in string.split(i_delim):
        title = name.rstrip()
        key   = ""
        value = ""
        d[name.split(kv_delim)[0]] = name.split(kv_delim)[1]

    return d

def firstItemMatching(t_1, t_2):

    len_t1 = len(t_1)
    len_t2 = len(t_2)
    if len_t1 != len_t2:
        print "\nlengths of %s and %s do not match. \nCheck file contents" % (t_1, t_2)
        sys.exit(1)
    else:
        for i in xrange(len_t1):
            if t_1[i][0] == t_2[i][0]:
                return True
            else:
                print "\nItem %s and %s do not match. \nCheck file contents" % (t_1[i][0], t_2[i][0])
                sys.exit(1)

def doesDirExist(dir):

    if os.path.isdir(dir):
        return True
    else:
        print "\nDirectory: %s does not exist!" % (dir)
        sys.exit(1)

def doesFileExist(filename):

    if os.path.isfile(filename):
        print "\nFile: %s does exist. \nCarrying on" % (filename)
        return True
    else:
        print "\nFile: %s does not exist" % (filename)
        sys.exit(1)

def rankByAverage(ld_compare, compareTo, NNListFile, stat, randomVarsi, l_NNAppendVal):

    '''
    rank by the average NN training
    '''

    for i in xrange(len(ld_compare)):
        d_sorted = sorted(ld_compare[i][1].iteritems(), key = operator.itemgetter(0))
        t_info = t_average = []
        for i, type in enumerate(d_sorted):
            name  = type[0]
            value = type[1]
            if 'n' not in name:
                l_info = [name, value, '-']
                t_info.append(l_info)
            else:
                l_info = [name, value, NNUtils.getNNInfo()]
                t_average.append(l_info)

        compareValue = 0
        t_NNAverage = averageNNValue()
        for i in range(len(t_average)):
            t_NNAverage.append(t_average[i])
            if t_average[i][0] == compareTo:
                compareValue += t_average[i][1]

        sortedTuple = tuple(sorted(t_NNAverage, key = lambda item: item[1]))
        print '\n\n' + stat + '\nCORRECTION        VALUE    % FROM ' + compareTo + '    NN INFORMATION'
        for i in xrange(len(t_sorted)):
            name  = t_sorted[i][0]
            value = t_sorted[i][1]
            info  = t_sorted[i][2]
            percentDiff = round(100 * (float(value) - float(compareValue)) / float(compareValue), 2)
            print '%-17s %-10s %-15s %-20s' % (name, round(value, 4), percentDiff, info)


def rankAverageTestTrain(t_test, t_train, NNList, randomVars):

    '''
    rank by the average test train vales
    '''
    td_rank = []
    for i in xrange(len(t_test)):
        t_rank = []
        for j in xrange(len(t_test[i])):
            corr      = t_test[i][j][0]
            test_val  = t_test[i][j][1]
            train_val = t_train[i][j][1]
            rank = abs(train_val - test_val) / train_val
            l_rank = [corr, rank]
            t_rank.append(l_rank)

        d_rank = {}
        for i in xrange(len(t_rank)):
            d_rank[t_rank[i][0]] = t_rank[i][1]
            td_rank.append(d_rank)

    for i in xrange(len(td_rank)):
        d_sorted = sorted(ld_sensCalc[i][1].iteritems(), key = operator.itemgetter(0))
        t_info = t_average = []
        for i, type in enumerate(d_sorted):
            name  = type[0]
            value = type[1]
            if 'n' not in name:
                l_info = [name, value, '-']
                t_info.append(l_info)
            else:
                l_info = [name, value, NNUtils.getNNInfo()]
                t_average.append(l_info)

        for i in range(len(t_average)):
            t_NNAverage.append(t_average[i])

        print '\n\n RANK TEST TRAIN: ' + stat + '\nCORRECTION      VALUE     NNINFORMATION'
        for i in xrange(len(t_sorted)):
            name  = t_sorted[i][0]
            value = t_sorted[i][1]
            info  = t_sorted[i][2]
            print '%-17s %-10s %-20s' % (name, round(value, 4), info)
        
        
def rankByValue(ld_compare, compareTo, stat):

    '''
    rank by each individual correction
    '''
    t_i = []
    for i in xrange(len(ld_compare)):
        str_ident = ld_compare[i][0]
        t_info = []
        compareValue = 0
        d_sorted = sorted(ld_compare[i][1].iteritems(), key = operator.itemgetter(0))
        # Loop over the the sens values to write a table out
        for i, type in enumerate(d_sorted):
            name  = type[0]
            value = type[1][0]
            error = type[1][1]
            l_info = [name, value, error]
            t_info.append(l_info)

            if name == compareTo:
                compareValue += value
        t_sorted = tuple(sorted(t_info, key = lambda item: item[1]))
        ll_i = []
        print '\n\n' + stat + ' ' + str_ident + '\nCORRECTION                VALUE        ERROR       % FROM ' + compareTo
        for i in xrange(len(t_sorted)):
            name  = t_sorted[i][0]
            value = t_sorted[i][1]
            error = t_sorted[i][2]
            percentDiff = round(100 * (float(value) - float(compareValue)) / float(compareValue), 3)
            print '%-25s %-12s %-12s %-6s' % (name, round(value, 5), round(error, 5), percentDiff)
            l_i = [name, value, error]
            ll_i.append(l_i)

        t_i.append(ll_i)

    return t_i


def rankTestTrain(t_test, t_train, NNList):

    '''
    rank by the train - test values
    '''
    # Create a dictionary with test:train
    td_rank = []
    for i in xrange(len(t_test)):
        t_rank = []
        for j in xrange(len(t_test[i])):
            corr      = t_test[i][j][0]
            test_val  = t_test[i][j][1]
            train_val = t_train[i][j][1]
            rank = abs(train_val - test_val) / train_val
            l_rank = [corr, rank]
            t_rank.append(l_rank)

        d_rank = {}
        for i in xrange(len(t_rank)):
            d_rank[t_rank[i][0]] = t_rank[i][1]
            td_rank.append(d_rank)

    for i in xrange(len(td_rank)):
        d_sorted = sorted(td_rank[i], key = operator.itemgetter(0))
        t_info = []
        for i, type in enumerae(d_sorted):
            name  = type[0]
            value = type[1]
            if 'n' in name:
                l_info = [name, value, NNUtils.getNNInfo()]
            else:
                l_info = [name, value, '-']

            t_info.append(l_info)

        t_sorted = tuple(sorted(t_info, key = lambda item: item[1]))
        print '\n\n RANK TEST TRAIN: ' + stat + '\nCORRECTION      VALUE     NNINFORMATION'
        for i in xrange(len(t_sorted)):
            name  = t_sorted[i][0]
            value = t_sorted[i][1]
            info  = t_sorted[i][2]
            print '%-17s %-10s %-20s' % (name, round(value, 4), info)


def averageNNValue(t_NN, randomVars):

    '''
    calculate the average training value
    '''
    sortedNN = sorted(t_NN)
    t_NNAv  = []
    avValue = 0
    for i in xrange(len(sortedNN)):
        iter = i + 1
        avValue += sortedNN[i][1]
        if iter % randomVars == 0:
            average = avValue / randomVars
            l_NN  = [sortedNN[i][0], average, sortedNN[i][2]]
            t_NNAv.append(l_NN)
            average = 0

    return t_NNAv


def updateListVars(prefix, name, suffix):

    newName = prefix + name.replace(',', suffix + ',' + prefix) + suffix
    
    return newName

def separateTestTrain(d_list):

    '''
    Separate the test and train elements so we can rank them
    '''

    t_train = t_test = []
    for i in xrange(len(d_list)):
        if 'train' in d_list[i][0]:
            t_train.append(d_list[i])
        elif 'test' in d_list[i][0]:
            t_test.append(d_list[i][0])
        else:
            pass

    return t_test, t_train

def makeTupleFromString(string, lDelim, tDelim):

    l = []
    t = []
    for item in string.split(tDelim):
        l = [x.strip() for x in item.split(lDelim)]
        t.append(l)

    return t


def getSelection(entry, min, max, branch):

    value = getattr(entry, branch)
    if max == '':
        if value == float(min):
            return True
        else:
            return False
    else:
        if value > float(min) and value < float(max):
            return True
        else:
            return False

def Info(string):

    print '+' * (11 + len(string))
    print '+ INFO:: ' + string + ' +'
    print '+' * (11 + len(string))
    print ''


def Error(string):
    print 'ERROR:: ' + string
    sys.exit(1)

def runLatex(file, location):

    cmd =  'cd ' + location + '; '
    cmd += 'pdflatex ' + file + ' > /dev/null; '
    cmd += 'pdflatex ' + file + ' > /dev/null; '
    os.system(cmd)

    Info('FILE: ' + location + file + '.pdf Created')


