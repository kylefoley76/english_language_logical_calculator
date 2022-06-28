import add_path
from settings import *
from general import *
import general_functions as gf
import gen_dict_func as gdf
import print_log as pl
from pack_conjunctions import get_attach_name
from random import randint
from dangling_variables import handle_dangling_varis


class full_reductionalcl:
    def main(self, **kwargs):
        cls = pi.open_pickle('classless_dict')
        cls1 = to.from_dict2cls(cls)
        vgf.copy_class(self, cls1)
        self.pickle = kwargs.get('pi')
        self.debug = kwargs.get('db')
        self.const_dct = pi.open_pickle('const_dct')
        dct = pi.open_pickle('half_dct')
        self.arity = dct['arity']
        self.contr_combos = {}
        self.uni_neg_args = {}
        self.uni_neg_guide = {}
        self.get_universal_negation()
        self.get_universal_negation4()
        self.get_self_contradictions1()
        cls['contr_combos'] = self.contr_combos
        cls['connected_sents'] = self.connected_sents
        self.save_pickle(cls)

    def get_base_arity_4_un(self):
        self.base_ar4un = {
            1: ['b'],
            2: ['b', 'c'],
            3: ['b', 'c', 'e'],
            4: ['b', 'c', 'e', 'f'],
            5: ['b', 'c', 'e', 'f', 'g'],
            6: ['b', 'c', 'e', 'f', 'g', 'h'],
            12: ['b', 'c', 'e']
        }

    # (d - c I t:) ∧ (m - d EN ~k) ∧ ~(k - b MV c e f g h)
    # (o - b MV n e f g h)

    # 1: (d - b I t:) ∧ (m - d EN ~k) ∧ ~(k - b S c)
    # (n - o S c)
    # 2: (d - c I t:) ∧ (m - d EN ~k) ∧ ~(k - b S c)
    # (n - b S o)

    def get_universal_negation(self):
        self.thing = self.ssent2num['(d - b I t:)']
        ennum = self.ssent2num['(d - b EN ~c)']
        self.ensent = [ennum, 'm', 'd', 'k']
        self.get_base_arity_4_un()
        for rel, y in self.pos.items():
            if isrelat(rel):
                arity = int(self.arity[rel])
                if arity == 12:
                    arity = 3

                snum = self.word2snum.get(rel)
                if snum:
                    if snum == '31.1':
                        bb = 8

                    self.get_universal_negation2(arity, snum)

    def get_universal_negation4(self):
        for snum in self.en_sent:
            if snum[0] != '0' and snum[-1] == '3':
                self.bsnum = gf.get_sent_type(snum, True)
                arity = 2
                self.varis = jsonc(self.base_ar4un[arity])
                for z in range(1, arity + 1):
                    self.get_universal_negation3(arity, snum, z, ".6")

    def get_universal_negation2(self, arity, snum):
        kind = gf.get_sent_type(snum)
        if kind in [1, 2]:
            new_type = uni_neg_type(kind)
            self.bsnum = gf.get_sent_type(snum, True)
            self.varis = jsonc(self.base_ar4un[arity])
            for z in range(1, arity + 1):
                self.get_universal_negation3(arity, snum, z, new_type)

    def get_universal_negation3(self, arity, snum, z, new_type):
        det_varis = jsonc(self.base_ar4un[arity])
        new_varis = [0, 'o', 'p', 'q', 'r', 's', 't']
        new_dvar = new_varis[z]
        det_varis[z - 1] = new_dvar
        att_var = self.varis[z - 1]
        tbsent = [self.thing, 'd', att_var]
        det_sent = [snum, 'n'] + det_varis
        bsent = ["0" + snum] + ['k'] + self.varis
        bsnum_new = self.bsnum + new_type + str(z)
        lst = [tbsent, self.ensent, bsent]
        avaris, consq_num, num_lst = gf.simple_sort_n_name(lst)
        self.uni_neg_args[bsnum_new] = num_lst
        self.uni_neg_guide[bsnum_new] = consq_num
        digital_def = "  ".join(consq_num)
        self.connected_sents[digital_def] = bsnum_new
        att_sent = [bsnum_new] + avaris
        lst1 = [det_sent, att_sent]
        _, _, avaris2 = gf.simple_sort_n_name(lst1, True)
        filter1 = gf.fss([bsnum_new, snum])
        self.contr_combos[filter1] = avaris2
        return

    def temp11(self):
        lst = [
            "(d - b UNA c)",
            "(d - b INH c)",
            "(d - b EXE c)",
            "(d - b I bo)",
            "(d - b I zg)",
            "(d - b I pa)",
            "(d - b I nn)",
            "(d - b I ne)",
            "(d - b I ip)",
        ]

        lst1 = [
            "(d - b I ne)",

        ]

        self.exceptions2 = [self.ssent2num[x] for x in lst1]

    def get_self_contradictions1(self):
        self.exceptions = ['294.2', '106.2', '416.2']
        self.exceptions2 = ['36.2', '38.2', '133.2', '224.2']
        self.exceptions2 = ['116.2']
        # self.temp11()

        st1 = {'particle', 'molecular sensation', 'property', 'point',
               'number', 'SEN', 'moment', '/', 'ABB', 'definite description',
               'sensorium', 'particularⁿ', 'cosmic resident', 'atomic sensation',
               'INA', 'real', 'SUM', 'EE', 'DI', '>', 'FRA', 'INI'}

        st2 = {'386.2', '298.2', '45.2', '417.2', '401.2', '3.2',
               '339.2', '236.2', '75.2', '410.2', '350.2', '265.2',
               '101.2', '99.2', '296.2', '38.2', '80.2', '168.2',
               '103.2', '154.2', '280.2', '366.2'}

        for x, lst in self.entail_dct.items():
            for e, calc in en(lst):
                if len(calc[0]) == 1 and list(calc[0])[0][-1] == '2':
                    self.snum = list(calc[0])[0]
                    if self.meets_conditions():
                        if self.snum[0] == '0':
                            bb = 8

                        # p(self.snum)
                        guide = self.entail_guide[x][e]
                        # calc = self.entail_dct.get(gf.fsi(x))
                        if calc:
                            self.get_self_contradictions2(guide, calc)
                        else:
                            p(self.ssent2num[x])

        return

    def meets_conditions(self):
        kind = 0
        if self.snum in self.cj_sent:
            return False
        if kind and self.snum not in self.exceptions:
            return True
        elif not kind and self.snum in self.exceptions2:
            return True
        return False

    def get_self_contradictions2(self, guide, calc):
        filter1 = calc[0]
        self.varis = calc[1][1:]
        dangling_sents = []
        for cqidx, consq in en(calc[2]):
            cvaris = set(consq[2:])
            self.diff = cvaris - set(self.varis)
            tnum = consq[0]
            if tnum not in self.exceptions and tnum not in self.cj_sent:
                sent_type = gf.get_sent_type(tnum)
                if sent_type == 9:
                    conn_sent = self.embed_detach_dct[tnum]


                elif cvaris.isdisjoint(self.varis):
                    dangling_sents.append(cqidx)
                    # p('')
                    # pp(guide[2])
                    # p(self.ssent2num[consq[0]])
                    # p("")

                elif not self.diff:
                    tnum2 = opp(tnum)
                    filter2 = set(filter1) | {tnum2}
                    consq2 = jsonc(consq)
                    consq2[0] = tnum2
                    lst = jsonc(calc[3])
                    lst.append(consq2)
                    a, b, num_lst = gf.simple_sort_n_name([lst, consq2], True)
                    self.contr_combos.setdefault(gf.fss(filter2), []).append(num_lst)
                elif self.diff:
                    self.use_uni_neg(consq, sent_type, calc, cvaris)

        if dangling_sents:
            pass
            # practice with CARI on this one
            # handle_dangling_varis().main(calc, dangling_sents, guide, self.debug)


    def use_uni_neg(self, consq, sent_type, calc, cvaris):
        '''
        here we need to find out which variable both the definiendum
        and the consq sent have in common.  we do this with

        st2 = list(varis & cvaris)

        once we know that we need to find out which variable we are negating
        so that we can get the correct sentence from the uni_neg_args

        for example, if the premises are:

        (b I pa)
        (f I t:) → ~(b S f)

        where (b I pa) entails (b S c)

        Then the subject is the same, and the object is negated, which
        means we need to get the object sentence from the uni_neg_args
        which is done by making the second digit a 2 after 7 or 8.


        we then to find out if that common variable is the subject, object
        etc of the consq sent.  if it is the subject then it is the
        second argument of the args list.  if object, then third argument.
        we then need to make sure that the number in the args list matches
        the number in the definiendum list of variables which is the
        varis list.  we do this by finding out the index of the common var
        in varis, like so:

        didx = varis.index(common_var)

        we next find out the index of common var in the cvaris, like so:

        cidx = consq[2:].index(common_var) + 1

        if 0, then subject, if 1 then object etc

        using the cidx we next get the number from the args and add 1
        since the first variable in the args is always the sent_id.

        var_in_args = args[cidx]

        we then insert var_in_args into the varis using the didx.  this
        will ensure that the variables are the same.

        varis2[didx] = var_in_args

        we then need to loop through all the variables in the varis2
        list and make sure they are different from the args list.
        '''

        tnum = consq[0]
        if tnum == '3.3':
            bb = 8

        common_varis = list(set(self.varis) & cvaris)
        uncommon_varis = list(cvaris - set(self.varis))
        for uncommon_var in uncommon_varis:
            if sent_type in [1, 2, 3]:
                new_type = uni_neg_type(sent_type)
            else:
                assert False
            base = gf.get_sent_type(tnum, True)
            uidx = consq[2:].index(uncommon_var) + 1
            un_snum = base + new_type + str(uidx)
            args = self.uni_neg_args.get(un_snum)
            if args:
                varis2 = jsonc(calc[1])
                guide = self.uni_neg_guide[un_snum]
                varis_in_args = []
                for common_var in common_varis:
                    cidx = consq[2:].index(common_var) + 1
                    didx = varis2.index(common_var)
                    var_in_args = args[cidx]
                    for e, x in en(varis2):
                        if e != didx and x == var_in_args:
                            inte = randint(10, 1_000_000_000)
                            varis2[e] = str(inte)

                    varis2[didx] = var_in_args

                    varis_in_args.append(var_in_args)

                highest = self.get_highest(tnum)
                assert str(highest) not in args
                for e, x in en(varis2):
                    if x not in varis_in_args:
                        varis2[e] = str(highest)
                        highest += 1
                varis2 = [self.snum] + varis2
                lst1 = [varis2, [un_snum] + args]
                a, b, num_lst = gf.simple_sort_n_name(lst1, True)
                filter2 = gf.fss([self.snum, un_snum])
                self.contr_combos[filter2] = num_lst

    def get_highest(self, tnum):
        """
        the arguments for universal negations are always the same
        depending on their arity.  a relation with the arity of 1
        always used 5 different arguments, for an arity of 2, there
        are always 6 different arguments.
        """
        if tnum in self.en_sent:
            return 7
        else:
            rel = self.word2snum[tnum]
            arity = self.arity[rel]
            return int(arity) + 5

    def save_pickle(self, cls):
        if self.pickle:
            p('pickled')
            pi.save_pickle(cls, 'classless_dict')


