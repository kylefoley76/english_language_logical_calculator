import add_path
from settings import *
from general import *
from collections import Counter
import general_functions as gf

ssent2num = {}


class fs(frozenset):
    def __init__(self, *args, **kwargs):
        super(frozenset, self).__init__()

    def __str__(self):
        str1 = lbr + "{}" + rbr
        return str1.format(','.join(str(x) for x in self))


def break_arrows(str1, definiendum):
    if arrow not in str1 and shift not in str1 and shift not in str1:
        return [str1]
    else:
        if str1.strip()[-1] in [arrow, shift, shift]:
            p(f"in {definiendum} whose definitions is {str1} the sentence ends with an invalid character")

        str1 = str1.replace(arrow, shift)
        str1 = str1.replace(shift, shift)
        list5 = []

        list2 = str1.split(shift)
        list2 = [x.strip() for x in list2]

        for sent in list2:
            if sent.count("(") > 1 or sent.count(")") > 1:
                sent = sent.replace("|", "")
                list5.append(sent.strip())

        return list5


def divide_at_i(str1, i):
    return str1[:i], str1[i + 1:]


def get_half_bicond(sent, left=True):
    idx = sent.index(iff)
    sent = sent[:idx - 1] if left else sent[idx + 2:]
    if sent[:2] == "((" and sent[:-2] == "))":
        return sent[1:-1]
    else:
        return sent


def isant(sent_num):
    if sent_num == "1.1" or sent_num.startswith("1.1."):
        return True
    else:
        return False


def remove_extra_paren(sentence, embed=False):
    if embed:
        return sentence[1:-1]

    num = 0
    has_extra_paren = True
    for idx, letter in enumerate(sentence):
        if letter == "(":
            num += 1
        elif letter == ")":
            num -= 1
        if num == 0 and idx != 0 and idx + 1 != len(sentence):
            has_extra_paren = False

    if has_extra_paren:
        return sentence[1:-1]

    return sentence


def get_ancestors(hnum):
    ancestors = []
    del hnum[-1]
    while len(hnum) > 1:
        str1 = ".".join(hnum)
        ancestors.append(str1)
        del hnum[-1]
    ancestors.append("1")
    return ancestors


def get_new_sent(sp_sent):
    ssd = sp_sent.hnum2csent
    gr = sp_sent.greek_di
    greek2eng = {gr[k]: v.name_tv for k, v in ssd.items()}
    str1 = gf.from_greek2english(greek2eng, sp_sent.greek)
    return str1, ssd


def renumber_ss_dct(name2csent, sp_sent_lst, ssent2num):
    for sp_sent in sp_sent_lst:
        name2csent2 = {x: atomic_sent(y, **{}) for x, y in name2csent.items()}
        sp_sent.hnum2csent = {x: name2csent2[y] for x, y in sp_sent.name.items()
                              if not sp_sent.conn[x]}
        for x, y in sp_sent.hnum2csent.items():
            tv = sp_sent.tvalue[x]
            if tv:
                y = atomic_sent(y, **{})
                y.tvalue = tv
                y.name_tv = y.build_sent()
                y.sent_idtv = tv + y.sent_id
                sp_sent.hnum2csent[x] = y
                y.snum = ssent2num["~" + y.base_form]
    return


def make_negative(csent):
    csent = atomic_sent(csent, **{})
    csent.name_tv = "~" + csent.name
    csent.sent_idtv = "~" + csent.sent_id
    csent.tvalue = "~"
    csent.snum = "0" + csent.snum
    return csent


