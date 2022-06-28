import subprocess, time, os, shutil
from itertools import chain, combinations
import pickling as pi
# import pickle as pi
import tempfile, functools
import requests, keyboard
import PyPDF2
from bs4 import BeautifulSoup as beautiful_soup
from torrequest import TorRequest
import zipfile, tarfile
from subprocess import Popen, PIPE
import Levenshtein as lvn
from abbreviations import *
from PIL import ImageFont


######### timers
def timer(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        run_time = significant_digits(run_time, 2)
        print(f"Finished {func.__name__!r} in {run_time} secs")
        return value

    return wrapper_timer

def get_between_sline(s, ld='<', add_com=0):
    on = 0
    if ld == '<':
        rd = '>'
    elif ld == '[':
        rd = ']'
    elif ld == '{':
        rd = '}'
    t = ""
    for x in s:
        if x == ld:
            on = 1
        elif x == rd:
            on = 0
            if add_com:
                t += ','
            else:
                t += ' '
        elif on:
            t += x
    return t.strip()


def timer3(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        run_time = significant_digits(run_time, 4)
        print(f"Finished {func.__name__!r} in {run_time} secs")
        return value

    return wrapper_timer


def timer2(func):
    """Print the runtime of the decorated function"""

    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        run_time = significant_digits(run_time, 2)
        print(run_time)
        return value

    return wrapper_timer


######### clss tools

def copy_class(new_cls, old_cls):
    attributes = [x for x in old_cls.__dict__]
    for attribute in attributes:
        if not attribute.startswith("__"):
            setattr(new_cls, attribute, getattr(old_cls, attribute))


def copy_class_json(new_cls, old_cls):
    attributes = [x for x in old_cls.__dict__]
    for attribute in attributes:
        obj = getattr(old_cls, attribute)
        if isinstance(obj, list) or isinstance(obj, dict):
            obj = ujsonc(obj)
        setattr(new_cls, attribute, obj)


def copy_partial_cls(new_cls, old_cls, atts):
    for att in atts:
        setattr(new_cls, att, getattr(old_cls, att))


def copy_classless_class(old_cls):
    class gclass:
        pass

    new_cls = gclass()
    attributes = [x for x in old_cls.__dict__]
    if any(isclass(x) for x in attributes):
        raise Exception
    else:
        for att in attributes:
            obj = getattr(old_cls, att)
            if type(obj) in [list, dict, set]:
                obj = ujsonc(obj)
            setattr(new_cls, att, obj)

    return new_cls


def copy_any_class(old_cls):
    class gclass:
        pass

    new_cls = gclass()
    attributes = [x for x in old_cls.__dict__]
    for attribute in attributes:
        obj = getattr(old_cls, attribute)
        if isclass(obj):
            obj = copy_any_class(obj)
        elif isinstance(obj, list):
            for e, x in en(obj):
                if isclass(x):
                    x = copy_any_class(x)
                    obj[e] = x
                else:
                    obj[e] = ujsonc(x)
        elif isinstance(obj, set):
            obj = ujsonc(obj)

        elif isinstance(obj, dict):
            for k, v in obj.items():
                if isclass(v):
                    v = copy_any_class(v)
                    obj[k] = v
                else:
                    obj[k] = ujsonc(v)

        setattr(new_cls, attribute, obj)
    return new_cls


def trim_class4(cls, lst):
    '''delete all attribs in lst'''
    for att in lst:
        if hasattr(cls, att):
            delattr(cls, att)


def trim_class_n_methods(cls, set1):
    class bclass: pass

    ins = bclass()
    for attribute in list(set1):
        setattr(ins, attribute, getattr(cls, attribute))

    return ins


def trim_class(cls, set1):
    attributes = set(x for x in cls.__dict__)
    for attribute in list(attributes):
        if attribute not in set1:
            delattr(cls, attribute)


def class2lst_num(dct, headers):
    mx = max(list(headers.values())) + 1
    lst = []
    lst1 = [''] * mx
    lst.append(lst1)
    lst1 = [[''] + list(headers.keys())]
    lst.append(lst1)
    for name, ins in dct.items():
        lst1 = [''] * mx
        for att, col in headers.items():
            val = getattr(ins, att)
            lst1[col] = val
        lst.append(lst1)
    return lst


###############  container functions


def clump_lst(lst, rlst=0):
    '''
    if you want to return a list of lists then rlst=1
    otherwise the list will be combined into a string

    '''

    lst1 = []
    lst2 = []
    for x in lst:
        if not hl(x):
            if rlst:
                if not lst2:
                    pass
                else:
                    lst1.append(lst2)
            else:
                lst1.append(' '.join(lst2))
            lst2 = []
        elif x:
            lst2.append(x)

    if rlst:
        lst1.append(lst2)
    else:
        lst1.append(' '.join(lst2))
    return lst1



def abridge(lst):
    lst1 = []
    on = 0
    for x in lst:
        if '__start' in x:
            on = 1
        elif '__stop' in x:
            break
        elif on:
            lst1.append(x)
    return lst1


def get_poem_dunder(lst, poem, itrans=0):
    lst1 = []
    on = 0
    for x in lst:
        if on and x.startswith('__'):
            if itrans:
                if on == 2:
                    break
                on = 2
            else:
                break
        elif  x.startswith(f'__{poem}'):
            p ('hey')
            on = 1

        elif on:
            lst1.append(x)
    return lst1



def dct_idx(dct, idx=0, kv='k'):
    if not dct:
        return {}

    if kv == 'k':
        return list(dct.keys())[idx]
    elif kv == 'i':
        return list(dct.items())[idx]
    else:
        return list(dct.values())[idx]

def largest_member(dct, tie=0):
    # values must be integers or floats
    dct = sort_dct_val_rev(dct)
    if len(dct)>1 and tie:
        s = dct_idx(dct)
        t = dct_idx(dct,1,'v')
        if s == t:
            return (s,t)

    return dct_idx(dct)




def get_key(dict1, val):
    for k, v in dict1.items():
        if v == val:
            return k
    else:
        return None

def from_dct_sum2perc(dct):
    '''
    the dict must have integers as values
    this will convert the integers into percentages of a
    whole
    '''
    tot = 0
    for k,v in dct.items():
        tot += v
    dct1 = {}
    for k,v in dct.items():
        dct1[k] = int((v/tot)*100)
    return dct1



def sort_dct_by_dct(to_be_ordered, orderer):
    dct2 = {}
    orderer = sort_dct_val_rev(orderer)
    for k,v in orderer.items():
        dct2[k] = to_be_ordered[k]
    return dct2

def sort_dct_by_dct2(to_be_ordered, orderer):
    dct2 = {}
    for k,v in to_be_ordered.items():
        dct2[k] = orderer[k]
    dct2 = sort_dct_val_rev(dct2)
    return sort_dct_by_dct(to_be_ordered, dct2)


def get_multiple_keys(dict1, val):
    lst = []
    for k, v in dict1.items():
        if v == val:
            lst.append(k)
    return lst


def dct_replace(x, y, dct):
    if x not in dct:
        return dct
    dct1 = {}
    for k, v in dct.items():
        if k == x:
            dct1[y] = v
        else:
            dct1[k] = v

    return dct1


def divide_range_nonzero(divisions: int, start: int, stop: int, idx: int):
    total = stop - start
    fstart, fstop = divide_range(divisions, total, idx)
    return fstart + start, fstop + stop


def split_dct(dct, start, stop=-1):
    if stop == -1:
        stop = len(dct)
    lst1 = list(dct.keys())[start:stop]
    lst2 = list(dct.values())[start:stop]
    return {k: v for k, v in zip(lst1, lst2)}


def divide_range_w_max(num: int, maxi: int):
    '''
    suppose you have a number 5,000,000 whereas
    the highest acceptable number is 1,000,000.
    this function will divide the number such that
    each division has the same amount and each
    division is less than the highest acceptable number.
    further it will make a list of the ranges so as
    to divide the list
    '''

    b = (num // maxi) + 1
    c = num // b
    lst = []
    m = 0
    lst_num = 0
    for z in range(int(b)):
        m += c
        if z == b - 1:
            lst.append([lst_num, num])
        else:
            lst.append([lst_num, m])
        lst_num = m

    return lst

def divide_range_w_min(total: int, targ:int, mini: int):
    '''
    suppose you want to divide a quantity such that each
    quantity is close to the target 300.  but you don't want the
    remainder to be below a certain amount.  that is what
    the mini specifies
    '''


    while 1:
        c = total % targ
        if c < mini:
            targ += 1
        else:
            break

    lst = []
    d = 0
    while 1:
        d += targ
        if d > total:
            break
        lst.append(d)

    return lst



def ideal_amount(lst, num):
    dct = {}
    acceptable = [x for x in range(num - 2, num + 5)]
    c = 2
    found = False
    while True:
        rem = len(lst) % c
        sz = len(lst) // c
        if sz in acceptable:
            found = True
            if rem == 0:
                return c
            else:
                dct[rem] = c
        elif sz not in acceptable and found:
            break
        c += 1

    highest = max(list(dct.keys()))
    return dct[highest]


def divide_lst(lst, divisions):
    lst1 = []
    for i in range(divisions):
        if i == divisions - 1:
            bb = 8

        start1, stop1 = divide_range(divisions, len(lst), i)
        lst1.append(lst[start1:stop1])

    return lst1


def divide_lst_by_size(lst, sz):
    lst1 = []
    while len(lst) > sz:
        lst2 = lst[:sz]
        lst1.append(lst2)
        lst = lst[sz:]
    if lst:
        lst1.append(lst)
    return lst1


def divide_range(divisions: int, total: int, idx: int, begin=0):
    sec = total // divisions
    start = (idx * sec) + begin
    if total % divisions != 0 and idx == divisions:
        stop = total
    else:
        stop = start + sec
    return start, stop


def divide_dictionary(dict1, divisions):
    total = len(dict1)
    keys = list(dict1.keys())
    tdicts = []
    for i in range(divisions):
        start, stop = divide_range(divisions, total, i)
        dict2 = {}
        for j in range(start, stop):
            dict2[keys[j]] = dict1[keys[j]]
        tdicts.append(dict2)

    return tdicts


def slice_dictionary(dct, start, stop=0):
    if not stop:
        stop = len(dct)
    keys = list(dct.keys())
    dct1 = {}
    for k in keys[start:stop]:
        dct1[k] = dct[k]
    return dct1


################## combo functions


def multiple_cartesian3(lst, lst2):
    result = []
    for i in range(0, len(lst)):
        for j in range(0, len(lst2)):
            if type(lst[i]) != list:
                lst[i] = [lst[i]]

            temp = [num for num in lst[i]]
            temp.append(lst2[j])
            result.append(temp)

    return result


def multiple_cartesian2(lst):
    temp = lst[0]
    for i in range(1, len(lst)):
        temp = multiple_cartesian3(temp, lst[i])

    return temp


def multiple_cartesian(lst):
    lst2 = []
    dct = {}
    for x in lst:
        for y in range(1, 4):
            z = str(x) + "." + str(y)
            dct.setdefault(x, []).append(z)

    for x, y in dct.items():
        lst2.append(y)

    return multiple_cartesian2(lst2)


class get_combos_dif_dim:
    def main(self, ranges):
        '''
        the ranges needs to be a list of integers
        in order to get this to work you need to input a range and
        in each slot you need to specify how large the slots are, so it could
        be
        [2,2,2] will produce a 3 * 8 matrix
        '''

        global lgt
        # for some reason you need a 1 dummy at the end of this list
        ranges.append(1)
        # ranges = [2, 2, 2, 2, 2, 2, 2, 2, 2, 1]
        num2 = mult_lst(ranges[:-1])
        num2 = good_numbers(num2, 2)

        lgt = len(ranges) - 1
        combination = []
        self.all_combos = []

        for r in range(ranges[0]):
            self.get_all_combos2(ranges, combination, 0, r)
        self.combinations = combination
        num = len(self.all_combos)
        num = good_numbers(num, 2)

        if num != num2:
            p('numbers do not match')
        else:
            pass
            # p(f'{num} well-formed formulas')

        return self.all_combos

    def get_all_combos2(self, ranges, combination, n, val):
        global lgt
        combination.append(val)
        if n == lgt:
            # p (combination)
            combination.pop()
            x = combination
            self.add2tuple(x, len(ranges) - 1)
            return

        for r in range(ranges[n + 1]):
            self.get_all_combos2(ranges, combination, n + 1, r)
        combination.pop()

    def add2tuple(self, x, y):
        if y == len(x):
            # tpl = (x[0], x[1], x[2], x[3])
            # tpl = (x[0], x[1], x[2], x[3], x[4], x[5], x[6], x[7], x[8])
            # self.all_combos.append(tpl)
            self.all_combos.append(tuple(x))
            return


################# internet functions


def use_beautiful_soup(str1, single=False, xml=0):
    if not xml:
        soup = beautiful_soup(str1, 'html.parser')
    else:
        soup = beautiful_soup(str1, 'xml')
    obj = soup.text
    if not single:
        return obj.split('\n')
    else:
        return obj[:-1]


def reset_tor():
    tr = TorRequest(password='Finnegan76!')
    tr.reset_identity()
    response = tr.get('http://ipecho.net/plain')
    p(f'now using ip {response.text}')
    return tr


def web_to_text_tor(url, tr):
    response = tr.get(url)
    soup = beautiful_soup(response.text, "html.parser")
    web_page = soup.text
    return web_page.split("\n")


def web_to_text(url, auth=False):
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) '
                             'AppleWebKit/537.51.2 (KHTML, like Gecko) '
                             'Version/7.0 Mobile/11D257 Safari/9537.53'}
    # url = "https://www.huffpost.com/"
    if not auth:
        req = session.get(url, headers=headers)
    else:
        req = session.get(url, headers=headers, auth=auth)

    bs = beautiful_soup(req.text, 'html.parser')
    web_page = bs.text
    return web_page.split("\n")


def get_code(url, auth=False):
    session = requests.Session()
    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) '
                             'AppleWebKit/537.51.2 (KHTML, like Gecko) '
                             'Version/7.0 Mobile/11D257 Safari/9537.53'}
    # url = "https://www.huffpost.com/"
    if not auth:
        req = session.get(url, headers=headers)
    else:
        req = session.get(url, headers=headers, auth=auth)

    return req.text.split("\n")


