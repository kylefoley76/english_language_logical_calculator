import add_path
from settings import *
from general import *
import general_functions as gf
from random import choice
from sentences.main_loop import get_result
from dictionary.gen_dict_func import atomic_sent
from dictionary.split_sentences import split_sentencescl


class test_di_instantcl:
    def __init__(self, end, begin = 0, single=0, kind=0, debug=0):
        gf.proof_kind = "test_instant"
        self.debug = debug
        if not kind:
            claims = pi.open_pickle('claims')
            self.claims = claims[1]
        else:
            self.change_var()
        if not end:
            self.order = [single]
        else:
            self.order = [x for x in range(begin, end)]
        get_result(self)

    def change_var(self):
        dictionary = pi.open_pickle("classless_dict")
        dictionary = to.from_dict2cls(dictionary)
        for self.word in dictionary.definitions.keys():
            if self.meets_conditions():
                word = self.word.lower() + "*" if self.word[0].isupper() else self.word
                lsts = pi.open_pickle("csents/" + word)
                for lst in lsts:
                    self.sp_sent = lst
                    self.hnum2csent = self.sp_sent.hnum2csent
                    self.variables = set()
                    gf.get_used_var(self, self.hnum2csent.values())
                    self.change_var2()
                    self.get_consequent()

    def change_var2(self):
        atts = ['sent_id', 'subj', 'obj', 'obj2', 'obj3', 'obj4', 'obj5']
        self.var_map = {}
        greek_def = self.sp_sent.greek
        for hnum, csent in self.hnum2csent.items():
            greek_sent = self.sp_sent.greek_di[hnum]

            for att in atts:
                item = getattr(csent, att)
                if item:
                    vari = self.var_map.get(item)
                    if vari:
                        setattr(csent, att, vari)
                    elif not vari:
                        if not gf.isvariable(item):
                            pass
                        else:
                            vari = next(self.variables)
                            self.var_map[item] = vari
                            setattr(csent, att, vari)
                elif att != 'sent_id':
                    break
            ssent = csent.build_sent()
            ssent = ssent[1:] if ssent[0] == "~" else ssent
            greek_def = greek_def.replace(greek_sent, ssent)
        self.new_def = greek_def

    def get_consequent(self):
        sp_sent2 = split_sentencescl().main(self.new_def)
        ant = "~" + sp_sent2.name['1.1']
        new_sents = [ant]
        conn = sp_sent2.conn['1.2']
        if conn == cj:
            for x, y in sp_sent2.name.items():
                if x.startswith('1.2') and x.count(".") == 3:
                    if sp_sent2.conn[x]:
                        y = y[1:-1]
                    new_sents.append(y)
        else:
            consq = sp_sent2.name['1.2']
            if conn:
                consq = consq[1:-1]
            new_sents.append(consq)
        new_sents.append(contradictory)
        self.claims = [new_sents]
        return

    def meets_conditions(self):
        if self.word == 'GVB':
            return True
        else:
            return False


if eval(not_execute_on_import):
    args = vgf.get_arguments()
    debug = 1
    if len(args) == 1:
        debug = 0

    kind = 0
    begin = 8
    end = 16
    single = 0
    test_di_instantcl(end, begin, single, kind, debug)
