import add_path
from settings import *
from general import *
from split_sentences import split_sentencescl
import general_functions as gf
from fix_parens2 import adjust_paren
import gen_dict_func as gdf


#	the code starts in the choose_sentence function, then passes the sentence
#	to the find_sentences function.  There if the paren are incorrect it will generate
#	all possible ways that the paren can be corrected for you to choose.
#	after the different possibilities are generated the code will pass the sentences into
#	the find_sentences2 function where it will pick the sentences apart into a heirarchy
#	because it has to do that anyway, but also to help you see where a mistake is made.

#	the code begins the process of finding an incorrect paren by scrolling
#	through each character in a sentence and it
#	counts the ( and ) as well as the connectives which are # → ≡ → ⟷ ⊢ ⊻ ∨
#	when it encounters a ( it adds 1 as seen in the adjust paren function
#	when it encounters a ) it substract 1
#	when it encounters a connective it puts in list1 in the adjust paren function
#	the connective, then the parentheses count followed by the index number of the connective
#	for example
#	#   & 0
#	#  & 2
#	#  ≡ 1
#	#  & 2
#	#  & 2
#	#  & 2
#	#  → 1
#	#  & 2
#	#  & 2
#	#  & 2
#	#  & 2
#	#  & 2
#	#  & 0
#	#  & 0
#	#  & 0

#	one sentence might generate the above list, though we have not included the index
#	number of the connectives.

#	we divide the connectives into two groups: singular → ⊢ ≡ ⟷ #
#	and plural: & ⊻ ∨
#	The plural connectives can appear side by side more than once in a row with same
#	paren count.  so
#	p & q & r is legal
#	but p → q → r is not legal

#	after we have generated list1 in the adjust_paren function we then pass this list
#	to the check_errors function where we check for 7 different ways the sequence
#	of connectives and parentheses can be violated.
#	the rules which these connectives break are explained by each case.
#	case 6 and case 9 are violated in the adjust_paren function.
#	for cases 1, 4, and 5 there are known patterns which require special adjustment
#	but for cases 2, 3, 6, 7, and 8 we pass the list to the get_alterable_locations
#	function. there we try every possible parentheses addition and deletion
#	within certain limitations.
#	this generates a list of sentences.  These sentences are put into the sents list
#	in the find_sentences function.  The code will loop through each sentence
#	and make another adjustment or output 1 if the sentence is correct and put
#	this sentence into the correct list.
#	The code will make a maximum of 4 attempts to fix the sentence after which
#	it will give up
#	once all correct possibilities have been ascertained the code will
#	travel into the ask_if_accept function where it will p out all possibilties
#	for you to select.
#	If no correct sentence was found then the code will travel into the
#	choose_new_sent function where you will be asked to manually delete the parens
#	yourself

#	one other important detail the ⇿ sign indicates a sentence within a sentence
#	so what stands to the right of ⇿ is an embedded sentence which must also
#	obey all of the parentheses rules


