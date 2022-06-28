import add_path
from settings import *
from general import *
import gen_dict_func as gdf
import xlrd
from shutil import copy2



class base_dclass:
    def __init__(self):
        self.xl_sheets = {
            "new": ("d", "k", 1, 1),
            "newer2": ("a", "k", 1, 1),
            "dec_pro": ("b", "e", 2, 1),
            "verbs": ("a", "j", 1, 1),
            "plurals": ("a", "d", 2, 1),
            "ontology": ("a", "b", 1, 1),
            "contents": ("a", "c", 1, 1),
            "relata": ("c", "k", 1, 1)}


    def get_all_pickles(self):
        for k, v in self.xl_sheets.items():
            self.open_ex_pkl(k)

    def open_ex_pkl(self, name):
        lst = pi.open_pickle("excel_dict/" + name)
        setattr(self, name, lst)

    def get_xlsheet(self, sheet):
        self.wb = ef.load_workbook(base_dir + 'excel/dictionary2.xlsx')
        self.from_excel_2_sh(sheet)

    def get_xlmsheet(self, book, sheet):
        tpl = self.xl_sheets[sheet]
        self.wb = xlrd.open_workbook(base_dir + f'excel/{book}.xlsx')
        sheet2 = self.wb.sheet_by_name(sheet)
        p(f"last row in {sheet} is {sheet2.nrows}")
        lst = ef.from_sheet_tpl_read(sheet2, tpl[3], xlcol(tpl[1]))
        setattr(self, sheet, lst)
        pi.save_pickle(lst, "excel_dict/" + sheet)


    def get_all_sheets(self):
        self.wb = ef.load_workbook(base_dir + 'excel/dictionary2.xlsx')
        for k, v in self.xl_sheets.items():
            self.from_excel_2_sh(k)

    def get_all_msheets(self):
        self.wb = xlrd.open_workbook(base_dir + f'excel/dictionary2.xlsx')
        for k, v in self.xl_sheets.items():
            self.from_excel_2_shm(k)
        return

    def from_excel_2_shm(self, sheet):
        tpl = self.xl_sheets[sheet]
        sheet2 = self.wb.sheet_by_name(sheet)
        p(f"last row in {sheet} is {sheet2.nrows}")
        lst = ef.from_sheet_tpl_read(sheet2, tpl[3], xlcol(tpl[1]))
        setattr(self, sheet, lst)
        pi.save_pickle(lst, "excel_dict/" + sheet)

    def from_excel_2_sh(self, sheet):
        tpl = self.xl_sheets[sheet]
        sheet2 = ef.get_sheet(self.wb, sheet)
        end = ef.get_last_row(sheet2, xlcol(tpl[0])) + 1
        lst = ef.from_sheet_tpl(sheet2, tpl[2], end, xlcol(tpl[1]))
        setattr(self, sheet, lst)
        pi.save_pickle(lst, "excel_dict/" + sheet)


class get_decision_pro(base_dclass):
    def __init__(self):
        base_dclass.__init__(self)
        self.open_ex_pkl("dec_pro")
        self.dec_procedure = {}
        self.double_pos = []
        self.funct_dict = {}
        self.special_cat = set()
        self.total_pos = set()
        self.word_subsets = {}
        self.main_loop()

    def main_loop(self):
        self.dec_pro_guide = {}
        found = False
        for e, lst in en(self.dec_pro[1:]):
            f = e + 1
            val2 = lst[2]
            val = lst[1]
            if val2 != None and val2.startswith("third and fourth"):
                found = True
            if not found and val != None:
                if len(val) == 1:
                    self.total_pos.add(val + "z")
                else:
                    self.total_pos.add(val)

            if found:
                val = lst[1]
                val2 = lst[2]
                val3 = float_x_int(lst[3])
                val4 = float_x_int(lst[4])


                if val4 == 1:
                    self.double_pos.append(val)
                elif val4 == 2:
                    self.special_cat.add(val3)

                if val != None:
                    if len(val) == 1:
                        val += "z"
                    self.dec_procedure.update({val: val3})
                    self.dec_pro_guide.update({val: val2})
                if val2 == None and self.dec_procedure != {}:
                    self.build_word_subsets(f)
                    break

                if val3 != None and val3 >= 0 and val3 < 99:
                    self.funct_dict.update({val3: "self." + val2 + "()"})

    def build_word_subsets(self, rw):
        rw += 2
        assert self.dec_pro[rw][2] == "word subsets"
        rw += 2
        while rw < len(self.dec_pro):
            a, b = self.dec_pro[rw][2].split(" " + conditional + " ")
            rw += 1
            self.word_subsets[a] = b