def web_to_text2(str1, parser='xml', headers=0, strange_char=0):
    ## xml, or lxml or html.parser
    if headers:
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 7_1_2 like Mac OS X) '
                                 'AppleWebKit/537.51.2 (KHTML, like Gecko) '
                                 'Version/7.0 Mobile/11D257 Safari/9537.53'}

        response = requests.get(str1, headers=headers)
    else:
        response = requests.get(str1)

    if response.status_code != 200:
        p(f'bad status {response.status_code} {str1}')
        return [], response.status_code
    final_url = response.url

    if strange_char:
        r = response
        encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
        soup = beautiful_soup(r.content, from_encoding=encoding)
    else:
        r = response.text
        soup = beautiful_soup(r, parser)
    web_page = soup.text
    return web_page.split("\n"), final_url


def temp12(str1):
    r = requests.get(str1)
    parser = 'html.parser'
    # if response.status_code != 200:
    #     p(f'bad status {response.status_code}')
    #     return [], response.status_code

    final_url = r.url
    # soup = beautiful_soup(r.content)
    encoding = r.encoding if 'charset' in r.headers.get('content-type', '').lower() else None
    soup = beautiful_soup(r.content, from_encoding=encoding)
    web_page = soup.text
    web_page2 = soup.get_text()


##################   subprocess functions


