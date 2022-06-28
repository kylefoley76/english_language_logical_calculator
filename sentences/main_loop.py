import add_path
from settings import *
from general import *
from print_log import print_nums
# import general_functions as gf
from instantiate import instantiatecl
from dictionary.gen_dict_func import atomic_sent
from prepare_artificial import prepare_artificialcl


class get_result:
    def __init__(self, cls):
        self.order = cls.order
        self.claims = cls.claims
        self.debug = cls.debug
        if not gf.proof_kind == 'test_instant':
            self.dictionary = pi.open_pickle("classless_dict_old")
        else:
            dictionary = pi.open_pickle("classless_dict")
        self.dictionary = to.from_dict2cls(dictionary)
        gf.get_bul_num(self.dictionary.ssent2num)
        self.get_ax_atts()
        self.loop_claims()

    def get_ax_atts(self):
        lst = ['ax_dct', 'ax_dct_long', 'ax_sents', 'con_num']
        axiom_dictionary = pi.open_pickle('axiom_dictionary')
        for x in lst:
            setattr(self.dictionary, x, axiom_dictionary[x])

    def loop_claims(self):
        num_proved = 0
        self.correct = 0
        num_bugs = 0

        for self.snum in self.order:
            self.sent_lst = self.claims[self.snum]
            if self.sent_lst[0] != 'pass':
                num_proved += 1
                print_nums(self.snum)

                if gf.skip_errors:
                    try:
                        self.main()
                    except:
                        num_bugs += 1
                        p(f" {self.snum} bug")
                else:
                    self.main()

    @vgf.timer2
    def main(self):
        cls = prepare_artificialcl(self)
        cls.kind = "many_sent"
        right = instantiatecl().main(cls)
        if right:
            p(f'{self.snum} right')

        else:
            p ('')
            p(f'{self.snum} wrong')
            p ("")
        return
