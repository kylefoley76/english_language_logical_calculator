from settings import *
from get_definitions import base_dclass
from general import *

class fill_relata(base_dclass):
    def main(self, dictionary):
        base_dclass.__init__(self)
        self.open_ex_pkl("relata")
        self.open_ex_pkl("ontology")
        self.pos = dictionary.pos
        self.rel_abbrev = dictionary.rel_abbrev
        self.base_word_di = dictionary.base_word_di
        self.groups = {}
        self.word = ""
        self.subject = ""
        self.object = ""
        self.object2 = ""
        self.object3 = ""
        self.object4 = ""
        self.all_relata = set()
        self.main_loop()
        dictionary.groups = self.groups
        dictionary.ontology = self.ontology
        dictionary.all_relata = self.all_relata
        return self.build_ontologycl().main(dictionary)


    def main_loop(self):
        f = 0
        for lst in self.relata[2:]:
            self.word = vgf.get_key(self.base_word_di, lst[3])
            if self.word == None:
                p(f"{lst[3]} is misspelled in the fill_relata class")
            else:
                self.word = self.rel_abbrev.get(self.word, self.word)
                self.tpos = self.pos.get(self.word)
                if self.check_errors():
                    f += 1
                    self.get_objects(lst)
                    self.fill_group()
                else:
                    p(self.word)


    def check_errors(self):
        if self.word == None:
            p(f"{self.word} is misspelled in the fill_relata class")
            return False
        if self.tpos == None:
            p(f"{self.word} is misspelled in the fill_relata class")
            return False
        return True

    def get_objects(self, lst):
        objects = ['subject', 'object', 'object2', 'object3', 'object4', 'object5']
        for str1, obj in zip(lst[5:], objects): setattr(self, obj, str1)

    def fill_group(self):
        if isrelat(self.word):
            self.fill_group2(self.word + "s", self.subject)
            self.fill_group2(self.word + "o", self.object)
            self.fill_group2(self.word + "b", self.object2)
            self.fill_group2(self.word + "c", self.object3)
            self.fill_group2(self.word + "d", self.object4)
        else:
            self.fill_group2(self.word, self.subject)

    def fill_group2(self, word, str1):
        if str1 == None: return
        if "," in str1:
            st = set(str1.split(","))
            st = set([x.strip() for x in st])
            self.check_errors2(st)
            self.groups.update({word: st})
            self.all_relata |= st
        else:
            if self.pos.get(str1) == None:
                p(f"the relata {str1} for word {self.word} is misspelled")

            self.groups.update({word: str1})
            self.all_relata.add(str1)

    def check_errors2(self, st):
        for x in list(st):
            if self.pos.get(x) == None:
                p(f"the relata {x} for word {self.word} is misspelled")

    class build_ontologycl:
        def main(self, dictionary):
            self.pos = dictionary.pos
            self.ws = dictionary.ontology
            self.groups = dictionary.groups
            self.all_relata = dictionary.all_relata
            self.forward_onto = []
            self.excl_class = {}
            self.reverse_dict = {}
            self.cond_properties = {}
            self.branched_concepts = []
            self.branched_ontology = []
            self.reverse_dict2 = {}
            self.main_loop()
            self.check_ontology()
            self.trim(dictionary)
            dictionary.forward_onto = self.forward_onto
            dictionary.excl_class = self.excl_class
            return dictionary

        def main_loop(self):
            self.step_one()
            self.step_two()
            self.step_three()
            self.get_exclu_class()
            self.get_branched_classes()
            self.get_branched_classes2()
            self.expand_forward_ontology()


        def step_three(self):
            c = set()
            c.add("thing")
            self.reverse_dict2.update({"thing": c})
            self.reverse_dict3 = {}
            for k, v in self.cond_properties.items():
                set1 = {v}
                new_class = v
                set1.add(k)
                while True:
                    new_class = self.cond_properties.get(new_class)
                    if new_class == None:
                        break
                    set1.add(new_class)
                self.reverse_dict3.update({k: set1})

        def step_two(self):
            for k, v in self.reverse_dict.items():
                set1 = {v}
                new_class = v
                set1.add(k)
                list5 = [k]
                while new_class != 'thing':
                    new_class = self.reverse_dict.get(new_class)
                    assert new_class != None, (f"you misspelled {v} in your ontology")
                    set1.add(new_class)
                    list5.append(new_class)
                self.reverse_dict2.update({k: set1})

        def get_start(self):
            for e, defin in en(self.ws):
                if defin[1] != None and defin[1].startswith('thing'):
                    return e

        def step_one(self):
            start = self.get_start()
            for lst in self.ws[start:]:
                defin = lst[1]
                branch = False
                if jdisj in defin:
                    defin = defin.replace(jdisj, xorr)
                if conditional in defin:
                    list4 = defin.split(conditional)
                    branch = True
                    list2 = [list4[1], list4[0]]
                else:
                    list2 = defin.split(iff)

                if xorr in list2[1]:
                    list3 = list2[1].split(xorr)
                    list3 = [x.strip() for x in list3]

                    if branch or list2[0].strip() in self.branched_concepts:
                        for str1 in list3:
                            if str1 not in self.reverse_dict.keys():
                                self.branched_concepts.append(str1)
                            self.cond_properties.update({str1: list2[0].strip()})
                        self.branched_ontology.append([list2[0].strip(), set(list3)])

                    else:
                        for str1 in list3: self.reverse_dict.update({str1: list2[0].strip()})
                        self.forward_onto.append([list2[0].strip(), set(list3)])

        def get_branched_classes(self):
            self.branched = []
            self.branched_dict = {}
            for key, value in self.reverse_dict3.items():
                self.groups.update({key: key})
                if key not in self.reverse_dict2.keys():
                    self.branched.append(key)
                    for concept in value:
                        if concept in self.reverse_dict2.keys():
                            self.branched_dict.update({key: concept})
                            break

        def get_branched_classes2(self):
            possibilities = [self.branched, self.reverse_dict2.keys()]
            possibilities = [i for i in product(*possibilities)]
            for possibility in possibilities:
                if possibility[0] == possibility[1]:
                    pass
                else:
                    str1 = possibility[0] + "." + possibility[1]
                    str2 = possibility[1] + "." + possibility[0]
                    tv = self.excl_class.get(str1)
                    if str1 == 'male.female':
                        bb = 8

                    tv2 = self.excl_class.get(str2)

                    if tv == None:
                        parent = self.branched_dict.get(possibility[0])
                        if parent == possibility[1]:
                            tv = 'necessary'
                        else:
                            str3 = parent + "." + possibility[1]
                            tv = self.excl_class.get(str3)
                            assert tv != None
                            str4 = possibility[1] + "." + parent

                        if tv == 'necessary':
                            self.excl_class.update({str1: 'necessary'})
                            self.excl_class.update({str2: 'possible'})
                        elif tv == 'impossible':
                            self.excl_class.update({str1: 'impossible'})
                            self.excl_class.update({str2: 'impossible'})
                        else:
                            self.excl_class.update({str1: 'possible'})
                            self.excl_class.update({str2: tv2})

        def expand_forward_ontology(self):
            new_dict = {}
            for lst in self.forward_onto[1:]:
                new_dict.update({lst[0]: list(lst[1])})
            newer_dict = {}
            for k, children in new_dict.items():
                j = 0
                while j < len(children):
                    group = children[j]
                    new_child = new_dict.get(group)
                    if new_child != None:
                        children += new_child
                    j += 1
                newer_dict.update({k: set(children)})

            self.forward_onto = newer_dict

        def in_same_set(self, x, k, tdict):
            for lst in tdict:
                if x in lst[1] and k in lst[1]:
                    return True
            return False

        def get_exclu_class(self):
            excl_class = self.get_mut_excl_cls(self.reverse_dict2, self.forward_onto)
            excl_class2 = self.get_mut_excl_cls(self.reverse_dict3, self.branched_ontology)
            self.excl_class = {**excl_class, **excl_class2}

        def get_mut_excl_cls(self, rdict, tdict):
            excl_class = {}
            combos = combinations(rdict.items(), 2)
            for combo in combos:
                pair1 = combo[1][0] + "." + combo[0][0]
                pair2 = combo[0][0] + "." + combo[1][0]
                if pair2 == 'sexless.person' or pair2 == 'person.sexless':
                    bb = 8

                if self.in_same_set(combo[0][0], combo[1][0], tdict):
                    excl_class.update({pair1: "impossible"})
                    excl_class.update({pair2: "impossible"})
                else:
                    vname = combo[0][0]
                    yname = combo[1][0]
                    v = combo[0][1]
                    y = combo[1][1]
                    if v - y != set() and y - v != set():
                        sym_diff = v ^ y
                        for lst in tdict:
                            set2 = lst[1]
                            if len(list(set2 & sym_diff)) > 1:
                                excl_class.update({pair1: "impossible"})
                                excl_class.update({pair2: "impossible"})
                                break
                        else:
                            excl_class.update({pair1: "possible"})
                            excl_class.update({pair2: "possible"})

                    else:
                        possible = False
                        if len(v & y) == len(v):
                            possible = True
                            pair1 = vname + "." + yname
                            pair2 = yname + "." + vname
                        else:
                            pair2 = vname + "." + yname
                            pair1 = yname + "." + vname

                        if possible:
                            excl_class.update({pair1: "possible"})
                            excl_class.update({pair2: "necessary"})
                        else:
                            excl_class.update({pair1: "possible"})
                            excl_class.update({pair2: "necessary"})

            return excl_class

        def check_ontology(self):
            self.for_error_check = set(self.reverse_dict2.keys()) | set(self.branched_concepts)
            for k in self.reverse_dict2.keys(): self.groups.update({k: k})
            b = len(self.reverse_dict2.keys())
            p(f"{b} categories")
            all_words = set(self.pos.keys())
            mispelled_ontology = self.for_error_check - all_words
            for word in list(mispelled_ontology):
                p(f"the word {word} in your ontology is mispelled")
            relata_not_in_ont = self.all_relata - self.for_error_check
            for word in list(relata_not_in_ont):
                p(f"the word {word} is in your relata but not in your ontology")

        @staticmethod
        def trim(dictionary):
            for x in ['all_relata', 'ontology', 'base_word_di']:
                delattr(dictionary, x)