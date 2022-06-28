import add_path
from settings import *
from general import *
from random import choice, shuffle
import general_functions as gf
import dictionary.gen_dict_func as gdf
from fix_parens import choose_sentence




class make_random_bad_sentence:
    def __init__(self):
        self.skip_errors = 0
        self.accuracy = 0
        self.accurate = []
        self.random_paren = []
        self.num = 0
        self.new_def = ""
        self.correct = True
        self.failures = []
        self.correct_sents = []
        self.horts_done = False
        self.make_correct = True
        # self.correct_sents = pi.open_pickle("test_fix_paren")
        return

    def begin_mrbs(self):
        self.fix_dict()

        for self.pnum in range(1, 4):
            for k in range(0, 50):
                # print(k)
                self.word = choice(list(self.dictionary.definitions.keys()))
                self.definitions = self.dictionary.definitions[self.word]
                self.loop_definitions()

            b = int((len(self.failures) / self.num) * 100)
            print(f"{b}% error rate for level {self.pnum}")
            p(self.num)
        # pi.save_pickle(self.failures, "failures")
        # pi.save_pickle(self.correct_sents, "test_fix_paren")

    def fix_dict(self):
        self.dictionary = pi.open_pickle("classless_dict")
        self.dictionary = to.from_dict2cls(self.dictionary)

    def loop_definitions(self):
        if self.word != "0":
            for str1 in self.definitions:
                arrow_list = gdf.break_arrows(str1, self.word)
                for self.sentence in arrow_list:
                    self.sentence = self.sentence.replace("|", "")
                    self.def_guide = self.sentence

                    if self.sentence.count("(") > 3:

                        if self.skip_errors == 1:
                            self.step_one = False
                            try:
                                self.loop_sent()
                            except:
                                if not self.step_one:
                                    self.failures.append(["failed at step two", self.sentence, self.new_def, ""])
                                else:
                                    self.failures.append(["failed at step one", self.sentence, "", ""])
                        else:
                            self.loop_sent()

    def loop_sent(self):
        self.step_one = True
        self.add_bad_paren()
        self.add_bad_paren2()
        self.add_bad_paren3()
        self.num += 1
        # p(self.num)
        self.step_one = False
        try:
            self.result = choose_sentence().main(self.new_def, self.word, "auto select")
            check_accuracy(self)
            self.add2failures()
        except:
            p (f"{self.new_def} threw an error in the choose sentence class")
            self.add2failures()


    def add_bad_paren(self):
        self.oparen = []
        self.cparen = []
        for e, let in en(self.sentence):
            if let == "(":
                self.oparen.append(e)
            elif let == ")":
                self.cparen.append(e)

        shuffle(self.oparen)
        shuffle(self.cparen)
        return

    def add_bad_paren2(self):
        self.positions = []
        orig_oparen = jsonc(self.oparen)
        orig_cparen = jsonc(self.cparen)

        for x in range(self.pnum):
            b = choice([1, 2, 3, 4])
            if b == 1:
                self.positions.append(['add cparen', self.cparen.pop()])
            if b == 2:
                self.positions.append(['add oparen', self.oparen.pop()])
            if b == 3:
                self.positions.append(['del cparen', self.cparen.pop()])
            if b == 4:
                self.positions.append(['del oparen', self.oparen.pop()])

        if len(self.positions) > 1:
            self.positions = sort_by_col(self.positions, 1)

        self.random_paren.append([self.positions, orig_oparen, orig_cparen, self.def_guide])
        pi.save_pickle(self.random_paren, "random_paren")


    def add_bad_paren3(self):
        for position in reversed(self.positions):
            if position[0] == "add oparen":
                self.def_guide = add_at_i(position[1], self.def_guide, "{")
            if position[0] == "add cparen":
                self.def_guide = add_at_i(position[1], self.def_guide, "}")
            if position[0] == "del oparen":
                self.def_guide = replace_at_i(position[1], self.def_guide, "[")
            if position[0] == 'del cparen':
                self.def_guide = replace_at_i(position[1], self.def_guide, "]")

        self.new_def = self.def_guide
        self.new_def = self.new_def.replace("{", "(")
        self.new_def = self.new_def.replace("}", ")")
        self.new_def = self.new_def.replace("[", "")
        self.new_def = self.new_def.replace("]", "")
        # p (self.new_def)
        # p (self.def_guide)
        # p (self.sentence)
        return

    def add2failures(self):
        if f"{self.num} wrong" in self.accurate:
            pass
            self.failures.append(["", self.new_def, self.sentence, self.def_guide])
            pi.save_pickle(self.failures, "failures")


