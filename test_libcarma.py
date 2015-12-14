import math as math
import cmath as cmath
import numpy as np
import random as random
import cffi as cffi
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib import gridspec, cm
import matplotlib.cm as colormap
import matplotlib.mlab as mlab
import time
import pdb

from _libcarma import ffi
from mpl_settings import *

goldenRatio=1.61803398875
fhgt=10.0
fwid=fhgt*goldenRatio
dpi = 300

AnnotateXXLarge = 72
AnnotateXLarge = 48
AnnotateLarge = 32
AnnotateMedium = 28
AnnotateSmall = 24
AnnotateXSmall = 20
AnnotateXXSmall = 16

LegendLarge = 24
LegendMedium = 20
LegendSmall = 16

LabelXLarge = 32
LabelLarge = 28
LabelMedium = 24
LabelSmall = 20
LabelXSmall = 16

AxisXXLarge = 32
AxisXLarge = 28
AxisLarge = 24
AxisMedium = 20
AxisSmall = 16
AxisXSmall = 12
AxisXXSmall = 8

normalFontSize=32
smallFontSize=24
footnoteFontSize=20
scriptFontSize=16
tinyFontSize=12

LabelSize = LabelXLarge
AxisSize = AxisLarge
AnnotateSize = AnnotateXLarge
AnnotateSizeAlt = AnnotateMedium
AnnotateSizeAltAlt = AnnotateLarge
LegendSize = LegendMedium

gs = gridspec.GridSpec(1000, 2250) 

set_plot_params(fontfamily='serif',fontstyle='normal',fontvariant='normal',fontweight='normal',fontstretch='normal',fontsize=AxisMedium,useTex='True')

ffiObj = cffi.FFI()
C = ffi.dlopen("./libcarma.so")

dt = 0.02
p = 2
q = 1
ndims = p + q + 1
Theta = [0.75, 0.01, 7.0e-9, 1.2e-9]
Theta_cffi = ffiObj.new("double[%d]"%(len(Theta)))
for i in xrange(len(Theta)):
	Theta_cffi[i] = Theta[i]
numBurn = 1000000
numCadences = 60000
noiseSigma = 1.0e-18
startCadence = 0
burnSeed = 1311890535
distSeed = 2603023340
noiseSeed = 2410288857
fracInstrinsicVar = 1.0e-1
fracSignalToNoiseKepler = 35.0e-6
fracSignalToNoiseLSST = 1.0e-3
fracSignalToNoiseSDSS = 1.0e-2
fracSignalToNoise = fracSignalToNoiseKepler
nthreads = 4
nwalkers = 100
nsteps = 10
maxEvals = 1000
xTol = 0.005
maxT = 1.0e4
zSSeed = 2229588325
walkerSeed = 3767076656
moveSeed = 2867335446
xSeed = 1413995162
initSeed = 3684614774

cadence = np.array(numCadences*[0])
mask = np.array(numCadences*[0.0])
t = np.array(numCadences*[0.0])
x = np.array(numCadences*[0.0])
y = np.array(numCadences*[0.0])
xerr = np.array(numCadences*[0.0])
yerr = np.array(numCadences*[0.0])
Chain = np.zeros((nsteps,nwalkers,ndims))
LnLike = np.zeros((nsteps,nwalkers))
IR = 0

cadence_cffi = ffiObj.new("int[%d]"%(numCadences))
mask_cffi = ffiObj.new("double[%d]"%(numCadences))
t_cffi = ffiObj.new("double[%d]"%(numCadences))
x_cffi = ffiObj.new("double[%d]"%(numCadences))
y_cffi = ffiObj.new("double[%d]"%(numCadences))
xerr_cffi = ffiObj.new("double[%d]"%(numCadences))
yerr_cffi = ffiObj.new("double[%d]"%(numCadences))
for i in xrange(numCadences):
	cadence_cffi[i] = i
	mask_cffi[i] = 1.0
	t_cffi[i] = dt*i
	x_cffi[i] = 0.0
	y_cffi[i] = 0.0
	xerr_cffi[i] = 0.0
	yerr_cffi[i] = 0.0
Chain_cffi = ffiObj.new("double[%d]"%(ndims*nwalkers*nsteps))
for i in xrange(ndims*nwalkers*nsteps):
	Chain_cffi[i] = 0.0
