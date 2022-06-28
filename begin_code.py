import add_path
from sentences.main_loop import get_result
from general import *
from other.time_functions import time_functionscl

# 181 involves determining the antecedents of pronouns which we're
# not doing now, so it's wrong


class begin_codecl:
    def __init__(self, arg1 = "", arg4 = "", arg5 = ""):
        lst = vgf.get_arguments()
        if arg1 == 'te':
            self.arg1 = 'unt'
            self.arg2 = 0
            self.arg3 = 0
            self.arg4 = 'no'
            self.arg5 = ""
        elif len(lst) > 1:
            self.arg1 = lst[1]
            self.arg2 = lst[2]
            self.arg3 = lst[3]
            self.arg4 = lst[4]
            self.arg5 = lst[5]
        else:
            self.arg1 = "unt" # 241
            self.arg2 = 0
            self.arg3 = 0
            self.arg4 = "no"
            self.arg5 = ""

        self.prepare_main_loop()

    def prepare_main_loop(self):
        # gf.skip_errors = False
        # gf.print_kind = self.arg4
        # gf.test_type = self.arg1


        if self.arg1 == 'sc':  # search category
            # gf.cat_sought = float(self.arg5)
            self.cat_sought = float(self.arg5)

        self.claims = pi.open_pickle("claims")
        self.get_order()

        if self.arg5 == 'tf':
            get_result(self)
            return
        else:
            output = get_result(self)

        if self.arg5 not in ['dnt', 'tf']: # do not test, do not pickle
            if self.arg1 in ['nu']:  # no universals
                testn.prepare_nr(output, "correct_version")
            elif self.arg1 in ['un']:
                testn.prepare_nr(output, "universals")
            elif self.arg1 in ['nut']:
                testn.test_nr_child(output, "")
            elif self.arg1 in ['unt']:
                testn.test_nr_child(output, "universals")
            elif self.arg1 == 'nutz':
                testn.prepare_nr(output, "scope")
            elif self.arg1 == 'nuts':
                testn.test_nr_child(output, "scope")


    def get_order(self):
        if not self.arg2 and not self.arg3: self.arg4 = "no"
        start = 0 if not self.arg2 else int(self.arg2)
        stop = len(self.claims) if not self.arg3 or self.arg3 == '0' else int(self.arg3)
        self.order = [x for x in range(start, stop)]

if eval(not_execute_on_import):
    kind = 1
    if kind == 1:
        begin_codecl()
    else:
        time_functionscl("begin_codecl('dnt', 'no', 'tf')", True)

'''
blank prints just arguments,
ai prints all info
no prints nothing
non will print only the numbers
os means only scope [of universal]
ud prints the total sent list at the end of
the uninstantiable definitions
eu prints the info from the eliminate universals
if prints the abb total sent after detach inferences
'''