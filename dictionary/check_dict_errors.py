import add_path
from settings import *
from general import *
from get_definitions import base_dclass
import general_functions as gf


class get_plurals(base_dclass):
    def main(self, dictionary):
        base_dclass.__init__(self)
        self.open_ex_pkl("plurals")
        self.pos = dictionary.pos
        self.plurals_di = {}
        self.non_am_plurals = set()
        self.new_nouns = set(x for x, y in self.pos.items() if y[0] == 'n' and y[:2] != 'np')
        self.no_plural = set()
        self.singulars = set()

        self.main_loop()

        attributes, methods = vgf.get_atts_meths(self)
        pi.save_pickle([attributes, methods], "plural_atts")

        dictionary.plurals_di = self.plurals_di
        dictionary.non_am_plurals = self.non_am_plurals

        return dictionary

    def main_loop(self):
        for lst in self.plurals[2:]:
            plural = lst[1]
            singular = lst[2]
            self.singulars.add(singular)
            special = float_x_int(lst[3])

            if plural == singular:
                self.pos[plural] = 'nqzz'

            elif singular != None:
                self.plurals_di[plural] = singular
                self.pos[plural] = 'npnp'
            else:
                self.no_plural.add(plural)
            if special != None:
                self.non_am_plurals.add(plural[:-1])

    def check_errors(self):
        pl_sh_nouns = set(self.plurals_di.keys()).union(self.no_plural)
        pl_sh_nouns = self.singulars.union(pl_sh_nouns)
        set1 = self.new_nouns - pl_sh_nouns

        if len(set1) > 0:
            p(f"""
            the following are in the new sheet but not
            in the plural sheet
            {set1}
            """)
        else:
            p('every noun in the new sheet is also in the plural sheet')


