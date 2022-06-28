import general_functions as gf
from settings import *
from general import *
from itertools import combinations
import print_log as pl
from fix_parens import choose_sentence
from split_sentences import split_sentencescl
import gen_dict_func as gdf


class elim_disjuncts:
    '''
    the final outer parentheses for this class is rather challenging.
    if the sent.kind is 'ep_disj' then the output is the new_str
    which must never have a final outerparen.  It gets put into
    a larger sentence in the digital_definitions class which will
    already have the outer paren there.
    '''


    def main(self, sp_sent_lst, ssent2num, pure_sents=[]):
        if sp_sent_lst[0].kind not in ["perfect_disjuncts", "ep_disj", 'pure']:
            return sp_sent_lst
        sp_sent = sp_sent_lst[0]
        hnum2csent = sp_sent.hnum2csent
        if sp_sent.kind == 'perfect_disjuncts':
            str1, ssd = gdf.get_new_sent(sp_sent)
            self.sp_sent = split_sentencescl().main(str1)
            self.sp_sent.hnum2csent = ssd
            self.sp_sent.kind = sp_sent.kind
        else:
            self.sp_sent = sp_sent
        name2csent = {v.name_tv: v for k, v in hnum2csent.items()}
        self.mainc = self.sp_sent.mainc
        self.new_sents = []
        self.new_str = ""
        self.negated_disjuncts = {}
        self.negated_disjuncts2 = {}
        self.neg_counterpart = {}
        self.get_pure_sents(name2csent, pure_sents)
        self.negate_csents()
        self.get_disjuncts()
        self.get_negated_disjuncts()
        self.get_neg_counterparts()
        self.build_detach_edisj()
        self.build_negated_antecedent()
        self.build_reverse_consq()
        self.resplitfu(ssent2num)
        self.handle_embed_disj()
        self.abbreviate_n_view()
        if self.sp_sent.kind in ['ep_disj']:
            return self.new_str
        else:
            return self.sp_sent_lst

    def abbreviate_n_view(self):
        return
        self.sp_sent = cls.sp_sent_lst[6]
        dct = {}
        for k, v in self.sp_sent.greek_di.items():
            if v:
                dct[self.sp_sent.name[k]] = v
        for k, v in self.sp_sent.name.items():
            for m, n in dct.items():
                v = v.replace(m, n)
            self.sp_sent.name[k] = v

    def get_pure_sents(self, name2csent, pure_sents):
        if not pure_sents:
            self.conjuncts = []
            self.defined = self.sp_sent.name['1.1']
            self.name2csent = name2csent
        else:
            self.defined = pure_sents[0]
            self.conjuncts = pure_sents[1]
            self.name2csent = merge_2dicts(name2csent, pure_sents[2])



    def get_disjuncts(self):
        self.disjuncts = []
        self.pure_disjuncts = []
        self.name2hnum = {}
        self.name2numchild = {}
        if self.mainc == xorr:
            for x, y in self.sp_sent.name.items():
                if x.count(".") == 1:
                    if self.conjuncts:
                        z = f"{y} {cj} {self.conjuncts}"
                        self.pure_disjuncts.append(z)
                    self.disjuncts.append(y)
                    self.name2hnum[y] = x
        else:
            for x, y in self.sp_sent.name.items():
                if x.count(".") == 2 and x.startswith("1.2."):
                    self.disjuncts.append(y)
                    self.name2hnum[y] = x
        return

    def build_reverse_consq(self):
        '''
        if the original sent is
        p ↔ (q ⊻ r)
        then this function will produce
        q → (p ∧ ~r)
        r → (p ∧ ~q)

        if the original sent is
        p ↔ (q ∧ (r ⊻ s))

        the this will result in:
        (q ∧ r) → (p ∧ ~s)
        (q ∧ s) → (p ∧ ~r)
        '''

        if self.mainc in [iff, xorr]:
            disjuncts = self.pure_disjuncts if self.conjuncts else self.disjuncts
            for e, disjunct in en(disjuncts):
                if self.conjuncts:
                    disjunct2 = self.disjuncts[e]
                    disjunct = "(" + disjunct + ")"
                else:
                    disjunct2 = disjunct
                str2 = f"({self.defined} {cj} {self.neg_counterpart[disjunct2]})"
                str1 = build_connection(disjunct, horseshoe, str2)
                if self.sp_sent.kind == 'ep_disj':
                    str1 = '(' + str1 + ")"
                self.new_sents.append(str1)
        return

    def build_detach_edisj(self):
        '''
        if the original sent is
        p ↔ (q ⊻ r ⊻ s)
        then this function will produce
        p → (q → (~r ∧ ~s) ∧ r → (~q ∧ ~s) ∧ (s → (~r ∧ ~s))

        if the original sent is

        m ↔ ((p ∧ q) ⊻ (r ∧ s))
        then this gets converted to:
        m ⊃
        (((p ∧ q) ⊃ ((r ⊃ ~s) ∧ (s ⊃ ~r)) ∧
        (r ∧ s) ⊃ ((p ⊃ ~q) ∧ (q ⊃ ~p)))

        to make an inference from a negated sentence and if
        the sentence has conjuncts then only one of the
        conjuncts needs to be false in order for the
        conjunct to be false, for this reason we use
        negated_disjuncts2

        ~p ⊃ (r ∧ s)

        at least one conjunct from each disjunct accept one
        must be negated.  this gives rise to a large number
        of possibilities.  for this reason it will be
        coded later.

        if the original sent is
        p ↔ (q ⊻ r ⊻ s)
        then the following are contradictions
        p ⊃ ((~q ∧ ~r) ⊃ s)
        '''

        consq_sent = []
        for e, disjunct in en(self.disjuncts):
            others = [x for f, x in en(self.disjuncts) if f != e]
            others = [y for x in others for y in self.negated_disjuncts[x]]
            if self.conjuncts:
                others.append(self.conjuncts)

            if len(others) > 1:
                consq = "(" + f" {cj} ".join(others) + ")"
            else:
                consq = others[0]

            str2 = "(" + build_connection(disjunct, horseshoe, consq) + ")"
            consq_sent.append(str2)
        self.inference_from_negation(consq_sent)
        if self.sp_sent.kind != 'ep_disj':
            str3 = "(" + f" {cj} ".join(consq_sent) + ")"
            str3 = build_connection(self.defined, horseshoe, str3)
            self.new_sents.append(str3)
        else:
            self.new_sents = consq_sent
        return

    def negate_csents(self):
        dct = {}
        for x, y in self.name2csent.items():
            neg_sent = "~" + x
            if neg_sent not in self.name2csent:
                neg_sent = gdf.make_negative(y)
                dct[neg_sent.name_tv] = neg_sent
        return merge_2dicts(self.name2csent, dct)

    def get_negated_disjuncts(self):
        '''
        if a conjunctive disjunct is negated, for example:
        ((p ∧ q) ⊻ (r ∧ s))
        then this gets converted to:
        (p ∧ q) ⊃ ((r ⊃ ~s) ∧ (s ⊃ ~r))
        (r ∧ s) ⊃ ((p ⊃ ~q) ∧ (q ⊃ ~p))

        or
        ~p → (r ∧ s)
        ~q → (r ∧ s)
        ~r → (p ∧ q)
        ~s → (p ∧ q)
        '''

        for disjunct in self.disjuncts:
            hnum = self.name2hnum[disjunct]
            conn = self.sp_sent.conn[hnum]
            if conn:
                children = self.sp_sent.children[hnum]
                if len(children) > 2:
                    assert False, "you havent coded for this yet"
                elif len(children) == 2:
                    ant = self.sp_sent.name[children[0]]
                    con = self.sp_sent.name[children[1]]
                    cond1 = "(" + build_connection(ant, horseshoe, "~" + con) + ")"
                    cond2 = "(" + build_connection(con, horseshoe, "~" + ant) + ")"
                    self.negated_disjuncts[disjunct] = [cond1, cond2]
                    neg_children = ["~" + ant, "~" + con]
                    self.negated_disjuncts2[disjunct] = neg_children
                else:
                    assert False

            else:
                self.negated_disjuncts[disjunct] = ["~" + disjunct]
                self.negated_disjuncts2[disjunct] = ["~" + disjunct]

        return

    def build_negated_antecedent(self):
        '''
        we are discontinuing this because contradictions to the definiendum
        are obtained by detaching an affirmed definiendum

        if the original sent is
        p ↔ (q ⊻ r)

        we do not do the following because

        ~p → (~q ∧ ~r)

        ~p is derived using the negated consequent

        (~q ∧ ~r) → ~p
        '''
        if self.mainc == iff and not self.conjuncts:
            lst = [y for x in self.negated_disjuncts.values() for y in x]
            consq = "(" + f" {cj} ".join(lst) + ")"
            ant = "~" + self.defined
            str1 = build_connection(consq, horseshoe, ant)
            if self.sp_sent.kind == 'ep_disj':
                str1 = "(" + str1 + ")"
            self.new_sents.append(str1)

    def get_neg_counterparts(self):
        for k, v in self.negated_disjuncts.items():
            lst = []
            for x, y in self.negated_disjuncts.items():
                if x != k:
                    for b in y:
                        lst.append(b)
            str1 = f" {cj} ".join(lst)
            self.neg_counterpart[k] = str1
        return

    def inference_from_negation(self, consq_sent):
        """
        if a disjunct is detached such as
        (p ⊻ q ⊻ r)
        then we can build the following conditionals

        (~p ∧ ~q) → r
        (~r ∧ ~q) → p
        (~p ∧ ~r) → q

        if the disjunct is conjunctive such as

        (p ∧ q ∧ w) ⊻ (r ∧ s ∧ x) ⊻ (t ∧ u)

        then we need to form all combinations where one of the conjuncts
        is negated from all of the disjuncts except one:

        (~p ∧ ~r) → (t ∧ u)
        (~p ∧ ~s) → (t ∧ u)
        (~p ∧ ~x) → (t ∧ u)
        (~q ∧ ~r) → (t ∧ u)
        (~q ∧ ~s) → (t ∧ u)
        (~q ∧ ~x) → (t ∧ u)
        (~w ∧ ~r) → (t ∧ u)
        (~w ∧ ~s) → (t ∧ u)
        (~w ∧ ~x) → (t ∧ u)

        And now we infer the second disjunct:

        (~p ∧ ~t) → (r ∧ s ∧ u)
        (~p ∧ ~u) → (r ∧ s ∧ u)
        (~q ∧ ~t) → (r ∧ s ∧ u)
        (~q ∧ ~u) → (r ∧ s ∧ u)
        (~w ∧ ~t) → (r ∧ s ∧ u)
        (~w ∧ ~u) → (r ∧ s ∧ u)

        And do likewise for the first disjunct
        """
        if not self.conjuncts:
            for consq_cj, lst in self.negated_disjuncts2.items():
                lst_disj = []
                for sent1, lst1 in self.negated_disjuncts2.items():
                    if lst != lst1:
                        lst_disj.append(lst1)

                ranges = [len(x) for x in lst_disj]
                combos = vgf.get_combos_diff_dim().step2b(ranges)
                for combo in combos:
                    neg_disj = []
                    for e, idx in en(combo):
                        sent = lst_disj[e][idx]
                        neg_disj.append(sent)
                    ant = f" {cj} ".join(neg_disj)
                    if cj in ant:
                        ant = f"({ant})"
                    str1 = "(" + build_connection(ant, horseshoe, consq_cj) + ")"
                    consq_sent.append(str1)
            if len(consq_sent) > 300:
                p(f'the definition of {self.defined} has {len(consq_sent)} disjuncts')

        return

    def resplitfu(self, ssent2num):
        if self.sp_sent.kind in ['perfect_disjuncts', 'pure']:
            self.sp_sent_lst = []
            for ssent in self.new_sents:
                sp_sent = choose_sentence().main(ssent, 'temp')
                sp_sent.kind = 'former_disjunct'
                self.sp_sent_lst.append(sp_sent)
            gdf.renumber_ss_dct(self.name2csent, self.sp_sent_lst, ssent2num)
        return

    def handle_embed_disj(self):
        if self.sp_sent.kind in ['ep_disj']:
            self.new_str = f" {cj} ".join(self.new_sents)
        return


