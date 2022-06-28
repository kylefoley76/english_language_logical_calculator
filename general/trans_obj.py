import pickling as pi
# import pickle as pi
import subprocess, csv
from collections import ChainMap as chainmap
import os, ffmpeg
from tika import unpack
from moviepy.editor import *
from abbreviations import *
import very_general_functions as vgf


def from_txt2lst_tab_delim(file, str_only=0,skipex=1):
    if not file.endswith('.txt'):
        file += '.txt'
    files_used.add(file)

    try:
        lst = [line for line in open(file, 'r')]
    except:
        lst = [line for line in open(file, 'r+', encoding="latin-1")]

    if not lst:
        return lst

    for e, x in en(lst):
        if e == 21:
            bb = 8

        x = x.replace(' %%% ', '\n')

        if x and x[-1] == '\n':
            x = x[:-1]
        x = x.split("\t")
        if not str_only:
            lst[e] = vgf.convert_nums(x)
        else:
            lst[e] = x
    if skipex:
        lst1 = []
        found = 0
        for x in lst:
            if found:
                lst1.append(x)
            elif type(x[0]) == str and x[0][0] == '!':
                pass
            else:
                lst1.append(x)
                found = 1
        lst = lst1

    return vgf.del_last_empty_lst(lst)


def from_2dlst2dct(lst):
    return {x[0]: x[1] for x in lst if len(x) > 1}







def from_lst2txt_tab_delim(lst1, name, no_perc=False, make_copy=True):
    if make_copy:
        lst = jsonc(lst1)
    else:
        lst = lst1
    if not name.endswith('txt'):
        name += '.txt'

    with open(name, 'w+', encoding='utf8') as f:
        for x in lst:
            assert type(x) == list
            for e, z in en(x):
                # if :
                #     z = ""

                z = str(z)

                if z and z[-1] == '\n':
                    z = z[:-1]
                if no_perc:
                    z = z.replace("\n", ' ')
                else:
                    z = z.replace("\n", ' %%% ')
                x[e] = z

            str1 = "\t".join(x)
            f.write(str1 + "\n")

    return

def from_lst2print_lst(lst):
    str1 = "\t\tlst = ["
    p (str1)
    end = "\t]"
    for x in lst:
        str2 = f"'{x}',"
        p (str2)
    p (end)

def from_dct2print_dct(lst):
    str1 = '\t\tdct = {'
    p (str1)
    for x in lst:
        y = vgf.strip_n_split(x, ':')
        str1 = f"'{y[0]}':'{y[1]}',"
        p (str1)
    p ('\t\t}')

def from_mkv2mp4():
    fold = '/Volumes/old/sarah_silverman_show/all_mkv/'
    fold2 = '/Volumes/old/sarah_silverman_show/all_mov/'
    lst = os.listdir(fold)
    for x in lst:
        if x[0] != '.':
            for y in os.listdir(f"{fold}{x}"):
                if y[0] != '.':
                    src = f'{fold}{x}/{y}'
                    dest = f'{fold2}{x}/'
                    if not os.path.exists(dest):
                        os.mkdir(dest)
                    dest1 = f'{dest}{y[:-4]}.mov'
                    dest2 = f'{dest}{y[:-4]}.mp3'
                    subprocess.run(['ffmpeg', '-i', src, '-c', 'copy', dest1])

                    vid = VideoFileClip(src)
                    audio = vid.audio
                    audio.write_audiofile(dest2)
                    bb = 8

def from_rtf2lst(file):
    with open(f'{file}.rtf', 'r') as file:
        text = file.read()
    return text

def open_any(file):
    with open(file, 'r') as file:
        text = file.read()
    return text


def from_sclst2para(lst):
    str1 = lst[0]
    for x in lst[1:]:
        str1 += f', {x}'
    return str1


