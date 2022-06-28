import sys

sys.path.append('/Users/kylefoley/PycharmProjects/inference_engine2/inference2/Proofs/')
from settings import *
import excel_functions as ef
import very_general_functions as vgf
import xlrd

def renumber_sheet():
    for e, sent in enumerate(claims):
        g = sent_to_row.get(sent[0])
        ef.put_into_excel(ws, g, 2, e)

tm = time.time()
arguments = sys.argv

try:
    arg1 = arguments[1]
except:
    arg1 = "0"



if arg1 == 'cw':
    ef.update_excel_screen("inference_engine2.xlsx")
    ef.save_excel_sheet("inference_engine2.xlsx")
    ef.close_wb("inference_engine2.xlsx")

wb = xlrd.open_workbook(base_dir + 'excel/inference_engine2.xlsx')


def get_claims(wb):
    ws = wb.sheet_by_name('Sheet1')
    claims = []
    last_row = ef.get_last_rowm(ws, 500, 2)
    set_of_sentences = []

    for z in range(3):
        tclaims = []

        if z == 1:
            ws = wb.sheet_by_name('artificial')
        elif z == 2:
            ws = wb.sheet_by_name('statement')

        for row_num in range(2, last_row + 2):
            str1 = ef.get_from_excelm(ws, row_num, 2)
            str2 = ef.get_from_excelm(ws, row_num, 3)

            if str1 and not str2:
                set_of_sentences.append(str1)

            elif set_of_sentences and not str1:
                tclaims.append(copy.deepcopy(set_of_sentences))
                set_of_sentences = []

        claims.append(tclaims)


    if claims == []:
        raise Exception('no sentences')
    return claims

claims = get_claims(wb)

kind = 0

p (f'natural claims {len(claims[0])}')
p (f'artificial claims {len(claims[1])}')
p (f'statement logic {len(claims[2])}')


vgf.save_pickle(claims, "claims")

tm = vgf.good_numbers(time.time() - tm, 2)
p (f"time {tm}")

if arg1 == 'cw':
    renumber_sheet()
    wb.save(base_dir + 'excel/inference_engine2.xlsx')
    ef.open_wb('inference_engine2.xlsx', base_dir + "excel/")
