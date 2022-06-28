import add_path
from settings import *
from general import *
import general_functions as gf
import gen_dict_func as gdf
import print_log as pl


class pack_conjunctionscl:
    def main(self, cls, cls1):
        atts = [
            'sent_id2csent',
            'sent_id2conn',
            'iff_dct',
            'new_sent_constr',
            'detach_embed',
            'embeds2b_named',
            'ssent2num',
            'variables',
            'done_conjuncts',
            'done_entail',
            'do_not_sort',
            'sent_id2ssent',
            'sent_id2old_ssent',
            'sent_id2num2var'
        ]

        lst1 = [
            'entail_dct',
            'entail_guide',
            'embed_detach_dct',
            'inums2snums',
            'detached_varis',
            'word',
            'odef',
            'kind',
            'connected_sents',
            'word2snum',
            'arbitrary',
            'abb_word'
        ]

        vgf.copy_partial_cls(self, cls, atts)
        vgf.copy_partial_cls(self, cls1, lst1)
        self.sent_id2abb_num = {}
        self.embed_guide = {}
        self.num2var2num = {}
        skind = 'inum' if self.kind == 'premise' else 'snum'
        self.sent_id2bsent = {x: gf.strip_sentence2(y, skind)
                              for x, y in self.sent_id2csent.items()}

        self.main_loop()
        self.add_definition()
        if self.kind == 'premise':
            cls1.all_sents = self.all_sents
            cls1.attached_sents = self.attached_sents
            cls1.sent_id2csent = self.sent_id2csent

    def main_loop(self):
        b = 0
        self.last = False
        for sent_id, y in self.new_sent_constr.items():
            b += 1
            if b == len(self.new_sent_constr):
                self.last = True
            if sent_id == 'm' + l1:
                bb = 8

            if sent_id not in self.do_not_sort:
                lst2 = self.iff_dct.get(sent_id)
                if lst2:
                    self.bicond = lst2
                    lst = self.new_sent_constr.get(lst2[0])
                    lst3 = [self.sent_id2bsent[x] for x in lst2]
                    self.name_embed3(sent_id, lst, lst3)
                elif sent_id not in self.sent_id2bsent:
                    self.bicond = []
                    sub = False
                    conn = self.sent_id2conn[sent_id]
                    if conn == cj:
                        self.build_conjunction1(sent_id, y)
                    elif conn == horseshoe:
                        tpl = (y[0], y[1])
                        sent_id2 = self.done_entail.get(tpl)
                        if sent_id2 and sent_id != sent_id2:
                            sub = True
                            osent_id = sent_id
                            sent_id = sent_id2
                        else:
                            self.done_entail[tpl] = sent_id
                        self.build_bsent(y[0], y[1], "EN", sent_id)
                        if sub: self.replace_conj(osent_id, sent_id, horseshoe)
                        if sent_id in self.embeds2b_named:
                            self.name_embed3(sent_id)

    def name_embed3(self, sent_id, lst=[], lst2=[]):
        if not lst:
            lst = self.new_sent_constr.get(sent_id)
            lst2 = [self.sent_id2bsent[sent_id]]

        for x in lst:
            conn = self.sent_id2conn.get(x)
            if conn:
                lst2.append(self.sent_id2bsent[x])
                lst3 = self.new_sent_constr[x]
                for y in lst3:
                    bsent = self.sent_id2bsent[y]
                    if bsent not in lst2:
                        lst2.append(self.sent_id2bsent[y])
            else:
                bsent = self.sent_id2bsent[x]
                if bsent not in lst2:
                    lst2.append(self.sent_id2bsent[x])

        kwargs = {
            'side': lst2,
            'arbitrary': self.arbitrary,
            'word': self.word,
        }
        self.tant = gf.sort_bsents().step2b(**kwargs)
        self.name_embed4(sent_id)

    def name_embed4(self, sent_id):
        ins = get_attach_name()
        ins.embed_kind = 'name_embed'
        ins.connected_sents = self.connected_sents
        abb_num, varis, digital = ins.name_embed1(self)
        assert abb_num
        self.sent_id2abb_num[sent_id] = abb_num
        abb_digital = [abb_num] + [sent_id] + varis
        self.sent_id2bsent[sent_id] = abb_digital
        if not self.kind == 'premise':
            abb_digital2 = abb_digital[0] + "," + ".".join(abb_digital[1:])
            str1 = self.sent_id2old_ssent[sent_id]
            str2 = self.get_sent_id2new_ssent(sent_id)
            lst1 = [str1, str2, abb_digital2, digital]
            self.embed_guide[abb_num] = lst1
        if self.last and self.kind == 'premise':
            self.prepare_premise(sent_id)

    def get_sent_id2new_ssent(self, sent_id):
        if sent_id == 'j' + l1:
            bb = 8

        if self.bicond:
            str3 = self.sent_id2ssent[self.bicond[0]]
            str4 = self.sent_id2ssent[self.bicond[1]]
            lst1 = [str3, str4]
            banned = self.bicond
        else:
            lst1 = [self.sent_id2ssent[sent_id]]
            banned = [sent_id]
        for x in self.tant:
            if x[1] not in banned:
                lst1.append(self.sent_id2ssent[gf.na(x)])
        str2 = f" {cj} ".join(lst1)
        self.sent_id2ssent[sent_id] = str2
        return str2

    def prepare_premise(self, k):
        lst = self.sent_id2bsent[k]
        del lst[1]
        self.all_sents = [lst]
        self.attached_sents = {k: self.sent_id2bsent}

    def build_bsent(self, subj, obj, relation, sent_id):
        ssent = gf.build_ssent(sent_id, subj, relation, obj)
        self.sent_id2ssent[sent_id] = ssent
        subj, obj, stilde, otilde = self.cut_off_tilde(subj, obj)
        base_sent = f"(d - {stilde}b {relation} {otilde}c)"
        snum = self.ssent2num.get(base_sent)
        assert snum
        self.sent_id2bsent[sent_id] = [snum, sent_id, subj, obj]

    @staticmethod
    def by_varpos_type(bsents):
        if len(bsents[0]) > 3 and len(bsents[1]) > 3:
            if bsents[0][3] == bsents[1][2]:
                return bsents
            elif bsents[0][2] == bsents[1][3]:
                return [bsents[1], bsents[0]]
            else:
                pl.print_arb("arbitrary conjunct")
                return bsents
        else:
            pl.print_arb("arbitrary conjunct")
            return bsents

    @staticmethod
    def cut_off_tilde(subj, obj):
        stilde = ""
        otilde = ""
        if subj[0] == "~":
            stilde = "~"
            subj = subj[1:]
        if obj[0] == '~':
            otilde = "~"
            obj = obj[1:]

        return subj, obj, stilde, otilde

    def build_conjunction1(self, sent_id, lst_conj):
        sub = False
        if len(lst_conj) > 2:
            bsents = [self.sent_id2bsent[x] for x in lst_conj]
            siblings = [y for x, y in self.sent_id2bsent.items() if y not in bsents]
            kwargs = {
                'side': bsents,
                'siblings': siblings,
                'arbitrary': self.arbitrary,
                'word': self.word,
            }
            ordered = gf.sort_bsents().step2b(**kwargs)
            lst_conj = [gf.na(x) for x in ordered]
            self.build_bullet_sent(lst_conj, sent_id)
        else:
            lst_conj = self.simple_sort(lst_conj)
            tpl = tuple(lst_conj)
            sent_id2 = self.done_conjuncts.get(tpl)
            if sent_id2 and sent_id != sent_id2:
                sub = True
                osent_id = sent_id
                sent_id = sent_id2
            else:
                self.new_sent_constr[sent_id] = lst_conj
                self.done_conjuncts[tpl] = sent_id
            subj, obj = lst_conj[0], lst_conj[1]
            self.build_bsent(subj, obj, circle, sent_id)
            if sub: self.replace_conj(osent_id, sent_id, cj)

        return

    def build_bullet_sent(self, lst_conj, sent_id):
        subj = lst_conj[0]
        obj = f" {bullet} ".join(lst_conj[1:])
        bsent = [gf.bul_num, sent_id] + lst_conj
        self.sent_id2bsent[sent_id] = bsent
        _ = gf.build_ssent(sent_id, subj, bullet, obj)
        self.sent_id2ssent[sent_id] = _

    def replace_conj(self, x, y, conn):
        for dct in ['detach_embed', 'new_sent_constr', 'iff_dct']:
            item = getattr(self, dct)
            for lst in item.values():
                try:
                    b = lst.index(x)
                    lst[b] = y
                except:
                    pass

        for k, lsts in self.detach_embed.items():
            for lst in lsts:
                try:
                    b = lst.index(x)
                    lst[b] = y
                except:
                    pass

        _ = vgf.dct_replace(x, y, self.new_sent_constr)
        self.new_sent_constr = _
        _ = vgf.dct_replace(x, y, self.embeds2b_named)
        self.embeds2b_named = _
        _ = vgf.dct_replace(x, y, self.detach_embed)
        self.detach_embed = _
        _ = vgf.dct_replace(x, y, self.iff_dct)
        self.iff_dct = _
        _ = vgf.dct_replace(x, y, self.sent_id2old_ssent)
        self.sent_id2old_ssent = _
        _ = vgf.dct_replace(x, y, self.sent_id2num2var)
        self.sent_id2num2var = _

        del self.sent_id2conn[x]
        self.sent_id2conn[y] = conn

    def simple_sort(self, lst_conj):
        x = self.sent_id2bsent[lst_conj[0]][0]
        y = self.sent_id2bsent[lst_conj[1]][0]
        if y[0] == "0": y = eval("-" + y[1:])
        if x[0] == "0": x = eval("-" + x[1:])
        if float(x) < float(y):
            return lst_conj
        elif float(x) > float(y):
            return [lst_conj[1], lst_conj[0]]
        else:
            bsents = [self.sent_id2bsent[x] for x in lst_conj]
            bsents = self.by_varpos_type(bsents)
            lst_conj = [gf.na(x) for x in bsents]
            return lst_conj

    def add_definition(self):
        if self.kind == 'premise':
            return
        for x, y in self.iff_dct.items():
            sent_abb = self.sent_id2abb_num[x]
            for z in y: self.sent_id2abb_num[z] = sent_abb

        self.molecule = gf.fss([self.word2snum[self.abb_word]])
        for k in reversed(list(self.detach_embed.keys())):
            v = self.detach_embed[k]
            self.tant = [self.sent_id2bsent[x] for x in v[0]]
            self.tconsq = [self.sent_id2bsent[x] for x in v[1]]
            ant_ssent = f" {cj} ".join([self.sent_id2ssent[x] for x in v[0]])
            consq_ssent = f" {cj} ".join([self.sent_id2ssent[x] for x in v[1]])
            self.new_def_name = build_connection(ant_ssent, horseshoe, consq_ssent)
            ins = get_attach_name()
            ins.connected_sents = self.connected_sents

            if not k[0].isdigit():
                embed_num = self.sent_id2abb_num[k]
                tnum = self.sent_id2num2var[k]
                ins.embed_kind = 'detach_embed'
                # ins.var2num = self.num2var2num.get(tnum, {})
            else:
                embed_num = 0
                ins.embed_kind = 'definition'
                ins.parent_varis = []

            ins.main(self, embed_num)
            if ins.embed_kind == 'definition':
                self.num2var2num[k] = ins.var2num

        return