def save_open_file(file):
    os.system(
        f'''/usr/bin/osascript -e 'tell app "TextEdit" to save (every window whose name is "{file}")' ''')


def close_file(str1):
    os.system(
        f'''/usr/bin/osascript -e 'tell app "TextEdit" to close (every window whose name is "{str1}")' ''')


def make_new_file(file, lines):
    outF = open(file, "w")
    outF.writelines(lines)
    outF.close()


def open_w_text_edit(file):
    # file = "/Users/kylefoley/codes/byu_docs/dictionaries/first_name_research/btn_tree_start_r/Jane.rtxt"
    script = f'''
    tell application "TextEdit"
	    open file "{file}"
    end tell
    '''
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # stdout, stderr = p.communicate(script)
    # os.system(
    #     f'''/usr/bin/osascript -e 'tell application "TextEdit" open file "{file}" end tell' ''')
    #


def open_w_ms(file):
    file = f'Macintosh HD/{file}'
    file = file.replace("/", ":")
    # file = "/Users/kylefoley/codes/byu_docs/dictionaries/first_name_research/btn_tree_start_r/Jane.rtxt"
    script = f'''
    tell application "Microsoft Word"
	    open file "{file}"
    end tell
    '''
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    # stdout, stderr = p.communicate(script)
    # os.system(
    #      f'''/usr/bin/osascript -e 'tell application "Microsoft Word" open file "{file}" end tell' ''')


def close_and_save(file):
    if not file[:-4] == '.txt':
        file += '.txt'
    os.system(f'''/usr/bin/osascript -e 'tell app "TextEdit" to save (every window whose name is "{file}")' ''')
    os.system(f'''/usr/bin/osascript -e 'tell app "TextEdit" to close (every window whose name is "{file}")' ''')


def open_txt_file(file):
    if "." not in file[-4:]:
        file += '.txt'
    p = subprocess.call(['open', file])


def write_str_lst(lst, file):
    f = open(file, 'w+')
    for x in lst:
        f.write(x + "\n")
    f.close()
    open_txt_file(file)


