import add_path
from general import *
import sys
from shutil import copy2
from settings import xlcol, base_dir
from get_definitions import get_pos, get_definitionscl, base_dclass, get_decision_pro
import general_functions as gf
from build_ontology import fill_relata
from check_dict_errors import other_dict_operations, get_plurals
from time_functions import time_functionscl
from get_shifts import get_shiftscl
import digital_definition as dd
import full_reduction as fr


## check behavior of periods in relationship
##todo make error message where every constant must appear in the definition


@vgf.timer
def new_books(args):
    arg2 = args[1] if len(args) > 1 else ""
    copy2(base_dir + "pickles/half_dct.pkl", base_dir + "pickles/half_dct_old.pkl")
    copy2(base_dir + "pickles/classless_dict.pkl", base_dir + "pickles/classless_dict_old.pkl")
    copy2(base_dir + "excel/" + file_nm, base_dir + "excel/" + file_nm[:-5] + "_backup.xlsx")
    if arg2 == 'sa':  # save
        ef.save_all_books()
        ef.update_excel_screen(file_nm)
        ef.change_symbols()
        ef.save_excel_sheet(file_nm)

    if args[1] == 'nbm':
        if len(args) == 2:
            base_dclass().get_xlmsheet("dictionary2", 'newer2')
        else:
            raise Exception

    else:
        base_dclass().get_all_sheets()


def get_ssent2num(arg2):
    classless_dct = pi.open_pickle("classless_dict")
    str1 = classless_dct['word2snum'].get(arg2)
    str2 = classless_dct['ssent2num'].get(arg2)

    p(str1)
    p (str2)


def temp13():
    lst = [x for x in range(4)]
    done = set()
    current_combos = []
    added = True
    b = 0
    while added:
        for x in range(2, 4):
            combos = list(combinations(lst, x))
            for y in combos:
                if y not in done:
                    current_combos.append(y)
                    done.add(y)

        #### do stuff to the current combos here
        ### which will produce more members to be added to the list

        if not b:
            for x in range(6, 8):
                lst.append(x)

        elif b == 1:
            for x in range(9, 10):
                lst.append(x)

        elif b == 2:
            for x in range(11, 13):
                lst.append(x)
        else:
            added = False

        b += 1
        current_combos = []

    return


@vgf.timer
def print2text():
    newer2 = pi.open_pickle('excel_dict/newer2')
    file = base_dir + "excel/newer2.txt"
    vgf.fromlst2txt(newer2, file, False)
    return


def from_txt2excel(test=False):
    src2 = base_dir + "excel/newer2.txt"
    lst = to.from_txt2lst_tab_delim(src2)
    src = base_dir + "excel/dictionary2.xlsx"
    dest = base_dir + "excel/dictionary2_backup.xlsx"
    copy2(src, dest)
    pi.save_pickle(lst, 'excel_dict/newer3')
    lst = ef.change_to_none(lst)
    lst = ef.fromstr2int(lst)
    if test:
        lst2 = pi.open_pickle("excel_dict/newer2")
        if lst2 == lst:
            p('success')
        else:
            b = 0
            for x, y in zip(lst2, lst):
                for e, a in en(x):
                    if y[e] != a:
                        p(f"row {b} column {e}")
                        p(f"old {y[e]} new {a}")
                b += 1

    else:
        wb = ef.load_workbook(base_dir + "excel/dictionary2.xlsx")
        ws = ef.get_sheet(wb, 'newer3')
        ef.from_lst2sheet(ws, lst)
        wb.save(src)
        ef.open_wb('dictionary2.xlsx', base_dir + 'excel/')


@vgf.timer
def build_dictionary(**kwargs):
    """
    db - debug
    te - test
    fh - first half
    sh - second half
    pi - pickle
    fs -
    fr - full reduction
    pa - partial
    cat - categories
    er - erase ssent2num

    """
    first_half = kwargs.get("fh")
    second_half = kwargs.get("sh")
    second_half_only = kwargs.get('sho')
    partial = kwargs.get('pa')
    observe = kwargs.get('ob')
    category_table = kwargs.get('cat')
    check_circularity = kwargs.get('cc')
    full_reduction = kwargs.get('fr')
    forked = kwargs.get('forked')
    fork_num = kwargs.get('fork_num')
    kwargs['do_all'] = True if not first_half and not second_half else False

    if forked:
        start = kwargs['start']
        stop = kwargs['stop']
        dictionary = kwargs['dictionary']
        dictionary.def2sp_sent = vgf.split_dct(dictionary.def2sp_sent, start, stop)
        ins = dd.get_standard_form(**kwargs)
        ins.from_first_half(dictionary)
        ins.main()
        p(f'fork number {fork_num} done')


    elif second_half or second_half_only:
        if second_half and kwargs.get('pi') == True:
            kwargs['pi'] = False
            kwargs['fr_pickle'] = True
        ins = dd.get_standard_form(**kwargs)
        ins.from_pickle()
        if partial:
            ins.define_partial()
        else:
            ins.main()
        if second_half:
            fr.check_circularity().from_second_half(ins, **kwargs)

    elif full_reduction:
        fr.full_reductionalcl().main(**kwargs)


    elif check_circularity:
        bool1 = kwargs.get("pi")
        if bool1:
            kwargs['fr_pickle'] = True
        fr.check_circularity().from_pickle(**kwargs)

    elif category_table:
        fr.build_category_table().main(**kwargs)


    elif observe:
        dictionary = pi.open_pickle('classless_dict')
        dictionary = to.from_dict2cls(dictionary)

    else:
        dictionary = get_decision_pro()

        dictionary = get_pos().main(dictionary)

        dictionary = get_definitionscl().main(dictionary)

        ins = dd.digital_definitioncl(dictionary, **kwargs)

        if first_half:
            ins.main()
        else:
            dictionary = ins.main()
            if kwargs.get('pi'):
                kwargs['fr_pickle'] = True
                del kwargs['pi']

            ins = dd.get_standard_form(**kwargs)
            ins.from_first_half(dictionary)
            ins.main()
            fr.check_circularity().from_second_half(ins, **kwargs)

    return


if eval(not_execute_on_import):
    args = vgf.get_arguments()
    file_nm = "dictionary2.xlsx"

    if len(args) == 1:
        args.append('fr')
        args.append('db')
        args.append('')
    try:
        p (f"args used {args[1:]}")
    except:
        pass

    if args[1][:2] == 'nb':  # use nbm
        new_books(args)

    elif args[1] == "ss":
        get_ssent2num(args[2])

    elif args[1] == 'l2t':
        print2text()

    elif args[1] == 't2e':
        from_txt2excel(True)

    elif args[1] == 'tf':
        time_functionscl('build_dictionary(**{"second_half":True})', True)

    else:

        kwargs = {}
        for x in args:
            kwargs[x] = True

        build_dictionary(**kwargs)

"""
claims
axiom_dictionary
classless_dict
const_dct
half_dct
test_fix_paren
failures
random_paren
newer2
remaining_constants
shift_combos
atomic_sents
calc_ax_output
"""