class other_dict_operations:
    def main(self, dictionary):
        self.pos = dictionary.pos
        self.new = dictionary.new
        self.total_pos = dictionary.total_pos
        self.negated_det = {}
        self.am_pos = {}
        self.pos_categories = {}

        self.add_apostrophe()
        self.negated_determiners()
        self.pkl_determiners()
        self.get_am_pos_dict()
        self.categorize_pos()
        self.get_compound_words().main(dictionary)
        dictionary.pos = self.pos
        dictionary.negated_det = self.negated_det
        dictionary.pos_categories = self.pos_categories
        dictionary.am_pos = self.am_pos
        self.check_dict_errorscl().main(dictionary)

        return dictionary

    def add_apostrophe(self):
        dict1 = {}
        for x, y in self.pos.items():
            if y[:2] == 'na':
                dict1.update({x + "'s": 'nnnn'})
            elif y[:2] == 'np':
                dict1.update({x + "'s": 'nlnl'})
            elif y[:2] == 'ns':
                dict1.update({x + "'s": 'nono'})

        self.pos = merge_2dicts(self.pos, dict1)

    def negated_determiners(self):
        start = gf.findposinmd("Negated Determiners", self.new, xlcol("f"), 40)
        stop = gf.findposinmd(None, self.new, xlcol("f"), start + 2)

        for rw in range(start + 2, stop):
            defin = self.new[rw][xlcol("f")]
            word = self.new[rw][xlcol("d")]
            self.negated_det[word] = defin

        self.negated_determiners2()

    def negated_determiners2(self):
        for k, v in self.negated_det.items():
            if v.count("(") == 2:
                idx = v.index(iff)
                lst = v[idx + 1:].split()
                for x in lst:
                    if len(x) > 1 and "(" not in x:
                        self.negated_det[k] = [v, x]
                        break
            else:
                self.negated_det[k] = [v, 0]
        pi.save_pickle(self.negated_det, "negated_det")

    def pkl_determiners(self):
        list1 = []
        for k, v in self.pos.items():
            if v[0] == 'd':
                list1.append(k)
        pi.save_pickle(list1, 'determiners')

    def categorize_pos(self):
        dict1 = {}
        dict1["nouns"] = set(x for x in self.total_pos if x[0] == 'n')
        dict1["pronouns"] = set(x for x in self.total_pos if x[0] == 'p')
        dict1["relations"] = set(x for x in self.total_pos if x[0] == 'r')
        self.pos_categories = dict1

    def get_am_pos_dict(self):
        st1 = set()
        for x in self.pos.values():
            if x[0] == 'y':
                st1.add(x)

        for tps in st1:
            tpos = tps[1:]
            set2 = set()
            for i in range(0, len(tpos) - 1, 2):
                xpos = tpos[i: i + 2]
                xpos = xpos[0] if xpos[1] == 'z' else xpos
                set2.add(xpos)

            self.am_pos[tps] = set2

    class get_compound_words:
        def main(self, dictionary):
            self.compound_words = {}
            lst1 = ["doubles", "triples", 'quadruples',
                    'quintuples', 'sextuples']
            for x in lst1:
                self.compound_words[x] = set()

            self.main_loop(dictionary.pos)

            pi.save_pickle(self.compound_words, 'compound_words')

        def main_loop(self, pos):
            for tword in pos.keys():
                m = tword.count(" ")
                if m == 0:
                    pass
                elif m == 1:
                    self.compound_words['doubles'].add(tword)
                elif m == 2:
                    self.compound_words['triples'].add(tword)

                elif m == 3:
                    self.compound_words['quadruples'].add(tword)

                elif m == 4:
                    self.compound_words['quintuples'].add(tword)

                elif m == 5:
                    self.compound_words['sextuples'].add(tword)

                else:
                    raise Exception(f'{tword} is a septuple')

    class check_dict_errorscl:
        def main(self, dictionary):
            self.pos = dictionary.pos
            self.dec_procedure = dictionary.dec_procedure
            self.total_pos = dictionary.total_pos
            self.synonyms = dictionary.synonyms
            self.non_am_plurals = dictionary.non_am_plurals
            self.def_constants = dictionary.def_constants
            self.definitions = dictionary.definitions
            self.plurals_di = dictionary.plurals_di
            self.new = dictionary.new

            self.check_decision_pro()
            self.check_synonyms()
            self.check_superscripts()
            self.check_constant_spelling()
            self.check_nones()
            self.check_ambiguous_words()
            self.trim(dictionary)

        def check_decision_pro(self):
            missing_pos = set()
            for x, y in self.pos.items():
                if y[0] != 'y':
                    z = self.dec_procedure.get(y[2:])
                    if z == None:
                        p(f"{x} does not have a decision procedure")
                    if y[:2] not in self.total_pos:
                        missing_pos.add(y[:2])
            if missing_pos != set():
                p(f"the following pos do not appear on the dec_pro sheet:")
                p(missing_pos)

        def check_synonyms(self):
            for key, syn in self.synonyms.items():
                pos = self.pos.get(key)
                if pos[1] != 'd' and pos[0] != 'x':
                    if syn not in self.pos.keys():
                        print(f"{syn} does not have a synonym in your dictionary")

        def check_superscripts(self):
            for k, v in self.pos.items():
                tword = k
                if len(k) > 2 and k[-2] in superscripts:
                    tword = k[:-2]
                elif k[-1] in superscripts:
                    tword = k[:-1]
                if tword != k:
                    if tword in self.non_am_plurals:
                        pass

                    elif tword not in self.pos.keys():
                        p(f"{k} is not unsuperscripted")

        def check_constant_spelling(self):
            for k, v in self.def_constants.items():
                for x, y in v.items():
                    if y.startswith("now"):
                        y = 'now'

                    if y not in self.pos.keys():
                        print(f"{y} has not been defined")
                    if y in self.synonyms.keys():
                        print(f"the word {y} which appears in the definition for {k} is a synonym")

                lst = list(v.values())
                ct = counter(lst)
                for b, c in ct.items():
                    if c > 1:
                        p(f"""
                    in the definition of {k} the word {b} has two different abbreviations
                    """)

            return

        def check_nones(self):
            found = False
            if None in self.pos.keys():
                found = True
                print("pos has none in it")
                p("the three words which appear before it are: ")
                j = list(self.pos.keys()).index(None)
                for k in list(self.pos.keys())[j - 3:j]:
                    print(k)

            if None in self.definitions.keys():
                found = True
                j = list(self.definitions.keys()).index(None)
                print("definitions has none in it")
                p("the three words which appear before it are: ")
                for k in list(self.definitions.keys())[j - 3:j]:
                    print(k)

            if found: raise Exception

        def check_ambiguous_words(self):
            # this is merely to make sure that all ambiguous words
            # appear in our dictionary
            for lst in self.new:
                self.defin = lst[xlcol("f")]
                self.word = lst[xlcol("d")]

            if self.defin != None and self.defin.startswith("ambig"):
                list1 = self.defin[len("ambiguous:"):].split(",")
                list1 = [x.strip() for x in list1]
                for word in list1:
                    if word not in self.pos.keys() and \
                            word not in self.plurals_di.keys():
                        print(f"the word {word} is not in your dictionary even though it is ambiguous")

        @staticmethod
        def trim(dictionary):
            for x in ['new', 'popular', 'sort_kind', 'negated_det',
                      "non_am_plurals","total_pos", "word_to_row",
                      'verbs']:
                delattr(dictionary, x)




