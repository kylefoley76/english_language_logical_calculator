from settings import *
import general_functions as gf
from general import *
import gen_dict_func as gdf

"""
for some reason one of the shifts of INA is producing this
but it still produces the correct result
((n - b INA c) ∧ (b L k) ∧ (b L m) ∧ (b L e) ∧ (b L f) ∧ (j L b)
 ∧ (h L b) ∧ (d L b) ∧ (g L b) ∧ (j O b) ∧ (h O b) ∧ (m O b) ∧ 
 (k O b) ∧ (b O g) ∧ (b O e) ∧ (b O f) ∧ (b F j) ∧ (b F k) ∧ 
 (b F g) ∧ (b F f) ∧ (h F b) ∧ (d F b) ∧ (m F b) ∧ (e F b)) → 
 (c W j) ∧ (c W k) ∧ (c W m) ∧ (c W d) ∧ (c W e) ∧ (c W f) ∧ 
 (c W g) ∧ (c W h) ∧ (j L k) ∧ (h L m) ∧ (g L f) ∧ (d L e) ∧ 
 (h O d) ∧ (m O e) ∧ (k O f) ∧ (j O g) ∧ (h F j) ∧ (m F k) ∧ 
 (e F f) ∧ (d F g)

"""



class split_sentencescl:
    def main(self, sentence, definiendum=""):
        self.sentence = sentence
        self.definiendum = definiendum
        if definiendum == 'thought':
            bb = 8

        self.has_period = True
        self.has_prime = True
        self.has_cyrillic = False
        self.vars = gf.get_variables()
        self.work_flow_ss()
        return self.sent_dict

    def work_flow_ss(self):
        self.sentence = gdf.remove_extra_paren(self.sentence)
        self.sentence = self.sentence.replace("|", "")
        while self.has_period or self.has_prime:
            self.essential_letters = []
            self.get_essential_letters()
            cls = period_eliminationcl(self)
            self.sentence = cls.sentence
            self.vars = cls.vars
        self.adjust_pcount()
        self.number_sentences()
        self.get_embeds()
        self.sent_dict.conn["1"] = self.sent_dict.mainc
        self.get_parent_conns()
        self.get_descendants()
        self.get_children()
        add_pipes(self)
        return

    def get_essential_letters(self):
        self.has_period = False
        self.has_prime = False
        special = all_connectives + ["(", ")"]
        special2 = jsonc(special)
        self.arrow_sentence = False
        special2.append(mini_e)
        self.period_elim = []
        count = 0
        for e, letter in en(self.sentence):
            if letter == "(":
                count += 1

            elif letter == ")":
                count -= 1
            if letter in [shift, arrow]:
                self.arrow_sentence = True

            if count == 0 and letter in all_connectives:
                self.mainc = letter

            if letter in special2:
                self.essential_letters.append([letter, e, count])
            if letter.isupper() or isrelat(letter) or letter in special \
                    or letter == "." or letter == "'":
                self.period_elim.append([letter, e])
                if letter == ".":
                    self.has_period = True
                elif letter == "'":
                    self.has_prime = True

            elif letter.islower():
                if self.sentence[e + 1] in superscripts:
                    try:
                        self.vars.remove(self.sentence[e:e + 2])
                    except:
                        pass
                else:
                    try:
                        self.vars.remove(letter)
                    except:
                        pass

    def adjust_pcount(self):
        last_e = lambda e, y: e == len(y) - 1
        tlist = [0]
        y = self.essential_letters
        molecular = False
        if not self.arrow_sentence:
            return
        self.mainc = arrow
        for e, lst in en(self.essential_letters):
            if e == 21:
                bb = 8
            if lst[0] in non_arrow_connectives:
                molecular = True
            elif lst[0] in [shift, arrow, shift] or last_e(e, y):
                tlist.append(e)
                last_arrow = tlist[0]
                del tlist[0]

            if (lst[0] == shift or last_e(e, y)) and molecular:
                g = 1 if last_e(e, y) else 0

                for f in range(last_arrow + 1, e + g):
                    self.essential_letters[f][2] += 1
                    f += 1

                molecular = False

        return

    def number_sentences(self):
        self.sentences = []
        self.heir_num = [1]
        self.greek_num = 946
        arr_adj = 0
        do_not_add = False
        self.sent_dict = fill_stats(self)
        for e, lst in en(self.essential_letters):
            if e == 26:
                bb = 8

            if lst[0] == "(":
                if lst[2] + 1 > len(self.heir_num):
                    self.heir_num.append(1)
                elif do_not_add:
                    do_not_add = False
                    arr_adj = 0
                else:
                    self.heir_num[lst[2] - arr_adj] += 1
                    arr_adj = 0

            elif lst[0] == ")":
                self.pcount = lst[2]
                if len(self.heir_num) > self.pcount + 2:
                    del self.heir_num[-1]
                self.conn = ""
                self.number_sentences2(e, lst)

            if self.embedded_arrow(lst, e):
                self.pcount = lst[2]
                del self.heir_num[-1]
                self.number_arrow_sent(e)
                self.heir_num[-1] += 1
                do_not_add = True

            if lst[0] in [shift, arrow, shift]:
                try:
                    if self.essential_letters[e + 1][2] - self.essential_letters[e][2] == 2:
                        self.heir_num.append(1)
                        arr_adj = 1
                except:
                    pass

        self.get_greek_sent()

        return

    def number_sentences2(self, e, lst):
        f = e - 1
        while True:
            if f == 40:
                bb = 8

            if self.essential_letters[f][0] == "(" and \
                    self.essential_letters[f][2] == lst[2] + 1:
                start = self.essential_letters[f][1]
                self.sent = self.sentence[start:lst[1] + 1]
                self.sentences.append(self.sent)
                end = self.essential_letters[e][1]
                self.get_sent_stats(f, end)
                break

            elif self.essential_letters[f][2] == self.pcount + 1 and \
                    self.essential_letters[f][0] == ")" and \
                    (e - f) > 1:
                self.conn = self.essential_letters[f + 1][0]
                assert self.conn in all_connectives
            f -= 1

    def number_arrow_sent(self, e):
        f = e - 1
        if e == len(self.essential_letters) - 1:
            end = len(self.sentence)
        else:
            end = self.essential_letters[f][1] + 1
        while True:
            if f == 24:
                bb = 8

            if self.essential_letters[f][0] in [shift, arrow, shift]:
                start = self.essential_letters[f + 1][1]
                self.sent = self.sentence[start: end]
                self.sentences.append(self.sent)
                self.get_sent_stats(f, end)
                break


            elif self.essential_letters[f][2] == 1 and \
                    self.essential_letters[f][0] in all_connectives:
                self.conn = self.essential_letters[f][0]
                assert self.conn in all_connectives
            f -= 1

    def embedded_arrow(self, lst, e):
        if lst[0] in [shift, arrow, shift]:
            if self.essential_letters[e - 1][2] == 1:
                return True
        elif self.arrow_sentence and e == len(self.essential_letters) - 1 and \
                lst[2] == 1:
            return True
        return False

    def get_greek_sent(self):
        self.greek = self.sentence
        for num, sent in self.sent_dict.greek_di.items():
            if sent != None:
                trange = self.sent_dict.range.get(num)
                if iscyrillic(sent):
                    left = self.greek[:trange[0]]
                    right = self.greek[trange[1] + 1:]
                    self.greek = left + sent + right
                    assert len(self.greek) == len(self.sentence)


                elif trange[0] == 0:
                    blanks = " " * trange[1]
                    self.greek = sent + blanks + \
                                 self.greek[trange[1] + 1:]
                    assert len(self.greek) == len(self.sentence)

                else:
                    blanks = " " * (trange[1] - trange[0])
                    left = self.greek[:trange[0]]
                    if cyr1 in left:
                        bb = 8

                    center = sent + blanks
                    right = self.greek[trange[1] + 1:]
                    self.greek = left + center + right
                    assert len(self.greek) == len(self.sentence)

        self.get_greek_sent2()

    def get_greek_sent2(self):
        self.greek = self.greek.replace(" ", "")
        tconnectives = jsonc(all_connectives)
        tconnectives.append(mini_e)
        for conn in tconnectives:
            str1 = " " + conn + " "
            self.greek = self.greek.replace(conn, str1)
        self.sent_dict.greek = self.greek

    def get_sent_stats(self, f, end):
        lst = self.essential_letters[f]
        hnum = [str(x) for x in self.heir_num]
        lst_num = ".".join(hnum)
        if lst_num == '1.1.2.4':
            bb = 8

        self.sent_dict.name[lst_num] = self.sent
        self.sent_dict.hnum[lst_num] = jsonc(self.heir_num)
        self.sent_dict.conn[lst_num] = self.conn
        self.get_tvalue(lst, lst_num)
        self.sent_dict.greek_di[lst_num] = None
        if self.conn == "":
            self.greek_num += 1
            '''
            this is meant to skip over the cyrillic letters, otherwise
            with certain very large equations an error will arise when
            we try to replace the greek letters
            '''
            if self.greek_num == 1078: self.greek_num = 1200
            if iscyrillic(self.sent_dict.name[lst_num]):
                self.sent_dict.greek_di[lst_num] = self.sent_dict.name[lst_num]
            else:
                self.sent_dict.greek_di[lst_num] = chr(self.greek_num)
        start = lst[1]
        self.sent_dict.range[lst_num] = [start, end]
        return

    def get_tvalue(self, lst, lst_num):
        prev_let = ""
        pprev_let = ""
        idx = lst[1]
        if idx >= 1:
            prev_let = self.sentence[idx - 1]
        if idx > 1:
            pprev_let = self.sentence[idx - 2]
        tvalue = ""
        if prev_let == "~" and not pprev_let == "~":
            tvalue = "~"
        self.sent_dict.tvalue[lst_num] = tvalue

    def get_embeds(self):
        for num, conn in self.sent_dict.conn.items():
            hnum = jsonc(self.sent_dict.hnum.get(num))
            hnum = [str(x) for x in hnum]
            _ = gdf.get_ancestors(hnum)
            self.sent_dict.parents[num] = _

    def get_parent_conns(self):
        dct1 = {}
        for x, y in self.sent_dict.parents.items():
            parent = y[0]
            dct1[x] = self.sent_dict.conn[parent]
        self.sent_dict.pconn = dct1

    def get_descendants(self):
        self.sent_dict.descendants = {}
        for k, parents in self.sent_dict.parents.items():
            for parent in parents:
                self.sent_dict.descendants.setdefault(parent, set()).add(k)

    def get_children(self):
        self.sent_dict.children = {}
        for k, desc in self.sent_dict.descendants.items():
            gen = len(self.sent_dict.hnum.get(k, "1"))
            for x in list(desc):
                if gen + 1 == len(self.sent_dict.hnum[x]):
                    self.sent_dict.children.setdefault(k, set()).add(x)
        for x, y in self.sent_dict.children.items():
            y = list(y)
            y.sort()
            self.sent_dict.children[x] = y
        for x, y in self.sent_dict.descendants.items():
            y = list(y)
            y.sort()
            self.sent_dict.descendants[x] = y
        return



    def print_ss(self):
        if self.piped_sent == "":
            p(self.sentence)
        else:
            lst = self.piped_sent.split("|")
            for y in lst:
                p(y)


