

from general import *
import add_path
from settings import *
import general_functions as gf
import gen_dict_func as gdf
import print_log as pl
from pack_conjunctions import get_attach_name
from random import randint



class handle_dangling_varis:
    def main(self, calc, dangling_sents, guide, debug):
        """
        this is for those sentence which contain no variables which appear
        in the antecedent.  for example, in the sentence

        (f I yy)

        the 'f' does not appear in the antecedent of

        (c I ip) ⊃ (d H c) ∧ (c I f) ∧ (f I yy)

        we then need to make a chain of sentences until we have a set of sentences
        where there is at least one varis which appears in the antecedent.  in this
        case we can stop as soon as we have

        (c I f)

        we then put the dangling sentence into the antecedent of a new conditional
        sentence and the other sentence is a negated consequent

        (f I yy) → ~(c I f)

        for reasons i don't understand we can also do

        (c I f) → ~(f I yy)


        in the following sentence:

        '(b - c I ne) → ((d - h W c) ∧ (f - h W e) ∧ (g - h W k) ∧ (j - e I rl) ∧ (m '
        '- k I rl) ∧ (n - e I ni) ∧ (o - k I ni) ∧ (p - c I ro))'

        the sentence

        (e I rl)

        has e which does not appear in the antecedent, but the next sentence which
        has e

        (h W e)

        also has h which does not appear in the antecedent, but

        (h W c)

        has h and c and c appears in the antecedent, so we have a set of three sentences

        (h W c), (h W e), (e I rl)

        we then form all the conditionals which meets the following criteria:

        1. each variable in the consequent either appears in the main antecedent
        or in the sub-antecedent

        Hence we can form the following

        ((h W c) ∧ (h W e)) → ~(e I rl)

        ((h W c) ∧ (e I rl)) → ~(h W e)

        ((h W e) ∧ (e I rl)) → ~(h W c)

        The following two sentences also form a valid chain:

        (h W c), (h W e)

        Hence we can form:

        (h W e) → ~(h W c)

        2. If the variable appears in only one sentence and is dangling, then
        we need to add that it is a thing to the antecedent like so

        ((h W c) ∧ (e I t:)) → ~(h W e)

        ____________________

        in the above example we also have the sentences:

        (h W k), (k I rl)

        but we cannot add them to the above set because they do not lead to a valid chain
        """

        # consq, sent_type, calc, cvaris, cqidx

        avaris = set(calc[1])
        self.special = []
        self.guide = guide
        self.debug = debug

        for num in dangling_sents:
            dsent = calc[2][num]
            cvaris_wid = set(dsent[1:])

            for e, bsent in en(calc[2]):
                if e != num:
                    tvaris = set(bsent[1:])
                    if bool(cvaris_wid & tvaris) and bool(tvaris & avaris):
                        found = True
                        break
            else:
                self.special.append(num)

        if self.special:
            plural_varis = self.get_plural_varis(calc[2], avaris)
            self.get_potentials(calc[2], plural_varis)
            self.build_tree(plural_varis, avaris, cvaris_wid)
            self.get_tree_by_snum(calc[2], plural_varis, avaris)
            self.get_generations()
            self.eliminate_cousins()
            self.get_necessary_trees()
            self.get_optional_sents()
            self.final_build()
            self.build_guide()

        return False

    def get_potentials(self, calc, plural_varis):
        self.potentials = {}
        self.rev_potentials = {}
        self.guide_potentials = {}
        self.idx2ssent = {}
        for e, lst in en(calc):
            st = set(lst[1:])
            if self.debug:
                self.idx2ssent[e] = self.guide[5][lst[1]]

            self.guide_potentials[e] = self.guide[5][lst[1]]
            st2 = st & plural_varis
            if st2:
                self.potentials[e] = st2
            for x in st2:
                self.rev_potentials[x] = self.rev_potentials.get(x, set()).union({e})

    def get_plural_varis(self, calc, avaris):
        lst = []
        for x in calc:
            lst += list(set(x[1:]))

        for x in avaris: lst.append(x)
        dct = counter(lst)
        return set(x for x, y in dct.items() if y > 1)

    def build_tree(self, plural_varis, avaris, cvaris_wid):
        self.children = {}
        self.child_snum = {}
        self.parents_snum = {}
        self.parents = {}
        founders = avaris & plural_varis
        for founder in founders:
            self.parents[founder] = {-1}
        i = 0
        while i < len(self.parents.keys()):
            parent = list(self.parents.keys())[i]
            self.current_loop(parent)
            i += 1
        return

    def current_loop(self, parent):
        grandparents = self.parents[parent]
        for num, x in self.potentials.items():
            if parent in x and grandparents.isdisjoint(x):
                st = x - {parent}
                self.children[parent] = self.children.get(parent, set()).union(st)
                for x in st:
                    self.parents[x] = self.parents.get(x, set()).union({parent})

    def get_tree_by_snum(self, calc, plural_varis, avaris):
        self.needed = set()
        for x, y in self.potentials.items():
            if avaris & y:
                self.needed.add(x)

        self.ancestors = {}
        self.ospecial = jsonc(self.special)
        i = 0
        while i < len(self.special):
            x = self.special[i]

            varis = self.potentials[x]
            varis = varis & plural_varis
            for vari in varis:
                parents = jsonc(self.rev_potentials[vari])
                parents.remove(x)
                self.ancestors[x] = self.ancestors.get(x, set()).union(set(parents))
            for pidx in self.ancestors[x]:
                if pidx not in self.special and pidx not in self.needed:
                    self.special.append(pidx)
            i += 1
            if i > 40:
                p('caught in infinite loop')
                assert False

        return

    def get_generations(self):
        self.num2gen = {x: 0 for x in range(len(self.potentials))}
        for x in self.needed: self.num2gen[x] = 1
        i = 1
        while 0 in self.num2gen.values():
            if i == 1:
                st = self.needed
            self.loop_generations(i + 1, st)
            i += 1
            if i > 5:
                assert False, "caught in infinite loop"
        return

    def loop_generations(self, gen, st):
        st1 = set()
        for x, y in self.ancestors.items():
            if y & st:
                st1.add(x)
                if not self.num2gen[x]:
                    self.num2gen[x] = gen

        if gen > 5:
            assert False, "caught in infinite loop"

        if 0 in self.num2gen.values():
            self.loop_generations(gen + 1, st1)

    def eliminate_cousins(self):
        self.incest_parents = {}
        self.straight_parents = {}
        for x, y in self.ancestors.items():
            num_gen = self.num2gen[x]
            self.straight_parents[x] = set(z for z in y if self.num2gen[z] < num_gen)
            self.incest_parents[x] = set(z for z in y if self.num2gen[z] == num_gen)

        return

    def get_necessary_trees(self):
        self.all_chains = {}
        self.nec_disordered = {}
        self.optional = {}
        for dangler in self.ospecial:
            lst = list(self.straight_parents[dangler])
            i = 0
            while i < len(lst):
                chain = []
                idx = lst[0]
                self.nec_disordered.setdefault(dangler, set()).add(idx)
                chain.append(idx)
                self.loop_real_parents(chain, idx, dangler)
                i += 1

        # {6},{9,2},{4}{0,1}
        '''
        6, 2, 0
        6, 2, 1
        9, 4, 3

        '''
        return

    def loop_real_parents(self, chain, idx, dangler):
        i = 0
        lst = list(self.straight_parents[idx])
        self.nec_disordered.setdefault(dangler, set()).add(idx)

        while i < len(lst):
            idx = lst[i]
            if idx not in chain:
                if idx not in self.needed:
                    chain2 = jsonc(chain)
                    chain2.append(idx)
                    self.loop_real_parents(chain2, idx, dangler)
                else:
                    self.nec_disordered.setdefault(dangler, set()).add(idx)
                    chain2 = jsonc(chain)
                    chain2.append(idx)
                    if not self.all_chains.get(dangler) or chain2 not in self.all_chains[dangler]:
                        self.all_chains.setdefault(dangler, []).append(chain2)
            i += 1

        return

    def get_optional_sents(self):
        for x in self.ospecial:
            lst = [x]
            opt_needed = set()
            i = 0
            while i < len(lst):
                current = lst[i]
                st = self.ancestors.get(current)
                for y in st:
                    if y in self.needed:
                        opt_needed.add(y)

                    elif y != x and y not in lst:
                        lst.append(y)
                i += 1
                if i > 50:
                    assert False, 'caught in infinite loop'
            nec_dis = self.nec_disordered.get(x)
            opt_needed = opt_needed - nec_dis
            self.optional[x] = (set(lst[1:]) - nec_dis) | opt_needed

        return

    def get_optional_sents2(self):
        ### this is a possible short solution
        for x in self.ospecial:
            y = self.num2gen[x]
            st = set(k for k, v in self.num2gen.items()
                     if self.num2gen[k] <= y and k != x)
            nec = self.nec_disordered[x]
            self.optional[x] = st - nec

        return

    def final_build(self):
        self.valid_combos = []
        self.snum2combo = []
        for x in self.ospecial:
            self.get_all_combos(self.all_chains[x], self.optional[x] ,x)
            self.get_valid_combos(x)

        return

    def get_all_combos(self, tnecessary, toptional, current):
        toptional = vgf.powerset(toptional, True)
        toptional = [list(x) for x in toptional]
        all_combos = []
        for x in tnecessary:
            x.append(current)
            for y in toptional:
                if not y:
                    all_combos.append(x)
                else:
                    z = x + y
                    all_combos.append(z)
        self.all_combos = all_combos

    def get_valid_combos(self, current):
        lst1 = [self.potentials[current]]
        for e, x in en(self.all_combos):
            lst = [self.potentials[y] for y in x] + lst1
            if gf.is_valid_chain3(lst):
                if set(x) not in self.valid_combos:
                    self.valid_combos.append(set(x))
                    self.snum2combo.append([set(x ) -{current} ,current])
            else:
                p('invalid')
                p(lst)

        p("")
        p("")
        p("")
        return

    def build_guide(self):
        self.valid_strings = []
        for y in self.snum2combo:
            st = y[0]
            consq = self.idx2ssent[y[1]]


            lst = [self.idx2ssent[z] for z in st]
            str1 = build_conjunction(lst)
            str2 = build_connection(str1, horseshoe, consq)
            self.valid_strings.append(str2)
            p("")
            pp(str2)
            p('')

        return