LnLike_cffi = ffiObj.new("double[%d]"%(nwalkers*nsteps))
for i in xrange(nwalkers*nsteps):
	LnLike_cffi[i] = 0.0

intrinStart = time.time()
yORn = C._makeIntrinsicLC(dt, p, q, Theta_cffi, IR, maxT, numBurn, numCadences, startCadence, burnSeed, distSeed, cadence_cffi, mask_cffi, t_cffi, x_cffi, xerr_cffi)
intrinStop = time.time()
print "Time taken to compute intrinsic LC: %f (min)"%((intrinStop - intrinStart)/60.0)

observedStart = time.time()
yORn = C._makeObservedLC(dt, p, q, Theta_cffi, IR, maxT, fracInstrinsicVar, fracSignalToNoise, numBurn, numCadences, startCadence, burnSeed, distSeed, noiseSeed, cadence_cffi, mask_cffi, t_cffi, y_cffi, yerr_cffi)
observedStop = time.time()
print "Time taken to compute observed LC: %f (min)"%((observedStop - observedStart)/60.0)

for i in xrange(numCadences):
	cadence[i] = cadence_cffi[i]
	mask[i] = mask_cffi[i]
	t[i] = t_cffi[i]
	x[i] = x_cffi[i]
	y[i] = y_cffi[i]
	xerr[i] = xerr_cffi[i]
	yerr[i] = yerr_cffi[i]

fig1 = plt.figure(1,figsize=(fwid,fhgt))
ax1 = fig1.add_subplot(gs[:,:])
ax1.ticklabel_format(useOffset = False)
ax1.plot(t, x, color = '#7570b3', zorder = 5)
ax1.errorbar(t, y, yerr, fmt = '.', capsize = 0, color = '#d95f02', markeredgecolor = 'none', zorder = 10)
yMax=np.max(x[np.nonzero(x[:])])
yMin=np.min(x[np.nonzero(x[:])])
ax1.set_ylabel(r'$F$ (arb units)')
ax1.set_xlabel(r'$t$ (d)')
ax1.set_xlim(t[0],t[-1])
ax1.set_ylim(yMin,yMax)

LnLikeStart = time.time()
LnLikeVal = C._computeLnlike(dt, p, q, Theta_cffi, IR, maxT, numCadences, cadence_cffi, mask_cffi, t_cffi, y_cffi, yerr_cffi)
LnLikeStop = time.time()
print "LnLike: %+17.17e"%(LnLikeVal)
print "Time taken to compute LnLike of LC: %f (min)"%((LnLikeStop - LnLikeStart)/60.0)

'''
fitStart = time.time()
C._fitCARMA(dt, p, q, IR, maxT, numCadences, cadence_cffi, mask_cffi, t_cffi, y_cffi, yerr_cffi, nthreads, nwalkers, nsteps, maxEvals, xTol, zSSeed, walkerSeed, moveSeed, xSeed, initSeed, Chain_cffi, LnLike_cffi)
fitStop = time.time()
print "Time taken to estimate C-ARMA params: %f (min)"%((fitStop - fitStart)/60.0)

for stepNum in xrange(nsteps):
	for walkerNum in xrange(nwalkers):
		LnLike[stepNum, walkerNum] = LnLike_cffi[walkerNum + stepNum*nwalkers]
		for dimNum in xrange(ndims):
			Chain[stepNum, walkerNum, dimNum] = Chain_cffi[dimNum + walkerNum*ndims + stepNum*ndims*nwalkers]

fig2 = plt.figure(2,figsize=(fwid,fhgt))

ax1 = fig2.add_subplot(gs[:,0:999])
ax1.ticklabel_format(useOffset = False)
ax1.scatter(Chain[int(nsteps/2.0):,:,0], Chain[int(nsteps/2.0):,:,1], c = np.max(LnLike[int(nsteps/2.0):,:]) - LnLike[int(nsteps/2.0):,:], marker='.', cmap = colormap.gist_rainbow_r, linewidth = 0)
ax1.set_xlim(np.min(Chain[int(nsteps/2.0):,:,0]),np.max(Chain[int(nsteps/2.0):,:,0]))
ax1.set_ylim(np.min(Chain[int(nsteps/2.0):,:,1]),np.max(Chain[int(nsteps/2.0):,:,1]))
ax1.set_xlabel(r'$a_{1}$')
ax1.set_ylabel(r'$a_{2}$')

ax2 = fig2.add_subplot(gs[:,1249:2249])
ax1.ticklabel_format(useOffset = False)
ax2.scatter(Chain[int(nsteps/2.0):,:,2], Chain[int(nsteps/2.0):,:,3], c = np.max(LnLike[int(nsteps/2.0):,:]) - LnLike[int(nsteps/2.0):,:], marker='.', cmap = colormap.gist_rainbow_r, linewidth = 0)
ax2.set_xlim(np.min(Chain[int(nsteps/2.0):,:,2]),np.max(Chain[int(nsteps/2.0):,:,2]))
ax2.set_ylim(np.min(Chain[int(nsteps/2.0):,:,3]),np.max(Chain[int(nsteps/2.0):,:,3]))
ax2.set_xlabel(r'$b_{0}$')
ax2.set_ylabel(r'$b_{1}$')
'''