class atomic_sent:
    def __init__(self, item, **kwargs):
        global ssent2num
        entry = kwargs.get("entry", "from_matrix")
        ssent2num = kwargs.get('ssent2num', {})
        self.new_var = kwargs.get('new_var')
        if entry == 'from_matrix':
            vgf.copy_class(self, item)
            self.ivar = set(jsonc(item.ivar))
            self.var_idx = jsonc(item.var_idx)
            self.sdct = jsonc(item.sdct)
        else:
            self.var_idx = {}
            self.used_atts = []
            self.get_num_dict()
            self.idx = 0
            if entry in ['artificial', 'definition']:
                self.reduce_atomic(item)
            else:
                self.sdct = item
            self.get_let_dict2()
            self.modality = kwargs.get('modality', 2)
            self.get_base_form(entry)
            self.snum = ssent2num.get(self.base_form, '1.1')
            self.inum = self.snum
            self.sort_used_atts()
            self.ivar = set(x for x in self if gf.isvariable(x))
            self.name = self.build_sent()
        return

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if value[0] == '~':
            self.name_tv = value
            self._name = value[1:]
            self.tvalue = "~"
        elif value[0] != "~":
            self.name_tv = value
            self._name = value
            self.tvalue = ""

    @property
    def sent_id(self):
        return self._sent_id

    @sent_id.setter
    def sent_id(self, value):
        if value:
            self.dash = "-"
            self._sent_id = value
            self.sent_idtv = self.tvalue + value
            self.used_atts.insert(0, "sent_id")
            if hasattr(self, "ivar"):
                self.ivar.add(value)
            self.var_idx[3] = value

        else:
            self._sent_id = value
            self.sent_idtv = ""
            old_sent_id = self.sent_id
            if old_sent_id:
                if hasattr(self, "ivar"):
                    self.ivar.remove(old_sent_id)
                del self.var_idx[3]
                self.used_atts.remove("sent_id")
            self.dash = ""

    def get_num_dict(self):
        self.num_dct = {
            'sent_id': 3,
            'equalizer': 4,
            "equals": 5,
            "subj": 1,
            "relation": 6,
            "obj": 2,
            "obj2": 7,
            "obj3": 8,
            "obj4": 9,
            "obj5": 10,
        }

    def sort_used_atts(self):
        dct1 = {k: list(self.num_dct.keys()).index(k) for k in self.used_atts}
        tpl = sort_dict_by_val(dct1)
        self.used_atts = [x[0] for x in tpl]

    def rebuild_var_idx(self):
        self.var_idx = {}
        for attr in self.num_dct.keys():
            varis = getattr(self, attr)
            if varis:
                num = self.num_dct[attr]
                self.var_idx[num] = varis
        self.ivar = set(x for x in self if gf.isvariable(x))

    def get_let_dict2(self):
        for attr, word in self.sdct.items():
            setattr(self, attr, word)
            if word and attr in self.num_dct:
                num = self.num_dct.get(attr)
                self.var_idx[num] = word
                if attr not in self.used_atts:
                    self.used_atts.append(attr)

    def build_sent(self):
        words = [getattr(self, x) for x in pos_dct().keys() if getattr(self, x)]
        sent = " ".join(words)
        sent = sent.replace("~ ", "~")
        sent = sent.replace("( ", "(")
        return sent.replace(" )", ")")

    def get_base_form(self, entry=""):
        self.base_dct = {
            'sent_id': "d",
            'equalizer': 'e',
            'subj': 'b',
            'obj': 'c',
            'obj2': 'f',
            "obj3": 'g',
            'obj4': 'h',
            'obj5': 'j'
        }

        if self.sent_id:
            self.base_dct['dash'] = '-'

        lst = []
        for x in pos_dct().keys():
            word = getattr(self, x)
            if word:
                if self.meets_conditions(x, word, entry):
                    if x in ['subj', 'obj', 'equalizer']:
                        lst1 = [
                            ('subj', 'obj'),
                            ('subj', 'equalizer'),
                            ('obj', 'equalizer')
                        ]
                        for tpl in lst1:
                            att1 = getattr(self, tpl[0])
                            att2 = getattr(self, tpl[1])
                            if att1 == att2:
                                self.base_dct[tpl[1]] = self.base_dct[tpl[0]]

                    word2 = self.base_dct.get(x)
                    if word2:
                        lst.append(word2)
                    else:
                        lst.append(word)
                else:
                    lst.append(word)
        base_form = " ".join(lst)
        base_form = base_form.replace("~ ", "~")
        base_form = base_form.replace("( ", "(")
        self.base_form = base_form.replace(" )", ")")

    @staticmethod
    def meets_conditions(att, word, entry):
        if word in ['i', '1']:
            return False
        if att == 'obj' and word == 'b' and entry == 'from_calc':
            return False
        if ":" in word:
            return False
        if not gf.isvariable(word):
            return False
        return True

    def reduce_atomic(self, ssent):
        ssent = ssent.replace("~", "~ ")
        ssent = ssent.replace(neg, neg + " ")
        self.sdct = pos_dct()
        if ssent[:3] == '~ (':
            self.sdct['tvalue'] = "~"
            ssent = ssent[2:]
        ssent = re.sub(r'[\(\)]', "", ssent)
        ssent = vgf.strip_n_split(ssent)

        if ssent[-2] == "~":
            self.sdct['otilde'] = "~"
            del ssent[-2]
        if "~" in ssent:
            self.sdct['stilde'] = "~"
            ssent.remove("~")

        list1 = ["subj", "relation", "obj", "obj2", "obj3", "obj4", "obj5"]
        list2 = ["sent_id", "dash"]
        list3 = ["equalizer", "equals"]
        if "-" in ssent:
            self.sdct['dash'] = "-"
            if "=" in ssent:
                word_names = list2 + list3 + list1
            else:
                word_names = list2 + list1

        elif "=" in ssent:
            word_names = list3 + list1
        else:
            word_names = list1

        for e, word in en(ssent):
            word_name = word_names[e]
            self.sdct[word_name] = word

        return

    def __contains__(self, item):
        return item in self.name_tv

    def __eq__(self, item):
        return self.name_tv == item

    def __ne__(self, item):
        return self.name_tv != item

    def __str__(self):
        return self.name_tv

    def __gt__(self, other):
        return self.snum > other.snum

    def __lt__(self, other):
        return self.snum < other.snum

    def __repr__(self):
        return self.name_tv

    def __iter__(self):
        return self

    def __next__(self):
        if self.idx == len(self.base_dct.keys()):
            self.idx = 0
            raise StopIteration
        vari = 0
        while not vari:
            attr = list(self.base_dct.keys())[self.idx]
            vari = getattr(self, attr)

            if not vari and self.idx > 2:
                self.idx = 0
                raise StopIteration

            self.idx += 1
            if self.idx == len(self.base_dct.keys()):
                break
            if not gf.isvariable(vari):
                vari = False
        return vari