def open_pdf(file):
    pfile = open(file, 'rb')
    return PyPDF2.PdfFileReader(pfile)


def get_pdf_page(num, pdf_file):
    pageObj = pdf_file.getPage(num)
    return pageObj.extractText()


def simple_move(**kwargs):
    src = kwargs.get('src')
    target = kwargs.get('target')
    lst = kwargs.get("lst")
    fork_num = kwargs.get('fork_num', 0)
    start = kwargs.get('start', 0)
    stop = kwargs.get('stop', len(lst))
    start_time = time.time()
    total_files = stop - start
    p('start')
    b = 0
    for e, x in en(lst[start:stop]):
        if pi.open_pickle("bool1"):
            if not os.path.exists(target + x):
                p(x)
                b += 1
                shutil.copy2(src + x, target + x)
                print_intervals(b, 10, fork_num, stop - start)
                # if e and e % 50 == 0:
                #     calculate_progress(total_files - e, e, start_time, fork_num)

        else:
            break

    p(f'done fork {fork_num}')


def calculate_progress(remaining, done_files, start_time, fork_num):
    total_time = time.time() - start_time
    files_per_second = done_files / total_time
    remaining_minutes = (remaining / files_per_second) / 60
    if (remaining_minutes * 5) > 300:
        remaining_hours = remaining_minutes / 300
        remaining_hours = good_numbers(remaining_hours, 3)
        p(f"remaining hours {remaining_hours} for fork {fork_num}")
    else:
        remaining_minutes = remaining_minutes / 5
        remaining_minutes = good_numbers(remaining_minutes, 3)
        p(f"remaining minutes {remaining_minutes} for fork {fork_num}")


################ other functions



def err_idx(num, lst):
    if num > len(lst):
        return len(lst)
    return num


def get_text_size(text, font_size=18, font_name='Times New Roman'):
    font = ImageFont.truetype(font_name, font_size)
    size = font.getsize(text)
    return size



def cut_list(lst, start, stop):
    if stop < 0:
        start1 = start + stop
        stop = start + (stop)*-1
    else:
        start1 = start
    start1 = beg_list(lst, start1)
    stop = end_list(lst, stop)
    return lst[start1:stop]


def beg_list(lst,num):
    try:
        c = lst[num]
        return num
    except:
        return 0

def end_list(lst, num):
    try:
        c = lst[num]
        return num
    except:
        return len(lst)

def outside(s, l, r):
    if s.count(l) != 1 or s.count(r) != 1:
        return ""

    if s[0] == l:
        return s[s.index(r) + 1:].strip()
    elif s[-1] == r:
        return s[:s.index(l):].strip()
    else:
        return ""

def inside(s, l, r):
    if s.count(l) != 1 or s.count(r) != 1:
        return ""
    t = lambda s, l, r: s[s.index(l) + 1:s.index(r)]
    return t(s,l,r)


def tclean(x):
    x = x.lower()
    return re.sub(r'[^a-zA-Z]', '', x)


def titlecase(curText: str):
    Exclusions = [
        "a", "an", "the",  # Articles
        "and", "but", "or", "by", "nor", "yet", "so",  # Conjunctions
        "about", "above", "across", "after", "against", "along", "among", "around", "at", "before",  # Prepositions
        "behind", "between", "beyond", "but", "by", "concerning", "despite", "down", "during",
        "except", "following", "for", "from", "in", "including", "into", "like", "near", "of",
        "off", "on", "out", "over", "plus", "since", "through", "throughout", "to", "towards",
        "under", "until", "up", "upon", "with", "within", "without"
    ]
    """ Take a string and return it in a fashion that follows proper title case guidelines """

    Exclusions += top_100_roman(0)
    under = ""
    if curText.startswith('_'):
        for e, x in en(curText):
            if x != '_':
                under = "_" * e
                break
        curText = curText[e:]

    outString = ""
    fragments = re.split(r'(\".*?\")|(\'.*?\')|(“.*?”)|(‘.*?’)',
                         curText)  # Extract titles in quotation marks from string

    for fragment in fragments:  # Treat and re-assemble all fragments
        if fragment:  # skip empty matches generated by the OR in regex
            fragString = ""
            tokens = fragment.split();  # Break string into individual words

            if tokens:
                for word in tokens:  # Check each word

                    punct = word[-1]  # Check for trailing punctuation mark
                    if punct.isalpha():
                        punct = ""
                    else:
                        word = word[:-1]

                    if word.lower() in Exclusions:  # if it is excluded,
                        fragString += word.lower() + punct + " "  # make it lowercase
                    else:  # otherwise,
                        fragString += word.capitalize() + punct + " "  # capitalize it

                cap = 1
                if not fragString[0].isalpha():
                    cap = 2

                outString += (fragString[:cap].upper() + fragString[cap:]).strip() + " "

    return under + (outString[:1].upper() + outString[1:]).strip()


def walk_directory(path, ext='.txt', list_of_files={}):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(ext):
                list_of_files[filename] = os.sep.join([dirpath, filename])
    return list_of_files


def walk_directory_lst(path, ext='.txt', list_of_files=[]):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for filename in filenames:
            if filename.endswith(ext):
                list_of_files.append([filename, os.sep.join([dirpath, filename])])
    return list_of_files


def sort_mix(x):
    return sorted(x, key=lambda L: (L.lower(), L))


def sort_mix_dct_key(dct):
    lst = list(dct.keys())
    lst = sort_mix(lst)
    return {x: dct[x] for x in lst}


def from_uppercase2greek(str1):
    for e, x in en(str1):
        if ord(x) > 64 and ord(x) < 91:
            str1 = str1.replace(x, chr(ord(x) + 880))
    return str1


def from_greek2uppercase(str1):
    for e, x in en(str1):
        if ord(x) > 944 and ord(x) < 971:
            str1 = str1.replace(x, chr(ord(x) - 880))

    dct = {
        chr(993): "<",
        chr(994): ">",
        chr(995): "/",
        chr(996): "|",
        chr(997): ":",
        chr(998): "&",
        chr(999): "\\",
    }
    for x, y in dct.items():
        str1 = str1.replace(x, y)

    return str1


