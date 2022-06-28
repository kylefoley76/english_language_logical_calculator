
old = False
from general import *
horseshoe = chr(8835)
consist = "\u2102"  # consistency
top = chr(8868)
old_bottom = chr(8869)
bowtie = chr(8904)
contradictory = chr(390)
neg = chr(172)
lneg = chr(10858)
infer = chr(8680)
idd = chr(8781)  # translation symbol

if old:
    iff = chr(8801)
    iff2 = chr(8596)
else:
    iff2 = chr(8801)
    iff = chr(8596)

jiff = chr(10746)  # u29fa,hex 29fa justified biconditional
# 2b04 is also a candidate for jiff, u21c6
mini_c = chr(8658)
mini_e = chr(8703)
# bullet= "\u2981" too large
bullet= "\u2219"
circle = "\u25e6"  # interior conjunction
jdisj = chr(8853)  # circle_cross
after = chr(8857)  # hex 2299, circle_dot
before = chr(8865)  # hex 22a1, box_dot

implies = chr(8866)
conditional = chr(8594)
cond_conn = [conditional, implies]
refers = chr(8701)
minus = chr(8722)
nonseq = chr(8876)
elip = chr(8230)
arrow = chr(8883)
shift = chr(8882)  # u22b2

cyr1 = chr(1078)  # u0436
cyr2 = chr(1080)  # was backn
cyr3 = chr(1102)  # u044e
cyr4 = chr(1103)  # was backr
cyr5 = chr(1113)  # u0459
cyr6 = chr(1114)  # 045a

cyrillic_let = [cyr1, cyr2, cyr3, cyr4, cyr5, cyr6]

xorr = chr(8891)
idisj = chr(8744)
cj = chr(8743)
aid = chr(8776)  # almost identical
lbr = chr(10647)
rbr = chr(10648)
bicond_conn = [iff, jiff]
circle_x = chr(8855)  # circle_x
equi = chr(8660)
ne = "\u2260"  # not equal

args = vgf.get_arguments()


def print_symbols():
    dct1 = {
        "t": conditional,
        "x": iff,
        "a": circle,
        "w": arrow,
        "l": bullet,
        "=": jdisj,
        "7": cj,
        "e": mini_e,
        "i": implies,
        "k": infer,
        "p": bowtie,
        "c": mini_c,
        "m": minus,
        "d": idisj,
        "r": shift,
        "b": contradictory,
    }
    for x, y in dct1.items():
        p(f"{x}   {y}")


try:
    if args[1] == 'sy':
        print_symbols()
except:
    pass

l0 = "\u2080"
l1 = "\u2081"
l2 = "\u2082"
l3 = "\u2083"
l4 = "\u2084"
l5 = "\u2085"
l6 = "\u2086"
l7 = "\u2087"
l8 = "\u2088"
l9 = "\u2089"
ua = "\u1d43"
ub = "\u1d47"
uc = "\u1d9c"
ud = "\u1d48"
ue = "\u1d49"
uf = "\u1da0"
ug = "\u1d4d"
ui = "\u2071"
uk = "\u1d4f"
um = "\u1d50"
un = "\u207f"
uo = "\u1d52"
up = "\u1d56"
ut = "\u1d57"
uv = "\u1d5b"
uu = "\u1d58"
uw = "\u02b7"
uy = "\u02b8"
uj = "\u02B2"
ul = "\u02E1"
ur = "\u02b3"
us = "\u02e2"
uh = "\u02b0"
u1 = "\u00b9"
u2 = "\u00b2"
u3 = "\u00b3"
u4 = "\u2074"
u5 = "\u2075"
u6 = "\u2076"
u7 = "\u2077"
u8 = "\u2078"
u9 = "\u2079"
u0 = "\u2070"

superscripts = [ua, ub, uc, ud, ue, uf, ug, ui, uj, uk, ul, um, un, uo,
                up, ur, us, ut, uu, uw, uv, uy, uh, u1, u2, u3, u4, u5,
                u6, u7, u8, u9, u0]

