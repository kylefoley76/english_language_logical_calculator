import add_path
from settings import *
from general import *
import general_functions as gf
import gen_dict_func as gdf
from fix_parens import choose_sentence
from get_shifts import get_shiftscl, elim_disjuncts
from split_sentences import split_sentencescl
from pack_conjunctions import pack_conjunctionscl
import print_log as pl
from shutil import copy2
from split_sentences import fill_stats
from gen_dict_func import atomic_sent


def check_ssent2num(self):
    for x, y in self.ssent2num.maps[0].items():
        z = self.ssent2num.maps[1][y]
        if x != z:
            p('different')
            sys.exit()
    for x, y in self.ssent2num.maps[1].items():
        z = self.ssent2num.maps[0][y]
        if x != z:
            p('different')
            # sys.exit()


def meets_conditions(test, word, tpos, changed, partial, loop=0):
    if word == 'DM':
        bb = 8

    if not loop:  # the first loop
        kind = 1
        # kind = 0
    else:  # the second
        kind = 1
    if test and loop:
        kind = 1
    # kind = 0
    # exceptions = ['GVB', 'void', 'particle', 'ABA', 'CARI', 'SUE]
    exceptions2 = ['9', 'ASF', 'cosmos']

    exceptions = ['CARI']

    if tpos[0] != "c":
        if partial:
            if word in changed:
                return True
            else:
                return False
        elif kind == 2 and word not in exceptions2:
            return True
        elif kind == 1 and word not in exceptions2:
            return True
        elif not kind and word in exceptions:
            return True
    return False


