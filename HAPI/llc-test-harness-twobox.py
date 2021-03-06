#!/usr/bin/env python

""" 
acq2106_llc-run-full-auto-two.py UUT1 UUT2
"""



import argparse
import acq400_hapi
import time
import os


EXTCLKDIV = int(os.getenv("EXTCLKDIV", "10"))
SIMULATE = os.getenv("SIMULATE", "")
AISITES = os.getenv("AISITES", "1,2,3,4,5,6")
AOSITES = os.getenv("AOSITES", "1,2")

def hit_resets(svc):    
    for knob in svc.help():
        if (knob.endswith('RESET')):
            svc.set_knob(knob, '1')            
            
def clear_counters(uuts):
    for uut in uuts:
        for cx in [ 'cA', 'cB']:
            hit_resets(uut.svc[cx])
            
def init_common(uut):
    uut.s1.CLKDIV = EXTCLKDIV
    uut.s1.clkdiv = EXTCLKDIV
    
def init_ai(uut):
    init_common(uut)
    
    for s in uut.modules:
        uut.modules[s].simulate = '1' if str(s) in SIMULATE else '0'
    uut.s0.spad = '1,16,0'
    uut.cA.spad = '1'
    uut.cA.aggregator = 'sites={}'.format(AISITES)
    uut.cB.spad = '1'
    uut.cB.aggregator = 'sites={}'.format(AISITES)

def init_ao(uut, slave=False):
    aom = "s{}".format(AOSITES.split(',')[0])
    if slave:
	uut.svc[aom].clk = '1,2,1'
    uut.svc[aom].trg = '1,1,1'
#    uut.svc[aom].CLKDIV = 1
    uut.svc[aom].clkdiv = 1
    uut.svc[aom].lotide = 256
    uut.s0.distributor = "sites={} comms=2 pad=0 on".format(AOSITES)
    print("init_ao() done {} {}".format(uut.uut, aom))
    
        
def run_main(args):
    uuts = [ acq400_hapi.Acq2106(addr) for addr in args.uuts ]
   
    print("initialise {} uuts {}".format(len(uuts), args.uuts)) 
    clear_counters(uuts)    
    init_ai(uuts[0])
    # if two boxes ASSUME second box AO
    if len(uuts) > 1:
        init_ao(uuts[1])
    else:
	print("init_ao {}".format(uuts[0].uut))
        init_ao(uuts[0], slave=True)
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="aq2106_llc-run-full-auto-two.py")
    parser.add_argument("uuts", nargs='+', help="name the uuts")
    run_main(parser.parse_args())