class study_failures(make_random_bad_sentence):
    def __init__(self):
        self.failures2 = jsonc(pi.open_pickle("failures"))
        # self.correct_sents = pi.open_pickle("test_fix_paren")
        self.info = pi.open_pickle("random_paren")
        self.accuracy = 0
        self.failures = []
        kind = 1
        self.accurate = []
        self.fixed = []
        for e, lst in en(self.failures2):
            self.new_def = lst[1]
            self.sentence = lst[2]
            self.def_guide = lst[3]
            self.make_correct = True
            print(e)
            if e != 999:
                self.num = 1
                self.result = choose_sentence().main(self.new_def, "", "check definitions2")
                check_accuracy(self)

            else:
                pass

        b = len(self.fixed) / len(self.failures2)
        p(b)

    def remove_fixed(self):
        for num in reversed(self.fixed):
            del self.failures2[num]
        pi.save_pickle(self.failures2, "failures")
        return


class test_fix_paren1:
    # 1 bad sentence, 2 good sentence
    def __init__(self, test='auto select', build_pickle=False):
        self.accurate = []
        self.test = test
        self.correct = True
        kind = 2
        self.mistake_found = False
        if build_pickle:
            wb = ef.load_workbook_read(base_dir + "excel/fix paren.xlsx")
            ws = ef.get_sheet_read(wb, "Sheet1")
            self.ws = ef.from_sheet_tpl_read(ws, 1, 5, False)
            self.build_test_dict()
            pi.save_pickle(self.test_dict, "test_fix_paren")
        elif kind == 1:
            self.test_fp = pi.open_pickle("failures")
            self.use_test_dict()
        else:
            self.test_fp = pi.open_pickle("test_fix_paren")
            self.use_test_dict()

    def build_test_dict(self):
        self.test_dict = {}
        for rw in self.ws[1:]:
            if rw[3].lower() == 'right':
                self.test_dict[rw[1]] = [rw[4], ""]
            elif rw[3].lower() == 'wrong':
                lst = self.test_dict.get(rw[1])
                assert lst != None, f"{rw[1]}"
                lst[1] = rw[4]
                self.test_dict[rw[1]] = lst

    def use_test_dict(self):
        exceptions = [503]
        for self.num, lst in self.test_fp.items():
            # p(self.num)
            if int(self.num) not in exceptions:
                vgf.print_intervals(self.num, 50)
                self.sentence = lst[0]
                self.incorrect_sent = lst[1]
                self.make_correct = False

                if self.incorrect_sent != "":
                    self.incorrect_sent = self.incorrect_sent.replace("|", "")
                    self.make_correct = True
                    self.result = choose_sentence().main(self.incorrect_sent, "", self.test)
                    check_accuracy(self)
                else:
                    self.result = choose_sentence().main(self.sentence, "", self.test)
                    check_accuracy(self)

        if len(self.accurate) == 0:
            p('you passed the fix paren test')
        else:
            for x in self.accurate:
                p(x)

        return


def check_accuracy(cls):
    if cls.result == "go to next sentence":
        cls.accurate.append(f"{cls.num} wrong")

    elif not cls.make_correct:
        if cls.result != 'correct paren':
            cls.accurate.append(f"{cls.num} wrong")

    else:


        if cls.result != 'correct paren':

            if cls.result[0] == 'minor adjustment':

                cls.result = cls.result[1:]


            cls.sentence = cls.sentence.replace("|", "")
            for tresult in cls.result:
                tresult.sentence = tresult.sentence.replace("|", "")
                if tresult.sentence.replace(" ", "") == cls.sentence.replace(" ", ""):
                    break


            else:
                cls.accurate.append(f"{cls.num} wrong")


def manual_test():
    lst = []
    lst2 = ["","(hey) $ (you)", "", ""]
    lst.append(lst2)
    lst2 = ["","hey) & (you)", "", ""]
    lst.append(lst2)
    lst2 = ["","hey) & (you", "", ""]
    lst.append(lst2)
    failures = pi.open_pickle("failures")
    lst.append(failures[0])
    pi.save_pickle(lst, 'manually_add_paren')


def fix_pickle():
    lst = pi.open_pickle("test_fix_paren")
    del lst[104]
    pi.save_pickle(lst, "test_fix_paren")


if eval(not_execute_on_import):

    args = vgf.get_arguments()
    arg1 = args[1]
    arg2 = args[2]
    if arg1 == "":
        arg1 = 'mp'
        arg2 = 'as'
        # arg2 = 'check definitions'
        # if arg2 == 'as': arg2 = 'auto select'

    if arg1 == 'mrbs':
        b = make_random_bad_sentence()
        b.begin_mrbs()
    elif arg1 == "mp":  # make pickle
        test_fix_paren1("",True)
    elif arg1 == 'te':
        test_fix_paren1(arg2)
    elif arg1 == 'sf':
        study_failures()
    elif arg1 == 'fp':
        fix_pickle()