class get_shiftscl:
    def main(self, cls):
        lst = ['word', 'sp_sent', 'shift_combos']
        vgf.copy_partial_cls(self, cls, lst)
        self.hnum2csent = cls.sp_sent.hnum2csent
        self.print_on = False
        self.test = False
        return self.main_loop()

    def main_loop(self):
        self.all_combos = 0
        self.dsentences = {}
        self.valid_shifts = {0: 1, 1: 1}
        self.get_groups()
        self.get_var_groups()
        self.get_intersections()
        self.eliminate()
        self.deduce_from_arrow().main(self)
        b = sum(self.valid_shifts.values())
        self.all_combos += b
        return self.redo_splits().main(self)

    def get_groups(self):
        self.groups = {}
        for num, ssent in self.sp_sent.name.items():
            if one_sentence(ssent):
                if num.count(".") > 1:
                    periods = [x for x in re.finditer(r"\.", num)]
                    sec_period = periods[1].regs[0][0]
                    parent = num[:sec_period]
                    self.groups.setdefault(parent, []).append(num)
                elif num.count(".") == 1:
                    self.groups.setdefault(num, []).append(num)

        return

    def get_var_groups(self):
        dct = self.sp_sent.parents
        self.has_sent_id = set(dct[x][0] for x, y in self.hnum2csent.items() if y.sent_id)
        self.var_groups = {x: set() for x in self.groups.keys()}

        for k in self.var_groups.keys():
            if k not in self.groups.keys():
                v = [k]
            else:
                v = self.groups[k]
            self.get_var_groups2(k, v)
        return

    def get_var_groups2(self, k, v):
        for sent in v:
            csent = self.hnum2csent.get(sent)
            if csent:
                self.var_groups[k] |= csent.ivar

    def get_intersections(self):
        combos = combinations(list(self.var_groups.keys()), 2)
        self.intersects1 = set()
        self.has_intersection = []

        for combo in combos:
            b = combo[0]
            c = combo[1]
            if c == '1.1':
                d = b
                b = c
                c = d
            vari1 = self.var_groups[b]
            vari2 = self.var_groups[c]
            if len(vari1 & vari2) > 0:
                if b == '1.1':
                    self.intersects1.add(c)
                else:
                    self.has_intersection.append([b, c])

        return

    def eliminate(self):
        b = self.sp_sent.sentence.count(shift) + 2
        self.shifts = self.shift_combos[b]
        # self.replace_sent_ids()

        for e, lst in en(self.shifts[2:]):
            f = e + 2
            self.tants = jsonc(lst[0])
            self.tcons = lst[1]
            # if self.has_legal_cons():
            self.tants.remove('1.1')
            self.tintersect1 = [x for x in self.tants if x in self.intersects1]
            self.get_temp_hintersect()
            if self.is_valid_shift():
                self.valid_shifts[f] = 1
            else:
                self.valid_shifts[f] = 0

        if self.word == 'INA':
            self.valid_shifts[3] = 0

        return

    def replace_sent_ids(self):
        to_be_deleted = []
        if self.has_sent_id:
            self.shifts = jsonc(self.shifts)
            for e, x in en(self.shifts):
                if any(y in self.has_sent_id for y in x[1]):
                    to_be_deleted.append(e)

            e = len(self.shifts)
            while e > -1:
                if e in to_be_deleted:
                    del self.shifts[e]
                e -= 1
            return

    def get_temp_hintersect(self):
        self.temp_hintersect = []
        for x in self.has_intersection:
            if all(y in self.tants for y in x):
                self.temp_hintersect.append(x)
        return

    def is_valid_shift(self):
        unknown = [x for x in self.tants if x not in self.tintersect1]
        b = 0
        while unknown:
            if b > 20: raise Exception("infinite loop")
            for ant in unknown:
                if self.is_valid_shift2(ant):
                    unknown.remove(ant)
                    break
            else:
                return False
            b += 1
        return True

    def is_valid_shift2(self, ant):
        for pair in self.temp_hintersect:
            if ant in pair:
                other = pair[1] if ant == pair[0] else pair[0]
                if other in self.intersects1:
                    return True
        return False

    class deduce_from_arrow:
        def main(self, cls):
            self.valid_shifts = cls.valid_shifts
            self.sp_sent = cls.sp_sent
            self.shifts = cls.shifts
            self.print_on = cls.print_on
            self.halves = {}
            self.shifts2 = []
            self.main_loop()
            self.tprint()
            cls.dsentences = self.dsentences
            cls.halves = self.halves
            cls.shifts = self.shifts2

        def main_loop(self):
            self.all_val_shifts = []
            self.dsentences = {}
            self.all_unval_shifts = []
            b = 0
            for x, y in self.valid_shifts.items():
                lst = self.shifts[x]
                ant = lst[0]
                con = lst[1]
                ant.sort()
                con.sort()
                antecedent = self.get_side(ant)
                consequent = self.get_side(con)
                antecedent = f" {cj} ".join(antecedent)
                consequent = f" {cj} ".join(consequent)
                antecedent = self.add_paren(antecedent, len(ant))
                consequent = self.add_paren(consequent, len(con))
                ssent = build_connection(antecedent, conditional, consequent)
                if y:
                    self.shifts2.append(lst)
                    self.halves[b] = [antecedent, consequent]
                    self.dsentences.update({b: ssent})
                    self.all_val_shifts.append(ssent)
                    b += 1
                else:
                    self.all_unval_shifts.append(ssent)

        def get_side(self, lst):
            lst1 = []
            for x in lst:
                ssent = self.sp_sent.name[x]
                conn = self.sp_sent.conn[x]
                if not conn or conn == cj:
                    lst1.append(ssent)
                else:
                    lst1.append(self.add_paren(ssent, 2))

            return lst1

        def tprint(self):
            if self.print_on:
                lst = [self.all_val_shifts, self.all_unval_shifts]
                pl.print_arrow(lst, self.print_on)

        @staticmethod
        def add_paren(side, num):
            lparen = ""
            rparen = ""
            if num > 1:
                lparen = "("
                rparen = ")"

            return lparen + side + rparen

    class redo_splits:
        def main(self, cls):
            lst = ['shifts', 'dsentences', 'halves', 'sp_sent', 'hnum2csent']
            vgf.copy_partial_cls(self, cls, lst)
            self.sp_sent_lst = []
            self.shift2dct = {}
            self.get_shift2dct()
            self.redo_names()
            self.get_familial_relat()
            self.put_on_csent()
            return self.sp_sent_lst

        def get_shift2dct(self):
            for k, v in self.sp_sent.hnum.items():
                self.sp_sent.hnum[k] = [str(x) for x in v]

            for f, self.shift in en(self.shifts):
                if f == 3:
                    bb = 8

                ins = resplit()
                ins.sentence = self.dsentences[f]
                ins.true_name['1'] = ins.sentence
                ins.true_name['1.1'] = self.halves[f][0]
                ins.true_name['1.2'] = self.halves[f][1]
                ins.mainc = conditional
                ins.true_conn['1'] = conditional
                dct = {}
                for g in range(2):
                    if not g:
                        str1 = '1.1'
                    else:
                        str1 = '1.2'

                    if len(self.shift[g]) == 1:
                        hnum = self.shift[g][0]
                        conn = self.sp_sent.conn[hnum]
                        dct[hnum] = str1
                        if conn:
                            ins.true_conn[str1] = conn
                            self.connective_hnum(str1, dct, hnum)
                        else:
                            dct[hnum] = str1
                            ins.true_conn[str1] = ""
                    else:
                        ins.true_conn[str1] = cj
                        self.get_ohnum2nhnum(dct, g, str1)

                ins.ohnum2nhnum = dct
                self.sp_sent_lst.append(ins)
            return

        def get_ohnum2nhnum(self, dct, g, str1):
            b = 1
            for ohnum in self.shift[g]:
                tconn = self.sp_sent.conn[ohnum]
                if tconn == cj:
                    c = 1
                    first = True
                    thnum = ohnum + "." + str(c)
                    while thnum in self.sp_sent.name or first:
                        new_hnum = f"{str1}.{b}"
                        dct[thnum] = new_hnum
                        tconn2 = self.sp_sent.conn[thnum]
                        if tconn2:
                            root_length = thnum.count(".") + 1
                            self.connective_hnum(new_hnum, dct, thnum, root_length)

                        first = False
                        b += 1
                        c += 1
                        thnum = ohnum + "." + str(c)

                elif tconn:
                    new_hnum = f"{str1}.{b}"
                    dct[ohnum] = new_hnum
                    self.connective_hnum(new_hnum, dct, ohnum)
                    b += 1
                else:
                    new_hnum = f"{str1}.{b}"
                    dct[ohnum] = new_hnum
                    b += 1

        def connective_hnum(self, new_hnum, dct, ohnum, root_length=2):
            for tnum in self.sp_sent.name.keys():
                if tnum != '1':
                    hnum_lst = self.sp_sent.hnum[tnum]
                    if len(hnum_lst) > 2:
                        root_num = ".".join(hnum_lst[:root_length])
                        if root_num == ohnum and tnum != ohnum:
                            remainder = ".".join(hnum_lst[root_length:])
                            dct[tnum] = new_hnum + "." + remainder

        def redo_names(self):
            for e, ins in en(self.sp_sent_lst):
                for hnum, name in self.sp_sent.name.items():
                    if hnum not in ['1']:
                        new_hnum = ins.ohnum2nhnum.get(hnum)
                        if new_hnum:
                            ins.name[new_hnum] = name
                            ins.tvalue[new_hnum] = self.sp_sent.tvalue[hnum]
                            ins.conn[new_hnum] = self.sp_sent.conn[hnum]

                for hnum, name in ins.true_name.items():
                    ins.name[hnum] = name
                    ins.tvalue[hnum] = ""
                    ins.conn[hnum] = ins.true_conn[hnum]

        def get_familial_relat(self):
            for ins in self.sp_sent_lst:
                ins.hnum_lst = {k: k.split(".") for k in ins.name.keys()}
                for hnum, lst in ins.hnum_lst.items():
                    _ = gdf.get_ancestors(lst)
                    ins.parents[hnum] = _
                self.get_descendants(ins)
                self.get_children(ins)

        @staticmethod
        def get_descendants(ins):
            for k, parents in ins.parents.items():
                for parent in parents:
                    ins.descendants.setdefault(parent, []).append(k)

        @staticmethod
        def get_children(ins):
            for k, desc in ins.descendants.items():
                gen = k.count(".")
                for x in desc:
                    if x.count(".") == gen + 1:
                        ins.children.setdefault(k, []).append(x)

        def put_on_csent(self):
            for sp_sent in self.sp_sent_lst:
                sp_sent.hnum2csent = {}
                for k, v in sp_sent.ohnum2nhnum.items():
                    csent = self.hnum2csent.get(k)
                    if csent:
                        sp_sent.hnum2csent[v] = gdf.atomic_sent(csent, **{})
            return


class resplit:
    def __init__(self):
        self.name = {}
        self.true_name = {}
        self.true_conn = {}
        self.conn = {}
        self.hnum_lst = {}
        self.children = {}
        self.descendants = {}
        self.hnum2csent = {}
        self.parents = {}
        self.sentence = ""
        self.kind = 'former_arrow'
        self.tvalue = {}
        self.mainc = ""