superscript_dict = {
    ua: "a",
    ub: "b",
    uc: "c",
    ud: "d",
    ue: "e",
    uf: "f",
    ug: "g",
    uh: "h",
    ui: "i",
    uj: "j",
    uk: "k",
    ul: "l",
    um: "m",
    un: "n",
    uo: "o",
    up: "p",
    ur: "r",
    us: "s",
    ut: "t",
    uu: "u",
    uv: "v",
    uw: "w",
    uy: "y"}


def get_subscripts():
    single_subscripts = [l1, l2, l3, l4, l5, l6, l7, l8, l9]
    all_subscripts = [x for x in single_subscripts]
    lst2 = [l0] + single_subscripts
    for x in single_subscripts:
        for y in lst2:
            all_subscripts.append(x + y)
    return all_subscripts


subscripts = get_subscripts()

alpha = chr(945)
beta = chr(946)
delta = chr(948)

dec_pro_dict = {0: "redun",
                1: "det_nouns",
                2: "syn",
                3: "sp_syn",
                4: "word_sub",
                5: "neg_det",
                6: "i",
                7: "det",
                8: "pron",
                9: "cname_pos",
                10: "pname_pos",
                11: "and",
                12: "adj",
                13: "cia",
                14: "relp",
                15: "as",
                16: "rda",
                17: "rdb",
                18: "there",
                19: "uni",
                20: 'many'}

ten_blanks = [""] * 10

not_blank = lambda x: x != None and x != "" and x != " "

make_pos = lambda x: x[1:] if x[0] == '0' else x

build_contradiction2 = lambda x: x + f" {cj} ~" + x

remove_duplicates_sd = lambda x: list(set(x))

is_molec = lambda x: True if x[-2:] in [".2", '.9'] else False

strip_sent = lambda x: re.sub(r'[()~ ]', "", x)

opp = lambda x: "0" + x if x[0] != '0' else x[1:]

remove_paren = lambda x: re.sub(r'[()]', "", x)

name_sent = lambda x, output_prop_name: output_prop_name[strip_sent(x)]

one_sentence = lambda x: not bool(re.search(xorr + "|" +
                                       implies + "|" +
                                       iff + "|" +
                                       idisj + "|" +
                                       jiff + "|" +
                                       shift + "|" +
                                       arrow + "|" +
                                       circle_x + "|" +
                                       conditional + "|"+
                                       horseshoe + "|"+
                                        cj + "|"+
                                        bowtie +
                                       "|&|#", x))

non_lit_dct = {
    mini_e: "ID",
    ">": "GR",
    minus: "MI",
    "+": "PL",
    "=": "EQ",
    circle: "CJ",
}

rev_non_lit_dct = {
    "ID": mini_e,
    "GR": ">",
    "MI": minus,
    "PL": "+",
    "EQ": "=",
    "CJ": circle,
}






#takes '33.1' and converts it to 1
idxl_num = lambda x: x[:x.rindex(x, ".") * -1]
# takes '33.1' and converts it to 33
sent_num = lambda x: x[:x.find('.')] if x.find('.') > 0 else x

snum_initial = lambda x: x[:x.index(":")]

snum_last = lambda x: x[x.index(":") + 1:]

build_ssent = lambda x: "(" + " ".join(x) + ")"

build_connection = lambda x, y, z: x + " " + y + " " + z

build_conjunction = lambda x: "(" + f" {cj} ".join(x) + ")"

build_lemma = lambda x, y: x + "." + y

from_words2sent = lambda x: "(" + " ".join(x) + ")"

pos_counterpart = lambda x, y, z: x[y.index(z)]

is_concept = lambda x, y, z: z.get(y) if x in ["I", "JJ", "VV"] else None

pair = lambda x, y, z: z.join(sorted([x, y]))

math_sym = ["+", minus, "*", "/", ">"]