class check_circularity:
    def main(self, **kwargs):
        self.debug = kwargs.get('db')
        self.pickle = kwargs.get('fr_pickle')
        self.word2mol_guide = {}
        self.get_ranking2()
        self.get_all_reducts()
        self.get_guide(1)
        self.test_class()
        if self.debug:
            self.get_unreduced_mol()
        return

    def from_pickle(self, **kwargs):
        cls = pi.open_pickle('classless_dict')
        self.const_dct = pi.open_pickle('const_dct')
        cls1 = to.from_dict2cls(cls)
        vgf.copy_class(self, cls1)
        self.main(**kwargs)
        cls['word2rank'] = self.word2rank
        self.save_pickle2(cls)

    def from_second_half(self, cls, **kwargs):
        vgf.copy_class(self, cls)
        self.main(**kwargs)
        cls.word2rank = self.word2rank
        self.save_pickle(cls)

    def get_ranking2(self):
        self.word2mol = sort_dct_by_key_dct(self.word2mol)
        # self.no_disj_in_def()
        self.mol_ancest = jsonc(self.word2mol)
        if self.debug:
            self.get_guide()
        self.word2rank = {}
        for tnum, lst in self.word2mol.items():
            if tnum == '412.2':
                bb = 8

            if not len(lst):
                self.word2rank[tnum] = 1
            else:
                trank = self.word2rank.get(tnum)
                if not trank:
                    gancestors = {self.ssent2num[tnum]} if self.debug else set()
                    self.get_ranking3(1, lst, tnum, {tnum}, gancestors)
        return

    def get_ranking3(self, rank, lst, onum, ancestors, gancestors):
        exceptions2 = ["(d - b J zl)", '(d - b J fe)']
        self.exceptions = [self.ssent2num.get(x) for x in exceptions2]
        if any(x == onum for x in self.exceptions):
            self.word2rank[onum] = 1
            return

        b = 0
        if onum == '227.2':
            bb = 8
        if rank > 30:
            bb = 8

        if self.debug:
            oguide = self.ssent2num[onum]

        while b < len(lst):
            tnum = lst[b]
            if self.debug:
                tguide = self.ssent2num[tnum]

            trank = self.word2rank.get(tnum)
            if trank == 1:
                pass
            elif trank == None:
                nlst = self.word2mol.get(tnum)
                if nlst:
                    ancestors.add(onum)
                    if self.debug: gancestors.add(oguide)
                    self.get_ranking3(rank + 1, nlst, tnum, ancestors, gancestors)
                else:
                    self.word2rank[tnum] = 1

            elif trank > rank:
                rank = trank + 1
            b += 1

        # self.word2rank[onum] = rank

        self.word2rank[onum] = max(self.word2rank[x] for x in lst) + 1

    def alert_error(self, oguide, onum, tguide, tnum):
        self.mol_ancest.setdefault(onum, set()).add(tnum)
        if self.debug:
            self.gmol_ancest.setdefault(oguide, set()).add(tguide)
        if self.debug:
            item = oguide
            dct = self.gmol_ancest
        else:
            item = onum
            dct = self.mol_ancest

        p(f"""
        for molecule {item} the ancestory is circular
        
        {dct}
        
        is circular for molecule
        """)
        assert False

    def get_all_reducts(self):
        self.word2rank = sort_dict_by_val_dct(self.word2rank)
        self.all_reducts = {}
        self.all_reducts_guide = {}
        for k, v in self.word2rank.items():
            if k == '87.2':
                bb = 8

            if v == 1 or k in self.exceptions:
                pass
            else:
                if v == 2:
                    lst = self.word2mol[k]
                    st = set(lst)
                    for num in lst:
                        item = self.word2mol.get(num)
                        if item: st |= set(item)
                    self.all_reducts[k] = st
                elif v > 2:
                    st = set(self.word2mol[k])
                    for num in list(st):
                        item = self.all_reducts.get(num)
                        if item: st |= set(item)
                    self.all_reducts[k] = st

                assert not k in self.all_reducts[k], f"{k} is circular"

        return

    def get_guide(self, kind=0):
        if not kind:
            dct = self.word2mol
            dct1 = self.word2mol_guide
        else:
            dct = self.all_reducts
            dct1 = self.all_reducts_guide

        for k, v in dct.items():
            new_key = self.ssent2num[k]
            dct1[new_key] = [self.ssent2num[x] for x in v]

        if not kind:
            self.word2mol_guide = sort_dct_by_key_dct(self.word2mol_guide)
            self.gmol_ancest = jsonc(self.word2mol_guide)

    def test_class(self):
        for k, v in self.all_reducts.items():
            b = self.word2rank[k]
            if any(self.word2rank[x] >= b for x in v):
                assert False
            if all(self.word2rank[x] != b - 1 for x in v):
                assert False

    def get_unreduced_mol(self):
        unreduced = set()
        unreduced_num = set()
        exceptions = ['104.2']
        for x in self.word2rank.keys():
            y = gf.fsi(x)
            if y not in self.entail_dct:
                unreduced_num.add(x)
                unreduced.add(self.ssent2num[x])

        self.all_reducts_guide = sort_dct_by_key_dct(self.all_reducts_guide)
        dct2 = vgf.slice_dictionary(self.all_reducts_guide, 300)

        word2rank_guide = {self.ssent2num[x]: y for x, y in self.word2rank.items()}
        word2rank_guide = sort_dct_by_key_dct(word2rank_guide)

        starter_words = set()
        starter_sents = set()
        b = 0
        for x, y in self.word2rank.items():
            if x not in exceptions:
                z = self.word2snum.get(x)
                if z.islower():
                    z = self.const_dct.get(z)

                if 'relationship' not in z and y == 2:

                    b += 1
                    reduct = self.all_reducts[x]
                    reduct.add(x)
                    starter_sents |= reduct
                    for d in reduct:
                        z = self.word2snum.get(d)

                        if z in ['c', 'f']:
                            pass
                        else:
                            if z.islower():
                                z = self.const_dct[z]
                            starter_words.add(z)
                            if z == 'predicate':
                                bb = 8

                    if b > 10:
                        break

        p('starter sents')
        for x in starter_sents:
            p(self.ssent2num[x])

        st2 = starter_sents & unreduced_num
        for y in st2:
            x = self.word2snum[y]
            if x:
                if x[0].islower():
                    p(self.const_dct[x])
                else:
                    p(x)
            else:
                p(f"{self.ssent2num[y]} not in word2snum")

        p('starter words')
        p('')
        for x in starter_words: p(x)

        return

    def save_pickle(self, cls):
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
                    'word2mol',
                    'pos',
                    'arity',
                    'word2rank',
                    'cj_sent',
                    'en_sent',
                    'arbitrary'}

            classless_dict = {x: getattr(cls, x) for x in atts}
            pi.save_pickle(classless_dict, 'classless_dict')

    def save_pickle2(self, cls):
        if self.pickle:
            pi.save_pickle(cls, 'classless_dict')


class build_category_table:
    def main(self, **kwargs):
        relata = pi.open_pickle("relata")
        dictionary = pi.open_pickle('classless_dict')
        dictionary = to.from_dict2cls(dictionary)
        half_dct = pi.open_pickle('half_dct')
        half_dct = to.from_dict2cls(half_dct)
        bb = 8
