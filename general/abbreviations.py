import sys, pdb, json, re
from operator import itemgetter
from math import log10, floor
import functools

# try:
#
#     assert platform
# except:
#     platform = 'm'

# ujson installed with pip install --target='/users/kylefoley/codes/venv/lib/python3.8/site-packages/' git+git://github.com/esnme/ultrajson.git
# import ujson

## tough modules
# import keyboard
# import pyautogui
# import pause
# from AppKit import NSWorkspace
# import easygui
# import xlwings


print(sys.version)

p = print

en = enumerate

db = pdb.set_trace
conditional = chr(8594)
ds = ".DS_Store"
ds1 = '._.DS_Store'

vol='/users/kylefoley/'

fdir = vol+ 'documents/'
fdir2 = vol+'documents/'
mdir = vol+'documents/codes/'
files_used = set()
pdir = fdir + 'pcode/'
#
# if platform == 'm':
#     import ujson
# elif platform == 'l':
#     fdir = '/mnt/disks/temp_dir1/'

base_dir = '/Users/kylefoley/documents/pcode/'
dwn_dir = '/users/kylefoley/downloads/'

dia = 'àáäâèéêëìíïîòóöôùúûüçßñ'
diau = 'ÀÁÄÂÈÉÊËÌÍÏÎÒÓÖÔÙÚÛÜÇÑ' + dia

open_apost = chr(8220)

closed_apost = chr(8221)

large_dash = chr(8212)

upside_down_q = chr(191)

ellip = chr(8230)

obje = chr(65532)

letter_2numbers = "abcdefghijklmnopqrstuvxyz"

letters = "abcdefghijklmnopqrstuvxyz"

dsstore = '.DS_Store'

not_execute_on_import = '__name__ == "__main__"'


is_year = lambda x: bool(re.search(r'^(1|2)\d\d\d$', x))

hl = lambda x: bool(re.search(r'\S', x)) #has non-characters

ha = lambda x: bool(re.search(r'[a-zA-Z]', x)) #has alphabetic characters

hn = lambda x: bool(re.search(r'[0-9]', x)) # has numbers

onn = lambda x: not bool(re.search(r'[^0-9]', x)) and bool(re.search(r'[0-9]', x))

percent = lambda x, tot: int(round(x / tot, 2) * 100)

per_comp = lambda x, y: int(round(x / x+y, 2) * 100)

merge_2dicts = lambda x, y: {**x, **y}

jsonc_lam = lambda x: json.loads(json.dumps(x))

ujsonc = lambda x: json.loads(json.dumps(x))

saset = lambda x: set(y for y in x)

jsons = lambda x: json.dumps(json.loads(x))

jsont = lambda x: json.loads(json.dumps(x))

reg = lambda x, y: bool(re.search(x, y))

megs = lambda x: sys.getsizeof(x) / 1_048_576

gigs = lambda x: sys.getsizeof(x) / 1_073_741_824



sort_by_col = lambda lst, col: sorted(lst, key=itemgetter(col))

sort_by_col_rev = lambda lst, col: sorted(lst, key=itemgetter(col), reverse=True)

sort_by_col_h2l = lambda lst, col: sorted(lst, key=itemgetter(col), reverse=True)

sort_dct_val_tpl = lambda x: sorted(x.items(), key=itemgetter(1))

sort_dct_val_rev_tpl = lambda x: sorted(x.items(), key=itemgetter(1), reverse=True)

sort_dct_key_tpl = lambda x: sorted(x.items(), key=itemgetter(0))

sort_dct_key_tpl_rev = lambda x: sorted(x.items(), key=itemgetter(0), reverse=True)

from_tpl2dct = lambda x: {z[0]: z[1] for z in x}

sort_dct_key = lambda x: from_tpl2dct(sort_dct_key_tpl(x))

sort_dct_key_rev = lambda x: from_tpl2dct(sort_dct_key_tpl_rev(x))

sort_dct_val = lambda x: from_tpl2dct(sort_dct_val_tpl(x))

sort_dct_val_rev = lambda x: from_tpl2dct(sort_dct_val_rev_tpl(x))

print_timedelta = lambda x: str(x).split(".")[0]

delete_at_i = lambda x, sent: sent[:x] + sent[x + 1:]

replace_at_i = lambda idx, sent, char: sent[:idx] + char + sent[idx + 1:]

insert_lstr_i = lambda idx, sent, char, le: sent[:idx] + char + sent[idx + le:]

add_at_i = lambda idx, sent, char: sent[:idx] + char + sent[idx:]

get_between = lambda sent, l, r: sent[sent.index(l)+1:sent.index(r)]



# significant_digits = lambda x, places: round(x, -int(floor(log10(x))) + (places - 1)) if x != 0 else 0

def significant_digits(x, places):
    if x != 0:
        try:
            places1 = -int(floor(log10(x))) + (places - 1)
            x = round(x, places1)
        except IndexError:
            return x

    else:
        x = 0
    return x


intr = lambda x: int(round(x, 0))

float_x_int = lambda x: int(x) if type(x) in [float, int] and int(x) == x else x



xlcol = lambda x: letter_2numbers.index(x) + 1

pc = lambda x: x.__dict__




mult_lst = lambda z: functools.reduce(lambda x, y: x * y, z)

class2str = lambda x: f"<class '{x}'>"


def jsonc(obj):
    if type(obj) == dict:
        for x, y in obj.items():
            if type(x) == int:
                try:
                    obj = ujsonc(obj)
                except:
                    obj = jsonc_lam(obj)
                return {int(k): v for k, v in obj.items()}
            else:
                break
    try:
        obj = ujsonc(obj)
    except:
        obj = jsonc_lam(obj)
    return obj
