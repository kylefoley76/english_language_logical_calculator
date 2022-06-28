

from general import *
from settings import *
# import general_functions as gf
import gen_dict_func as gdf
import print_log as pl
from itertools import product, combinations


class meets_conditions_set:
    def main(self, cls):
        '''we want to make sure that we are not repeating instantiations
        for this reason we need to take out all of the sentences
        in our set of detached sentences that have succeeded in detaching
        or were detached by the current frozen set under investigation'''

        lst = ['done', 'set_o_sents', 'fs1', 'inums2snums', 'invalid_chains',
               'all_sents', 'def_num', 'embed_detach_dct']

        vgf.copy_partial_cls(self, cls, lst)
        self.entail_guide = cls.dictionary.entail_guide.get(self.fs1)
        val = self.done.get(self.fs1)
        if not val:
            if self.meets_conditions_set2(self.set_o_sents):
                cls.num2var = self.num2var
                cls.all_sents = self.all_sents
                return True
        else:
            new_set_o_sents = self.set_o_sents - val
            new_set_o_sents = list(new_set_o_sents)
            num_lst = gf.get_sent_idx2(new_set_o_sents)
            if self.fs1 <= set(num_lst):
                if self.meets_conditions_set2(new_set_o_sents):
                    cls.num2var = self.num2var
                    cls.all_sents = self.all_sents
                    return True

        return False

    def meets_conditions_set2(self, new_set_o_sents):
        '''we first need to get all of the sentences relevant
        to the current detachment since there might be more
        than one of the same sentence type.  we then need
        to come up with all the possible ways that the frozen
        set can be instanatiated.  this is the point of
        multiple cartesian.  for each potential set we need
        to first check that it is a valid chain then check
        to see if it is instantiable'''

        relevant_sents = {}
        if self.entail_guide:
            base_fs = self.inums2snums[self.fs1]
        else:
            base_fs = set(gf.from_inum2snum(x) for x in self.fs1)

        all_relevant_sents = []
        for inum in new_set_o_sents:
            snum = gf.from_inum2snum(inum)
            if snum in base_fs:
                relevant_sents.setdefault(snum, []).append(inum)
                all_relevant_sents.append(inum)

        # todo eventually move this to the digital definitions
        self.oslots = {}
        for inum in self.fs1:
            snum = gf.from_inum2snum(inum)
            self.oslots.setdefault(snum, []).append(inum)

        if len(all_relevant_sents) == len(self.fs1):
            if self.is_instantiable(all_relevant_sents):
                return True
            else:
                return False
        else:

            lst_o_lsts = [x for x in relevant_sents.values()]
            self.sorted_frozen = list(self.fs1)
            self.sorted_frozen.sort()
            ### eventually we just need to subtract all of the
            ## invalid chains from the combos

            combos = vgf.multiple_cartesian2(lst_o_lsts)
            for combo in combos:
                ivars = [self.ivars[x] for x in combo]
                if set(combo) <= self.invalid_chains:
                    pass
                else:
                    if gf.is_valid_chain2(ivars):
                        if self.is_instantiable(combo):
                            return True

                    fs2 = gf.fss(set(combo))
                    self.invalid_chains.add(fs2)

            return False

    def is_instantiable(self, combo):
        dct = {x: self.all_sents[x] for x in combo}
        dct = gf.sort_bsents().step2b(dct)
        str1, var2num = self.bsent2num(dct)
        if str1 == self.def_num[0]:
            st = set(combo)
            self.done[self.fs1] = self.done.get(self.fs1, set()).union(st)
            self.num2var = {v: k for k, v in var2num.items()}
            return True
        else:
            return False

    @staticmethod
    def bsent2num(dct):
        '''
        once the sentences have been properly orders we convert
        the variables to numbers and see if the new string of
        numbers and relations matches that which is found in the
        definition
        '''
        str1 = ""
        var2num = {}
        b = 1
        for inum, bsent in dct.items():
            snum = gf.from_inum2snum(inum)
            str1 += snum + ","
            for let in bsent:
                if not gf.isvariable(let):
                    greek = non_lit_dct.get(let)
                    if greek:
                        str2 = greek
                    else:
                        str2 = let
                else:
                    num = var2num.get(let)
                    if num:
                        str2 = num
                    else:
                        b += 1
                        str2 = str(b)
                        var2num[let] = str2

                str1 += "." + str2
            str1 += "  "
        str1 = str1.replace(",.", ",")
        str1 = str1.strip()

        return str1, var2num