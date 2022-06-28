import add_path
from settings import *
import general_functions as gf
import dictionary.gen_dict_func as gdf
from dictionary.fix_parens import choose_sentence
from dictionary.digital_definition import get_standard_form
from dictionary.pack_conjunctions import get_attach_name


class prepare_artificialcl:
    def __init__(self, cls):
        self.dictionary = cls.dictionary
        self.connected_sents = self.dictionary.connected_sents
        self.all_sents = []
        self.variables = set()
        self.target = False
        self.entail_dct_chain = chainmap(self.dictionary.entail_dct.maps[0], {})
        self.attached_sents = {}
        self.main(cls)

    def main(self, cls):
        self.get_private_attribs(cls)
        self.add_cj_sent()
        self.get_target()
        self.get_all_sents()
        gf.get_used_var(self, self.all_csents)
        self.add_sent_id()
        self.redo_attached_sents()
        self.handle_attached_sents()
        self.handle_biconditionals()

    def add_cj_sent(self):
        gf.cj_sent = self.dictionary.cj_sent
        gf.en_sent = self.dictionary.en_sent
        gf.cj_sent.append(gf.bul_num)


    def get_private_attribs(self, cls):
        self.sent_lst = cls.sent_lst
        self.debug = cls.debug
        self.atomic_kwargs = {
            'entry': 'artificial',
            'ssent2num': self.dictionary.ssent2num,
        }
        self.detached_sents = set()
        self.detached_varis = set()
        self.odef = ""
        self.all_csents = []
        self.sp_sents = {}

    def get_target(self):
        if self.sent_lst[-1] == contradictory:
            self.target = False
        elif self.sent_lst[-1] == "C":
            self.target = True
        elif self.sent_lst[-1][0] == implies:
            self.target = self.sent_lst[-1][2:]
        del self.sent_lst[-1]

    def get_all_sents(self):
        b = 0
        for e, ssent in en(self.sent_lst):
            if ssent == 'deleted':
                pass
            elif not one_sentence(ssent):
                b += 1
                sp_sent = choose_sentence().main(ssent, "")
                self.build_sent_dct(sp_sent, b)
            else:
                csent = gdf.atomic_sent(ssent, **self.atomic_kwargs)
                self.all_csents.append(csent)
                self.detached_sents.add(csent.name_tv)
        return

    def build_sent_dct(self, sp_sent, b):
        sp_sent.hnum2csent = {}
        for hnum, ssent in sp_sent.name.items():
            if not sp_sent.conn[hnum]:
                ssent = sp_sent.tvalue[hnum] + ssent
                csent = gdf.atomic_sent(ssent, **self.atomic_kwargs)
                sp_sent.hnum2csent[hnum] = csent
                csent.hnum = hnum
                self.all_csents.append(csent)
        self.sp_sents[f"temp{b}"] = sp_sent

    def add_sent_id(self):
        self.sent2var = defaultdict(self.variables)
        self.old2new = {}
        for csent in self.all_csents:
            if csent.sent_id:
                self.old2new[csent.name_tv] = csent.name_tv
            else:
                old_ssent = csent.name_tv
                detached = True if csent.name_tv in self.detached_sents else False
                gf.name_sentence(csent, self.dictionary.ssent2num, self.sent2var)
                if detached:
                    bsent = gf.strip_sentence2(csent)
                    self.all_sents.append(bsent)
                    self.detached_varis |= csent.ivar
                self.old2new[old_ssent] = csent.name_tv
        self.sent_id2csent = {x.sent_idtv: x for x in self.all_csents}
        return

    def redo_attached_sents(self):
        for word, sp_sent in self.sp_sents.items():
            for hnum, name in sp_sent.name.items():
                if not sp_sent.conn[hnum]:
                    tilde = sp_sent.tvalue[hnum]
                    name = tilde + name
                    sp_sent.name[hnum] = self.old2new[name]

    def handle_attached_sents(self):
        self.done_conjuncts = {}
        self.done_entail = {}
        ins = get_standard_form(**{})
        ins.from_premise(self)
        self.sent_id2sp_sent = {}
        for word, sp_sent in self.sp_sents.items():
            sp_sent.kind = 'premise'
            ins.sp_sent_lst = [sp_sent]
            a, b, c = ins.loop_definition()
            self.all_sents += a
            sent_id = list(b.keys())[0]
            self.sent_id2sp_sent[sent_id] = sp_sent
            self.attached_sents = merge_2dicts(self.attached_sents, b)
            self.sent_id2csent = merge_2dicts(self.sent_id2csent, c)
        return

    def handle_biconditionals(self):
        self.kind = 'premise'
        lst = list(self.attached_sents.keys())
        combos = list(combinations(lst, 2))
        for x, y in combos:
            x1 = self.attached_sents[x][x]
            y1 = self.attached_sents[y][y]
            xsub = x1[2]
            ysub = y1[2]
            xobj = x1[3]
            yobj = y1[3]
            if xsub == yobj and ysub == xobj:
                assert False
                #todo not done yet
                bsents = jsonc(self.attached_sents[x])
                self.tant = list(bsents.values())
                self.tant.append(y1)
                self.tant = gf.sort_bsents().step2b(self.tant, True)
                ins = get_attach_name()
                ins.connected_sents = self.connected_sents
                snum, varis, _ = ins.name_embed1(self)
                if snum: self.all_sents.append([snum] + varis)

        return