isrelat = lambda x: x.isupper() or x in ["\\", "=", circle] + math_sym

is_at_relat = lambda x: x.isupper() or x in ["\\", mini_e] + math_sym

nu = lambda x: "0abcdefghijklmnopqrstuvyz".index(x)

np = lambda x: "abcdefghijklmnopqrstuvyz".index(x)

add_digit = lambda x, y: float(str(x) + str(y))

clause_num = lambda x: x[:x.rindex(".") + 1]

iscyrillic = lambda x: any(y in x for y in cyrillic_let) and len(x) < 6

name_tv2name = lambda sent, tv: sent[1:] if tv == "~" else sent

sent_pos_name = {
    "sent_abb": "p",
    "number": 'n',
    "subj": 's',
    "obj": "o",
    "obj2": "b",
    "obj3": "c",
    "obj4": "d",
    "obj5": "e"}

unineg_dct = {
    2:".8",
    1:".7",
    3:".6"
}

uni_neg_type = lambda x: unineg_dct[x]

the_is_of_group = ["I", "is" + ug, "are" + ug, "be" + ug, "was" + ug, "were" + ug,
                   "am" + ug]

the_is_of_adjective = ["J", "JJ", "is" + ua, "be" + ua, "are" + ua, "was" + ua,
                       "am" + ua, "were" + ua]

var_names = ['subj', 'obj', 'obj2', 'obj3', 'obj4', 'obj5']

be_words = ["am", 'are', 'is', 'were', 'was', 'be']

be_words2 = ["am", 'are', 'were', 'was', 'be']

be_words3 = be_words2 + ["JJ", "I", "EX"]

spec_rel = the_is_of_adjective + the_is_of_group

special_connectives = [iff, conditional, horseshoe, xorr, idisj, "#", iff2, bowtie]

all_connectives = special_connectives + [implies, horseshoe, jiff, nonseq, "&",
                                         arrow, circle_x, jdisj, shift, cj]

non_conj_conn = special_connectives + [implies, horseshoe, jiff, nonseq, arrow, circle_x, jdisj, shift]

non_arrow_connectives = special_connectives + [implies, jiff, nonseq,
                                               "&", jdisj, cj, bowtie]

pos_word = ['subj', 'obj', 'obj2', 'obj3', 'obj4', 'obj5']

conditionals = [conditional, iff, "#", iff2, horseshoe, implies, bowtie]

singular_connectives = [conditional, horseshoe, implies, jiff, iff, "#", iff2, bowtie]

plural_connectives = ["&", xorr, idisj, cj]

numbers = [str(x) for x in range(30)]

non_literals = ["~", neg, "=", refers, mini_e, mini_c, ".", "'", "|", ":", ";",
                "\\", "!", "%", bullet] + subscripts + superscripts + \
               numbers + math_sym + cyrillic_let

omath_relations = math_sym + ["PL", "DI"]

penn_pos = {
    "CC": "c",
    "CD": 'cardinal number',
    "DT": 'd',
    "EX": "t",
    "IN": 'preposition or subordinating conjunction',
    "JJ": "a",
    "JJR": "adjective comparative",
    "JJS": "adjective superlative",
    "MD": "modal",
    "NN": 'n',
    "NNS": 'np',
    "NNP": 'proper noun singular',
    "NNPS": 'proper noun plural',
    "PDT": 'predeterminer',
    "POS": 'posseive ending',
    "PRP": "p",
    "PRP$": "pp",
    "RB": "e",
    "RBR": "adverb comparitive",
    "RBS": "adverb superlative",
    "RP": "b",
    "TO": "to",
    "VB": "r",
    "VBD": "r",
    "VBG": "r",
    "VBN": "r",
    "VBP": "r",
    "VBZ": "r",
    "WDT": 'wh determiner',
    "WP": "wh pronoun",
    "WP$": "possessive wh pronoun",
    "WRB": "wh adverb"
}
