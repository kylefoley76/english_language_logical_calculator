from settings import *
import general_functions as gf
from general import *
from split_sentences import split_sentencescl


class translate_abbreviationscl:
    def __init__(self, output, reducts, kind=""):
        self.map_var = output.map_var
        self.variables = output.variables
        self.reducts = reducts
        self.kind = kind
        self.lbicond = output.lbicond
        self.abbreviations = output.abbreviations
        self.word = output.word
        self.tvalue = output.tvalue
        self.dictionary = output.dictionary
        self.rn_sent = ""
        self.main_loop_ta()

    def main_loop_ta(self):
        self.change_constants()

        for m, self.reduct in enumerate(self.reducts):
            self.sentences = self.reduct.sentences
            self.greek = self.reduct.greek
            self.greek2 = self.greek
            self.substitute_ta()
            self.implmnt_trans()

        self.replace_greek()

        return

    def substitute_ta(self):
        for name, sent in self.sentences.items():
            if iscyrillic(sent.name):
                pass
            elif sent.word_dict["relat"] == "R" and self.kind == "transform_def":
                pass
            else:
                ogreek = sent.greek
                for var_name, ovar in sent.vars.items():
                    nvar = self.map_var.get(ovar)
                    if nvar != None:
                        sent.word_dict[var_name] = nvar
                    elif ovar in self.variables:
                        self.variables.remove(ovar)
                        self.map_var.update({ovar: ovar})
                    else:
                        sent.word_dict[var_name] = self.variables.pop(0)
                        self.map_var.update({ovar: sent.word_dict[var_name]})

                self.adjust_tvalue(sent, name)
                # gf.build_stan_sent(sent)
                self.greek = self.greek.replace(ogreek, sent.name)

        return

    def implmnt_trans(self):
        if self.translations_made():
            self.rn_sent = self.build_trans_sent()
            self.map_var = {}

    def adjust_tvalue(self, sent, name):
        if self.kind == "replace_def" and \
                sent.relat == "R" and \
                name != "1.1":
            sent.tvalue = self.tvalue

    def change_constants(self):
        if self.kind == "":
            self.tconstants = self.dictionary.def_constants.get(self.word, {})
            for k, v in self.tconstants.items():
                new_var = vgf.get_key(self.abbreviations, v)
                if new_var != None:
                    self.map_var.update({k: new_var})
                else:
                    old_value = v
                    if k not in self.variables:
                        v = self.variables[0]
                        del self.variables[0]
                        self.map_var.update({k: v})
                        self.abbreviations.update({v: old_value})
                    else:
                        self.variables.remove(k)
                        self.map_var.update({k: k})
                        self.abbreviations.update({k: old_value})

        return

    def translations_made(self):
        for k, v in self.map_var.items():
            if k != v:
                return True
        return False

    def build_trans_sent(self):
        list1 = []
        lst = [x for x in self.map_var.values()]
        st = set(x for x in self.map_var.values())
        if len(lst) != len(st):
            p("different variables are being instantiated by the same object")
            raise Exception

        for k, v in self.map_var.items():
            if k != v:
                str1 = "(" + k + idd + v + ")"
                list1.append(str1)

        return " ".join(list1)

    def replace_greek(self):
        for sent in self.sentences.values():
            if iscyrillic(sent.name):
                self.greek = self.greek.replace(sent.greek, sent.name)
        bgreek = self.reduct.sentences["1.1"].greek
        self.final_sent = self.greek.replace(bgreek, self.lbicond)
        self.adjective_category()
        self.sp_sent = split_sentencescl().main(self.final_sent)
        return

    def adjective_category(self):
        if hasattr(self.reducts[0], 'adj_cat') and self.reducts[0].adj_cat:
            for num, csent in self.sentences.items():
                if num != "1.1" and csent.relat == 'R':
                    obj = self.reducts[0].adj_cat
                    subj = csent.vars["subj"]
                    new_sent = "(" + subj + " I " + obj + ")"
                    old_sent = csent.name
                    new_sent = "(" + old_sent + f" {cj} " + new_sent + ")"
                    self.final_sent = self.final_sent.replace(old_sent, new_sent)
                    break