class build_contentscl():
    def build_contents(self, cls):
        self.new = cls.get_xlsheet(self, "new")
        self.contents = cls.get_xlsheet(self, "contents")
        self.loop_until_category_start()
        self.fill_categories()
        self.adjust_content_sheet()

    def loop_until_category_start(self):
        for self.start in range(2, 130):
            val = ef.get_from_excel(self.new, self.start, 6)
            val2 = ef.get_from_excel(self.new, self.start, 5)
            if val != None and val.startswith("Atomic Re") and val2 != None \
                    and val2 == ".":
                break

    def fill_categories(self):
        self.categories = []
        for e, lst in en(self.new[self.start:]):
            rw = e + self.start
            val = ef.get_from_excel(self.new, rw, 5)
            num = ef.get_from_excel(self.new, rw, 7)
            name = ef.get_from_excel(self.new, rw, 6)
            if val == ".":
                ef.make_bold(self.new, rw, 6)
                self.categories.append([num, name])

    def adjust_content_sheet(self):
        if len(self.categories) > self.start - 7:
            p(f"{len(self.categories)} categories)")
            p('too many categories')
        else:
            rw = 5
            for num, name in self.categories:
                ef.put_into_excel(self.new, rw, 5, num)
                ef.put_into_excel(self.contents, rw - 4, 1, num)
                ef.put_into_excel(self.contents, rw - 4, 2, name)
                ef.put_into_excel(self.new, rw, 6, name)
                ef.put_into_excel(self.new, rw, 7, 40)
                rw += 1

        self.contents.save(base_dir + "excel/dictionary2.xlsx")


class count_wordscl():
    def count_wordsfu(self, cls):
        self.num_cat = {}
        self.num_count = {}
        self.new = cls.new

        self.categories = [
            "Atomic Relations",
            "Atomic Relata",
            "Atomic Non-Literals",
            "Underivable Inference Rules",
            "Derived Inference Rules",
            "Molecular Non-Literals",
            "Axioms of Identity",
            "Hard-Coded Axioms",
            "Axioms of Instantiation",
            "Instantiable Axioms",
            "Non-Determiner Abbreviators",
            "Determiners",
            "Pronouns"]

        self.main_loop_cw()

    def main_loop_cw(self):
        start = gf.findposinmd("Atomic Relations", self.new, xlcol("f"), 20)
        assert start < 100, f"""you failed to find the start of the new sheet
        in the count words function"""

        for lst in self.new:
            defin = lst[xlcol("f")]
            word = lst[xlcol("d")]

        for lst in self.new[start:]:
            defin = lst[xlcol("f")]
            word = lst[xlcol("d")]

            if need_period and word == '.':
                pass

            if defin in self.categories and not need_period:
                need_period = False

        i = 29
        while True:
            i += 1
            defin = ws.cell(row=i, column=6).value
            if defin != None:
                defin = defin.strip()
                if defin in categories:
                    num, i = self.loop_to_period(i)
                    num_cat.update({num: defin})
                    num_count.update({num: 0})
                    if defin == 'Pronouns':
                        break

            if i > 3000:
                break

        self.stats = [num_cat, num_count]

    def print_stats(self):
        if self.print_stats2 == False: return
        basic_terms = sum(list(self.stats[1].values())[:3])
        print(f"basic terms: {basic_terms}")

        axioms = sum(list(self.stats[1].values())[7:11])
        print(f"axioms: {axioms}")

        for k, v in self.stats[0].items():
            num = self.stats[1].get(k)
            print(f"{v}: {num}")

    def count_objects(self):
        if self.sort_kind in self.stats[0].keys() and self.word != self.next_word:
            num = self.stats[1].get(self.sort_kind)
            self.stats[1][self.sort_kind] = num + 1

    def categorize_pos(self):
        dict1 = {}
        dict1["nouns"] = set(x for x in self.total_pos if x[0] == 'n')
        dict1["pronouns"] = set(x for x in self.total_pos if x[0] == 'p')
        dict1["relations"] = set(x for x in self.total_pos if x[0] == 'r')
        self.pos_categories = dict1

    def loop_to_period(self, i):
        while True:
            i += 1
            word = ws.cell(row=i, column=4).value
            kind = ws.cell(row=i, column=7).value
            if word != ".":
                return kind, i
            if i > 2000:
                raise Exception("infinite loop in collecting stats")