class get_pos(base_dclass):
    def main(self, cls):
        base_dclass.__init__(self)
        self.open_ex_pkl("newer2")
        b = pi.open_pickle('axioms')
        self.ax_sheet = b[0]
        self.ax_headers = b[1]
        self.new = self.newer2
        self.double_pos = cls.double_pos
        self.word_subsets = cls.word_subsets
        self.total_pos = cls.total_pos
        self.dec_procedure = cls.dec_procedure
        self.funct_dict = cls.funct_dict
        self.special_cat = cls.special_cat
        self.abbrev_relat = ""
        self.arity = {}
        self.super_di = {}
        self.base_pos = {}
        self.arity_num = {}
        self.base_word_di = {}
        self.pos = {}
        self.rel_abbrev = {}
        self.word_set_dict = {}
        self.word_to_row = {}
        self.done_pos = set()
        self.main_loop()
        self.add_atoms()
        return self

    def main_loop(self):
        for e, lst in en(self.new[5:]):
            self.rw = e + 5
            if lst[3]:
                self.tpos = lst[3]
                self.word = lst[4]
                self.base_pos[self.word] = self.tpos
                self.word_sets = float_x_int(lst[2])
                self.superscript = lst[xlcol("i")]
                self.super_di[self.word] = self.superscript
                self.abbrev_relat = lst[5]
                self.arity_num = lst[xlcol("j")]
                self.adjust_word()
                self.adjust_pos()
                self.pos[self.word] = self.tpos
                if self.abbrev_relat:
                    self.update_relations()
                else:
                    self.word_to_row[self.word] = self.rw
                self.base_word_di[self.word] = self.base_word
                self.put_into_word_sets()



    def update_relations(self):
        self.abbrev_relat = self.abbrev_relat
        self.word_to_row[self.abbrev_relat] = self.rw
        self.rel_abbrev[self.word] = self.abbrev_relat
        self.arity[self.abbrev_relat] = self.arity_num
        self.relation_errors()
        self.pos[self.abbrev_relat] = self.tpos
        self.word = self.abbrev_relat

    def adjust_word(self):
        if isinstance(self.word, int): self.word = str(self.word)
        self.word = self.word
        self.base_word = self.word
        self.nx_bsword = ""
        if self.rw < len(self.new) - 1:
            self.nx_bsword = self.new[self.rw + 1][4]
        self.handle_special_char()
        self.remove_paren()
        self.remove_comma()

    def handle_special_char(self):
        if self.word != "*":
            self.word = self.word.replace("*", "")
        if "..." in self.word:
            self.word = self.word.replace("...", elip)
        if chr(8230) in self.word:
            self.word = self.word.split(chr(8230))[0].strip()

    def remove_paren(self):
        if "(" in self.word:
            cc = self.word.index("(")
            self.word = self.word[:cc - 1]
            self.word = self.word.strip()

    def remove_comma(self):
        if "," in self.word:
            list1 = self.word.split(",")
            if list1[1].strip()[-1] == "-":
                self.word = list1[1].strip() + list1[0].strip()
            else:
                self.word = list1[1].strip() + " " + list1[0].strip()

    def adjust_pos(self):
        if self.tpos in self.double_pos:
            if len(self.tpos) == 1:
                self.tpos += "z"
            self.tpos += self.tpos
        if len(self.tpos) == 1:
            self.tpos += "zzz"
        elif len(self.tpos) == 2:
            self.tpos += "zz"
        elif len(self.tpos) > 3:
            pass
        else:
            raise Exception
        self.pos_errors2()

    def pos_errors2(self):
        if self.word in self.pos.keys():
            p(f"the word {self.word} has two definitions")

        if self.base_word == self.nx_bsword and \
                self.rw < len(self.new) - 1 and \
                self.new[self.rw + 1][3] != None:
            p(f"""the word {self.base_word} on row {self.rw}
             has its part of speech stated twice""")

        if self.superscript != None:
            if self.word[-1] not in superscripts:
                p(f"{self.word} superscript cell deleted")

        if self.word[-1] == ur and self.tpos[2] != 'r':
            p(f"{self.word} has superscript r and is not redundant")

        if self.word[-1] in superscripts and self.word[-1] not in [un, uv, ua, ur]:
            letter = superscript_dict.get(self.word[-1])
            try:
                if self.superscript == 'arbitrary' or self.tpos[2] == 'r':
                    pass
                elif letter != self.superscript[0]:
                    print(f"you forgot to superscript {self.word}")
            except:
                print(f"you forgot to superscript {self.word}")

        if self.new[self.rw - 1][4] == self.base_word:
            p(f" in {self.word} the pos cell needs to be shifted up")

        if self.word == ".":
            raise Exception(f" in row {self.rw} there is a period and a pos")

        if self.tpos == 'npoa' and "plural of" not in self.new[self.rw][xlcol("f")]:
            p(f"{self.word} has 'plural of' in definition but not npos as part of speech")

    def relation_errors(self):
        if self.tpos[0] == 'r' and self.abbrev_relat in self.pos.keys() \
                and self.abbrev_relat != self.word:
            p(f"the relation {self.abbrev_relat} has two definitions")
        if self.tpos and self.tpos[0] == 'r' and \
                self.abbrev_relat == None:
            if len(self.tpos) == 4 and self.tpos in ["ruxx", "ruxy"]:
                pass
            elif len(self.tpos) == 4 and self.tpos[2] == "s":
                pass
            elif self.word == 'is':
                pass
            elif self.tpos[2:] in ['rd', "xz"]:
                pass
            else:
                p(f"you forgot to give {self.word} an abbreviated relation")
        if self.arity_num == None:
            p(f"you forgot to state the arity of {self.abbrev_relat}")

    def put_into_word_sets(self):
        if self.word_sets != None:
            if isinstance(self.word_sets, int):
                lst = str(self.word_sets)
            else:
                lst = self.word_sets.split()
            for x in lst:
                self.word_set_dict.setdefault(self.tpos[0] + x, set()).add(self.word)

    def fill_word_subsets(self):
        if self.kind == 'old':
            for k, v in self.word_subsets.items():
                setk = self.word_set_dict.get(k)
                setv = self.word_set_dict.get(v)
                set3 = set(ujsonc(setv))
                set3 |= setk
                self.word_set_dict[v] = set3

            pi.save_pickle(self.word_set_dict, "dict_pkl/word_set_dict")

    def add_atoms(self):
        headers = self.ax_headers
        col1 = headers['const']
        col2 = headers['const name']
        rel_col = headers['relat']
        nat_col = headers['nat lang']
        for rw in self.ax_sheet[1:]:
            const = rw[col1]
            const_name = rw[col2]
            relat = rw[rel_col]
            nat_rel = rw[nat_col]
            if not relat:
                break
            if const:
                self.pos[const] = 'nszz'
                self.pos[const_name] = 'nszz'
            self.pos[relat] = 'ruzz'
            self.pos[nat_rel] = 'ruzz'
            self.rel_abbrev[nat_rel] = relat
            self.arity[relat] = 2
        self.arity["+"] = 12
        self.arity[minus] = 12
        self.arity['K3'] = 3

        return



