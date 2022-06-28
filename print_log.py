p = print
en = enumerate
import pprint as pp
# import general_functions as gf

print_on = False

def print_arb(str1):
    if print_on:
        p ("")
        p (str1)
        p ("")




def print_arrow(lst, on=False):
    if on and len(lst[0] + lst[1]) < 20:
        p ('valid arrows:')
        p ('')
        for ssent in lst[0]:
            p ('')
            p (ssent)
        p ('')
        p ('invalid arrows:')
        for ssent in lst[1]:
            p ('')
            p (ssent)

def print_instantiatecl(obj, lst, on = 0):
    if obj == 'success' and on == 1:
        p ('success')

    elif on == 1:
        for x in lst:
            p (x)

    else:
        lst.append(obj)



def print_sent_types(cls):
    if cls.print_on:
        found = False
        for csent in cls.sentences.values():
            if len(csent.small_type) > 1:
                found = True

        if found:

            p('')
            p(cls.word)
            lst = cls.sentence.split("|")
            pp(lst)

            for csent in cls.sentences.values():

                p(csent.name)
                if cls.csent.large_type:
                    p(csent.large_type)
                    p(csent.small_type)
                else:
                    p(csent.small_type)



def print_eu(cls, meth, *args):
    if gf.print_kind == 'eu':
        p("")
        if meth == 'get_main_words':
            p(f"new definiendum: {cls.word}")
            p(f"concepts: {cls.concepts}")
            p(f"qrelat: {cls.qrelat}")
            p(f"determiner location: {cls.to_be_deleted}")
            p(f"words before deletion: {cls.sent_cls.word_list}")
        elif meth == 'delete_and_replace':
            p(f"words after deletion: {cls.sent_cls.word_list}")

        elif meth == "build_rclasses":
            p('definition after rclass replacement')
            p(cls.reduct.greek)
            p(cls.reduct.greekp)
        elif meth == 'get_ant_con':
            p("antecedent categories:")
            for lst in cls.ant.word_2_cat:
                p(lst)
            p("")
            p("consequent categories:")
            for lst in cls.con.word_2_cat:
                p(lst)
        elif meth == 'con_to_ins':
            p("from concepts to instances:")
            for x, y in cls.con_ins_map.items():
                p(f"{x}  {y}")
        elif meth == 'category_sort':
            side = 'antecedent' if args[1] == 0 else "consequent"
            p(f"{side} categories: {args[0].categories}")
        elif meth == "replace_var_def":
            p('definition after var replacement:')
            p(cls.reduct.greek)
            p(cls.reduct.greekp)

        return


def print_nums(num, bool1 = False):
    if gf.print_kind != 'no':
        p("")
        p("")
        p("")
        p(num)
    if bool1:
        p("")
        p("")
        p("")
        p(num)


def print_abb_inferences(lst):
    if gf.print_kind == 'if':
        p("")
        for x in lst:
            str1 = f"{x[0]} {x[3]}{x[2]}"
            str2 = f"{x[4]} {x[5]},{x[6]}"

            if len(str1) + len(str2) < 75:
                b = 65 - len(str1)
                str3 = " " * b
                p(f"{str1}{str3}{str2}")
            else:
                lst2 = x[2].split("|")
                for e, y in en(lst2):
                    if e == 0:
                        str1 = f"{x[0]} {y}{x[3]}"
                        str2 = f"{x[4]} {x[5]},{x[6]}"
                        b = 65 - len(str1)
                        str3 = " " * b
                        p(f"{str1}{str3}{str2}")
                    else:
                        c = len(str(x[0]))
                        str4 = c * " "
                        p (f"{str4} {y}")

        p("")


def tsent_print(cls, idx=0):
    if gf.print_kind[:2] == 'ud':

        p("")
        for e, lst in en(cls.inf.total_sent[idx:]):
            f = e + idx
            p(f"{f} {lst[1]}")
        p('')
        if gf.print_kind == "ai":
            for e, lst in en(cls.inf.total_sent):
                f = e + idx
                p(f"{f} {lst[4]}")


