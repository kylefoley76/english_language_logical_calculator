
import add_path
from general import *
import sys
from total_dictionary import build_dictionary
from test_fix_paren import test_fix_paren1, make_random_bad_sentence
from time_functions import time_functionscl
from calculate_axioms import calculate_axiomscl
from test_di_instant import test_di_instantcl

p = print


def all_testsfu(arg1):

    tests = arg1.split(",") if arg1 else []

    if not arg1 or "fp" in tests:
        test_fix_paren1()
        b = make_random_bad_sentence()
        b.begin_mrbs()

    if not arg1 or 'tin' in tests:
        try:
            test_di_instantcl(6)
        except:
            p ('bug in instantiation test')


    if not arg1 or 'cax' in tests:
        calculate_axiomscl().main(**{'test':True})

    if not arg1 or 'dig' in tests:
        try:
            build_dictionary().step2b("bd", "te", "")
        except:
            p ('you failed the build dictionary test')









args = vgf.get_arguments()
arg1 = args[1]
initial = arg1

if arg1 == "":
    arg1 = 'cax'

if arg1 != initial:
    p ('you are temporarily overriding the arguments in all tests')

if arg1 == 'tf':
    time_functionscl('all_testsfu("")')
else:
    all_testsfu(arg1)