##############################################################################################################


irr_cadence = np.array([index for index in xrange(numCadences)])
numCadences = irr_cadence.shape[0]
irr_mask = np.array(numCadences*[1.0])
irr_t = np.array([index*dt for index in xrange(numCadences)])
#for i in xrange(numCadences/2):
#	irr_t[i] += random.uniform(-dt/2.0, dt/2.0)
irr_x = np.array(numCadences*[0.0])
irr_y = np.array(numCadences*[0.0])
irr_xerr = np.array(numCadences*[0.0])
irr_yerr = np.array(numCadences*[0.0])
irr_Chain = np.zeros((nsteps,nwalkers,ndims))
irr_LnLike = np.zeros((nsteps,nwalkers))
IR = 1

irr_cadence_cffi = ffiObj.new("int[%d]"%(numCadences))
irr_mask_cffi = ffiObj.new("double[%d]"%(numCadences))
irr_t_cffi = ffiObj.new("double[%d]"%(numCadences))
irr_x_cffi = ffiObj.new("double[%d]"%(numCadences))
irr_y_cffi = ffiObj.new("double[%d]"%(numCadences))
irr_xerr_cffi = ffiObj.new("double[%d]"%(numCadences))
irr_yerr_cffi = ffiObj.new("double[%d]"%(numCadences))

for i in xrange(numCadences):
	irr_cadence_cffi[i] = irr_cadence[i]
	irr_mask_cffi[i] = irr_mask[i]
	irr_t_cffi[i] = irr_t[i]
	irr_x_cffi[i] = irr_x[i]
	irr_y_cffi[i] = irr_y[i]
	irr_xerr_cffi[i] = irr_yerr[i]
	irr_yerr_cffi[i] = irr_xerr[i]
irr_Chain_cffi = ffiObj.new("double[%d]"%(ndims*nwalkers*nsteps))
for i in xrange(ndims*nwalkers*nsteps):
	irr_Chain_cffi[i] = 0.0
irr_LnLike_cffi = ffiObj.new("double[%d]"%(nwalkers*nsteps))
for i in xrange(nwalkers*nsteps):
	irr_LnLike_cffi[i] = 0.0

irr_intrinStart = time.time()
yORn = C._makeIntrinsicLC(dt, p, q, Theta_cffi, IR, maxT, numBurn, numCadences, startCadence, burnSeed, distSeed, irr_cadence_cffi, irr_mask_cffi, irr_t_cffi, irr_x_cffi, irr_xerr_cffi)
irr_intrinStop = time.time()
print "Time taken to compute irregular intrinsic LC: %f (min)"%((irr_intrinStop - irr_intrinStart)/60.0)

irr_observedStart = time.time()
yORn = C._makeObservedLC(dt, p, q, Theta_cffi, IR, maxT, fracInstrinsicVar, fracSignalToNoise, numBurn, numCadences, startCadence, burnSeed, distSeed, noiseSeed, irr_cadence_cffi, irr_mask_cffi, irr_t_cffi, irr_y_cffi, irr_yerr_cffi)
irr_observedStop = time.time()
print "Time taken to compute irregular observed LC: %f (min)"%((irr_observedStop - irr_observedStart)/60.0)

for i in xrange(numCadences):
	irr_cadence[i] = irr_cadence_cffi[i]
	irr_mask[i] = irr_mask_cffi[i]
	irr_t[i] = irr_t_cffi[i]
	irr_x[i] = irr_x_cffi[i]
	irr_y[i] = irr_y_cffi[i]
	irr_xerr[i] = irr_xerr_cffi[i]
	irr_yerr[i] = irr_yerr_cffi[i]