class digital_definitioncl:
    def __init__(self, cls, **kwargs):
        atts = ['definitions', 'pos', 'arity']
        vgf.copy_partial_cls(self, cls, atts)
        self.kind2word = {}
        self.word2kind = {}
        self.changed = set()
        self.partial = False
        self.word2snum = chainmap({}, {})
        self.const_dct = pi.open_pickle("const_dct")
        self.old_definitions = pi.open_pickle('definitions_old')
        self.test = kwargs.get('te')
        self.erase_ssent2num = kwargs.get('er')
        self.pickle = kwargs.get('pi')
        self.do_all = kwargs.get('all')
        self.def2sp_sent = {}
        self.currently_used = set()

        ################## private attributes

        self.mol_num = 0
        self.base_molecules = set()

    def main(self):
        self.get_more_attribs()
        self.atomic_kwargs()
        self.main_loop()
        self.reduce_connectives()
        self.number_molecules()
        self.get_word2snum()
        self.fix_ssent2num()
        self.save_pickle()
        return self

    def get_more_attribs(self):
        if self.erase_ssent2num:
            lst = ['ssent2num', 'sent_map']
            axiom_dct = pi.open_pickle("axiom_dictionary")
            for x, y in axiom_dct.items():
                if x in lst:
                    setattr(self, x, y)
        else:
            dct = pi.open_pickle("classless_dict")
            self.ssent2num = dct['ssent2num']
            self.sent_map = dct['sent_map']
            cnmp = dct['word2snum']
            self.old_word2snum = chainmap({}, {})
            self.old_word2snum.maps[0] = jsonc(cnmp.maps[0])
            self.old_word2snum.maps[1] = jsonc(cnmp.maps[1])
            return


    def atomic_kwargs(self):
        self.atomic_kwargs = {
            'entry': 'definition',
            'ssent2num': self.ssent2num,
        }

    def main_loop(self):
        for self.word, definitions in self.definitions.items():
            tpos = self.pos[self.word]
            if meets_conditions(self.test, self.word, tpos, set(), False, 0):
                self.add2changed(definitions)
                lst = []
                for self.definition in definitions:
                    if any(x in self.definition for x in all_connectives):
                        self.sp_sent = choose_sentence().main(self.definition, self.word)
                        if self.sp_sent == 'go to next sentence':
                            p(f"""
                            in {self.word} we could not correct the definition:
                            {self.definition}
                            """)
                        else:
                            self.get_unique_molecules()
                            lst.append(self.sp_sent)
                            self.conn_kinds()
                self.def2sp_sent[self.word] = lst
        return

    def add2changed(self, definitions):
        old = self.old_definitions.get(self.word)
        if old and old != definitions:
            self.changed.add(self.word)
            p(f"changed {self.word}")

    def conn_kinds(self):
        if self.sp_sent.conn.get('1.2') and self.sp_sent.conn['1.2'] == xorr:
            kind = 'perfect_disjuncts'

        elif any(y == xorr for x, y in self.sp_sent.conn.items()) and \
                any(y == arrow for x, y in self.sp_sent.conn.items()):
            kind = 'arrow_disjuncts'

        elif any(y == arrow for x, y in self.sp_sent.conn.items()):
            kind = 'arrow_sentences'
            if self.sp_sent.sentence.count(arrow) > 1:
                p(f"in {self.word} there are two arrows")
                assert False
            if shift not in self.sp_sent.sentence:
                p(f"in {self.word} there needs to be a shift")
                assert False

        elif all(bool(y == cj) ^ bool(x == "1") ^ bool(y == '') for x, y in self.sp_sent.conn.items()):
            kind = 'perfect_conjuncts'

        elif any(y == xorr for x, y in self.sp_sent.conn.items()):
            kind = 'imperfect_disjunct'

        else:
            kind = 'other'
        self.sp_sent.kind = kind
        self.word2kind[self.word] = kind
        sent = self.sp_sent.sentence
        self.kind2word.setdefault(kind, {}).update({self.word: sent})

    def get_unique_molecules(self):
        single_sents = []
        for hnum, conn in self.sp_sent.conn.items():
            if not conn:
                tv = self.sp_sent.tvalue[hnum]
                ssent = tv + self.sp_sent.name[hnum]
                csent = gdf.atomic_sent(ssent, **self.atomic_kwargs)
                csent.hnum = hnum
                single_sents.append(csent)
                csent2 = self.new_csent(csent)
                csent2.sent_id = ""
                csent2.dash = ""
                csent2.tvalue = ""
                if csent2.relation == 'DM':
                    bb = 8

                csent2.get_base_form("definition")
                if csent2.base_form == '(e = b)':
                    p(self.word)
                    bb = 8

                self.currently_used.add(csent2.base_form)
                if csent2.base_form not in self.sent_map:
                    self.base_molecules.add(csent2.base_form)
                    self.sent_map[csent2.base_form] = csent2

        _ = {x.hnum: x for x in single_sents}
        self.sp_sent.hnum2csent = _
        return

    def get_word2snum(self):
        ##todo some relations which can have negated
        #related such as b CAR ~c are not working right

        for x, y in self.sent_map.items():
            snum = self.ssent2num[x]
            if y.sent_id and not snum[0] == '0':

                sent_type = gf.get_sent_type(snum)
                if sent_type not in [1, 2]:
                    word = 0
                elif sent_type == 1:
                    if "i" == y.obj or "i" == y.subj:
                        word = 0
                    elif ":" in y.obj:
                        word = y.obj
                        assert word in self.const_dct
                    elif y.relation in math_sym:
                        word = 0
                    else:
                        word = y.relation
                else:
                    if y.relation in ['I', "J", "V"]:
                        word = y.obj
                        assert word in self.const_dct

                    elif y.relation == mini_e:
                        if y.obj in self.const_dct:
                            word = y.obj
                            assert word in self.const_dct
                        else:
                            word = 0
                    else:
                        for x in pos_word:
                            if getattr(y, x) in self.const_dct:
                                word = 0
                                break
                        else:
                            word = y.relation

                if word:
                    self.word2snum[word] = snum
                    self.word2snum.maps[1][snum] = word

        return

    def reduce_connectives(self):
        if not self.partial:
            self.connectives = []
            lst1 = [
                ("", ""),
                ("", "~"),
                ("~", ""),
                ("~", "~")
            ]
            for k, v in self.pos.items():
                for e, tpl in en(lst1):
                    if v[0] == 'c' and k[0].isupper():
                        if k == 'EN' and e == 3:
                            bb = 8

                        stv = tpl[0]
                        otv = tpl[1]
                        str1 = f"({stv}b {k} {otv}c)"
                        self.connectives.append(str1)
                        csent = gdf.atomic_sent(str1, **self.atomic_kwargs)
                        self.sent_map[str1] = csent

        return

    def get_last_snum(self, str1):
        if self.erase_ssent2num:
            return 0
        else:
            nums = list(self.ssent2num.maps[1].keys())
            return max([int(float(x)) for x in nums if x.endswith(str1)]) + 1

    def get_missing_mol(self):
        if self.erase_ssent2num:
            return list(self.base_molecules) + self.connectives, 0
        else:
            new = set(self.base_molecules)
            existing = set(self.ssent2num.maps[0].keys())
            missing = new - existing
            self.get_deleted_mol()
            unused_snum = 0
            return missing, unused_snum

    def get_deleted_mol(self):
        old_def = set(self.old_definitions.keys())
        new_def = set(self.definitions.keys())
        st = old_def - new_def
        deleted_mol = set()
        for x in st:
            if x[0].islower():
                deleted_mol.add(vgf.get_key(self.const_dct, x))
            else:
                deleted_mol.add(x)

        deleted_mol = set(self.old_word2snum[mol] for mol in deleted_mol)
        variations = set()
        for x in deleted_mol:
            if x[-1] == '2':
                variations.add("0" + x)
                str1 = x[:-1] + "6"
                str2 = "0" + str1
                variations.add(str1)
                variations.add(str2)
        snums = variations | deleted_mol
        ssents = set(self.ssent2num[x] for x in snums)
        for x in ssents:
            del self.sent_map[x]
            del self.ssent2num[x]
        for x in snums:
            del self.ssent2num.maps[1][x]
        return




    def get_tnum(self, ssent, m, c, sixes):
        tnum = self.ssent2num.get(ssent)
        if tnum:
            tnum = int(float(tnum))

        if ssent in self.connectives:
            let = '.7'
            leti = '.3'
            if not tnum:
                c += 1
                tnum = c
        else:
            let = ".6"
            leti = '.2'
            if not tnum:
                m += 1
                tnum = m

        return tnum, let, leti, m, c

    def number_molecules(self):
        self.atomic_kwargs['entry'] = 'from_matrix'
        m = self.get_last_snum('.2')
        c = self.get_last_snum('.3')
        missing, sixes = self.get_missing_mol()
        renumbered = False

        for ssent in missing:
            if not renumbered:
                p('renumbered')
            renumbered = True

            tnum, let, leti, m, c = self.get_tnum(ssent, m, c, sixes)
            csent = self.sent_map[ssent]
            snum2 = str(tnum) + let
            self.new_csent2(csent, snum2)

            csent2 = self.new_csent(csent)
            csent2.tvalue = "~"
            snum2 = "0" + snum2
            self.new_csent2(csent2, snum2)

            csent2 = self.new_csent(csent)
            csent2.sent_id = "d"
            snum2 = str(tnum) + leti
            self.new_csent2(csent2, snum2)

            csent2 = self.new_csent(csent)
            csent2.sent_id = "d"
            csent2.tvalue = "~"
            snum2 = "0" + snum2
            self.new_csent2(csent2, snum2)

        b = self.sent_map.values()
        _ = [x.snum for x in b if x.relation == circle]
        self.cj_sent = _
        _ = [x.snum for x in b if x.relation == "EN"]
        self.en_sent = _

        return

    def new_csent(self, csent):
        self.atomic_kwargs['entry'] = 'from_matrix'
        csent2 = gdf.atomic_sent(csent, **self.atomic_kwargs)
        self.atomic_kwargs['entry'] = 'definition'
        return csent2

    def new_csent2(self, csent, snum2):
        csent.get_base_form()
        ssent = csent.base_form
        csent.snum = snum2
        self.ssent2num[ssent] = snum2
        self.ssent2num.maps[1][snum2] = ssent
        csent.name = csent.build_sent()
        self.sent_map[ssent] = csent

    def fix_ssent2num(self):
        self.ssent2num.maps[1] = {}
        _ = {v: k for k, v in self.ssent2num.maps[0].items()}
        self.ssent2num.maps[1] = _
        assert len(self.ssent2num.maps[0]) == len(self.ssent2num.maps[1])

    def save_pickle(self):
        atts = [
            'ssent2num',
            'word2snum',
            'cj_sent',
            'en_sent',
            'def2sp_sent',
            'sent_map',
            'word2kind',
            'kind2word',
            'changed',
            'pos',
            'arity',
        ]

        if self.pickle:
            p ('pickled definitions')
            copy2(base_dir + "pickles/definitions.pkl", base_dir + "pickles/definitions_old.pkl")
            pi.save_pickle(self.definitions, 'definitions')
            if not self.do_all:
                p('pickled half dct')
                classless_dict = {}
                for x in atts:
                    classless_dict[x] = getattr(self, x)
                pi.save_pickle(classless_dict, 'half_dct')