class get_definitionscl:
    def main(self, cls):
        lst = ['base_word_di', 'pos', 'rel_abbrev', 'word_to_row',
               'total_pos', 'dec_procedure', 'funct_dict',
               'arity', 'special_cat', 'new', 'base_pos',
               'super_di']
        vgf.copy_partial_cls(self, cls, lst)
        self.circular = []
        self.def_constants = {}
        self.definitions = {}
        self.popular = {}
        self.unnamed = {}
        self.sort_kind = {}
        self.syn_def = {}
        self.done = False
        self.synonyms = {}
        self.preserve = vgf.preserve_methods(self)
        self.get_sort_kind_npop()
        self.main_loop()
        self.update_synonyms()
        vgf.trim_class(self, self.preserve)
        return self

    def main_loop(self):
        for k, v in self.word_to_row.items():
            self.word = k
            if self.word == 'moment':
                bb= 8

            self.defin = str(self.new[v][xlcol("f")])
            if v < len(self.new) - 1:
                self.next_defin = self.new[v + 1][xlcol("f")]
                self.nx_bsword = self.new[v + 1][xlcol('d')]
            self.tpos = self.pos[k]
            self.row = v
            self.base_word = self.base_word_di[k]
            if self.is_defineable():
                self.add_to_constants()
                if not self.done:
                    self.loop_def_rows()
        return



    def get_sort_kind_npop(self):
        for k, v in self.word_to_row.items():
            self.sort_kind[k] = float_x_int(self.new[v][xlcol("g")])
            self.popular[k] = float_x_int(self.new[v][xlcol("h")])
            self.sort_errors(k)

    def sort_errors(self, k):
        if self.sort_kind[k] == None:
            print(f"you forgot to give {k} a sort category")
        if self.popular[k] == None:
            print(f"you forgot to state whether {k} is popular")

    def loop_def_rows(self):
        rw = self.row
        tdefin = self.new[rw][xlcol("f")]
        definition = ""
        if not self.done:
            while self.new[rw][4] == self.base_word and "e.g." not in tdefin:
                rw += 1
                if tdefin == None: break
                if definition == "":
                    definition = tdefin
                else:
                    definition += "| " + tdefin
                if rw == len(self.new):
                    break
                tdefin = self.new[rw][xlcol("f")]

            if definition == None:
                p(f"{self.word} in row {self.rw} does not have a definition")

            if ")| (" in definition:
                definition = definition.replace(")| (", "zzz%yyy")
                lst = definition.split("%")
                lst = [x.replace("zzz", ")") for x in lst]
                self.definitions[self.word] = [x.replace("yyy", "(") for x in lst]

            else:
                self.definitions[self.word] = [definition]



    def is_defineable(self):
        list1 = ["hard", "post", "plur", "ambi"]
        if self.word == 'few':
            bb = 8

        if self.defin == None:
            return False
        elif self.sort_kind in [100, 200] or self.sort_kind == '100':
            return False
        elif "#REF" in self.defin:
            return False
        elif self.defin.startswith("circular"):
            self.defin = self.defin[len("circular: "):]
            self.circular.append(self.word)
            return True
        elif "(" not in self.defin and "=" not in self.defin:
            return False
        elif self.defin[:4] in list1:
            return False
        elif self.tpos == 'yanns':
            return False  # only individual has this
        elif self.tpos[:2] in ["rn", "nd"]:
            return False
        elif self.tpos[2:] == 'xz':
            return False
        elif self.tpos[2] == 's' or self.tpos[0] == 'g':
            return False
        else:
            return True



    def add_to_constants(self):
        dict1 = {}
        unnamed = []
        self.done = False
        bool1 = False
        word_in_def = False
        if self.word == 'some' + up:
            bb = 8

        if "=" in self.defin and "," in self.defin and ")" not in self.defin:
            self.add_to_constants2(self.defin, dict1, unnamed)
            bool1 = True
            self.row += 1

        # first line: (x) v (y), b = cosmos
        elif ")," in self.defin:
            self.defin, abbrev = gdf.divide_at_i(self.defin, self.defin.index(","))
            self.definitions.update({self.word: [self.defin.strip()]})
            self.add_to_constants2(abbrev, dict1, unnamed)
            bool1 = True
            self.done = True
            if self.word in self.defin:
                self.add_to_constants3(self.defin, dict1)
                word_in_def = True

        # first line: b.c = unnamed
        # no other words other than 'unnamed' appear in the line
        elif "=" in self.defin and ")" not in self.defin and "." in self.defin \
                and "," not in self.defin:
            self.add_to_constants4()
            bool1 = True
            self.row += 1

        # todo find out if this can be deleted
        # first: b = moment [no comma, no period]
        elif "=" in self.defin and ")" not in self.defin:
            self.add_to_constants2(self.defin, dict1, unnamed)
            bool1 = True
            self.row += 1

        elif self.tpos[:2] == 'pp':
            self.add_to_constants3(self.defin, dict1)
            word_in_def = True
            self.definitions.update({self.word: [self.defin.strip()]})
            self.done = True
            self.def_constants.update({self.word: dict1})

        # pay attention that '=' and '= ' are different strings
        if self.next_defin != None and ("=" + self.word in self.next_defin or
                                        "= " + self.word in self.next_defin) and \
                self.base_word == self.nx_bsword:
            self.add_to_constants3(self.next_defin, dict1)
            word_in_def = True
            self.def_constants.update({self.word: dict1})

        if dict1 != {}:
            self.def_constants.update({self.word: dict1})

        if bool1:
            self.constant_errors(dict1, word_in_def)

    def constant_errors(self, dict1, word_in_def):
        if self.tpos[0] in ['n', "a", "e"]:
            if self.word not in dict1.values() and \
                self.next_defin and \
                    self.word not in self.next_defin and \
                    not word_in_def:
                p(f"{self.word} does not appear in its definition")

    def add_to_constants2(self, str1, dict1, unnamed):
        list1 = str1.split(",")
        list1 = [x.strip() for x in list1]
        for str1 in list1:
            list2 = str1.split("=")
            list2 = [x.strip() for x in list2]

            if list2[1] != 'unnamed':
                dict1.update({list2[0]: list2[1]})
            else:
                if "." in list2[0]:
                    list3 = list2[0].split(".")
                    unnamed = [x.strip() for x in list3]
                else:
                    unnamed.append(list2[0])
                self.unnamed.update({self.word: unnamed})

        return

    def add_to_constants3(self, str1, dict1):
        if "=" in str1:
            b = str1.index("=")
            abb = str1[b - 2:b].replace("(", "")
            abb = abb.strip()
            dict1.update({abb: self.word})

    def add_to_constants4(self):
        lst = self.defin[:self.defin.index(" =")].split(".")
        self.unnamed.update({self.word: lst})

    def update_synonyms(self):
        for self.word, rw in self.word_to_row.items():
            self.tpos = self.pos[self.word]
            if self.tpos[2:] in ['sn', "ss"] or self.tpos[:2] == 'nd':
                definition = self.new[rw][xlcol("f")]
                str2 = definition[definition.find("=") + 1:-1]
                str2 = str2.strip()
                str1 = definition[1:definition.find("=")]
                str1 = str1.strip()
                if self.word != str1:
                    print(f"the synonym {self.word} does not appear in its definition")
                if self.tpos[0] == "r":
                    if not str2[0].isupper():
                        print(f"the synonym for {str1} needs to be a capital letter")
                    else:
                        self.rel_abbrev[str1] = str2

                self.synonyms.update({str1: str2})
                self.pos.update({str1: self.tpos})
                self.syn_def.update({str1: definition})