class add_pipes:
    def __init__(self, cls):
        self.piped_sent = ""
        if len(cls.sentence) > 75:
            self.sent_dict = cls.sent_dict
            self.sentence = cls.sentence
            self.piped_sent = cls.sentence
            self.greek = cls.greek
            self.name = cls.sent_dict.name
            self.parents = cls.sent_dict.parents
            descendants2 = jsonc(cls.sent_dict.descendants)
            self.descendants = {}
            for x, y in descendants2.items():
                self.descendants[x] = set(y)
            self.children = cls.sent_dict.children

            self.conn = cls.sent_dict.conn
            self.hnum = cls.sent_dict.hnum
            self.small_name = jsonc(self.name)
            self.must_be_divided = set()
            self.must_be_line = set()
            self.name['1'] = self.sentence

            self.work_flow()

            cls.sent_dict.sentence = self.piped_sent
            cls.sent_dict.greek = self.greek

    def work_flow(self):
        self.sizes = {x: len(y) for x, y in self.name.items()}

        self.get_sent_end()

        self.must_be_alone(set(self.small_name.keys()), 2)

        self.divide_large_sent()

        self.get_eldest_sent()

        self.get_rem_small_sents()

        self.add_pipes2()

        self.pipe_greek_sent()

    def get_sent_end(self):
        self.sent_ends = {}
        for k, sent in self.name.items():
            self.sent_ends[k] = self.sentence.index(sent) + len(sent)

    def must_be_alone(self, set1, generation):
        for sent in list(set1):
            ancestors = self.hnum[sent]
            if len(ancestors) == generation and sent in set1:
                if self.sizes[sent] >= 70:
                    children = self.children[sent]
                    for child in children:
                        if self.sizes[child] > 70:
                            gchildren = self.children[child]
                            if all(x for x in list(gchildren)
                                   if self.sizes[x] < 35):
                                self.must_be_divided.add(child)
                                self.must_be_line.add(child)
                            else:
                                self.must_be_alone(gchildren, generation + 1)

                        elif self.sizes[child] > 35:
                            self.must_be_line.add(child)

        return

    def separate_families(self, set1):
        return set(x for x in list(set1)
                   if len(set(self.parents[x]) & set1) == 0)

    def get_eldest_sent(self):
        self.must_be_line = self.separate_families(self.must_be_line)

        self.done = set()
        for x in list(self.must_be_line):
            self.done |= self.descendants.get(x, set())

        self.done |= self.must_be_line

    def get_rem_small_sents(self):
        self.remaining = set()
        for k, v in self.name.items():
            if k not in self.done and \
                    len(self.descendants.get(k, set()) & self.done) == 0:
                self.remaining.add(k)

    def has_large_sent(self):
        if self.must_be_line != set():
            return True
        return False

    def has_small_sents(self):
        self.just_shift = True
        if any(x in conditionals for x in self.conn.values()):
            self.just_shift = False
        self.divide_sent()

    def divide_large_sent(self):
        for x in list(self.must_be_divided):
            sent = self.name[x]
            sent2 = self.divide_large_sent2(sent)
            self.piped_sent = self.piped_sent.replace(sent, sent2)

        return

    def divide_large_sent2(self, sent):
        sections = (len(sent) // 70) + 1
        avg_size = len(sent) // sections
        for y in range(sections - 1):
            end = avg_size * (y + 1)
            sent = self.adjust_end(end, sent)
        return sent

    def divide_sent(self):
        # in case 2 there are just arrows and circled crosses
        sections = (len(self.sentence) // 70) + 1
        avg_size = len(self.sentence) // sections
        for x in range(sections - 1):
            end = avg_size * (x + 1)
            if self.just_shift:
                self.adjust_end(end)
            else:
                self.within_conditional(end)

    def within_conditional(self, end: int):
        for k, v in self.sent_ends.items():
            if v > end:
                break

        parents = ujsonc(self.parents[k])
        parents.remove("1")
        for parent in reversed(parents):

            if self.conn.get(parent) in conditionals:
                self.within_conditional2(parent, end)
                return
        self.adjust_end(end)

    def within_conditional2(self, parent, end):
        pend = self.sent_ends[parent]
        begin = pend - self.sizes[parent]
        # todo make sure this doesn't result in a sentence
        # larger than 75
        if abs(pend - end) < abs(begin - end):
            self.newest_size(pend, begin)
            self.adjust_end(pend)
        else:
            self.within_conditional3(begin)

    def within_conditional3(self, begin):
        for let in reversed(self.piped_sent[:begin]):
            if let == " ":
                break
            begin -= 1
        self.piped_sent = add_at_i(begin, self.piped_sent, "|")
        self.update_sent_ends()

    def newest_size(self, pend, begin):
        tpend = 0
        if "|" in self.piped_sent[:pend]:
            tpend = vgf.rindex(self.piped_sent[:pend], "|")
        if pend - tpend > 70:
            self.within_conditional3(begin)
        else:
            self.adjust_end(pend)

    def newest_size2(self, end):
        begin = 0
        if "|" in self.piped_sent[:end]:
            begin = vgf.rindex(self.piped_sent[:end], "|")
        if (end - begin) > 70:
            osent = self.piped_sent[begin:end]
            sent = self.divide_large_sent2(osent)
            self.piped_sent = self.piped_sent.replace(osent, sent)

    def add_pipes2(self):
        if not self.has_large_sent():
            self.has_small_sents()
        else:
            self.loop_small_sents = False
            for k, v in self.name.items():
                if k in self.must_be_line:
                    self.conjoin_children()
                    end = self.sent_ends[k]
                    self.adjust_end(end)
                elif k in self.remaining:
                    self.loop_small_sents = True
                else:
                    self.conjoin_children()
                self.last_sent = k

    def conjoin_children(self):
        if self.loop_small_sents:
            end = self.sent_ends[self.last_sent]
            self.newest_size2(end)

            self.adjust_end(end)
            self.loop_small_sents = False

    def adjust_end(self, end: int, sent2=""):
        sent = self.piped_sent if sent2 == "" else sent2
        pattern_found = False
        for idx in range(end, len(sent) - 3):
            let = sent[idx]
            next_let = sent[idx + 1]
            unxt_let = sent[idx + 2]
            if let == " " and next_let in all_connectives and unxt_let == " ":
                pattern_found = True
            elif let in ["~", "("] and pattern_found:
                if sent[idx - 1] != "|":
                    sent = add_at_i(idx, sent, "|")
                break

        if sent2 == "":
            self.update_sent_ends()
            self.piped_sent = sent
        else:
            return sent

    def update_sent_ends(self):
        for k, v in self.sent_ends.items():
            self.sent_ends[k] = v + 1

    def pipe_greek_sent(self):
        loc = 0
        lst = []
        for let in self.piped_sent:
            if let in all_connectives:
                loc += 1
            elif let == "|":
                lst.append(loc)

        i = 0
        loc = 0
        while i < len(self.greek):
            let = self.greek[i]
            if let in all_connectives:
                loc += 1
                if loc in lst:
                    self.greek = vgf.add_at_i(i + 2, self.greek, "|")
                    i += 2
            i += 1

        return


class fill_stats:
    def __init__(self, cls):
        self.name = {}
        self.conn = {}
        self.hnum = {}
        self.greek_di = {}
        self.tvalue = {}
        self.range = {}
        self.parents = {}
        self.greek = ""
        self.sentence = cls.sentence
        self.mainc = cls.mainc
        self.bad_paren = None
        self.definiendum = cls.definiendum


class period_eliminationcl:
    def __init__(self, cls):
        self.period_elim = cls.period_elim
        self.sentence = cls.sentence
        self.vars = cls.vars
        if cls.has_period:
            e = 0
            while e < len(self.period_elim):
                lst = self.period_elim[e]
                if lst[0] == ".":
                    self.new_vars = []
                    self.get_start_stop(e)
                    self.subj = True
                    if self.period_elim[e - 1][0] == "(":
                        self.root_end = self.sstop
                    else:
                        j = e - 1
                        while self.period_elim[j][0] != "(":
                            j -= 1
                        self.root_start = self.period_elim[j][1]
                        self.root_end = self.period_elim[e - 1][1] + 2
                        self.subj = False

                    self.add_var(e)
                    f = e + 1
                    while self.period_elim[f][0] == ".":
                        self.add_var(f)
                        f += 1
                    self.add_var(f)
                    if self.subj:
                        self.root_start = self.period_elim[f][1] - 1
                    e = f
                    self.new_sent(e)
                e += 1

        if cls.has_prime:
            self.prime_elimination()

        return

    def add_var(self, e):
        start = self.period_elim[e - 1][1] + 1
        stop = self.period_elim[e][1]
        str1 = self.sentence[start: stop]
        str1 = str1.strip()
        self.new_vars.append(str1)

    def new_sent(self, e):
        rst = self.root_start
        ren = self.root_end
        root = self.sentence[rst: ren]
        new_sents = []
        old_length = self.sstop - self.sstart

        for var in self.new_vars:
            if self.subj:
                str1 = "(" + var + root
            else:
                str1 = root + var + ")"
            new_sents.append(str1)

        conn = self.rconn if self.lconn == None else self.lconn

        if self.lconn in [shift,arrow] and self.rconn in [shift, arrow]:
            new_conn = shift
        else:
            new_conn = cj
        new_conn = " " + new_conn + " "
        new_conjunct = new_conn.join(new_sents)
        if conn not in ["&", cj, shift, arrow, shift]:
            new_conjunct = "(" + new_conjunct + ")"

        self.sentence = self.sentence[:self.sstart] + new_conjunct + \
                        self.sentence[self.sstop:]

        diff = len(new_conjunct) - old_length
        for lst in self.period_elim[e:]:
            lst[1] += diff


        return

    def get_start_stop(self, e):
        g = e - 1
        while self.period_elim[g][0] != "(":
            g -= 1
        self.sstart = self.period_elim[g][1]
        h = e + 1
        self.lconn = None

        if self.period_elim[g - 1][0] in all_connectives:
            self.lconn = self.period_elim[g - 1][0]

        while self.period_elim[h][0] != ")":
            h += 1
        self.sstop = self.period_elim[h][1] + 1
        self.rconn = None
        try:
            if self.period_elim[h + 1][0] in all_connectives:
                self.rconn = self.period_elim[h + 1][0]
        except:
            pass

    def prime_elimination(self):
        e = 0
        while e < len(self.period_elim):
            lst = self.period_elim[e]
            if lst[0] == "'":
                self.get_start_stop(e)
                self.subj = False
                if self.period_elim[e - 1][0] == "(":
                    self.subj = True
                    self.root_end = self.sstop
                    self.root_start = self.period_elim[e + 1][1]
                else:
                    self.root_end = self.period_elim[e - 1][1] + 1
                    self.root_start = self.sstart
                stop = self.period_elim[e][1]
                start = self.period_elim[e - 1][1] + 1
                str1 = self.sentence[start: stop]
                self.cat_var = str1.strip()
                self.new_var = self.vars.pop(0)
                # del self.vars[0]
                self.build_conditional(e)
            e += 1

    def build_conditional(self, e):
        old_length = self.sstop - self.sstart
        ant = "(" + self.new_var + " I " + self.cat_var + ")"
        rst = self.root_start
        ren = self.root_end
        root = self.sentence[rst: ren]
        if self.subj:
            cons = "(" + self.new_var + " " + root
        else:
            cons = root + " " + self.new_var + ")"

        if self.between_arrows(e):
            new_cond = build_connection(ant, conditional, cons)
        else:
            new_cond = "(" + build_connection(ant, conditional, cons) + ")"

        self.sentence = self.sentence[:self.sstart] + new_cond + \
                        self.sentence[self.sstop:]

        diff = len(new_cond) - old_length
        for lst in self.period_elim[e:]:
            lst[1] += diff

    def between_arrows(self, e):
        f = e - 1
        down = False
        ocount = 0
        ccount = 0
        while True:
            if self.period_elim[f][0] == "(":
                ocount += 1
            elif self.period_elim[f][0] == ")":
                ccount += 1
            if ccount == 2:
                bb = 8

            assert ccount < 2
            if ocount > 1 and not down:
                down = True
                f = e + 1
            if self.period_elim[f][0] in non_arrow_connectives:
                return False
            elif self.period_elim[f][0] in [shift, arrow, shift]:
                return True
            if not down:
                f -= 1
            else:
                f += 1