class choose_sentence:
    def main(self, sentence, word, test='check definitions'):

        '''
        test state "check definitions", tests my ability to manually add symbols on the fly
        test state "auto select"  does not ask the user to select a possibility from multiple ones
        but is testing quickly to make sure everything is running right

        '''

        self.printcase = False  # ps which ad hoc case is being used
        self.test = test
        self.orig_sentence = sentence
        self.word = word
        self.result = 'try again'
        self.minor_adjustment = False
        self.sentence = sentence
        self.main_loop_cs()
        return self.result

    def main_loop_cs(self):
        lst = gdf.break_arrows(self.sentence, self.word)
        main_sent = self.sentence
        corrected = False
        if not lst:
            if self.test == 'check definitions':
                self.result = split_sentencescl().main(self.sentence, self.word)
                return

        for e, self.sentence in en(lst):
            osentence = self.sentence
            self.main_loop_cs2()
            if self.result == 'go to next sentence':
                return
            elif self.result == 'correct paren':
                if self.test == 'check definitions':
                    lst[e] = self.sentence

            elif self.minor_adjustment:
                self.minor_adjustment = False
                if self.test == 'check definitions':
                    corrected = True
                    p("")
                    p(f'minor adjustment made to {self.word}')
                    p(f'original sentence: {osentence}')
                    p(f"new sentence {self.sentence}")
                    p("")
                    str1 = osentence.replace(osentence, self.sentence, )
                    lst[e] = str1

        if self.test == 'check definitions':
            if corrected:
                raise Exception
            self.result = split_sentencescl().main(main_sent, self.word)

    def main_loop_cs2(self):
        while self.result == 'try again':
            self.check_errors_fp().begin_cefp(self)
            if self.result == 'go to next sentence':
                return

        while True:
            self.check_syntax_errors(self)
            if self.result == 'go to next sentence':
                break

            self.result = self.find_sentences().main(self)

            if self.result == []:
                self.result = 'go to next sentence'
                break

            elif self.result == 'correct paren':
                if self.minor_adjustment:
                    class sp_sent: pass

                    setattr(sp_sent, "sentence", self.sentence)
                    self.result = ["minor adjustment", sp_sent]
                break
            else:
                self.correct = jsonc(self.result)
                self.result = []
                for lst in self.correct:
                    self.sentence = lst[0]
                    try:
                        sp_sent = split_sentencescl().main(self.sentence, self.word)
                        sp_sent.bad_paren = self.orig_sentence
                        self.result.append(sp_sent)
                    except:
                        self.result.append("0 " + self.sentence)

                if self.test == 'check definitions':
                    self.ask_if_accept()
                    if self.result == 'go to next sentence':
                        break
                    elif self.minor_adjustment:
                        break
                    else:
                        self.sentence = self.sentence.replace("|", "")
                else:
                    break

    def ask_if_accept(self):
        if len(self.result) > 1:
            return self.multiple_possibilities()
        else:
            p(f"""
            the parentheses in
    
            {self.sentence}
    
            are wrong. This will be the heirarchy of the new sentence:
    
            """)
            b = 0
            for num, sent in self.result[0].name.items():
                p(num)
                p(f"{b}  {sent}")
                p("")
                b += 1

            p("")

            str1 = input(f"""
             if you don't like this solution then
             input 99 to manually correct the sentence.
             to give up and move to the next sentence press 0 
             otherwise press 1:  """)

            if str1 == '1':
                self.minor_adjustment = True
                return
            elif str1 == '0':
                self.result = "go to next sentence"
                return
            else:
                self.result = manually_add_paren(self.result[0])
                return

    def multiple_possibilities(self):
        c = 0
        p("""there are multiple ways to fix the parentheses 
        in this sentence
                """)
        for e, tresult in enumerate(self.result):
            if type(tresult) == str and tresult.startswith("0"):
                p("this sentence could not be reduced in the split_sentences:")
                p(tresult[2:])
            else:
                c = e
                p(f"""possibility {e}:
                {tresult.sentence}
                its heirarchy is the following:
                """)

                b = 0
                for num, sent in tresult.name.items():
                    p(num)
                    p(f"{b}  {sent}")
                    p("")
                    b += 1

            p("")

        str1 = input("""
        choose the possibility you want or input
        99 to manually correct the sentence, 
        or input 50 to give up and move to the next sentence: 
        """)

        if len(str1) == 1:
            self.minor_adjustment = True
            self.result = [self.result[int(str1)]]
        elif str1 == '99':
            try:
                sp_sent = split_sentencescl().main(self.orig_sentence)
            except:
                sp_sent = self.result[c]

            self.result = manually_add_paren(sp_sent, True)
        elif str1 == '50':
            self.result = "go to next sentence"

    class check_syntax_errors:
        def __init__(self, cls):
            self.sentence = cls.sentence
            self.test = cls.test
            self.minor_adjustment = cls.minor_adjustment
            self.result = cls.result
            self.fix_spaces_in_connectives()
            self.step_two()
            cls.result = self.result
            cls.minor_adjustment = self.minor_adjustment
            cls.sentence = self.sentence

        def fix_spaces_in_connectives(self):
            self.sentence = self.sentence.replace("|", "")
            osentence = self.sentence
            for conn in all_connectives + [mini_e]:
                if "  " + conn in self.sentence:
                    self.remove_spaces("  " + conn, " " + conn)
                if conn + "  " in self.sentence:
                    self.remove_spaces(conn + "  ", conn + " ")
                if ")" + conn in self.sentence:
                    self.sentence = self.sentence.replace(")" + conn, ") " + conn)
                if conn + "(" in self.sentence:
                    self.sentence = self.sentence.replace(conn + "(", conn + " (")
                if conn + "~(" in self.sentence:
                    self.sentence = self.sentence.replace(conn + "~(", conn + " ~(")

            if osentence != self.sentence:
                print(f"""
                the spacing between the connectives is wrong, so

                {osentence} 

                was replaced with:  

                {self.sentence}""")

            self.fix_spaces_in_paren()

        def remove_spaces(self, str1, str2):
            while str1 in self.sentence:
                self.sentence = self.sentence.replace(str1, str2)

        def fix_spaces_in_paren(self):
            while "( " in self.sentence or " )" in self.sentence:
                if "( " in self.sentence:
                    self.sentence = self.sentence.replace("( ", "(")
                elif " )" in self.sentence:
                    self.sentence = self.sentence.replace(" )", ")")

        def step_two(self):
            last_kind = "oparen"
            i = 1
            # the key symbol comes first, the value symbol second
            legal_followers = {
                "oparen": ["oparen", "literal", "itilde"],
                "literal": ["literal", "cparen", "-", "itilde"],
                "-": ['literal', 'oparen'],
                "cparen": ["cparen", "conn"],
                "conn": ["oparen", "otilde"],
                "itilde": ['literal', 'oparen', "itilde"],
                "otilde": ['oparen'],
                ":": ["literal", "cparen"],
                ";": ['literal', 'cparen'],
            }

            while i < len(self.sentence[1:]):
                letter = self.sentence[i]

                if letter == "-":
                    bb = 8

                if letter not in [" ", "|"]:
                    kind = self.get_kind(letter, last_kind)
                    pred_kind = legal_followers.get(last_kind)
                    if kind not in pred_kind:
                        self.minor_adjustment = True
                        if last_kind == 'literal' and kind == 'conn':
                            i -= 1
                            self.ad_hoc1(i, ")")
                            kind = 'cparen'
                        elif last_kind == 'conn' and kind == 'literal':
                            self.ad_hoc1(i, "(")
                            kind = 'oparen'
                        elif last_kind == 'otilde' and kind == 'literal':
                            self.ad_hoc1(i, "(")
                            kind = 'oparen'

                        else:
                            self.print_snippet(i, letter)

                            if self.result == 'go to next sentence':
                                return

                    last_kind = kind
                i += 1

        @staticmethod
        def get_kind(letter, last_kind):
            dict1 = {
                "(": "oparen",
                ")": "cparen",
                "-": "-"}

            kind = dict1.get(letter)
            if kind != None:
                return kind
            if letter == '~':
                if last_kind == 'conn':
                    return "otilde"
                else:
                    return "itilde"

            if isrelat(letter) or letter.islower() or letter in non_literals:
                return "literal"
            if letter in all_connectives:
                return "conn"

        # in this case a paren is missing like so:
        # (b R c) & d Q e)
        # (b R c & (d Q e)
        def ad_hoc1(self, i, str1):
            self.sentence = add_at_i(i, self.sentence, str1)

        def get_begin_end(self, i, j):
            end = len(self.sentence) if i > len(self.sentence) - j else i + j
            begin = 0 if i < j else i - j
            return begin, end

        def print_snippet(self, i, letter):
            begin, end = self.get_begin_end(i, 10)
            print(f"""
            in 

            {self.sentence}

            the symbol {letter} is in the wrong location here:

            {self.sentence[begin: end]} 

            eliminate the incorrect
            symbol by inputting the right sentence
             or press 0 to move to the next sentence:

            """)

            if self.test == 'auto select':
                self.result = 'go to next sentence'
            else:
                self.sentence = input("sentence: ")
                if self.sentence == "0":
                    self.result = 'go to next sentence'

    class find_sentences:
        def main(self, cls):
            self.sentence = cls.sentence
            self.test = cls.test
            self.printcase = cls.printcase
            self.i = 0
            self.sents = [[self.sentence, "", 0]]
            self.already_done = [self.sentence]
            self.first = True
            self.correct = []
            self.attempts = 0

            while self.i < len(self.sents):
                if self.i > 150:
                    break

                self.sentence = self.sents[self.i][0]

                if self.meets_conditions():

                    self.with_bracket = self.sents[self.i][1]

                    self.attempts = self.sents[self.i][2] + 1

                    self.suggestions = adjust_paren().begin_ap(self)

                    # the zeroeth index must be none in order to exit the last loop
                    if not self.suggestions[0]:
                        self.correct = 'go to next sentence'
                        break

                    elif self.suggestions == 'correct paren':
                        self.correct = 'correct paren'
                        break

                    self.delete_first()

                    self.add_to_correct()

                    self.add_to_sents()

                self.i += 1

            return self.correct

        def meets_conditions(self):
            self.diff = self.sentence.count("(") - self.sentence.count(")")

            if abs(self.diff) > 1 and self.attempts == 3:
                return False

            elif self.sentence[-1] != ")":
                if not self.test:
                    p(f"in "
                      f"{self.sentence} "
                      f"the last character must be a "
                      f"closed paren")
                return False

            elif self.first or self.correct == []:
                return True

            elif self.sentence not in [x for x in self.correct[0]]:
                return True

            return False

        def delete_first(self):
            if self.suggestions[0][1] != 1 and self.first:
                del self.sents[0]
                self.i -= 1
                self.first = False

        def add_to_sents(self):
            j = 0  # todo code for case where the symbol is wrong and i fix it
            m = 0
            if self.attempts < 4:
                while j < len(self.suggestions):
                    m += 1
                    if m > 50:
                        break

                    if self.suggestions[j][0] in self.already_done:
                        del self.suggestions[j]

                    elif self.suggestions[j][1] not in [1, 0]:
                        self.suggestions[j][2] = self.attempts
                        self.sents.append(self.suggestions[j])
                        self.already_done.append(self.suggestions[j][0])
                        j += 1

        def add_to_correct(self):
            if self.suggestions == []: return
            if self.suggestions[0][1] == 1 and \
                    (self.correct == [] or self.suggestions[0][0] not in [x for x in self.correct[0]]):
                self.correct.append([self.suggestions[0][0], self.with_bracket])

                del self.suggestions[0]

    class check_errors_fp:
        def begin_cefp(self, cls):
            self.sentence = cls.sentence
            self.result = cls.result
            self.test = cls.test
            self.word = cls.word
            self.minor_adjustment = cls.minor_adjustment

            if one_sentence(self.sentence):
                diff = self.sentence.count("(") - self.sentence.count(")")
                if diff != 0:
                    p('')
                    p(f"in the definition of {self.word} you have a wrong paren")
                else:

                    if self.word == "":
                        p(f"you cannot reduce {self.sentence}")
                    else:
                        p(f"""you cannot reduce 
                        {self.sentence} in 
                        {self.word}""")
                self.result = 'go to next sentence'
            else:

                diff = self.sentence.count("(") - self.sentence.count(")")
                if abs(diff) > 2:
                    if self.test == 'auto select':
                        self.result = 'go to next sentence'
                    else:
                        self.more_3_paren()

                elif self.sentence[-1] != ")":
                    self.no_oparen(False)
                elif self.sentence[0] not in ["(", "~"]:
                    self.no_oparen(True)
                else:
                    self.result = []

            cls.result = self.result
            cls.sentence = self.sentence
            cls.minor_adjustment = self.minor_adjustment

        def more_3_paren(self):
            try:
                self.result = manually_add_paren(self.sentence)

            except:
                p(f"""
                    the sentence:

                    {self.sentence}

                    has too many wrong parentheses with difference: {diff}""")

                p(""" 
                    
                    and we could not break the sentence down.
                    you'll need to fix them manually. if you
                    wish to move on the next sentence then
                    press 0
                    """)

                self.change_very_bad_sent()

        def no_oparen(self, oparen_missing):
            self.minor_adjustment = True
            if self.test in ['auto select']:
                if not oparen_missing:
                    self.sentence += ")"

                else:
                    self.sentence = "(" + self.sentence
            else:

                if oparen_missing:
                    str2 = 'an open'
                    str3 = 'first'
                else:
                    str2 = 'a closed'
                    str3 = 'last'
                if not self.test:
                    p(f"""
    
                    in 
    
                    {self.sentence} 
    
                    the {str3} character must be {str2} parenthesis or ~ 
                    If you accept this correction
                      press 1, to move to the next sentence press 0
                      to go to the next sentence, simply input
                      a new sentence
                      """)
                if self.test:
                    str1 = "1"
                else:
                    str1 = input("input: ")
                if str1 == "1" and not oparen_missing:
                    self.sentence += ")"
                elif str1 == "1" and oparen_missing:
                    self.sentence = "(" + self.sentence
                elif str1 == '0':
                    self.result = 'go to next sentence'

        def change_very_bad_sent(self):
            while True:
                self.sentence = input("input new sentence: ")
                if self.sentence == '0':
                    self.result = None
                    break
                diff = self.sentence.count("(") - self.sentence.count(")")
                if abs(diff) < 3:
                    break
                else:
                    p("the sentence is still wrong try again or press 0")


