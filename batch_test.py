from brian import *
from sys import *

# Parameters
N=200
timestep = 0.1 * ms
phi = 3.0 # original 3.0

area = 20000 * umetre ** 2
Cm = (1 * ufarad * cm ** -2) * area
gl = (5e-5 * siemens * cm ** -2) * area
El = -65 * mV #-65
EK = -80 * mV #-80
ENa = 55 * mV #55
g_na = (100 * msiemens * cm ** -2) * area
g_kd = (30 * msiemens * cm ** -2) * area
VTm = 55 * mV #55
VTh = 44 * mV #44
VTn = 44 * mV #44
# Time constants
taue = 5 * ms # Ah this is ok because dse/dt is in s**-1!
taui = 10 * ms
A = 20 * ms # dunno, but using ms to get s unitless
# Reversal potentials
Ee = 0 * mV
Ei = -80 * mV
# we = 6 * nS # excitatory synaptic weight (voltage)
# wi = 67 * nS # inhibitory synaptic weight
Iext_e = 1.5 * nA  # original value 1.5 uA/cm2?
Iext_i = 5 * nA  # original value 5 uA/cm2?
alpha_ee	= 0.215 # original 0.12
alpha_ei	= 0.2 # original 0.2
alpha_ie	= 0.06 # original 0.06
alpha_ii	= 0.02 # original 0.02

# The model

eqs = Equations('''
dv/dt = (gl*(El-v)+Iesyn+Iisyn+Iext-\
    g_na*(m*m*m)*h*(v-ENa)-\
    g_kd*(n*n*n*n)*(v-EK))/Cm : volt
dm/dt = phi*(alpham*(1-m)-betam*m) : 1
dn/dt = phi*(alphan*(1-n)-betan*n) : 1
dh/dt = phi*(alphah*(1-h)-betah*h) : 1
dse/dt = (A*sigma*(1-se)-se)/taue : 1
dsi/dt = (A*sigma*(1-si)-si)/taui : 1

alpham = 0.1*(mV**-1)*(25*mV-(v+VTm))/ \
    (exp((25*mV-(v+VTm))/(10*mV))-1.)/ms : Hz
betam = 4.0*exp((-(v+VTm))/(18*mV))/ms : Hz
alphah = 0.07*exp((-(v+VTh))/(20*mV))/ms : Hz
betah = 1./(1+exp((30*mV-(v+VTh))/(10*mV)))/ms : Hz
alphan = 0.01*(mV**-1)*(10*mV-(v+VTn))/ \
    (exp((10*mV-(v+VTn))/(10*mV))-1.)/ms : Hz
betan = .125*exp((-(v+VTn))/(80*mV))/ms : Hz
sigma = 1./(1+exp((-(v+20*mV))/(4*mV)))/ms : Hz

Iesyn : amp
Iisyn : amp
Iext : amp
''')

eqs_esyn = '''
g_jk : nS	# synaptic weight
Iesyn = (g_jk * se_pre)*(Ee-v_post)/100.0 : amp
'''

eqs_isyn = '''
g_jk : nS	# synaptic weight
Iisyn = (g_jk * si_pre)*(Ei-v_post)/100.0 : amp
'''

myclock=Clock(dt=timestep)
P = NeuronGroup(N, model=eqs,
    threshold=EmpiricalThreshold(threshold= 20 * mV,refractory=3*ms),
                                  # refractory=3 * ms),
    implicit=True, freeze=True, clock=myclock, reset=NoReset())
Pe = P.subgroup(N/2)
Pi = P.subgroup(N/2)

See = Synapses(Pe, Pe, model=eqs_esyn)
Sei = Synapses(Pe, Pi, model=eqs_esyn)
Sie = Synapses(Pi, Pe, model=eqs_isyn)
Sii = Synapses(Pi, Pi, model=eqs_isyn)
See[:,:] = True
Sei[:,:] = True
Sie[:,:] = True
Sii[:,:] = True
Pe.Iesyn = See.Iesyn
Pe.Iisyn = Sie.Iisyn # from I to E, inhibitory synapses
Pi.Iesyn = Sei.Iesyn # from E to I, excitatory synapses
Pi.Iisyn = Sii.Iisyn

# Initialization
P.v = El + (randn(len(P)) * 5 - 5) * mV

#Set up synaptic weights
print "Setting up synaptic weights..."

sq100 = sqrt(100.0/pi)
sq30 = sqrt(30.0/pi)
w_ee = zeros(len(Pe))
w_ei = zeros(len(Pe))
w_ie = zeros(len(Pe))
w_ii = zeros(len(Pe)) # Think about alternative wiring scheme. Gutkin's doesn't work with Pe != Pi
for j in range(0,len(Pe)):
	for k in range(0,len(Pe)):
		w_ee[abs(j-k)]=alpha_ee*sq100*exp(-100.0*(float(j-k)/N)**2.0)
		w_ei[abs(j-k)]=alpha_ei*sq30*exp(-30.0*(float(j-k)/N)**2.0)
		w_ie[abs(j-k)]=alpha_ie*sq30*exp(-30.0*(float(j-k)/N)**2.0)
		w_ii[abs(j-k)]=alpha_ii*sq30*exp(-30.0*(float(j-k)/N)**2.0)

for j in range(0,len(Pe)): # From cell j in Pe
	for k in range(0,len(Pe)): # To cell k in Pe
		if j == k: # No connection to itself
			See.g_jk[j,j] = 0.0 *nS
		else:
			See.g_jk[j,k] = w_ee[abs(j-k)]*nS
	for k in range(0,len(Pi)): # To cell k in Pi
		Sei.g_jk[j,k] = w_ei[abs(j-k)]*nS
		
for j in range(0,len(Pi)): # From cell j in Pi
	for k in range(0,len(Pe)): # To cell k in Pe
		Sie.g_jk[j,k] = w_ie[abs(j-k)]*nS
	for k in range(0,len(Pi)): # To cell k in Pi
		if j == k: # No connection to itself
			Sii.g_jk[j,j] = 0.0 *nS
		else:
			Sii.g_jk[j,k] = w_ii[abs(j-k)]*nS
			
print 'done.'

# External input
print "Setting up external input..."
Pi.Iext = TimedArray([Iext_i]*int((500*ms)/timestep),start=0*ms,dt=timestep)
for j in range(21,80):
	Pe[j].Iext = TimedArray([0*uA]*int((112*ms)/timestep)+[Iext_e*exp(-60.0*(float(j-(len(Pe)/2))/len(Pe))**2.0)]*int((30*ms)/timestep),start=0*ms,dt=timestep)
print "done."
	
# Record the number of spikes and voltage traces
trace = StateMonitor(Pe, 'v', record=arange(0,len(Pe)))
trace2 = StateMonitor(Pi, 'v', record=arange(0,len(Pi)))
filename = 'original.txt'
Me = FileSpikeMonitor(Pe,'Pe_'+filename)
Mi = FileSpikeMonitor(Pi,'Pi_'+filename)

print filename
print "Running simulation..."
run(500 * ms)
print "done."
print "Excitatory spikes: ", Me.nspikes
print "Inhibitory spikes: ", Mi.nspikes
print "wrote to ", filename
