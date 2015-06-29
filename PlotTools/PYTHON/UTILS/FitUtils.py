from ROOT import TF1
import math

class Bukin():
    def __call__( self, x, par ):

      debug=False

      if debug:
        print "******"
      # inputs
      xx =x[0]
      norm = par[0] # overall normalization
      x0 = par[1] # position of the peak
      sigma = par[2] # width of the core
      xi = par[3] # asymmetry
      rhoL = par[4] # size of the lower tail
      rhoR = par[5] # size of the higher tail
      if debug:
        print "xx",xx
        print "norm",norm
        print "x0",x0
        print "sigma",sigma
        print "xi",xi
        print "rhoL",rhoL
        print "rhoR",rhoR

      # initializations
      r1=0.0
      r2=0.0
      r3=0.0
      r4=0.0
      r5=0.0
      hp=0.0

      x1=0.0
      x2=0.0
      fit_result=0.0

      # set them other values
      consts=2*math.sqrt(2*math.log(2.0))
      hp=sigma*consts
      r3=math.log(2.0)
      r4=math.sqrt(math.pow(xi,2)+1.0)
      r1=xi/r4
      if debug:
        print "consts",consts
        print "hp",hp
        print "r3",r3
        print "r4",r4
        print "r1",r1
        print "x1",x1
        print "x2",x2
        print "x0",x0
        print "xx",xx
        print "xi",xi
        print "math.exp(-6.)",math.exp(-6.)

      if abs(xi)>math.exp(-6.):
        r5=xi/math.log(r4+xi)
      else:
        r5=1.0
      if debug:
        print "r5",r5

      x1=x0+(hp/2)*(r1-1)
      x2=x0+(hp/2)*(r1+1)
      if debug:
        print "x1",x1
        print "x2",x2
        print "x0",x0
        print "xx",xx

      if xx<x1:
        # Left Side
        r2=rhoL*math.pow((xx-x1)/(x0-x1),2)-r3+4*r3*(xx-x1)/hp*r5*r4/math.pow((r4-xi),2)
      elif xx < x2:
        # Centre
        if abs(xi)>math.exp(-6.):
          r2=math.log(1+4*xi*r4*(xx-x0)/hp)/math.log(1+2*xi*(xi-r4))
          r2=-r3*math.pow(r2,2)
        else:
          r2=-4*r3*math.pow(((xx-x0)/hp),2)
      
      else:
        r2=rhoR*math.pow((xx-x2)/(x0-x2),2)-r3-4*r3*(xx-x2)/hp*r5*r4/math.pow((r4+xi),2)

      if abs(r2)>100:
        fit_result=0
      else:
        # Normalize the result
        fit_result=math.exp(r2)
      
      result=norm*fit_result
      return result
