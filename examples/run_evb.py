import sys
sys.path.append('../')

import evba
from evba.evba import EVBA

yml = './test.yml' 
evba_run = EVBA(yml)
print(evba_run.cfg)
evba_run.setup_evb()