def are_compatible(cls, ent0, ent1, tpl):
    dct1 = {
        ("01", "11"): "ss",
        ("01", "12"): "so",
        ("02", "11"): "os",
        ("02", "12"): "oo"
    }
    form = dct1.get(tpl)

    tvalue = 1
    if cls.csent0.name == '(b H e:)':
        tvalue = 7
    elif cls.csent1.name == '(b H e:)':
        tvalue = 3
    elif cls.rel0 == cls.rel1 and \
            cls.rel0 not in ['+', minus, ">", "H", "I"] and \
            form in ['ss', 'oo']:
        tvalue = same_relations(cls, form)
    elif ent0 == 'thing' or ent1 == 'thing':
        pass
    elif cls.subcategories.get(ent1) == ent0 or cls.subcategories.get(ent0) == ent1:
        pass
    elif ent0 != ent1:
        tvalue = 5
    return tvalue


def same_relations(cls, form):
    num = str(cls.same_rel[cls.rel0])
    f = 0 if form == 'ss' else 1
    if num[f] == '1':
        return 1
    else:
        return 5


def pos_dct():
    return {
        "tvalue": "",
        'oparen': "(",
        "sent_id": "",
        'dash': "",
        'equalizer': "",  # 4
        'equals': "",
        'stilde': "",
        'subj': "",  # 7
        'relation': "",
        'otilde': "",
        'obj': "",  # 10
        'obj2': "",
        'obj3': "",
        'obj4': "",
        'obj5': "",
        'cparen': ")"
    }


