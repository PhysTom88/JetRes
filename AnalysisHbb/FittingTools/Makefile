##
## Makefile for FittingTools
##
include Makefile.arch

CXXFLAGS += -g3 -Wall -fPIC -Wno-deprecated -O3 ${ROOTFLAGS}
##
## Directories
##
BASE   = ${PWD}
ODIR   = ${BASE}/obj
LIBDIR = ${BASE}/lib
BINDIR = ${BASE}/bin
SRC    = ${BASE}/src
HEADER = ${BASE}/include

##
## INCLUDE areas for headers
##
INCLUDES = -I${BASE} -I${HEADER}

##
## Libraries used
##
LIBS     = ${ROOTLIBS} -lMinuit

##
## Remove command for make clean
##
RM       = /bin/rm

##
## Object List
##
OBJECT_LIST = runFitting.o Fitter.o ConfigFile.o

##
## Add Path Structure for Object to be produced
##
OBJ = $(patsubst %,$(ODIR)/%,$(OBJECT_LIST))

all: $(LIBDIR) $(TEMPDIR) $(BINDIR) $(ODIR) bins libs


$(TEMPDIR) :
	mkdir -p $@
$(LIBDIR) :
	mkdir -p $@
	@echo "Dir $@ Has Been Created"
$(BINDIR) :
	mkdir -p $@
	@echo "Dir $@ Has Been Created"
$(ODIR) :
	mkdir -p $@
	@echo "DIR $@ Has Been Created"

bins: $(BINDIR)/Fitter

libs: $(LIBDIR)/Fitter.so

#
# Object Files For Library and Bin
#
# Implicit Rule to Compile All Classes in SRC
$(ODIR)/%.o : $(SRC)/%.cxx
	@echo "Compiling $< to $@"
	@echo "$(CXX) $(CXXFLAGS) -c -o $@ $< ${INCLUDES}"
	@$(CXX) $(CXXFLAGS) -c -o $@ $< ${INCLUDES}
	@echo "$@ done"

##
## Bins
##
$(BINDIR)/Fitter : $(OBJ)
	$(CXX) $(CXXFLAGS) $(LIBS) $^ -o $@

##
## Library
##
$(LIBDIR)/Fitter.so : $(ODIR)/Fitter.o
	$(CXX) -shared $(CXXFLAGS) $(LIBS) $^ -o $@


##
## Tidy
##
clean:
	$(RM) -v -f $(ODIR)/*.o $(BINDIR)/* $(LIBDIR)/*