def elim_spec_char(x):
    if type(x) == str:
        ext = ""
        if x.endswith('.txt') or x.endswith('.pkl'):
            ext = x[-4:]
            x = x[:-4]

        if "/" in x:
            x = x.replace('/', chr(991))
        if x[0] == '.':
            x = x.replace('.', chr(992))
        if reg(r'[\<\>\/\|\:\&\\]', x):
            dct = {
                "<": chr(993),
                ">": chr(994),
                "/": chr(995),
                "|": chr(996),
                ":": chr(997),
                "&": chr(998),
                "\\": chr(999),
            }

            st = set(y for y in x if reg(r'[\<\>\/\|\:\&\\]', y))
            for let in st:
                x = x.replace(let, dct[let])

        x = from_uppercase2greek(x)
        if ext:
            x += ext
    return x


def decimal_places(num_dec, num):
    str1 = f"0:.{num_dec}f"
    str1 = "{" + str1 + "}"
    return float(str1.format(num))


def is_str_num(obj):
    try:
        b = int(obj)
        return True
    except:
        return False


def is_str_float(obj):
    if obj == 'INF':
        return False
    try:
        b = float(obj)
        return True
    except:
        return False


def test_2dicts(old_dict, new_dict, new_dict2={}):
    correct = True
    if old_dict == new_dict:
        return True
    else:
        for x, y in new_dict.items():
            m = old_dict.get(x)
            if not m:
                correct = False
                p('')
                p(f'{x} is not in the old dict')
                # p(f"{new_dict2.get(x)}")

            else:
                if m != y:
                    correct = False
                    p('')
                    p(f"{m} is wrong")
                    # p(f"{new_dict2.get(x)}")

        return correct


def test_2dicts_diff_keys(old_dict, new_dict):
    old_set = set(old_dict.values())
    new_set = set(new_dict.values())
    if old_set == set(new_dict.values()):
        return True
    else:
        for x, y in new_dict.items():
            if y not in old_set:
                p(f"{y} is not in the old set")
                p("")
        for x, y in old_dict.items():
            if y not in new_set:
                p(f"{y} is not in the new set")
                p("")

        return False


def old_dct_small2(old_dict, new_dict):
    for k, v in old_dict.items():
        new = new_dict[k]
        if v != new:
            p(f"""key {k} in the old is: 
            {v} 
            and in the new it is:
            {new}""")
            return False
    return True


def old_dct_small(old_dict, new_dict):
    old_set = set(old_dict.values())
    for v in new_dict.values():
        if "=" not in v:
            if v not in old_set:
                p(v)

    return True


def rindex(str1, char):
    b = len(str1) - 1
    for x in reversed(str1):
        if x == char:
            return b
        b -= 1
    raise Exception('you failed to find the character in rindex function')


def ujsonc_set(set1):
    return set(ujsonc(set1))


def get_first_non_blank(line):
    for x in line:
        if x != " ":
            return x


def get_log_lines(fil, extract_class=False):
    mlines = []
    doc_string_on = False
    for line in open(fil):
        if line == '\n':
            pass
        else:
            bare_line = line.replace(" ", "")
            bare_line = bare_line.replace("\n", "")

            # if  doc_string_on:
            #     p (line)
            if 'inextremely' in bare_line:
                bb = 8

            if doc_string_on:
                if bare_line.endswith("'''") or bare_line.endswith('"""'):
                    doc_string_on = False
                elif bare_line.startswith("'''") or bare_line.startswith('"""'):
                    doc_string_on = False

            else:
                if (re.search(r"^'''", bare_line) and re.search(r"'''$", bare_line) and bare_line.count("'") > 3) or \
                        (re.search(r'^"""', bare_line) and re.search(r'"""$', bare_line) and bare_line.count('"') > 3):
                    pass

                elif (bare_line.startswith("'''") or bare_line.startswith('"""')) and \
                        not re.search(r"\)$", bare_line):
                    doc_string_on = True
                elif extract_class and bare_line.startswith("#class"):
                    mlines.append(line)
                elif extract_class and bare_line.startswith("#end"):
                    return mlines
                elif bare_line.startswith("#") and "att_embeds" not in line:
                    pass
                elif line.endswith("\n"):
                    mlines.append(line[:-1])
                else:
                    mlines.append(line)
    return mlines


def powerset(list1, empty=False):
    b = chain.from_iterable(combinations(list1, r) for r in range(len(list1) + 1))
    if empty:
        return [set(x) for x in b]
    else:
        return [set(x) for x in b if b]