def from_txt2lst(file, str_only=False, skipex=0):
    if not bool(re.search(r'(txt|rtf|html|\.py)$',file)):
        file += '.txt'
    files_used.add(file)
    try:
        lst = [line for line in open(file, 'r')]
    except:
        lst = [line for line in open(file, 'r+', encoding="latin-1")]

    for e, x in en(lst):
        if x[-1] == '\n':
            lst[e] = x[:-1]

    lst = vgf.del_last_empty_rw(lst)
    if not str_only:
        for e, x in en(lst):
            try:
                lst[e] = int(x)
            except:
                try:
                    lst[e] = float(x)
                except:
                    lst[e] = x.replace(' %%% ', "\n")
                    pass
    else:
        lst = [x.replace(' %%% ', "\n") for x in lst]

    if skipex:
        lst = [x for x in lst if x and x[0] != '!']

    return lst


def from_lst2txt(lst, file_name, has_slash_n=False, ofile=False):
    '''
    has_slash_n == 2 means that each line is followed by /n
    and it does not replace the /n which are already in the text
    '''

    if bool(re.search(r'(\.txt|\.rtf|\.html|\.py)$',file_name)):
        pass
    elif not file_name.endswith('.txt'):
        file_name += '.txt'
    with open(file_name, 'w+') as f:
        for x in lst:
            x = str(x)
            assert ' %%% ' not in x, 'you cant have %%% in a file'
            if has_slash_n == 2:
                f.write(x + '\n')
            elif has_slash_n:
                f.write(x)
            else:
                x = x.replace('\n', ' %%% ')
                f.write(x + '\n')

    if ofile:
        p = subprocess.call(['open', file_name])


def from_lst2txt_t2p(lst, file_name):
    if not file_name.endswith('txt'):
        file_name += '.txt'
    with open(file_name, 'w+') as f:
        for x in lst:
            if len(x) < 45:
                f.write(x + '\n\n')
            else:
                f.write(x + " ")


def from_csv2lst(doc):
    lst = []
    with open(doc, encoding='latin-1') as csvfile:
        doc2 = csv.reader(csvfile)
        for row in doc2:
            lst.append(row)
    return lst


def from_table2dct(file):
    if not file.endswith('.txt'):
        file += '.txt'
    lst = from_txt2lst_tab_delim(file)
    headers = lst[0]
    dct = {}
    for x in lst[1:]:
        dct1 = {}
        key = x[0]
        for f, header in en(headers[1:]):
            e = f + 1
            if len(x) > e:
                num = x[e]
                dct1[header] = num
            else:
                dct1[header] = ""
        dct[key] = dct1
    return dct


def from_dct2table(dct, file):
    rw1 = list(dct.values())[0]
    headers = list(rw1.keys())
    headers.insert(0, "")
    lst = [headers]
    for k, v in dct.items():
        lst1 = [k] + list(v.values())
        lst.append(lst1)

    from_lst2txt_tab_delim(lst, file)


def from_lst2pdf(lst, file_name):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(0, 0)
    pdf.set_font('courier', 'B', 12.0)
    lst.insert(0, "")
    str1 = "\n".join(lst)
    str1 = str1.encode('latin-1', 'replace').decode('latin-1')
    # str1 = str1.replace('\u201c', "")
    # str1 = str1.replace('\u2019', "")
    # str1 = str1.replace('\u201d', "")

    # pdf.cell(ln=0, h=5.0, align='L', w=0, txt=str1, border=0)
    pdf.write(5, txt=str1)
    pdf.output(file_name, 'F')
    # vgf.open_txt_file(file_name)
    return


def from_dct2chainmap(dct):
    dct1 = {v: k for k, v in dct.items()}
    cm = chainmap(dct, dct1)
    return cm


def from_txt2str2str_dct(file_name):
    dct = {}
    with open(file_name, 'r+') as f:
        for x in f:
            x, y = x.split(' : ')
            x = x.replace(" @#@# ", " : ")
            y = y.replace(" @#@# ", " : ")
            x = x.replace(' %%% ', "\n")
            y = y.replace(' %%% ', "\n")
            dct[x] = y

    return dct


