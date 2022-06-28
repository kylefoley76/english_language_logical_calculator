import add_path
from settings import *
from general import *
import general_functions as gf
import gen_dict_func as gdf
import print_log as pl
from itertools import product, combinations
from instantiate import instantiatecl


class single_reductioncl:
    def main(self):
        self.entail_dct_chain = self.dictionary.entail_dct
        self.target = True
        self.kind = 'single_sent'
        for snum, rank in self.dictionary.word2rank.items():
            if snum =='62.2':
                bb= 8

            if gf.fsi(snum) in self.entail_dct_chain:
                self.variables = set()
                self.entail_dct_chain.maps[1] = {}
                ssent = self.dictionary.ssent2num[snum]
                csent = self.dictionary.sent_map[ssent]
                gf.get_used_var(self, [csent])
                self.all_sents = [gf.strip_sentence2(csent)]
                self.all_sents[0][0] = snum
                self.attached_sents = []
                instantiatecl().main(self)








        return



    def from_pickle(self, **kwargs):
        self.pickle = kwargs.get('pi')
        self.test = kwargs.get('te')
        self.debug = kwargs.get('db')
        cls = pi.open_pickle('classless_dict')
        self.dictionary = to.from_dict2cls(cls)
        self.main()

    # lst = ['dictionary', 'all_sents',
    #        'variables', 'target', 'entail_dct_chain',
    #        'attached_sents', 'sent_id2csent']
    #


if eval(not_execute_on_import):
    args = vgf.get_arguments()
    del args[0]
    args.append('db')
    p (f'current args: {args}')

    kwargs = {}
    lst = ['te', 'fh', 'sh', 'pi', 'fs', 'ob', 'fr', 'db']
    for x in lst:
        if x in args:
            kwargs[x] = True

    single_reductioncl().from_pickle(**kwargs)
