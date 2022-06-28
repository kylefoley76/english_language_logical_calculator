import add_path
from settings import *
from general import *
import gen_dict_func as gdf
from gen_dict_func import atomic_sent
from axiom_matrix import axiom_matrixcl


class calculate_axiomscl:
    def main(self, **kwargs):
        self.test = kwargs.get('test')
        self.use_molecules = kwargs.get('use_molecules')
        self.pickle_axioms = kwargs.get('pi')
        self.fermion_dct = {}
        self.sent_map = {}
        self.ssent2num = chainmap({}, {})
        self.private_attribs()
        self.main2()

    @vgf.timer
    def pickl_wb(self):
        wb = load_workbook(base_dir + "/excel/axioms.xlsx")
        self.ws = ef.get_sheet(wb, "matrix")
        b, c = self.process_sheet(self.ws)
        lst = [b, c]
        pi.save_pickle(lst, "axioms")

    def process_sheet(self, sh):
        last_col = ef.get_last_col(sh, 1)
        headers = ef.get_xl_categories(sh)
        lst_row = ef.get_lrow_of_sh(sh, 1000)
        sheet_lst = ef.from_sheet_tpl(sh, 1, lst_row + 1, last_col + 1)
        sheet_lst = ef.fromstr2int(sheet_lst)
        self.sheet_lst = sheet_lst
        self.headers = headers
        self.fix_one_zero()
        return self.sheet_lst, self.headers

    def private_attribs(self):
        self.at_const_dct = {}
        self.legal_sents = []
        lst = pi.open_pickle("axioms")
        self.sheet_lst = lst[0]
        self.headers = lst[1]
        self.print_on = False
        self.skeletons = []

    def main2(self):
        self.separate_atom_molec()
        self.build_at_const_dct()
        self.number_relations()
        self.loop_kinds()
        self.use_constants()
        self.get_atomic_numbers().main(self)
        self.save_pickle()
        axiom_matrixcl().from_calc_ax(self)

    def fix_one_zero(self):
        '''
        here we simply change the numbers to string in the excel spread sheet
        '''
        lst = ['const', 'const name', 'subj', 'obj', 'equal']
        for name in lst:
            col = self.headers[name]
            for e, lst1 in en(self.sheet_lst):
                val = lst1[col]
                if val != None:
                    if val in [0, 1]:
                        self.sheet_lst[e][col] = "1" if val else "0"

        return

    def separate_atom_molec(self):
        if self.use_molecules:
            dictionary = pi.open_pickle("classless_dict")
            old_sent_map = dictionary['sent_map']
            for x, y in old_sent_map.items():

                if bool(re.search(r'3|2|6|7', y.snum[-1])):
                    self.sent_map[x] = y
                    self.ssent2num[x] = y.snum
                    self.ssent2num.maps[1][y.snum] = x
        return

    def build_at_const_dct(self):
        '''the following is just a guide'''
        ccol = self.sheet_lst[1].index('const')
        cncol = self.sheet_lst[1].index('const name')
        rcol = self.sheet_lst[1].index('rel abb')
        rccol = self.sheet_lst[1].index('rel const')

        for lst in self.sheet_lst[2:]:
            const = lst[ccol]
            word = lst[cncol]
            rel = lst[rcol]
            relc = lst[rccol]
            if not rel: break
            if word:
                self.at_const_dct[word] = const
            self.at_const_dct[rel] = relc

        pi.save_pickle(self.at_const_dct, "at_const_dct")

    def number_relations(self):
        self.rel_num = {}
        self.con_num = {}
        lst = ['rel abb', 'const', 'rel const']
        g = 0
        for f, wrd in en(lst):
            col = self.headers[wrd]
            for e, lst in en(self.sheet_lst):
                if e > 1:
                    rel = lst[col]
                    if not rel: break
                    if not f:
                        self.rel_num[rel] = e - 1
                    else:
                        self.con_num[rel] = g - 2
                if f > 0: g += 1
        return

    def loop_kinds(self):
        '''
        here we loop through the rels column and build certain
        sentences which are undeniable or unaffirmable
        '''
        kind_col = self.headers['kind']
        rel_col = self.headers['rels']
        pos_col = self.headers['pos']
        neg_col = self.headers['neg2?']
        dct1 = {
            0: ["tvalue", "~"],
            4: ["equalizer", "e"],
            5: ['equals', "="],
            6: ['stilde', "~"],
            9: ['otilde', "~"],
        }

        for e, lst in en(self.sheet_lst[2:]):
            if e + 2 == 7:
                bb = 8

            kind = lst[kind_col]
            if not kind: break
            rels = self.get_rels(lst[rel_col])
            pos = lst[pos_col]
            self.get_skeletons2()
            self.modality = lst[neg_col]

            if pos != None:  # pos can be 0
                pos = str(pos).split(",")
                pos = [int(x) for x in pos]
                for x in pos:
                    val = dct1[x]
                    self.skeleton[val[0]] = val[1]

            for x in rels:
                if kind == 'reflexivity':
                    self.skeleton['obj'] = 'b'
                self.skeleton['relation'] = x
                self.build_atomic_sent()
                self.erase_skeleton_partially()
            self.get_skeletons2()

        return

    def use_constants(self):
        '''
        here we build atomic sentences which have a constant in them.
        the relc column specifies the relation of the new sentence.
        the subj column if not empty will specify the constant subject
        if enclosed in () then that means every constant except the one
        enclosed in ()
        the obj column does the same.  if the letters are separated by
        a space then a new sent will form with that constant.
        '''
        relc_col = self.headers['relc']
        subjc = self.headers['subj']
        objc = self.headers['obj']
        equalizerc = self.headers['equal']
        negated = self.headers['neg?']

        lst2 = ['equals', "subj", 'relation', 'obj']
        cols = [equalizerc, subjc, relc_col, objc]
        all_con = set(self.con_num.keys())
        all_con = all_con - {"0", "1"}

        for e, lst in en(self.sheet_lst[2:]):
            if not lst[relc_col]: break

            if e + 2 == 11:
                bb = 8

            relation = lst[relc_col]
            self.modality = lst[negated]
            self.get_skeletons2()
            for idx, col in zip(lst2, cols):
                if idx == 2:
                    bb = 8

                val = lst[col]
                if val and idx == "equals":
                    self.skeleton['equals'] = "="
                    self.skeleton['equalizer'] = val
                elif val:
                    self.skeleton[idx] = val
            self.skeleton['relation'] = relation

            for x in ['subj', 'obj']:
                val = self.skeleton[x]
                if val in ['b', "c", "0", "1"]:
                    pass

                elif val == "all" or " " in val or val.startswith("("):
                    if val == 'all':
                        lst3 = all_con
                    elif " " in val:
                        lst3 = val.split()
                    elif val.startswith("("):
                        lst3 = self.get_difference(val)

                    for con in lst3:
                        self.skeleton[x] = con
                        self.build_atomic_sent()
                        self.erase_skeleton_partially()
                    break
            else:
                self.build_atomic_sent()
                self.erase_skeleton_partially()

        return

    def erase_skeleton_partially(self):
        self.skeleton['tvalue'] = ""
        self.skeleton['sent_id'] = ""
        self.skeleton['dash'] = ""

    def get_difference(self, val):
        val = val[1:-1]
        val = set(val.split(" "))
        return set(self.con_num.keys()) - val

    def get_skeletons2(self):
        self.skeleton = gdf.pos_dct()
        self.skeleton['subj'] = 'b'
        self.skeleton['obj'] = 'c'

    def build_atomic_sent(self):
        dct1 = {
            'entry': 'from_calc',
            'modality': self.modality
        }

        if self.modality in [1, 2]:
            cls = gdf.atomic_sent(self.skeleton, **dct1)
            self.sent_map[cls.name_tv] = cls
            self.skeleton['sent_id'] = 'd'
            self.skeleton['dash'] = "-"
            cls = gdf.atomic_sent(self.skeleton, **dct1)
            self.sent_map[cls.name_tv] = cls
            self.skeleton['sent_id'] = ''
            self.skeleton['dash'] = ""

        if self.modality in [0, 2]:
            self.skeleton["tvalue"] = "~"
            cls = gdf.atomic_sent(self.skeleton, **dct1)
            self.sent_map[cls.name_tv] = cls
            self.skeleton["sent_id"] = 'd'
            self.skeleton["dash"] = "-"
            cls = gdf.atomic_sent(self.skeleton, **dct1)
            self.sent_map[cls.name_tv] = cls

        if self.print_on:
            p(cls.name_tv)

    def get_rels(self, str1):
        if str1.startswith("("):
            st = set(str1[1:-1].split())
            return set(self.rel_num.keys()) - st
        else:
            return set(str1.split())

    def save_pickle(self):
        lst = ['ssent2num', 'sent_map', 'con_num', 'sheet_lst',
               'fermion_dct', 'pickle_axioms', 'test', 'use_molecules']
        vgf.trim_class(self, lst)
        if not self.test and self.pickle_axioms:
            dct1 = {}
            for x in lst:
                if x not in ['test', 'pickle_axioms', 'ssent2num', 'sent_map']:
                    dct1[x] = getattr(self, x)
            pi.save_pickle(dct1, 'calc_ax_output')

    class get_atomic_numbers:
        def main(self, cls):
            atts = ['rel_num', 'con_num', 'sent_map', 'test',
                    'fermion_dct', 'ssent2num']
            vgf.copy_partial_cls(self, cls, atts)
            self.print_on = False
            gdf.con_num = self.con_num
            self.separate_bos_ferm()
            self.check_fermions()
            self.number_sents()
            self.update_sent_map()
            self.get_stats()
            self.print_atoms()
            self.test_module()
            cls.ssent2num = self.ssent2num
            self.trim_class()

        def separate_bos_ferm(self):
            '''
            what we need is a list of sents which
            1) make molecules (fermionic)
            1a) can be negated or affirmed
            1b) cannot be negated (maybe empty)
            1c) cannot be affirmed but make molecules (maybe empty)
            4) do not make molecules

            for the properties what we need is the subject, object, equalizer
            and sent id from each of list 1 and 2

            a bosonic sentence is a sentence which does not combine with
            other atomic sentences to make molecules.
            for this reason we do not have to worry
            too much about it when we try to convert our definitions into
            numbers.  we only need a database of the properties which can
            appear in axioms. for example, 0 = 0 + 0, no molecular sentence
            reduces to this.  they're like bosons in that they do not
            stack together to form larger structures.
            '''
            self.fermions = []
            self.bosons = []
            for x, csent in self.sent_map.items():
                num_num, sent_kind = gdf.get_let_num(csent.snum)
                if sent_kind in ['2', '3', '6', '7']:
                    pass
                else:
                    if csent.modality == 2:
                        csent.kind = 'fermion'
                        self.fermions.append(csent)
                    else:
                        csent.kind = 'boson'
                        self.bosons.append(csent)

            return

        def check_fermions(self):
            all_fermions = [x.__str__() for x in self.fermions]
            for x in self.fermions:
                if x.sent_id:
                    pass
                elif x.__str__().startswith("~"):
                    if x.__str__()[1:] not in all_fermions:
                        p(f"{x} is a fermion which is not affirmed")
                else:
                    if "~" + x.__str__() not in all_fermions:
                        p(f"{x} is a fermion which is not negated")
            return

        def print_atoms(self):
            if self.print_on:
                for i in range(2):
                    for x, y in self.ssent2num.maps[0].items():
                        if not i and "b" in y:
                            p(f"{x}  {y}")
                        elif i and not "b" in y:
                            p(f"{x}  {y}")

        def number_sents(self):
            """
            sentences ending in .1 are fermions and are named
            sentences ending in .2 are molecules and are named
            sentences ending in .3 are connectives and are named
            sentences ending in .4 are bosons and are named
            .5 - unnamed fermions
            .6 - unnamed molecules
            .7 - unnamed connectives
            .8 - unnamed bosons
            """

            for x in self.fermions:
                if not x.sent_id and not x.__str__().startswith("~"):
                    self.fermion_dct[x.name] = x.relation
            b = 1
            self.fermion_dct = sort_dict_by_val(self.fermion_dct)

            for x, y in self.fermion_dct:
                self.ssent2num[x] = str(b) + ".5"
                self.ssent2num["~" + x] = "0" + str(b) + ".5"
                self.ssent2num.maps[1][str(b) + ".5"] = x
                self.ssent2num.maps[1]["0" + str(b) + ".5"] = "~" + x
                b += 1

            bos_dct = {}
            for x in self.bosons:
                rnum = self.rel_num.get(x.relation)
                snum = self.con_num.get(x.subj, 1)
                onum = self.con_num.get(x.obj, 0)
                tv = 0 if x.tvalue == "" else 0
                if x.stilde == "~": tv += 1
                if x.otilde == "~": tv += 1

                if x.name == '(r; I t:)':
                    bb = 8

                num = tv + rnum + snum + onum
                bos_dct[x.name_tv] = num

            bosons = sort_dict_by_val(bos_dct)
            b = 1
            for x, y in bosons:
                if "-" not in x:
                    self.ssent2num[x] = str(b) + ".8"
                    self.ssent2num.maps[1][str(b) + ".8"] = x
                    b += 1

            self.number_named_fermions()

            return

        def number_named_fermions(self):
            lst = []
            lst1 = ['fermions', 'bosons']
            for att in lst1:
                obj = getattr(self, att)
                suffix = ".1" if att == 'fermions' else ".4"

                for csent in obj:

                    if csent.name == '(d - r; I t:)':
                        bb= 8

                    if csent.sent_id:
                        csent2 = gdf.atomic_sent(csent, **{'entry': 'from_matrix'})
                        csent2.sent_id = ""
                        csent2.get_base_form('from_calc')
                        snum = self.ssent2num[csent2.base_form]
                        snum = sent_num(snum)
                        self.ssent2num[csent2.name_tv] = snum + suffix
                        self.ssent2num.maps[1][snum + suffix] = csent2.name_tv
                        lst.append(snum + suffix)

                if len(lst) != len(set(lst)):
                    for csent in lst:
                        if lst.count(csent) > 2:
                            p(f"{csent.name} is named twice")

            return

        def update_sent_map(self):
            for x, y in self.ssent2num.maps[0].items():
                self.sent_map[x].snum = y

        def get_stats(self):
            print_stats = 0
            if print_stats:
                non_rel_const = len([x for x in self.con_num if not x.endswith(";")])
                rel_const = len([x for x in self.con_num if x.endswith(";")])
                relations = len(self.rel_num)
                p(f"non-relational constants: {non_rel_const} ")
                p(f"relational constants: {rel_const} ")
                p(f"relations: {relations} ")
                p(f'total constants: {len(self.con_num)}')
                p(f"atomic sentences: {len(self.fermions) + len(self.bosons)}")
                p(f"fermions: {len(self.fermions) / 2}")
                p(f"bosons: {len(self.bosons)}")

        def trim_class(self):
            if not self.test:
                lst = ['ssent2num', 'con_num']
                vgf.trim_class(self, lst)
                dct = to.from_cls2dict(self)
                pi.save_pickle(dct, "atomic_sents")

        def test_module(self):
            mistake = False
            if self.test:
                old_dict = pi.open_pickle("atomic_sents")
                old_atoms = old_dict['ssent2num']
                if old_atoms != self.ssent2num:
                    for x, y in self.ssent2num.maps[0].items():
                        if old_atoms.get(x) and old_atoms[x] != y:
                            p(f"{x} is wrong")
                            p('failed')
                            mistake = True
                            break
                if not mistake:
                    p('passed')

            return


if eval(not_execute_on_import):
    args = vgf.get_arguments()
    initial_arg = args[1]
    # args[1] = "te"
    # args[2] = "nb"

    kwargs = {}
    kwargs['use_molecules'] = False
    kwargs['test'] = False
    kwargs['pi'] = False

    if "um" in args:
        # um stands for use molecules
        # which means that we're using the
        kwargs['use_molecules'] = True
    if 'te' in args:
        kwargs['test'] = True
    elif 'te3' in args:
        kwargs['test'] = 3
    if 'pi' in args:
        kwargs['pi'] = True



    if args[1] != initial_arg:
        p('you are temporarily overriding the arguments')

    if 'nb' in args:
        calculate_axiomscl().pickl_wb()
    elif 'nbm' in args:
        p('its nb not nbm')

    else:
        calculate_axiomscl().main(**kwargs)
