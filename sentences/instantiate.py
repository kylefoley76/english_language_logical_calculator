from settings import *
# import general_functions as gf
from general import *
import gen_dict_func as gdf
import print_log as pl
from itertools import product, combinations
import instantiate_set as its


class instantiatecl:
    def main(self, cls):
        lst = ['dictionary', 'all_sents', 'kind',
               'variables', 'target', 'entail_dct_chain',
               'attached_sents', 'debug']
        vgf.copy_partial_cls(self, cls, lst)
        self.checked_atoms = []
        self.new_detached = {}
        self.inums2snums = self.dictionary.inums2snums
        self.embed_detach_dct = self.dictionary.embed_detach_dct
        self.bare_dct = {}
        self.done_mol = set()
        self.embed_var = {}
        self.set_o_sents = set()
        self.done = {}
        self.true_pos_sent = {}
        self.true_neg_sent = {}
        self.relevant_antecedants = set()
        self.rel_objs = set()
        self.all_sent_guide = []
        self.used_snum2obj = {}
        self.added = True
        self.consistent = True
        self.ivars = {}
        self.invalid_chains = set()
        # self.temp11()
        self.redund_sents = set()
        self.get_true_sent_guide()
        self.make_different()
        self.get_all_combos()
        # if self.kind == 'single_sent':
        #     self.single_loop()
        # else:
        #     self.main_loop()
        return self.consistent == self.target

    def get_true_sent_guide(self):
        for bsent in self.all_sents:
            snum = bsent[0]
            self.add2guide("from_true_sent", *(bsent,))
            tpl = tuple(bsent[2:])
            tpl2 = tuple([bsent[0]] + bsent[2:])
            self.redund_sents.add(tpl2)
            self.rel_objs |= set(bsent[1:])
            anum = snum
            pos = True
            if snum[0] == '0':
                anum = snum[1:]
                pos = False
            if pos:
                self.true_pos_sent.setdefault(anum, set()).add(tpl)
            else:
                self.true_neg_sent.setdefault(anum, set()).add(tpl)
        return

    def add2guide(self, kind, *args):
        if self.debug:
            ignore= False
            if kind == "from_true_sent":
                bsent = args[0]
                snum = bsent[0]
                snum = make_pos(snum)
                abb = self.dictionary.word2snum[snum]
                lst = [abb] + bsent[1:]
                self.all_sent_guide.append(lst)
            elif kind == 'from_det_truth':
                inum = args[0]
                varis = args[1]
                snum = args[2]
                snum = make_pos(snum)
                if not snum[-2:] == '.9':
                    # in_idx = gf.get_inum_idx(inum)
                    abb = self.dictionary.word2snum[snum]
                    # if in_idx: abb += "." + str(in_idx)
                    self.all_sent_guide.append([abb] + varis)
                else:
                    ignore = True
            if not ignore:
                self.used_snum2obj[snum] = abb

    def make_different(self):
        '''here we index all detached sentences by putting
        a digit on the end of the sentence.  we also turn
        the all_sents object from a list into a dictionary'''
        self.difference_dct = {}
        for e, bsent in en(self.all_sents):
            str1 = gf.get_sent_idx3(self.difference_dct, bsent[0])
            self.all_sents[e][0] = str1
        self.all_sents_dct = {x[0]: x[1:] for x in self.all_sents}
        self.set_o_sents = set(self.all_sents_dct.keys())
        return


    def get_all_combos(self):
        filter1 = gf.fss([self.all_sents[0][0], self.all_sents[1][0]])
        _, _, num_lst = gf.simple_sort_n_name(self.all_sents, True)
        lst1 = self.dictionary.contr_combos[filter1]
        if num_lst == lst1:
            self.consistent = False
        return


    def main_loop(self):
        b = 0
        while self.added and self.consistent:
            self.axiomatic_consistency()
            self.single_loop()
            # self.detach_molecules()
            b += 1
            if b > 15: raise Exception("infinite loop")

    def single_loop(self):
        b = 0
        while b < len(self.all_sents):
            x = list(self.all_sents.keys())[b]
            if not x[0] == '0' and x[-2:] == '.2' \
                    and x not in self.done_mol:
                self.fs1 = gf.fsi(x)
                self.def_num = self.entail_dct_chain.get(self.fs1)
                if self.def_num and self.detach_mol_easy():
                    self.determine_truth()
            b += 1
            if b > 30:
                bb = 8

        return

    def meets_conditions3(self, x):
        if not x[0] == '0' and x[-2:] == '.2' \
                and x not in self.done_mol:
            return True
        return False

    def detach_molecules(self):
        '''
        here we strive to pass our first step for detachment
        we loop through the entail_dct_chain and see if we have
        all the sentences needed for detachment, not worrying about
        the order of the variables.  if only one sentence is needed
        for detachment, then this is easy to accomplish and we can
        more or less skip right to handling the consequent then
        determining truth
        '''

        self.added = False
        lst = [list(x)[0] for x in self.entail_dct_chain.keys() if len(x) == 1]

        self.new_detached = {}
        self.num2var = {}
        for self.fs1, self.def_num in self.entail_dct_chain.items():
            if self.fs1 <= self.set_o_sents:
                if len(self.fs1) == 1:
                    if any(x in self.fs1 for x in ['93.2', '14.2', '12.1']):
                        bb = 8

                    if self.detach_mol_easy():
                        self.determine_truth()
                        break
                else:
                    pass
                    # if its.meets_conditions_set().main(self):
                    #     self.determine_truth()
                    #     break

        return

    def detach_mol_easy(self):
        snum = list(self.fs1)[0]
        self.guide = self.dictionary.entail_guide[self.fs1]
        # self.def_num = self.def_num[0]
        if snum[-2:] == '.9':
            bb = 8
            # ante_instantiable
            pass
            # self.guide = self.dictionary.rev_conn_sent.get(snum)
        uni_mol = self.get_uninstantiated_molecules()

        for self.inum, self.bsent in uni_mol.items():
            if self.meets_conditions2(snum):
                st = set([self.inum])
                self.done[self.fs1] = self.done.get(self.fs1, set()).union(st)
                self.get_num2var()
                return True
        return False

    def get_uninstantiated_molecules(self):
        '''here we need to make sure that we are not reinstantiating
        sentences which have already detached a definition.
        for this reason we loop through the all_sents and
        take out all the sentences which are currently
        in the tdone set'''

        tdone = self.done.get(self.fs1)
        if tdone:
            uni_mol = {}
            for name, bsent in self.all_sents.items():
                if name not in tdone:
                    uni_mol[name] = bsent
            return uni_mol
        else:
            return self.all_sents

    def meets_conditions2(self, snum):
        bare_snum = gf.from_inum2snum(self.inum)
        if bare_snum != snum:
            return False
        return True

    def ante_instantiable(self, ante):
        if any(x.isalpha() for x in ante):
            bsent = self.all_sents[self.inum]
            for x, y in zip(ante, bsent):
                if x.isalpha() and x != y:
                    return False
            return True
        else:
            return True

    def add_embeds(self, num2var, enum):
        '''the req is the sentence type that is needed to
        detach the consequent.  certain digits of the antecedent
         and the consequent need to be changed into variables
         and henceforth only those variables can detach the
         consequent.
        '''

        b = 1
        items = self.embed_detach_dct[enum]
        for item in items:
            req = item[0]
            self.relevant_antecedants |= set(req)
            ant_varis = jsonc(item[1])
            consq = jsonc(item[2])
            for e, vnum in en(ant_varis):
                varis = num2var.get(vnum)
                if not varis:
                    num2var[vnum] = str(b)
                    ant_varis[e] = str(b)
                    b += 1
                else:
                    ant_varis[e] = varis

            for lst1 in consq:
                for e, vnum in en(lst1[1:]):
                    varis = num2var.get(vnum)
                    if not varis:
                        varis = self.variables()
                        num2var[vnum] = varis
                        lst1[e + 1] = str(b)
                        b += 1
                    else:
                        lst1[e + 1] = varis

            self.entail_dct_chain.maps[1][req] = [[req, ant_varis, consq]]
        return

    def get_num2var(self):
        '''here we take the antecedent and convert the numbers
        into variables. this will form the num2var dct
        which will be used to convert the consequent into
        variables'''

        for att_sent in self.def_num:
            if self.fs1 == att_sent[0]:
                nums = att_sent[1]
                num2var = {x: y for x, y in zip(nums, self.bsent)}
                for lst in att_sent[2]:
                    lst1 = []
                    if lst[0][-2:] == '.9':
                        self.add_embeds(num2var, lst[0])

                    for vnum in lst[1:]:
                        varis = num2var.get(vnum)
                        if not varis:
                            varis = self.variables()
                            num2var[vnum] = varis
                        lst1.append(varis)
                    inum = gf.get_sent_idx3(self.difference_dct, lst[0])
                    self.new_detached[inum] = lst1
        return

    def determine_truth(self):
        '''here we need to rename our detached sentences
        and put them into either the positive or negative
        category.'''
        new_snum = []
        new_inum = []
        for inum, varis in self.new_detached.items():
            snum = gf.from_inum2snum(inum)
            if self.is_promising(snum, varis):
                self.added = True
                new_inum.append(inum)
                self.add2guide("from_det_truth", *(inum, varis, snum))
                new_snum.append(snum)
                # self.is_perfect_disjunct(snum, inum)
                ovaris = tuple(varis[1:])
                self.all_sents[inum] = varis
                self.set_o_sents.add(inum)
                anum = snum
                pos = True
                if snum[0] == '0':
                    anum = snum[1:]
                    pos = False

                if pos:
                    st = self.true_neg_sent.get(anum)
                    if st and ovaris in st:
                        self.consistent = False
                        return
                    else:
                        st1 = self.true_pos_sent.get(anum)
                        if not st1:
                            self.true_pos_sent[anum] = {ovaris}
                        elif ovaris not in st1:
                            st1.add(ovaris)
                else:
                    st = self.true_pos_sent.get(anum)
                    if st and ovaris in st:
                        self.consistent = False
                        return
                    else:
                        st1 = self.true_neg_sent.get(anum)
                        if not st1:
                            self.true_neg_sent[anum] = {ovaris}
                        elif ovaris not in st1:
                            st1.add(ovaris)
        if self.added:
            self.add2done(new_snum, new_inum)

    def is_perfect_disjunct(self, snum, inum):
        if snum in self.dictionary.perfect_disjuncts:
            self.done_mol.add(inum)

    def is_promising(self, snum, varis):
        tpl = tuple([snum] + varis[1:])
        if tpl in self.redund_sents:
            return False
        self.redund_sents.add(tpl)
        if set(varis) & self.rel_objs or snum in self.relevant_antecedants:
            return True

    def add2done(self, new_snum, new_inum):
        num_fs = gf.fss(new_snum)
        self.done[num_fs] = self.done.get(num_fs, set()).union(new_inum)
        self.done[self.fs1] = self.done.get(self.fs1, set()).union(new_inum)
        return

    def axiomatic_consistency(self):
        return
        for bsent in self.all_sents:
            z = sent_num(bsent[0])
            if is_atomic(z):
                self.checked_atoms.append(bsent)

        if self.checked_atoms:
            sent_matrix = list(combinations(self.checked_atoms, 2))
            for x, y in sent_matrix:
                xivar = set(self.bare_dct[x])
                yivar = set(self.bare_dct[y])
                if xivar & yivar:
                    ax_num = gf.get_bare_conj_name([x, y])
                    if not self.dictionary.ax_dct_long[ax_num]:
                        self.consistent = False
                        break

    def temp11(self):
        st1 = {
            "23.1",
            "23.1.1",
            "25.2",
            "25.2.1",
            "28.1",
            "31.3",
        }
        st2 = {
            "23.1",
            "23.1.1",
            "25.2",
            "25.2.1",
            "28.1",
            "31.3",
            "23.1.2",
            "23.1.3",
            "23.1.4",
            "25.2.2",
            "25.2.3",
            "28.1.1",
            "31.3.1",
            "31.3.2",
        }
        snum_no = {}
        for x in st1:
            y = gf.from_inum2snum(x)
            snum_no.setdefault(y, []).append(x)

        snum_no = {x: len(y) for x, y in snum_no.items()}

        snum_no1 = {}
        for x in st2:
            y = gf.from_inum2snum(x)
            snum_no1.setdefault(y, []).append(x)

        combo_dct = {}
        for x, y in snum_no1.items():
            le = snum_no[x]
            z = list(combinations(y, le))
            combo_dct[x] = z

        num_chains2 = [len(y) for y in combo_dct.values()]

        mult_dim_matrix = vgf.get_combos_diff_dim().step2b(num_chains2)