def manually_add_paren(sp_sent, write_info=False):
    diff = sp_sent.sentence.count("(") - sp_sent.sentence.count(")")

    if write_info:
        p(f"""
                the sentence:
    
                {sp_sent.sentence}
    
                has too many wrong parentheses with difference: {diff}""")
        p(f"""
                write the sentence number followed by a space then either ) (,
                to add a paren to the sentence, and add [ ] to delete a paren 
                if more than two sentences need correcting
                then separate these by a comma.
                if you would like to delete or add more than one paren
                to one sentence then input the sentence number
                followed by (( if you would like to add two open paren,
                or ]]] if you woule like to delete 3 closed paren.
                you may only choose sentences which do not have a connective in them
                also, do not worry if the same sentence appears twice
                we have that problem covered.
                put a close brace if you want to delete a paren which exists on a single sent
                and and open brace likewise
                to move to the next sentence press 0
                """)

        p(f"""
            This is the sentence heirarchy:
            """)

        b = 0
        for num, sent in sp_sent.name.items():
            p(num)
            p(f"{b}  {sent}")
            b += 1

    list3 = []
    # str1 = "0 [, 1 ], 1 (,9 )"
    str1 = input("new parens: ")
    list1 = vgf.strip_n_split(str1, ",")
    for str2 in list1:
        list3.append(vgf.strip_n_split(str2))

    sentence = sp_sent.sentence
    replacements = []
    for list2 in list3:

        num = int(list2[0])
        action = list2[1]
        sent = list(sp_sent.name.values())[num]
        size = len(action)

        if action.startswith("("):
            new_sent = action + sent
        elif action.startswith(")"):
            new_sent = sent + action
        elif action.startswith("["):
            str1 = "(" * size
            new_sent = sent
            sent = str1 + sent
        elif action.startswith("]"):
            new_sent = sent
            str1 = ")" * size
            sent += str1
        elif action.startswith("{"):
            str1 = "(" * size
            new_sent = sent.replace(str1, "")
        elif action.startswith("}"):
            str1 = ")" * size
            new_sent = sent.replace(str1, "")

        replacements.append([sent, new_sent])

    for replacement in replacements:
        sentence = sentence.replace(replacement[0], replacement[1])

    p("")
    p("new sentence:")
    p(sentence)

    return 'go to next sentence'