class ErrorWithCode(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return repr(self.code)


def special_round(x, sig=1):
    if x == 0: return x
    if x > 10:
        return int(x)
    elif x > 1:
        return round(x, 1)
    elif x > .1:
        return round(x, 1)
    else:

        return round(x, sig - int(floor(log10(abs(x)))) - 1)


def strip_n_split(str1, char=" "):
    lst = str1.split(char)
    return [x.strip() for x in lst]


class make_columns:
    def main(self, lst, width=35, rows=50):
        lst1 = []
        self.final = []
        self.width = width
        for x in lst:
            x = x.replace('\n', ' ')
            z = limit_str_70(x, width - 8, 1, 0)
            lst1 += z

        lsts = divide_lst_by_size(lst1, rows)
        self.step2(lsts)
        return self.final

    def step2(self, lsts):
        b = 0
        while b < len(lsts) - 1:
            lst2 = lsts[b]
            lst3 = lsts[b + 1]
            lst4 = []
            c = 0
            while c < len(lst2):
                line1 = lst2[c]
                try:
                    line2 = lst3[c]
                except:
                    line2 = ""
                # space1 = self.width - len(line1)
                # space = " " * space1
                line2 = line2.rjust(self.width)
                line1 = line1.ljust(self.width)

                line3 = f"{line1}{line2}"
                lst4.append(line3)
                c += 1
            b += 2

            self.final.append(lst4)

        if len(lsts) % 2 != 0:
            self.final.append(lsts[-1])


def merge_pdfs(lst, dir1):
    merger = PyPDF2.PdfFileMerger()

    for x in lst:
        merger.append(open(dir1 + x, 'rb'))
    with open(dir1 + 'result.pdf', 'wb') as f:
        merger.write(f)


def get_remaining_files(files: set, folder: str):
    return files - set(os.listdir(folder))


def get_idx_file(file, name):
    y = file[len(name):]
    if "." in y:
        idx = y.index('.')
        num = y[:idx]
    else:
        for e, z in en(y):
            if z.isdigit():
                break
        num = y[e:]

    return num


def get_num_series(folder, name=''):
    lst = []
    num_lst = []
    for x in os.listdir(folder):
        if x.startswith(name):
            num = get_idx_file(x, name)
            if num.isdigit():
                lst.append(int(num))
        else:
            if "." in x:
                idx = x.index('.')
                if x[:idx].isdigit():
                    num_lst.append(int(x[:idx]))

    if num_lst and not lst:
        return max(num_lst) + 1

    if not lst:
        return 1
    return max(lst) + 1


def backup(file, folder):
    if not folder[-1] == '/':
        folder += "/"
    idx = file.rindex('.')
    file1 = file[:idx]
    ext = file[idx:]
    file1 = re.sub(r'\d', '', file1)
    num = get_num_series(folder, file1)
    dest = f'{folder}{file1}{num}{ext}'
    shutil.copy(f"{folder}{file}", dest)


def sort_str_num(lst):
    dct = {}
    for x in lst:
        int1 = int(x)
        dct[x] = int1
    dct = sort_dct_val(dct)
    return list(dct.keys())


def good_numbers(x, places, kind='string', ignore_nine=0):
    if not ignore_nine and x > .99 and x < 1:
        return handle_nine(x)

    if type(x) == int:
        if x >= 0 and len(str(x)) <= places:
            return x
        elif x < 0 and len(str(x)) <= places + 1:
            return x

    c = 0
    while 1:
        x = significant_digits(x, places)
        if "e" in str(x) and str(x).index('e') > places + 1:
            d = str(x).index('e')
            x = significant_digits(x, places)
            if c > 3:
                x = str(x)
                x = float(x[:places + 1] + x[d:])
                return x
        else:
            break
        c += 1

    if kind == 'string':
        return number_comma(x)
    else:
        return x


def handle_nine(x):
    c = str(x)[2:]
    b = 0
    while b < len(c) and c[b] == '9':
        b += 1
    dig = 0
    if b < len(c):
        dig = c[b]

    return float(f"{b}.{dig}")


def number_comma(num):
    if num < 10:
        return str(num)

    return f"{int(num):,d}"


def create_working_environment(name):
    subprocess.run(["python3", "-m", name, "~/downloads/codes/"])


def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def print_intervals(number, interval, fork=None, total=0):
    if number > 0 and number % interval == 0 and number >= interval:
        if total:
            printProgressBar(number, total)
            # per = int((number / total) * 100)
            # number = f"{per}%"

        # if fork == None:
        #     p(number)
        # else:
        #     p(number)
        # else:
        #     p(f"fork {fork} - {number}")
        return


def print_percentage(num, perc, total):
    if num == 0: return
    if num % perc == 0 and num > perc:
        p(decimal_places(2, num / total))
        # p (number_comma(num))


def cut_string_index(str1, char):
    try:
        return str1[:str1.index(char)]
    except ValueError:
        return str1


def limit_str_70(str1, num=70, indent1=4, as_string=True, name=""):
    ostr = str1
    indent = " " * indent1
    if len(str1) > num:
        lst1 = []
        b = 0
        c = 0 if b == 0 else 5

        while len(str1) > num and ' ' in str1[c:]:
            dct = {}
            str4 = " "
            q = 0
            while not dct:
                lst = [e + c for e, x in en(str1[c:]) if x == str4]
                dct = {x: abs(num - x) for x in lst if x < num + 10}
                if not dct:
                    str4 = '-'
                else:
                    dct = sort_dct_val(dct)
                q += 1
                if q > 20:
                    if as_string:
                        return str1
                    else:
                        return [str1]

            val = list(dct.keys())[0]
            str2 = str1[:val]
            lst1.append(str2)
            str1 = indent + str1[val + 1:]
            b += 1
            c = 0 if b == 0 else 5
            if b > 200:
                p(name)
                assert False, 'infinite loop'
        lst1.append(str1)
        if as_string:
            final = '\n'.join(lst1)
            return final
        else:
            return lst1
    else:
        if as_string:
            return str1
        else:
            return [str1]


def get_atts_meths(cls):
    atts = [x for x in cls.__dict__]
    x = dir(cls)
    methods = [x for x in x if not x[:2] == "__" if x not in atts]
    return atts, methods


def setsetdefault(dct, key, value):
    if key in dct:
        val = dct[key]
        val |= value
        dct[key] = val
    else:
        dct[key] = value


def isclass(x):
    exceptions = [class2str('gen_dict_func.fs')]
    if str(type(x)) in exceptions:
        return False

    try:
        y = x.__dict__
        return True
    except:
        return False


def time_function(func, *args, **kwargs):
    b = time.time()
    func(*args, **kwargs)
    p(time.time() - b)


def determiners():
    list1 = pi.open_pickle("determiners").append("a" + up)
    return list1


def get_target_col_lst(lst, col_name, rw):
    for e, str1 in en(lst[rw]):
        if str1 == col_name:
            return e
    p(f'you failed to find {col_name} column in row {rw}')
    raise Exception


class class_equality:
    def __eq__(self, other):
        for att in self.__dict__:
            obj = getattr(self, att)
            try:
                ot_obj = getattr(other, att)
            except AttributeError:
                p(f'the other class does not have attribute: {att}')
                return False
            if obj != ot_obj:
                p(f"the attribute {att} does not match")
                return False

        return True


def preserve_methods(cls):
    return set(x for x in cls.__dict__)


def rint(num):
    b = round(num)
    return int(b)


def delete_attr(obj, list1):
    for att in list1:
        delattr(obj, att)


def setdefaultset(dct, key, value):
    dct[key] = dct.get(key, set()).union(value)
    return dct


def pycharm():
    if 'kylefoley' in sys.argv[0] and len(sys.argv) == 1:
        return 1


def get_arguments():
    arguments = sys.argv
    try:
        arg1 = arguments[1]
    except:
        arg1 = ""
    try:
        arg2 = arguments[2]
    except:
        arg2 = ""
    try:
        arg3 = arguments[3]
    except:
        arg3 = ""
    try:
        arg4 = arguments[4]
    except:
        arg4 = ""
    try:
        arg5 = arguments[5]
    except:
        arg5 = ""

    return [1, arg1, arg2, arg3, arg4, arg5]


def trim_list(lst):
    e = len(lst) - 1
    while lst[e]:
        del lst[e]
        e -= 1
    return lst


def del_last_empty_lst(lst):
    try:
        while len(lst[-1]) == 1 and not reg(r'\S', lst[-1][0]):
            del lst[-1]
        return lst
    except:
        while not lst[-1]:
            del lst[-1]
        return lst


def del_last_empty_rw(lst):
    if lst:
        while type(lst[-1] == str) and not reg(r'\S', lst[-1]):
            del lst[-1]
    return lst


def del_last_empty_lstolst(lst):
    if lst:
        while type(lst[-1][0] == str) and not reg(r'\S', lst[-1][0]):
            del lst[-1]
    return lst


def convert_nums(x):
    for e, z in en(x):
        try:
            z = int(z)
            x[e] = z
        except ValueError:
            try:
                z = float(z)
                x[e] = z
            except ValueError:
                pass

    return x


def sort_dct_keys_by_len(dct, rev=0):
    lst = list(dct.keys())
    lst = sort_lst_by_len(lst, rev)
    dct1 = {}
    for y in lst:
        dct1[y] = dct[y]
    return dct1


def sort_lst_by_len(lst, long_first=0):
    dct = {x: len(x) for x in lst}
    if long_first:
        dct = sort_dct_val_rev(dct)
    else:
        dct = sort_dct_val(dct)

    return list(dct.keys())


def nat_nums():  # number generator
    counter = 0
    while True:
        counter += 1
        yield str(counter)


def top_100_roman(miniscule=1, limit=101):
    lst = []
    for x in range(1, limit):
        lst.append(int2roman(x))
    lst1 = []
    if miniscule:
        for x in lst:
            lst1.append(x.lower())
            lst1.append(x)

        return lst1
    return lst


def int2roman(num):
    val = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    syb = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    roman_num = ""
    for i in range(len(val)):
        count = int(num / val[i])
        roman_num += syb[i] * count
        num -= val[i] * count
    return roman_num


def roman2int(s, small=0, mini=0):
    if mini:
        s = s.upper()
    roman = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000, 'IV': 4, 'IX': 9, 'XL': 40, 'XC': 90,
             'CD': 400, 'CM': 900}
    i = 0
    num = 0
    while i < len(s):
        if s[i] not in roman:
            return 0

        if i + 1 < len(s) and s[i:i + 2] in roman:
            num += roman[s[i:i + 2]]
            i += 2
        else:
            # print(i)
            num += roman[s[i]]
            i += 1

    if small:
        if num < 100:
            return num
        else:
            return 0

    return num


