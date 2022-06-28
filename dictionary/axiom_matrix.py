import add_path
from settings import *
from general import *
import general_functions as gf
from itertools import combinations_with_replacement, product
import gen_dict_func as gdf
from gen_dict_func import atomic_sent
from pack_conjunctions import get_attach_name

"""
sentences ending in .1 are fermions and are named
sentences ending in .2 are molecules and are named
sentences ending in .3 are connectives and are named
sentences ending in .4 are bosons and are not named
.5 - unnamed fermions
.6 - unnamed molecules
.7 - unnamed connectives
.8 - unnamed bosons
"""


class axiom_matrixcl:
    @vgf.timer
    def main(self):
        self.ax_dct = {}
        self.ax_dct_long = {}
        self.ax_sents = {}
        self.private_attribs()
        self.main2()

    def from_calc_ax(self, cls):
        lst = ['ssent2num', 'sent_map', 'con_num', 'sheet_lst',
               'pickle_axioms', 'test', 'use_molecules']
        vgf.copy_partial_cls(self, cls, lst)
        self.main()

    def no_changes2sheet(self, **kwargs):
        dct = pi.open_pickle("calc_ax_output")
        for att, val in dct.items():
            setattr(self, att, val)
        self.test = kwargs.get('test')
        self.pickle_axioms = kwargs.get('pi')
        self.main()

    def private_attribs(self):
        self.subcategories = {}
        self.print_on = False
        self.rel_props = {}
        self.non_math = {}
        self.num_entail = {}
        self.pos_cls = {}
        self.properties = {}
        self.same_rel = {}
        self.all_ax = set()
        self.at_const_dct = {}
        self.num_entail = []
        self.nat_lang = {}
        self.necessary = {}

    def main2(self):
        self.get_position_classes()
        self.get_subcategories()
        self.get_properties()
        self.loop_fermions().main(self)
        self.print_axioms()
        self.test_module()
        self.save_pickle()
        self.count_non_math()

    def get_position_classes(self):
        scol = self.sheet_lst[1].index('sname')
        ocol = self.sheet_lst[1].index('oname')
        rcol = self.sheet_lst[1].index('relat')
        smcol = self.sheet_lst[1].index('same')
        pcol = self.sheet_lst[1].index('prop')
        ncol = self.sheet_lst[1].index('nec')
        sdcol = self.sheet_lst[1].index('sent id2')
        ntcol = self.sheet_lst[1].index('nat lang')

        for lst in self.sheet_lst[2:]:
            relat = lst[rcol]
            if not relat: break
            subj = lst[scol]
            obj = lst[ocol]
            sent_id = lst[sdcol]
            self.pos_cls[relat] = [sent_id, subj, obj]
            self.same_rel[relat] = lst[smcol]
            self.rel_props[relat] = lst[pcol]
            self.nat_lang[relat] = lst[ntcol]
            self.necessary[relat] = lst[ncol]

    def get_excel_snt_num(self):
        ## this was originally designed for exceptions
        ##we might bring this back in the future
        acol = self.sheet_lst[1].index('anum')
        ascol = self.sheet_lst[1].index('atomic sent')
        for lst in self.sheet_lst[2:]:
            if not lst[acol]: break
            ssent = lst[ascol]
            exnum = lst[acol]
            pynum = self.ssent2num.get(ssent)
            if pynum:
                self.excel2python[str(exnum)] = pynum

        return

    def get_properties(self):
        scol = self.sheet_lst[1].index('subj2')
        pcol = self.sheet_lst[1].index('properties')
        sdcol = self.sheet_lst[1].index('sent id')
        for lst in self.sheet_lst[2:]:
            if not lst[scol]:
                break
            else:
                self.properties[lst[pcol]] = [lst[sdcol], lst[scol]]

    def get_exceptions(self):
        ecol = self.sheet_lst[1].index('exceptions')
        et = self.sheet_lst[1].index('et')
        for x in self.sheet_lst[2:]:
            if not x[ecol]: break
            ax_name = x[ecol]
            lst = ax_name.split(" ")
            for e, snum in en(lst):
                lst2 = snum.split(":")
                nnum = self.excel2python[lst2[0]]
                lst2[0] = nnum
                str1 = ":".join(lst2)
                lst[e] = str1
            ax_name = " ".join(lst)
            self.exceptions[ax_name] = x[et]
        return

    def get_subcategories(self):
        sucol = self.sheet_lst[1].index('subcategories')
        spcol = self.sheet_lst[1].index('supercategories')
        for e, lst in en(self.sheet_lst[2:]):
            if not lst[sucol]:
                break
            else:
                sub = lst[sucol]
                sup = lst[spcol]
                self.subcategories[sub] = sup

    class loop_fermions:
        def main(self, cls):
            lst = ['sent_map', 'ssent2num', 'properties', 'pos_cls',
                   'con_num', 'subcategories', 'all_ax', 'ax_sents',
                   'ax_dct', 'ax_dct_long', 'num_entail',
                   ]
            vgf.copy_partial_cls(self, cls, lst)
            for self.kind in ['double', 'triple']:
                if self.kind == 'double':
                    self.not_use = ['R', "+", minus]
                else:
                    self.not_use = ['R', 'C', "P", "M", "T", "+", minus]
                self.step_one()

        def step_one(self):
            self.get_fermions()
            self.build_object_dct()
            self.main_loop()

        def main_loop(self):
            combos = combinations_with_replacement(self.fermions, 2)
            last_csent0 = 1
            for e, combo in en(combos):
                tcsent0 = self.sent_map.get(combo[0])
                tcsent1 = self.sent_map.get(combo[1])

                if tcsent0 == last_csent0:
                    pass
                else:
                    self.csent0 = gdf.atomic_sent(tcsent0, **{'entry': 'from_matrix'})
                    self.csent0.snum = self.ssent2num[self.csent0.name]
                self.csent1 = gdf.atomic_sent(tcsent1, **{'entry': 'from_matrix'})
                self.csent1.snum = self.ssent2num[self.csent1.name]

                if tcsent1 < tcsent0:
                    csent2 = self.csent0
                    self.csent0 = self.csent1
                    self.csent1 = csent2

                self.csent0.inum = self.csent0.snum
                self.csent1.inum = self.csent1.snum
                self.get_var_lsts()
                self.build_conjuncts()
                self.adjust_sent_id()
                last_csent0 = self.csent0

            return

        def get_fermions(self):
            '''
            here we pick out only the fermions from the sent_map since
            they are the only ones that are used in building axioms
            '''

            self.exceptions2 = ['(i H e:)', '~(i H e:)']
            self.fermions = []
            for tpl in self.sent_map.items():
                if tpl[1].snum[0] == '0':
                    pass
                elif tpl[1].relation in self.not_use:
                    pass
                elif tpl[1].name_tv in self.exceptions2:
                    pass
                elif tpl[1].snum.endswith(".1"):
                    self.fermions.append(tpl[0])

        def build_object_dct(self):
            '''
            here we state what category the subject and object belong to
            so as to determine easily whether or not two sentences
            are consistent
            '''

            for ssent in self.fermions:
                if ssent == '(b H r:)':
                    bb = 8

                csent = self.sent_map.get(ssent)
                self.trim_csent(csent)
                relation = csent.relation
                lst = self.pos_cls[relation]

                if relation in ["+", minus]:
                    setattr(csent, "equal_cat", "number")
                setattr(csent, 'sid cat', lst[0])

                if ":" in csent.subj:
                    num = self.con_num[csent.subj]
                    setattr(csent, "subj_cat", str(num) + "c")
                else:
                    setattr(csent, "subj_cat", lst[1])

                if ":" in csent.obj:
                    lst2 = self.properties.get(csent.obj)
                    osubj = lst2[1]
                    if osubj: setattr(csent, "subj_cat", osubj)
                    num = self.con_num[csent.obj]
                    str_num = str(num) + "c"
                    setattr(csent, "obj_cat", str_num)
                else:
                    setattr(csent, "obj_cat", lst[2])

        @staticmethod
        def trim_csent(csent):
            atts = ['base_form',
                    'unaffirmable', 'undeniable']
            vgf.trim_class4(csent, atts)
            return

        def get_var_lsts(self):
            '''
            here we figure out all the different ways that the variables
            in two sentences can match.  constants cannot match except
            for the constants, v: and f: are members of the constant u:.
            the var_lst is composed of lsts of numbers.  the first digit
            in each number stands for whether it is the first conjunct which is 0
            or the second conjunct which is 1.  the second number stands for
            the position name of the variable, 1 for subject, 2 for object, etc
            only variables are considered in building this list.
            '''
            self.rel0 = self.csent0.relation
            self.rel1 = self.csent1.relation
            self.var_lsts = []
            self.has_three = False
            self.reflexive = False
            self.cur_const = []
            for e, csent in en([self.csent0, self.csent1]):
                tvaris = []
                if csent.equalizer:
                    self.has_three = True
                for num, vari in csent.var_idx.items():
                    if num in [6, 3]:
                        pass
                    elif e == 0 and num == 2 and vari == 'b':
                        pass
                    elif vari == 'b' and num == 2 and e == 1:
                        self.reflexive = True
                    elif vari not in self.con_num.keys():
                        tvaris.append(str(e) + str(num))
                    else:
                        tnum = 2 if num == 1 else 1
                        obj = self.properties.get(vari)
                        if obj:
                            obj = obj[1]
                            self.cur_const.append((str(e) + str(tnum), obj))

                self.var_lsts.append(tvaris)

        def build_conjuncts(self):
            tprod = list(product(*self.var_lsts))
            if len(tprod) == 1 and self.csent0.snum == self.csent1.snum:
                pass
            else:
                if self.has_three:
                    if self.reflexive:
                        tprod = self.remove_doubles(tprod)
                    tprod = self.add_doubles(tprod)

                for e, x in en(tprod):
                    if type(x[0]) == str:
                        tprod[e] = (x,)
                    else:
                        break

                for e, x in en(tprod):
                    self.get_tvalue(x)
                    self.build_conjuncts2(x)
                    self.build_ax_str().main(self)

            return

        def adjust_sent_id(self):
            self.csent0.var_idx[3] = self.csent0.sent_id
            self.csent1.var_idx[3] = self.csent1.sent_id

        @staticmethod
        def remove_doubles(tprod):
            lst = []
            for x in tprod:
                if x not in lst:
                    lst.append(x)
            return lst

        @staticmethod
        def add_doubles(tprod):
            doubles = []
            for tpl in tprod:
                for tpl2 in tprod:
                    if not set(tpl) & set(tpl2):
                        tpl2 = [tpl, tpl2]
                        tpl2.sort()
                        if tuple(tpl2) not in doubles:
                            doubles.append(tuple(tpl2))
            tprod += doubles
            return tprod

        def get_tvalue(self, tpl):
            '''
            in one sentence there will be a variable which appears in the other
            sentence.  here we determine whether or not it is consistent for the
            same object to exist in the different positions of the sentences
            '''

            self.entail_type = 1
            for pair in tpl:
                assert pair[0][0] == '0'
                pos_num0, pos_num1 = decompose_pair(pair)

                if pos_num0 == 3:
                    ent0 = 'number'
                else:
                    str1 = "subj_cat" if pos_num0 == 0 else "obj_cat"
                    ent0 = getattr(self.csent0, str1)

                if pos_num1 == 3:
                    ent1 = 'number'
                else:
                    str1 = "subj_cat" if pos_num1 == 0 else "obj_cat"
                    ent1 = getattr(self.csent1, str1)

                self.entail_type = gdf.are_compatible(self, ent0, ent1, tpl)
                assert self.entail_type

        def build_conjuncts2(self, tpl):
            self.var_name = {
                '3': 'sent_id',
                '4': 'equalizer',
                '1': 'subj',
                '2': "obj",
            }
            lst = ['f', 'g', 'h', 'n']
            if self.reflexive:
                lst = ['f', 'g', 'g', 'n']

            for att in ['equalizer', 'subj', 'obj', 'sent_id']:
                vari = getattr(self.csent1, att)
                if vari and not vari in self.con_num:
                    setattr(self.csent1, att, lst.pop(0))

            for pair in tpl:
                pos_num0, pos_num1 = pair[0][1], pair[1][1]
                att = self.var_name[pos_num0]
                var0 = getattr(self.csent0, att)
                att2 = self.var_name[pos_num1]
                setattr(self.csent1, att2, var0)
                if self.reflexive and att2 in ['subj', 'obj']:
                    if not self.csent1.subj in self.con_num.keys():
                        setattr(self.csent1, "subj", var0)
                    if not self.csent1.obj in self.con_num.keys():
                        setattr(self.csent1, "obj", var0)

            return

        class build_ax_str:
            def main(self, cls):
                lst = ['kind', 'csent0', 'csent1', 'sent_map',
                       'ssent2num', 'entail_type', 'all_ax',
                       'ax_sents', 'ax_dct', 'ax_dct_long',
                       'num_entail']
                vgf.copy_partial_cls(self, cls, lst)
                self.begin()

            def begin(self):
                if self.csent1.snum == self.csent0.snum:
                    self.csent1.inum += ".1"

                if self.kind == 'triple':
                    str1 = self.build_triple_axioms()
                else:
                    self.tant = gf.sort_csents2([self.csent0, self.csent1])
                    ins = get_attach_name()
                    self.ax_name = ins.name_embed1(self)
                    self.conj0 = self.csent0.name_tv
                    self.conj1 = self.csent1.build_sent()
                    str1 = self.build_conditional()
                self.add2axioms(str1)

            def build_triple_axioms(self):
                self.csent0.sent_id = "d"
                self.csent1.sent_id = "j"
                self.conj2 = self.csent0.build_sent()
                self.conj3 = self.csent1.build_sent()
                pcsent0 = self.sent_map['(d - b P c)']
                pcsent0 = gdf.atomic_sent(pcsent0, **{'entry': 'from_matrix'})
                pcsent0.subj = self.csent0.sent_id
                pcsent0.sent_id = "p"
                pcsent0.obj = "k"
                pcsent0.snum = self.ssent2num[pcsent0.name_tv]
                pcsent1 = self.sent_map['(d - b P c)']
                pcsent1 = gdf.atomic_sent(pcsent1, **{'entry': 'from_matrix'})
                pcsent1.subj = self.csent1.sent_id
                pcsent1.sent_id = "q"
                pcsent1.obj = "m"
                pcsent1.snum = self.ssent2num[pcsent1.name_tv]
                pcsent0.inum = pcsent0.snum
                pcsent1.inum = pcsent1.snum + ".1"
                self.conj0 = pcsent0.build_sent()
                self.conj1 = pcsent1.build_sent()
                conjunct = build_connection(self.conj2, cj, self.conj3)
                lst1 = [self.csent0, self.csent1, pcsent0, pcsent1]
                lst1 = gf.sort_csents2(lst1)
                self.tant = lst1
                ins = get_attach_name()
                self.ax_name = ins.name_embed1(self)
                if self.entail_type != 1:
                    lst = self.ax_name.split("  ")
                    ant = " ".join(lst[:3])
                    con = lst[3]
                    self.num_entail.append(build_connection(ant, conditional, con))
                str1 = self.build_conditional()
                return build_connection(conjunct, cj, str1)

            def build_conditional(self):
                if self.entail_type in [5, 7]:
                    str2 = "" if self.entail_type == 5 else "~"
                    str1 = str2 + self.conj0 + " " + conditional + " ~" + self.conj1
                elif self.entail_type == 3:
                    str1 = build_connection(self.conj0, conditional, self.conj1)
                elif self.entail_type:
                    str1 = build_connection(self.conj0, bowtie, self.conj1)
                else:
                    str1 = self.conj0 + " " + conditional + " ~" + self.conj1

                return str1

            def add2axioms(self, str1):
                if str1 not in self.all_ax:
                    self.ax_dct[self.ax_name] = self.entail_type
                    self.additional_axioms()
                    self.all_ax.add(str1)
                    self.ax_sents[self.ax_name] = str1
                else:
                    p(f"{str1} is appearing twice")

            def additional_axioms(self):
                if self.kind == 'double':
                    if self.ax_name == "0": return
                    lst = self.ax_name.split()
                    true_true = self.ax_name
                    true_false = lst[0] + " 0" + lst[1]
                    false_true = "0" + lst[0] + " " + lst[1]
                    false_false = "0" + lst[0] + " 0" + lst[1]
                    if self.entail_type in [7, 1, 3]:
                        self.ax_dct_long[true_true] = 1
                    else:
                        self.ax_dct_long[true_true] = 0
                    if self.entail_type in [7, 1, 5]:
                        self.ax_dct_long[true_false] = 1
                    else:
                        self.ax_dct_long[true_false] = 0
                    if self.entail_type in [1, 3, 5]:
                        self.ax_dct_long[false_true] = 1
                    else:
                        self.ax_dct_long[false_true] = 0
                    self.ax_dct_long[false_false] = 1
                    return

    def use_exceptions(self):
        ## this was originally for sparseness and abundance
        # but those are no longer axioms

        if self.kind == 'double':
            for k, v in self.exceptions.items():
                self.build_ax_str().additional_axioms0(self)
                self.additional_axioms()
                self.ax_dct[k] = v

    def print_axioms(self):
        if self.print_on:
            while True:
                range1 = input("range, 99 to stop: ")
                lst = range1.split()
                start = int(lst[0])
                stop = int(lst[1])
                if start == 99:
                    break
                for e, x in en(list(self.ax_sents.values())[start:stop]):
                    if "=" not in x:
                        p(f"{e + start}  {x} ")

    def test_module(self):
        if self.test:
            axiom_dictionary = pi.open_pickle('axiom_dictionary')
            self.test_sent_map()
            lst = ['ax_dct', 'ax_dct_long', 'ax_sents', 'con_num']
            for x in lst:
                old_dct = axiom_dictionary[x]
                new_dct = getattr(self, x)

                if vgf.test_2dicts(old_dct, new_dct, self.ax_sents):
                    p('the {x} dictionary is the same')
                else:
                    p('failed')



    def test_sent_map(self):
        dictionary = pi.open_pickle("classless_dict")
        old_sent_map = dictionary['sent_map']
        old_ssent2_num = dictionary['ssent2num']
        if vgf.test_2dicts(old_sent_map, self.sent_map, old_sent_map):
            p('sent map matches')
        else:
            p('sent map does not match')

        if vgf.test_2dicts(old_ssent2_num, self.ssent2num, {}):
            p('ssent2num matches')
        else:
            p('ssent2num does not match')


    def save_pickle(self):

        if self.pickle_axioms:
            lst = ['ax_dct', 'ax_dct_long', 'ax_sents', 'con_num',
                   'sent_map', 'ssent2num']

            dictionary = {}
            for att in lst:
                obj = getattr(self, att)
                dictionary[att] = obj

            pi.save_pickle(dictionary, "axiom_dictionary")
            p('axioms pickled')


    def count_non_math(self):
        b = len(self.ax_dct)
        p(f"total axioms {b}")
        c = len(self.ax_sents)
        assert b == c, "the ax_sents does not match the ax_dct"
        b = 0
        for y in self.ax_sents.values():
            if "=" not in y:
                b += 1
        p(f"non-math axioms: {b}")


# pseudo decorator
def split_pair(func):
    @functools.wraps(func)
    def split_pair2(*args):
        idx_dct = {
            "1": 0,
            "2": 1,
            '4': 3
        }
        pos_num0, pos_num1 = func(*args)
        pos_num0 = idx_dct[pos_num0]
        pos_num1 = idx_dct[pos_num1]
        return pos_num0, pos_num1

    return split_pair2


@split_pair
def decompose_pair(*args):
    pair = args[0]
    pos_num0 = pair[0][1]
    pos_num1 = pair[1][1]
    return pos_num0, pos_num1


if eval(not_execute_on_import):
    args = vgf.get_arguments()
    initial_arg = args[1]
    # args[1] = "fb"
    kwargs = {}
    kwargs['test'] = False
    kwargs['pickle_axioms'] = False

    if 'te' in args:
        kwargs['test'] = True
    elif 'te3' in args:
        kwargs['test'] = 3
    if 'pi' in args:
        kwargs['pickle_axioms'] = True

    if args[1] != initial_arg:
        p('you are temporarily overriding the arguments')

    axiom_matrixcl().no_changes2sheet(**kwargs)
