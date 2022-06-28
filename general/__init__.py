import sys

vol = '/users/kylefoley/'

sys.path.append(f'{vol}documents/pcode/general/')

s = '/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages'
s1 = '/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/aeosa'
t = f'{vol}documents/codes/venv3/lib/python3.8/site-packages'
tu = f'{vol}documents/codes/venv3/lib/python3.8/site-packages/aeosa'

sys.path.append(t)
sys.path.append(tu)
try:
    sys.path.remove(s)
    sys.path.remove(s1)
except:
    pass

import general.very_general_functions as vgf
import general.time_func as tf
import general.trans_obj as to
import general.excel_functions as ef
import general.pickling as pi
from general.abbreviations import *