fig3 = plt.figure(3,figsize=(fwid,fhgt))
ax1 = fig3.add_subplot(gs[:,:])
ax1.ticklabel_format(useOffset = False)
ax1.plot(irr_t, irr_x, color = '#7570b3', zorder = 5)
ax1.errorbar(irr_t, irr_y, irr_yerr, fmt = '.', capsize = 0, color = '#d95f02', markeredgecolor = 'none', zorder = 10)
yMax=np.max(irr_x[np.nonzero(irr_x[:])])
yMin=np.min(irr_x[np.nonzero(irr_x[:])])
ax1.set_ylabel(r'$F$ (arb units)')
ax1.set_xlabel(r'$t$ (d)')
ax1.set_xlim(t[0],t[-1])
ax1.set_ylim(yMin,yMax)

irr_LnLikeStart = time.time()
LnLikeVal = C._computeLnlike(dt, p, q, Theta_cffi, IR, maxT, numCadences, irr_cadence_cffi, irr_mask_cffi, irr_t_cffi, irr_y_cffi, irr_yerr_cffi)
irr_LnLikeStop = time.time()
print "LnLike: %+17.17e"%(LnLikeVal)
print "Time taken to compute LnLike of LC: %f (min)"%((irr_LnLikeStop - irr_LnLikeStart)/60.0)

irr_fitStart = time.time()
C._fitCARMA(dt, p, q, IR, maxT, numCadences, irr_cadence_cffi, irr_mask_cffi, irr_t_cffi, irr_y_cffi, irr_yerr_cffi, nthreads, nwalkers, nsteps, maxEvals, xTol, zSSeed, walkerSeed, moveSeed, xSeed, initSeed, irr_Chain_cffi, irr_LnLike_cffi)
irr_fitStop = time.time()
print "Time taken to estimate C-ARMA params: %f (min)"%((irr_fitStop - irr_fitStart)/60.0)

for stepNum in xrange(nsteps):
	for walkerNum in xrange(nwalkers):
		irr_LnLike[stepNum, walkerNum] = irr_LnLike_cffi[walkerNum + stepNum*nwalkers]
		for dimNum in xrange(ndims):
			irr_Chain[stepNum, walkerNum, dimNum] = irr_Chain_cffi[dimNum + walkerNum*ndims + stepNum*ndims*nwalkers]

fig4 = plt.figure(4,figsize=(fwid,fhgt))

ax1 = fig4.add_subplot(gs[:,0:999])
ax1.ticklabel_format(useOffset = False)
ax1.scatter(irr_Chain[int(nsteps/2.0):,:,0], irr_Chain[int(nsteps/2.0):,:,1], c = np.max(irr_LnLike[int(nsteps/2.0):,:]) - irr_LnLike[int(nsteps/2.0):,:], marker='.', cmap = colormap.gist_rainbow_r, linewidth = 0)
ax1.set_xlim(np.min(irr_Chain[int(nsteps/2.0):,:,0]),np.max(irr_Chain[int(nsteps/2.0):,:,0]))
ax1.set_ylim(np.min(irr_Chain[int(nsteps/2.0):,:,1]),np.max(irr_Chain[int(nsteps/2.0):,:,1]))
ax1.set_xlabel(r'$a_{1}$')
ax1.set_ylabel(r'$a_{2}$')

ax2 = fig4.add_subplot(gs[:,1249:2249])
ax1.ticklabel_format(useOffset = False)
ax2.scatter(irr_Chain[int(nsteps/2.0):,:,2], irr_Chain[int(nsteps/2.0):,:,3], c = np.max(irr_LnLike[int(nsteps/2.0):,:]) - irr_LnLike[int(nsteps/2.0):,:], marker='.', cmap = colormap.gist_rainbow_r, linewidth = 0)
ax2.set_xlim(np.min(irr_Chain[int(nsteps/2.0):,:,2]),np.max(irr_Chain[int(nsteps/2.0):,:,2]))
ax2.set_ylim(np.min(irr_Chain[int(nsteps/2.0):,:,3]),np.max(irr_Chain[int(nsteps/2.0):,:,3]))
ax2.set_xlabel(r'$b_{0}$')
ax2.set_ylabel(r'$b_{1}$')

plt.show()