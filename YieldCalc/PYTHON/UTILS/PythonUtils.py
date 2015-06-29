##
## Generic Python functions
##

## import os and sys modules
import os, sys

def makeListFromString(string, delim):

    l = []
    for item in string.split(delim):
        l.append(item.strip())

    return l


def makeListFromFile(file):

    f = open(file, 'r')
    l = []
    for line in f:
        if not line.startswith('#'):
            l.append(line.strip())

    return l


def makeTupleFromFile(file, delim):

    f = open(file, 'r')
    t = []
    for line in f:
        if not line.startswith('#'):
            item = [x.strip() for x in line.split(delim)]
            t.append(item)

    return t


def doesFileExist(file):

    if os.path.isfile(file):
        print "\nFile: %s does exist. \nCarrying on" % (file)
        return True
    else:
        print "\nFile: %s does not exist" % (file)
        sys.exit(1)


def keepEntry(sample, i):

    if sample == 'test':    
        if i % 2 == 1:
            return True
    elif sample == 'train':
        if i % 2 == 0:
            return True
    elif sample == 'all':
        return True
    else:
        print '\nsample %s not know, try test, train or all' % sample
        sys.exit(1)


def makeTupleFromString(string, lDelim, tDelim):

    l = []
    t = []
    for item in string.split(tDelim):
        l = [x.strip() for x in item.split(lDelim)]
        t.append(l)
    
    return t


def getSelection(entry, min, max, branch):

    value = getattr(entry, branch)
    if value > int(min) and value < int(max):
        return True
    else:
        return False

def Info(string):

    print 'INFO:: ' + string

def Error(string):

    print '\nERROR:: ' + string
    sys.exit(1)