class get_standard_form:
    def __init__(self, **kwargs):
        self.test = kwargs.get('te')
        self.pickle = kwargs.get('pi')
        self.skip_errors = kwargs.get('se')
        self.partial = kwargs.get('pa')
        self.arbitrary = {}
        self.atts = [
            'ssent2num',
            'word2snum',
            'cj_sent',
            'en_sent',
            'sent_map',
        ]
        self.atts2 = [
            'word2kind',
            'kind2word',
            'def2sp_sent',
            'const_dct',
            'arity',
            'changed',
            'pos']

    def from_first_half(self, cls):
        vgf.copy_partial_cls(self, cls, self.atts + self.atts2)

    def from_pickle(self):
        dct = pi.open_pickle('half_dct')
        for x, y in dct.items():
            setattr(self, x, y)
        self.const_dct = pi.open_pickle("const_dct")

    def from_premise(self, cls):
        atts4 = [
            'entail_dct',
            'entail_guide',
            'embed_detach_dct',
            'inums2snums'
        ]

        atts3 = [
            'connected_sents',
            'done_conjuncts',
            'done_entail',
            'variables',
            'detached_varis',
            'sent2var',
            'odef',
            'all_sents',
            'attached_sents',
            'sent_id2csent'
        ]
        vgf.copy_partial_cls(self, cls.dictionary, self.atts + atts4)
        vgf.copy_partial_cls(self, cls, atts3)
        self.shift_combos = {}
        self.word = 'premise'
        self.abb_word = 'premise'
        self.atomic_kwargs = {
            'entry': 'definition',
            'ssent2num': self.ssent2num,
        }

    def main(self):
        self.entail_dct = chainmap({}, {})
        self.entail_guide = {}
        self.embed_detach_dct = {}
        self.inums2snums = {}
        self.word2mol = {}
        self.connected_sents = {}
        self.main2()

    def define_partial(self):
        cls = pi.open_pickle("classless_dict")
        cls = to.from_dict2cls(cls)
        vgf.copy_class(self, cls)
        self.main2()

    def main2(self):
        pl.print_on = False
        self.shift_combos = pi.open_pickle("shift_combos")
        self.done_conjuncts = {}
        self.done_entail = {}
        self.detached_varis = set()
        self.sent2var = {}
        self.variables = set()
        gf.cj_sent = self.cj_sent
        gf.en_sent = self.en_sent
        gf.get_bul_num(self.ssent2num)
        gf.cj_sent.append(gf.bul_num)
        self.atomic_kwargs = {
            'entry': 'definition',
            'ssent2num': self.ssent2num,
        }

        self.main_loop()
        self.save_pickle()
        self.test_dictionary()

    def main_loop(self):
        b = 0
        for self.word, self.sp_sent_lst in self.def2sp_sent.items():
            b += 1
            vgf.print_intervals(b, 50)
            tpos = self.pos[self.word]
            if self.word == 'INA':
                bb = 8

            if meets_conditions(self.test, self.word,
                                tpos, self.changed,
                                self.partial, 1):
                # p(self.word)
                self.get_abb_word()
                if self.skip_errors:
                    try:
                        self.loop_definition()
                    except:
                        p(f"error in {self.word}")
                else:
                    self.loop_definition()
                self.done_conjuncts = {}
                self.done_entail = {}
                if self.ssent2num['(d - b J c)'] != '23.1':
                    p('changed')
                    sys.exit()

        return

    def get_abb_word(self):
        self.abb_word = self.word
        if self.abb_word not in self.word2snum:
            self.abb_word = vgf.get_key(self.const_dct, self.abb_word)
        return

    def loop_definition(self):
        legal_kinds = ['other', 'perfect_conjuncts', 'imperfect_disjunct',
                       'arrow_sentences', 'perfect_disjuncts', 'ep_disj',
                       'former_arrow', 'former_disjunct', 'premise']
        illegal_kinds = ['arrow_disjuncts']

        i = 0
        while i < len(self.sp_sent_lst):
            self.sp_sent = self.sp_sent_lst[i]
            self.kind = self.sp_sent.kind
            if self.kind not in illegal_kinds:
                if not self.kind == 'premise':
                    used_var = set(self.done_entail.values()) | set(self.done_conjuncts.values())
                    gf.get_used_var(self, self.sp_sent.hnum2csent.values(), used_var)
                    self.sent2var = defaultdict(self.variables)
                if self.meets_conditions2():
                    self.put_on_sent_id()
                    self.adjust_sp_name()
                    self.get_word2mol()
                self.elim_imp_disj().main(self)
                _ = elim_disjuncts().main(self.sp_sent_lst, self.ssent2num)
                self.sp_sent_lst = _
                self.sp_sent = self.sp_sent_lst[i]
                self.eliminate_arrows()
                self.odef = self.sp_sent.sentence
                if self.kind == 'premise':
                    return self.build_hierarchy().main(self)
                else:
                    self.build_hierarchy().main(self)
                    self.variables = []
            i += 1
            # p (i)
            if i == 3:
                bb = 8

    class elim_imp_disj:
        def main(self, cls):
            if cls.kind not in ['imperfect_disjunct', 'arrow_disjuncts']:
                return
            self.sp_sent = cls.sp_sent
            self.ssent2num = cls.ssent2num
            self.old_names = cls.old_names
            self.kind2 = 'ep_disj'
            self.pure_sents = []
            done = set()
            parent = self.sp_sent.sentence
            num = 945
            self.parent = self.rename_imp_disj(parent)
            greek2disj = {}
            dct1 = {y.name_tv: y for x, y in self.sp_sent.hnum2csent.items()}
            dct1a = {y.name: y for x, y in self.sp_sent.hnum2csent.items()}
            self.get_replacements(done, greek2disj, num)
            self.make_replacements(dct1, greek2disj)
            if self.kind2 == 'pure':
                cls.sp_sent = self.sp_sent
                cls.sp_sent_lst = self.sp_sent_lst
            else:
                # todo take this down after a while
                self.sp_sent = choose_sentence().main(self.parent, "temp")
                if type(self.sp_sent) == str: assert False
                if cls.kind == 'arrow_disjuncts':
                    self.sp_sent.kind = 'arrow_sentences'
                else:
                    self.sp_sent.kind = 'former_disjunct'
                cls.kind = self.sp_sent.kind
                self.sp_sent_lst = [self.sp_sent]
                dct3 = self.sp_sent.name
                dct2 = self.sp_sent.conn
                self.sp_sent.hnum2csent = {k: dct1a[dct3[k]]
                                           for k, v in dct2.items() if not v}
                for k, v in self.sp_sent.tvalue.items():
                    if v:
                        csent = self.sp_sent.hnum2csent[k]
                        self.sp_sent.hnum2csent[k] = gdf.make_negative(csent)
                cls.sp_sent = self.sp_sent
                cls.sp_sent_lst = [cls.sp_sent]

            return

        def get_replacements(self, done, greek2disj, num):
            for x, y in self.sp_sent.conn.items():
                arrow_used = False
                if y == xorr:
                    parents = self.sp_sent.parents[x]
                    if self.sp_sent.conn[parents[0]] == arrow:
                        hnum = x
                        arrow_used = True
                    elif self.sp_sent.conn[parents[0]] in [conditional, iff, horseshoe]:
                        hnum = parents[0]
                    elif parents[1] == '1':
                        hnum = '1'
                    else:
                        hnum = parents[1]

                    if hnum not in done:
                        if not hnum == '1':
                            done.add(hnum)
                        repl = chr(num)
                        if hnum == '1' and self.sp_sent.kind != 'arrow_disjuncts':
                            self.kind2 = 'pure'
                            self.get_pure_sents()
                            sent = self.sp_sent.name[x]
                        else:
                            sent = self.sp_sent.name[hnum]
                        sent = self.rename_imp_disj(sent)

                        if arrow_used or hnum == '1' or parents[1] == '1':
                            sent = sent[1:-1]

                        self.parent = self.parent.replace(sent, repl)
                        num += 1
                        greek2disj[repl] = sent

        def get_pure_sents(self):
            self.pure_sents.append(self.sp_sent.name['1.1'])
            lst = []
            for k, v in self.sp_sent.conn.items():
                if not v:
                    if k.startswith('1.2.') and k.count(".") == 2:
                        lst.append(self.sp_sent.name[k])
            str1 = f" {cj} ".join(lst)
            self.pure_sents.append(str1)
            dct = {v.name_tv: v for k, v in self.sp_sent.hnum2csent.items()}
            self.pure_sents.append(dct)

        def make_replacements(self, dct1, greek2disj):
            for repl, sent in greek2disj.items():
                sp_sent = split_sentencescl().main(sent)
                dct3 = sp_sent.name
                dct = {k: dct1[dct3[k]] for k, v in sp_sent.conn.items() if not v}
                sp_sent.hnum2csent = dct
                sp_sent.kind = self.kind2
                _ = elim_disjuncts().main([sp_sent], self.ssent2num, self.pure_sents)
                sent = _
                if self.kind2 == 'pure':
                    self.sp_sent_lst = sent
                else:
                    self.parent = self.parent.replace(repl, sent)

        def rename_imp_disj(self, sent):
            for k, v in self.sp_sent.conn.items():
                if not v:
                    old = self.old_names[k]
                    new = self.sp_sent.name[k]
                sent = sent.replace(old, new)
            return sent

    def eliminate_arrows(self):
        # p (self.word)
        if self.kind in ['arrow_sentences']:
            if self.sp_sent.sentence.count(shift) < 15:
                self.sp_sent_lst = get_shiftscl().main(self)
                self.sp_sent = self.sp_sent_lst[0]

    def meets_conditions2(self):
        if self.kind in [
            'former_arrow',
            'former_disjunct']:
            return False
        elif self.kind == 'premise':
            return False
        return True

    def adjust_sp_name(self):
        self.old_names = jsonc(self.sp_sent.name)
        for k, v in self.sp_sent.hnum2csent.items():
            self.sp_sent.name[k] = v.name
            v.snum = self.ssent2num.get(v.base_form)

    def get_word2mol(self):
        hnum2csent = self.sp_sent.hnum2csent
        csent = hnum2csent.get('1.1')
        if csent:
            mol_num = csent.snum
            for k, v in hnum2csent.items():
                if k != '1.1' and is_molec(v.snum):
                    snum = v.snum if v.snum[0] != "0" else v.snum[1:]
                    self.word2mol.setdefault(mol_num, []).append(snum)
        else:
            p(f"{self.word} is not reducible to atoms")
            p(self.odef)
            p("")

    def put_on_sent_id(self):
        self.odef = self.sp_sent.sentence
        for csent in self.sp_sent.hnum2csent.values():
            if not csent.sent_id:
                gf.name_sentence(csent, self.ssent2num, self.sent2var)
            else:
                self.sent2var[csent.name] = csent.sent_id
        return

    def save_pickle(self):
        if self.pickle:
            p('pickled')
            atts = {'ssent2num',
                    'sent_map',
                    'word2snum',
                    'entail_dct',
                    'entail_guide',
                    'embed_detach_dct',
                    'inums2snums',
                    'connected_sents',
                    'pos',
                    'arity',
                    'word2mol',
                    'cj_sent',
                    'en_sent',
                    'arbitrary'}

            classless_dict = {x: getattr(self, x) for x in atts}
            pi.save_pickle(classless_dict, 'classless_dict')


    def test_dictionary(self):
        if self.test:
            old_entail_info = pi.open_pickle('classless_dict')
            if self.entail_dct != old_entail_info['entail_dct']:
                p('failed first dictionary test')
            else:
                p('passed first dictionary test')
            if self.entail_guide != old_entail_info['entail_guide']:
                p('failed second dictionary test')
                for k, v in old_entail_info['entail_guide'].items():
                    new_v = self.entail_guide[k]
                    if new_v != v:
                        p(f"{k} is different")


            else:
                p('passed second dictionary test')
            if old_entail_info['connected_sents'] != self.connected_sents:
                p('failed connected sents test')
            else:
                p('passed connected sents test')

    class build_hierarchy:
        '''
        a named attached sentence is one of the form (p → q).  it is
        given a unique number ending in .9 and added to the
        connected_sents dictionary.  when it is sorted we need all
        of the relevant sentences that is composed of.
        when it is named we only need the EN sentences, the detached
        conjuncts and other named attached sentences if any.

        the new_sent_constr is just used to build new sentences and
        does not get passed onto the build_entailments class.  because
        we are only interested in new sentences iff sentences do not
        count since they are reduced to EN sentences, hence we are only
        building new EN sents and circle sentences

        the detach_embed is used so that when an embedded conditional
        is detached we know what the antecedents and consequents are.
        this is composed of a list of 2 lists. the antecedent needs
        to be composed of all detached and named attached sentences.

        the sorting_guide is only used for sorting when it comes time
        to build new sentences.

        the embed2b_named dict only needs to have the sentences which are
        on its level since those sentences which are children or grandchildren
        will be given a new name and we need only use that name.
        '''

        def main(self, cls):
            atts = ['kind', 'variables', 'atomic_kwargs', 'ssent2num',
                    'done_conjuncts', 'done_entail', 'arbitrary']
            vgf.copy_partial_cls(self, cls, atts)
            keys = ['conn', 'hnum2csent', 'tvalue',
                    'children', 'descendants',
                    'name', 'parents', 'mainc']
            vgf.copy_partial_cls(self, cls.sp_sent, keys)
            self.sent_id2csent = {v.sent_idtv: v
                                  for v in self.hnum2csent.values()}
            self.iff_dct = {}
            self.embeds2b_named = {}
            self.new_sent_constr = {}
            self.sent_id2conn = {}
            self.do_not_sort = []
            self.detach_embed = {}
            self.sent_id2old_ssent = {}
            self.sent_id2ssent = {}
            self.order_children()
            self.assign_var2conn()
            self.elim_iff_hier()
            self.get_sent_id2ssent()
            self.preparenum2var2num()
            pack_conjunctionscl().main(self, cls)
            if self.kind == 'premise':
                return cls.all_sents, cls.attached_sents, cls.sent_id2csent

        def order_children(self):
            dct = {}
            for x, y in self.children.items():
                dct[x] = x.count(".")
            dct = sort_dict_by_val_dct(dct)
            children2 = {}
            for x in reversed(list(dct.keys())):
                children2[x] = self.children[x]
            self.children = children2

        def assign_var2conn(self):
            dct = defaultdict(self.variables)
            self.new_sent_helper = {}
            z = self.hnum2csent
            for x, y in self.children.items():
                if x == '1':
                    bb = 8

                if y:
                    conn = self.conn[x]
                    if conn not in [iff, conditional, horseshoe]:
                        tpl = tuple(z[x] if type(z[x]) == str else z[x].sent_idtv for x in y)
                        varis = dct[tpl]
                    else:
                        left = x + ".1"
                        right = x + ".2"
                        var_lst1 = self.get_children(left)
                        var_lst2 = self.get_children(right)
                        varis1 = self.get_sent_id(left)
                        varis2 = self.get_sent_id(right)
                        tpl1 = (varis1, varis2)
                        tpl2 = (varis2, varis1)

                        if conn == iff:
                            varis = self.variables()

                            if x == '1' and self.kind not in ['premise', 'ep_disj']:
                                varis3 = '1'
                                varis4 = '2'
                            else:
                                self.embeds2b_named[varis] = []
                                varis3 = dct[tpl1]
                                varis4 = dct[tpl2]
                                self.iff_dct[varis] = [varis3, varis4]

                            self.detach_embed[varis3] = [var_lst1, var_lst2]
                            self.detach_embed[varis4] = [var_lst2, var_lst1]
                            self.new_sent_helper[varis3] = [varis1, varis2]
                            self.new_sent_helper[varis4] = [varis2, varis1]
                            self.hnum2csent[x + 'a'] = varis3
                            self.hnum2csent[x + 'b'] = varis4
                        elif conn in [conditional, horseshoe]:
                            tpl = (varis1, varis2)
                            if x == '1' and self.kind not in ['premise', 'ep_disj']:
                                varis = '1'
                            else:
                                varis = dct[tpl]
                                self.embeds2b_named[varis] = []

                            self.detach_embed[varis] = [var_lst1, var_lst2]
                            self.new_sent_helper[varis] = [varis1, varis2]

                    self.hnum2csent[x] = varis

            return

        def get_children(self, x):
            if x == "1":
                bb = 8

            conn = self.conn[x]
            z = self.children.get(x)
            if not z:
                return [self.get_sent_id(x)]
            elif conn == cj:
                return [self.get_sent_id(y) for y in z]
            else:
                return [self.get_sent_id(x)]

        def sort_bicond(self, left, right, varis1, varis2):
            left_children = self.descendants.get(left, [left])
            right_children = self.descendants.get(right, [right])

            if len(left_children) < len(right_children):
                return varis1, varis2
            if len(left_children) > len(right_children):
                return varis2, varis1

            left_snums = [self.hnum2csent[x].snum for x in left_children]
            right_snums = [self.hnum2csent[x].snum for x in right_children]
            left_snums.sort()
            right_snums.sort()

            for l, r in zip(left_snums, right_snums):
                if float(l) == float(r):
                    pl.print_arb('arbitrary biconditional')
                    return varis1, varis2
                elif float(l) < float(r):
                    return varis1, varis2
                elif float(l) > float(r):
                    return varis2, varis1

            assert False

        def meets_conditions3(self, hnum, conn):
            if self.kind in ['premise', 'ep_disj']:
                return True
            if hnum == '1':
                return False
            if hnum.count(".") == 1 and conn == cj:
                return False
            return True

        def elim_iff_hier(self):
            for hnum, v in self.children.items():
                conn = self.conn[hnum]
                if self.meets_conditions3(hnum, conn):
                    sent_id = self.get_sent_id(hnum)
                    if sent_id == 'k' + l1:
                        bb = 8

                    conn = self.conn[hnum]
                    if conn == conditional: conn = horseshoe
                    if sent_id in self.iff_dct:
                        descendants = self.iff_dct[sent_id]
                        left = descendants[0]
                        right = descendants[1]
                        left_kids = self.new_sent_helper[left]
                        right_kids = self.new_sent_helper[right]
                        self.new_sent_constr[left] = left_kids
                        self.new_sent_constr[right] = right_kids
                        self.new_sent_constr[sent_id] = [left, right]
                        self.sent_id2conn[left] = horseshoe
                        self.sent_id2conn[right] = horseshoe
                    else:
                        varis = self.get_sent_id(hnum)
                        _ = [self.get_sent_id(x) for x in v]
                        self.new_sent_constr[varis] = _
                        self.sent_id2conn[varis] = conn
                        ''''
                        this is for the super rare case where the sentence
                        is a conditional and the consequent is composed of
                        conjuncts only.  in that case, we do not need to
                        sort them
                        '''
                        if self.kind not in ['premise'] \
                                and conn == cj and \
                                hnum.count(".") == 1:
                            self.do_not_sort.append(varis)

            return

        def get_sent_id2ssent(self):
            for k, v in self.hnum2csent.items():
                if k == "1":
                    pass
                elif k[-1] in ['a', 'b']:
                    pass
                elif type(v) == str:
                    tv = self.tvalue[k]
                    self.sent_id2old_ssent[v] = tv + self.name[k]
                else:
                    self.sent_id2old_ssent[v.sent_idtv] = v.name_tv
                    self.sent_id2ssent[v.sent_idtv] = v.name_tv

            return

        def get_sent_id(self, hnum):
            item = self.hnum2csent[hnum]
            if type(item) != str:
                item = item.sent_idtv
            return item

        def preparenum2var2num(self):
            if self.kind in ['premise']:
                self.sent_id2num2var = {}
                return

            oneone = self.hnum2csent['1.1']
            onetwo = self.hnum2csent['1.2']
            if type(oneone) == gdf.atomic_sent:
                oneone = oneone.sent_id
            if type(oneone) == gdf.atomic_sent:
                onetwo = onetwo.sent_id
            normal = True
            if self.detach_embed['1'] == [onetwo, oneone]:
                normal = False

            self.sent_id2num2var = {}
            for x in self.detach_embed.keys():
                if x[0].isalpha():
                    for hnum, v in self.hnum2csent.items():
                        if hnum not in ['1', '2'] and \
                                gf.get_sent_id(self.hnum2csent, hnum) == x:
                            hnum = hnum[:3]
                            if (hnum == '1.2' and normal) or \
                                    (hnum == '1.1' and not normal):
                                self.sent_id2num2var[x] = '1'
                            else:
                                self.sent_id2num2var[x] = '2'
                            break