def get_let_num(str1):
    lst = str1.split(".")
    return lst[0], lst[1]


class get_constants:
    '''
    lc all - prints a list of constants
    lc + word will output the constant
    lc + new + word will assign a constant to that word
    '''

    def __init__(self, kind="", word="", constant=""):
        if " " in word:
            raise Exception('no space')
        if word:
            word = word.replace("_", " ")
        if kind == 'new':
            self.word = word
            self.load_pickles()
            self.get_letters()
            self.get_new_constant()
            self.save_pickles()
        elif kind == 'ac':  # assign constant
            self.load_pickles()
            self.const_dct[constant] = word
            self.constant = constant

        elif kind == 'luw':  # look up word
            self.load_pickles()
            cst = vgf.get_key(self.const_dct, word)
            p(cst)

        elif kind == 'luc':  # look up constant
            self.load_pickles()
            p(self.const_dct[word])

        elif kind == 'all':
            self.output_const_lst()
        elif kind == 'del':
            self.load_pickles()
            co = vgf.get_key(self.const_dct, word)
            self.constants.add(co)
            del self.const_dct[co]
            p(f'deleted constant {co}')

        else:
            raise Exception("wrong argument")

    @staticmethod
    def biconstants(use_three=False):
        st = set()
        for x in range(97, 123):
            for y in range(97, 123):
                str1 = chr(x) + chr(y)
                st.add(str1)

        if not use_three:
            for x in range(97, 123):
                for y in range(97, 123):
                    for z in range(97, 123):
                        str1 = chr(x) + chr(y) + chr(z)
                        st.add(str1)
        return st

    def get_letters(self):
        num2 = [120, 121, 122, 113]
        nums = [x for x in range(97, 120) if x != 113]
        num2 += nums
        self.let = [chr(x) for x in num2]
        self.normal_letters = [chr(x) for x in range(97, 120)]

    def output_const_lst(self):
        self.const_dct = pi.open_pickle('const_dct')
        tpl = sort_dict_by_val(self.const_dct)
        for k, v in tpl:
            p(f"{k}  {v}")

    def load_pickles(self):
        self.constants = pi.open_pickle('remaining_constants')
        self.const_dct = pi.open_pickle('const_dct')

    def save_pickles(self):
        pi.save_pickle(self.const_dct, "const_dct")
        pi.save_pickle(self.constants, "remaining_constants")

    def get_new_constant(self):
        already_used = vgf.get_key(self.const_dct, self.word)
        if already_used:
            p(f'already used: {already_used}  {self.word}')
            return

        lconstant = self.word.lower()
        b = 0
        done = False
        while True:
            if not b:
                fir_let = lconstant[0]
            else:
                try:
                    fir_let = self.let[b]
                except:
                    p(f"the word {word} cannot be abbreviated")
                    raise Exception
            if len(self.word) > 2:
                tlst = lconstant[1:]
            else:
                tlst = self.normal_letters

            for x in tlst:
                self.new_constant = fir_let + x
                if self.new_constant in self.constants:
                    self.const_dct[self.new_constant] = self.word
                    self.constants.remove(self.new_constant)
                    done = True
                    break

            if done: break
            b += 1
        p('')
        p(f'{self.new_constant}  {self.word}')


"""
lc all - prints a list of constants
lc + word will output the constant
lc + new + word will assign a constant to that word
"""

if eval(not_execute_on_import):
    args = vgf.get_arguments()
    b = get_constants(args[1], args[2])