def from_dct2lst2txt(dct, file):
    lst = []
    for x, y in dct.items():
        lst.append("")
        lst.append(x)
        lst.append('')
        lst += y
    from_lst2txt(lst, file)


def from_txt2dct2lst(file):
    lst = from_txt2lst(file)
    dct = {}
    lst1 = []
    key = ""
    for x, y, z in zip(lst, lst[1:], lst[2:]):
        if x == "" and z == "":
            if key:
                dct[key] = lst1
                lst1 = []
                key = y
            else:
                key = y
        else:
            lst1.append(y)

    return lst


def from_dct_lst2txt(dct, file):
    #if all keys are non-containers and all values are containers
    lst = []
    for x, y in dct.items():
        lst1 = [x]
        lst1 += list(y)
        lst.append(lst1)
    from_lst2txt_tab_delim(lst, file)

# def from_txt2dct_lst(file):



def from_dct2txt_1d(dct, file):
    lst = [[x, y] for x, y in dct.items()]
    from_lst2txt_tab_delim(lst, file)


def from_txt2dct_1d(file):
    lst = from_txt2lst_tab_delim(file)
    return {x[0]: x[1] for x in lst}


def from_cls2dict(cls):
    attributes = [x for x in cls.__dict__]
    dict1 = {}
    for attribute in attributes:
        if not attribute.startswith("__") and not attribute.endswith("__"):
            obj = getattr(cls, attribute)
            if vgf.isclass(obj):
                obj = from_cls2dict(obj)
            elif isinstance(obj, dict):
                dict2 = {}
                for k, v in obj.items():
                    if vgf.isclass(v):
                        v = from_cls2dict(v)
                    dict2[k] = v
                obj = dict2
            elif isinstance(obj, list):
                list1 = jsonc(obj)
                for e, v in en(obj):
                    if vgf.isclass(v):
                        v = from_cls2dict(v)
                    list1[e] = v
                obj = list1

            dict1[attribute] = obj

    return dict1


# todo make this into a decorator
def from_dict2cls(dict1):
    class tcls: pass

    def temp_func():
        for k, v in dict1.items():
            setattr(tcls, k, v)
        return tcls

    return temp_func()


def from_dct2spec_cls(dct, ins):
    for att in ins.__dict__:
        val = dct.get(att)
        if val:
            setattr(ins, att, val)


def from_tabdelim2lst(file):
    lst = []
    with open(file) as f:
        try:
            for e, x in en(f):
                if x.endswith('\n'):
                    x = x[:-2]
                slst = x.split('\t')
                for g, z in en(slst):
                    try:
                        z = float(z)
                        slst[g] = z
                    except ValueError:
                        z = int(z)
                        slst[g] = z
                    except ValueError:
                        pass

                lst.append(slst)
        except:
            p(e)
    pi.save_pickle(lst, 'most_frequent_words')
    return lst


def from_xml2txt(file1):
    lst = from_txt2lst(file1)
    s = '\n'.join(lst)
    lst2 = vgf.use_beautiful_soup(s,0,0)


def from_lst2str(lst, mx=0,mn=0, idx=0):
    if mx == 0:
        mx = len(lst)
    try:
        lst[mx]
    except:
        mx = len(lst)
    try:
        lst[mx]
    except:
        mx = len(lst)

    if idx:
        str1=''
        for x in lst[mn:mx]:
            try:
                str1 += ' '+x[idx]
            except:
                pass
        return str1.strip()

    return " ".join(lst[mn:mx])



def from_pdf2list(file):
    result = unpack.from_file(file)
    return (result['content']).split("\n")

def from_pdf_to_csv(filename):
    from io import StringIO

    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfdocument import PDFDocument
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFParser

    output_string = StringIO()
    with open(filename, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)

    return output_string.getvalue()