def number_abbrev(tpl):
    taken = {}  # new dict holding key/val = letter/number
    var_nums = []
    ins_nat_nums = nat_nums()  # initiate the geranator
    for var_tpl, snum in tpl:
        tvars = []
        for var in var_tpl:
            if var[-1] == ':':
                tvars.append(var)
                continue

            elif var not in taken:
                taken[var] = next(ins_nat_nums)  # update dict by use of generator

            tvars.append(taken[var])

        var_nums.append((snum, tvars))

    for snum, tvars in var_nums:
        print(f"{snum}   {tvars}")

    return


class compare_object:
    def compare_objectfu(self, x, y, get_all_errors=True):
        self.get_all_errors = get_all_errors
        self.is_true = True
        return self.compare_by_type(x, y)

    @staticmethod
    def print_co(x, y, str1):
        p(f"""
                    {x} 

                    {str1}

                    {y}
                    """)

    def compare_by_type(self, x, y):
        if type(x) != type(y):
            self.print_co(x, y, "is not the same type as:")
            return False
        elif isinstance(x, list) or isinstance(x, tuple):
            bool1 = self.compare_lists(x, y)
        elif isinstance(x, dict):
            bool1 = self.compare_dicts(x, y)
        else:
            if not x == y:
                self.print_co(x, y, "does not equal")
                if not self.get_all_errors:
                    return False
                else:
                    self.is_true = False
                    return False
            else:
                return True

        return bool1

    def compare_dicts(self, x, y):
        for k, v in x.items():
            z = y.get(k)
            bool1 = self.compare_by_type(v, z)
            if not bool1 and not self.get_all_errors:
                return False
        return True

    def compare_lists(self, x, y):
        for a, b in zip(x, y):
            bool1 = self.compare_by_type(a, b)
            if not bool1 and not self.get_all_errors:
                return False
        return True


def sort_numbered_files(dir1, slice1=0, short=False):
    lst = os.listdir(dir1)
    # dct = {x[:x.index(".")]: x for x in lst if x != ds}
    # dct = {int(x[:x.index(".")]): x for x in lst if x != ds}
    dct = {int(re.sub(r'[^0-9]', '', x)): x for x in lst if x != ds}
    dct = sort_dct_key(dct)
    if not slice1 and short:
        return list(dct.values())
    else:
        dct = {k: dir1 + v for k, v in dct.items()}
        if slice1:
            dct = slice_dictionary(dct, 0, slice1)
        return list(dct.values())