class get_attach_name:
    def __init__(self):
        '''
        if the conj_name is going to be used as a basis for instantiating a conditional,
        then we only need one sentence and its mirror image if that sentence is
        a biconditional combined into one.
        further, if the sentence is a definition then we do not need
        the instatiated abbreviations.

        if the conj_name is going to be detached then we need the for_conj and
        the rev_conj to be separated which will eventually be put into
        entail_dct_chain.maps[1]. the biconditional will be put into the true_sent
        list in the instantiation module with its instantiated abbreviations
        '''
        pass

    def main(self, cls, embed_num=0):
        atts = ['tant', 'tconsq', "kind",
                "entail_guide", 'word', 'connected_sents',
                'entail_dct', 'odef', 'new_def_name', 'sent_id2ssent',
                'embed_detach_dct', 'inums2snums', 'molecule']

        vgf.copy_partial_cls(self, cls, atts)
        self.chief()
        self.add2dct(embed_num)

    def chief(self):
        kwargs = {'side': self.tant,
                  'word': self.word,
                  }
        self.tant = gf.sort_bsents().step2b(**kwargs)
        snums = [gf.gdd().cut_snum(x[0]) for x in self.tant]
        if snums[0][:2] == '00':
            bb = 8

        self.filter1 = gf.fss(gf.get_sent_idx2(snums))
        self.inums2snums[self.filter1] = set(snums)
        self.ant_varis = gf.gdd().get_varis(self.tant)
        con_varis = gf.gdd().get_varis(self.tconsq)
        self.varis = self.ant_varis + con_varis
        self.var2num = gf.gdd().number_varis(self.varis)
        self.ant_varis_num = [self.var2num[x] for x in self.ant_varis]
        consq_num, _ = gf.gdd().get_consq_num(self.var2num, self.tconsq)
        self.consq_num_lst = _
        _, b = gf.gdd().get_consq_num(self.var2num, self.tant)
        self.tant_num_lst = b
        self.get_num2ssent()
        str2 = "  ".join(snums)
        str3 = ".".join(self.ant_varis_num)
        str4 = "  ".join(consq_num)
        self.digital_def = str2 + "  " + str3 + f" {horseshoe} " + str4

    def add2dct(self, embed_num):
        filter1 = self.filter1
        if self.embed_kind == 'definition':
            if self.molecule < filter1:
                fs1 = self.molecule
            else:
                fs1 = filter1

            dlst = [filter1, self.ant_varis_num, self.consq_num_lst, self.tant_num_lst]
            glst = [filter1, self.word, self.odef, self.new_def_name,
                    self.digital_def, self.num2ssent]
            self.entail_dct.setdefault(fs1, []).append(dlst)
            self.entail_guide.setdefault(fs1, []).append(glst)

        elif self.embed_kind == 'detach_embed':
            lst = [filter1, self.ant_varis_num, self.consq_num_lst,
                   self.tant_num_lst, self.num2ssent]
            self.embed_detach_dct.setdefault(embed_num, []).append(lst)

    def get_num2ssent(self):
        self.num2ssent = {}
        for lst in self.tant_num_lst + self.consq_num_lst:
            sent_id = lst[1]
            vari = vgf.get_key(self.var2num, sent_id)
            if lst[0][0] == '0':
                vari = "~" + vari
            self.num2ssent[sent_id] = self.sent_id2ssent[vari]





    def abridge_str(self, str1):
        if len(str1) > 75:
            remainder = 65
            while len(remainder) > 65:
                idx = str1[65:].rindex(" ")

    ############# from here and below the only methods that are needed are
    ######## kind and connected sents

    def name_embed1(self, cls):
        atts = ['kind', 'tant']
        vgf.copy_partial_cls(self, cls, atts)
        return self.name_embed2(self.tant)

    def name_embed2(self, lst):
        lst = self.convert2bsent(lst)
        varis, consq_num, _ = gf.gdd().step2b(lst)
        self.consq_num_lst = _
        self.resort_consq()
        self.digital_def = "  ".join(consq_num)
        if self.kind in ['triple', 'double']:
            return self.digital_def
        else:
            snum = self.number_connectives()
            return snum, varis, self.digital_def

    def convert2bsent(self, lst):
        if self.kind in ['triple', 'double']:
            return [gf.strip_sentence2(x, 'snum') for x in lst]
        else:
            return lst

    def resort_consq(self):
        embeds = [x for x in self.consq_num_lst if x[0][-2:] == '.9']
        non_embeds = [x for x in self.consq_num_lst if x[0][-2:] != '.9']
        self.consq_num_lst = [x for x in non_embeds + embeds]

    def number_connectives(self):
        snum = self.connected_sents.get(self.digital_def)
        if not snum and self.kind != 'premise':
            # p ('failed')
            snum = str(len(self.connected_sents) + 1) + ".9"
            self.connected_sents[self.digital_def] = snum
        elif self.kind == 'premise' and not snum:
            return 0

        return snum