def print_some_sent_info(cls):
    if gf.print_kind == 'ai':
        for k, v in cls.sent_dict.items():
            p(k)
            p("")
            for w, pos in zip(v.word_2_cat, v.pos_lst):
                p(f"{w[0]}  {w[1]}  {pos}")
            p("")

        p("""
        now numbering clauses
        """)
        for k, v in cls.sent_dict.items():
            try:
                p(k)
                p("")
                for w, cn in zip(v.word_list, v.clnums):
                    p(f"{w}  {cn}")

                p("")
            except:
                pass


class print_total_sent:
    def __init__(self, total_sent, print_kind):

        self.total_sent = total_sent

        self.largest_rule = 1

        for e, lst in en(self.total_sent):
            self.rule = lst[4]
            if lst[5] == "id":
                pass
            elif self.rule != "" and lst[5] != "":
                list1 = [str(x) for x in range(5, 9) if x != ""]
                self.rule = " " + ",".join(list1)
                if len(self.rule) > self.largest_rule:
                    self.largest_rule = len(self.rule)

                self.total_sent[e] = self.rule

        for lst in total_sent:
            self.num_str = lst[0]
            if lst[1].startswith('name sent'):
                print("")
                if lst[1] == 'name sent start':
                    self.name_sent_now = True
                elif lst[1] == 'name sent end':
                    self.name_sent_now = False

            else:

                size_num = 5 - len(str(lst[0]))
                self.space1 = " " * size_num
                self.sent_type = ""
                if lst[5] == 'id':
                    self.sent_type = 'sent id'
                elif lst[5] == 'natural':
                    self.sent_type = 'natural'
                self.word_str = lst[3] + lst[1]
                self.space_sentences()

    def space_sentences(self):
        if self.name_sent:
            print(self.word_str)
        else:
            third_column = self.largest_rule + 4
            max_size = 75 - third_column
            j = 0
            k = 0
            if " ," in self.word_str: self.word_str = self.word_str.replace(" ,", ",")
            five_spaces = " " * 5
            # the self.word_str always starts at position 5, there is always
            # 3 spaces between the rule and the self.word_str

            while 5 + third_column + len(self.word_str) > 75:
                k += 1
                if k > 10: raise Exception("printer caught in infinite loop")
                location = closest_to_max_size(self.word_str, max_size - 5, self.sent_type)
                remainder = self.word_str[location:]
                self.word_str = self.word_str[:location]

                if j == 0:
                    space2 = 75 - (4 + len(self.word_str) + self.largest_rule)
                    space2 = " " * space2
                    print(self.num_str + self.space1 + self.word_str + space2 + self.rule)
                else:
                    print(five_spaces + self.word_str)
                j += 1
                self.word_str = remainder
            else:
                if all(x in ["", " "] for x in self.word_str) and j > 0:
                    pass
                elif j > 0:
                    print(five_spaces + self.word_str)
                else:
                    space2 = 75 - (4 + len(self.word_str) + self.largest_rule)
                    space2 = " " * space2
                    print(self.num_str + self.space1 + self.word_str + space2 + self.rule)

        return

    def closest_to_max_size(word_str, max_size, sent_type):
        if sent_type == 'sent id' and len(word_str) < max_size:
            for idx in range(max_size, 0, -1):
                if word_str[idx] == ")":
                    return idx
        elif one_sentence(word_str[:max_size]):
            for idx in range(max_size, 0, -1):
                if word_str[idx] in " ":
                    return idx
        elif word_str.startswith("RELEVANT"):
            return 24

        else:
            for idx in range(max_size, 30, -1):
                if word_str[idx] in all_connectives:
                    return idx
            else:
                if word_str[30:max_size].count(")") < 2:
                    for idx in range(max_size, 0, -1):
                        if word_str[idx] in " ":
                            return idx
                else:
                    raise Exception