def check_nested_class(oclass, iclass, attributes: list):
    for attribute in attributes:
        if getattr(oclass, attribute) != getattr(iclass, attribute):
            p(f"the attribute {attribute} is different in {iclass.__class__.__name__}")
            raise Exception


def exit_3b():
    list1 = []
    while True:

        b = keyboard.read_key()
        print(b)
        d = "".join(list1)
        print(f"list1 {d}")
        if b == 'b':
            list1.append(b)
            if "".join(list1) == 'bbbbbb':
                break
        elif list1 != [] and b != 'b':
            list1 = []


def pdict(dict1):
    for k, v in dict1.items():
        p(f"{k} {v}")


def get_name2bytes(dir1: str, large=0, owner='kylefoley'):
    # dir1 must be a directory
    # each file must have the same owner in the directory
    cmd = ['ls', '-l', dir1]
    output = get_terminal_output(cmd, large)
    lst = output.split()
    name2bytes = {}
    for e, x in en(lst):
        if x == owner:
            bytes1 = lst[e + 2]
            name = lst[e + 6]
            name = name[:name.index('\\')]
            name2bytes[name] = int(bytes1)

    return name2bytes


def get_terminal_output(cmd: list, large=0):
    # cmd must be a list of strings which are terminal commands
    # if the output is large, set large to 1
    if not large:
        output = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
        return str(output)
    else:
        with tempfile.TemporaryFile() as tempf:
            proc = subprocess.Popen(cmd, stdout=tempf)
            proc.wait()
            tempf.seek(0)
            output = tempf.read()
            return str(output)


def make_dir_rec(str1):
    if str1[-1] == '/':
        str1 = str1[:-1]
    failures = []
    while 1:
        try:
            if os.path.exists(str1) and not failures:
                return

            os.mkdir(str1)
            for x in reversed(failures):
                os.mkdir(x)
            return

        except:
            if "/" not in str1:
                assert 0
            idx = str1.rindex("/")
            failures.append(str1)
            str1 = str1[:idx]


@timer3
def zipdir1(path, zip_path, num=0):
    if not num:
        num = ""
    zipf = zipfile.ZipFile(f'{zip_path}{num}.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir2(f'{path}', zipf)
    zipf.close()


def zipdir2(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            str1 = os.path.join(root, file)
            ziph.write(str1)


def zip_dir_sh(output_filename, dir_name):
    shutil.make_archive(output_filename, 'zip', dir_name)


def unzip(path_to_zip_file, directory_to_extract_to):
    with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
        zip_ref.extractall(directory_to_extract_to)


def unzip2(src, pfolder):
    # pfolder = r"D:\Download"
    # src = r"D:\Download\my_file.zip"
    if src[-4:] != '.zip':
        src += '.zip'

    with zipfile.ZipFile(src) as zip_file:
        for member in zip_file.namelist():
            filename = os.path.basename(member)
            # skip directories
            if not filename:
                continue

            # copy file (taken from zipfile's extract)
            source = zip_file.open(member)
            target2 = open(os.path.join(pfolder, filename), "wb")
            with source, target2:
                shutil.copyfileobj(source, target2)


def untar2(src, output_dir):
    tar = tarfile.open(src)
    for member in tar.getmembers():
        if member.isreg():  # skip if the TarInfo is not files
            member.name = os.path.basename(member.name)  # remove the path by reset it
            tar.extract(member, output_dir)  # extract


def get_memory():
    loc = locals()
    glo = globals()
    tot = merge_2dicts(loc, glo)
    sz_dct = {}
    tot_bytes = 0
    for x, y in tot.items():
        megs = sys.getsizeof(y)
        tot_bytes += megs
        megs = round(megs / 1_000_000, 1)
        sz_dct[x] = megs

    tot_bytes = round(tot_bytes / 1_000_000, 1)
    p(f'total megs {tot_bytes}')

    sz_dct = sort_dct_val_rev(sz_dct)
    for x, y in sz_dct.items():
        if y > 10:
            p(x, y)

    all_objects = gc.get_objects()
    obj_sz = {}
    for e, x in en(all_objects):
        sz = sys.getsizeof(x)
        megs = sz / 1_000_000
        obj_sz[e] = sz
        if megs > 10:
            p('more than 100')
            p(sz)
            p('')

    all_megs = sum(list(obj_sz.values()))
    p(f'megs {round(all_megs / 1_000_000, 1)}')


def tardir(src, dest, comp=0):
    if not comp:
        subprocess.run(['tar', 'cf', f'{dest}.tar', src])
    else:
        subprocess.run(['tar', 'czf', f'{dest}.tar.gz', src])


def pad_numbers(num, sz=7, add_one=0):
    num = str(num)
    b = sz - len(num)
    zeroes = ""
    if b:
        zeroes = "0" * b
    if add_one:
        zeroes = "1" + zeroes

    return zeroes + num


def nums_only(x):
    if '/' in x:
        x = x[x.rindex('/') + 1:]
    return x[:-4]


def read_pickles():
    lst = os.listdir(this_folder2)
    for x in lst:
        if not os.path.isdir(f'{this_folder2}{x}'):
            if x.endswith('.pkl'):
                p(x)
                str1 = input('open: y or n')
                if str1 == 'y':
                    obj = pi.open_pickle(f'{this_folder2}{x}', 1)
                    bb = 8





def jv(head, y, adj=.92):
    if head == y:
        return 1
    num = lvn.jaro_winkler(head, y)
    ln = len(y)
    hln = len(head)
    if num > adj and abs(ln - hln) < 5:
        if num > .99:
            num = .99
        return num


def get_greatest_num(current_directory, highest=True):
    numbers = []
    for current_pic in os.listdir(current_directory):
        if current_pic[0] != '.':
            if not os.path.isdir(current_directory + current_pic):
                num = re.findall(r"\d+", current_pic)
                if num != []:
                    numbers.append(int(num[0]))

    if numbers == []:
        return 0
    elif highest:
        return max(numbers)
    else:
        return min(numbers)
