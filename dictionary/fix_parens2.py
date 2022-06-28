from settings import *


class paren_loc:
    def __init__(self):
        self.add_cparen = []
        self.del_cparen = []
        self.add_oparen = []
        self.del_oparen = []


class adjust_paren:
    def begin_ap(self, cls, from_sentences=False):
        if from_sentences:
            self.sentence = cls
            self.test = False
            self.printcase = False
            if from_sentences == 2:
                self.from_sentences = False
            else:
                self.from_sentences = True
            self.idx = 0
            self.diff = 0
            self.first = True
            self.sentence = self.sentence.replace("|", "")

        else:
            self.sentence = cls.sentence
            self.test = cls.test
            self.printcase = cls.printcase
            self.from_sentences = False
            self.idx = cls.i
            self.diff = cls.diff
            self.first = cls.first
        self.done = []
        self.embed = False
        self.paren_loc = paren_loc()
        self.main_ap()
        return self.done

    def main_ap(self):
        self.get_conn_chain()

        self.remove_inner_edge()

        self.ad_hoc4()

        self.eliminate_successive_plurals()

        self.permitted_changes()

        self.loop_check_errors()

    def get_conn_chain(self, i=0, embed=False):
        count = 0
        tconn_chain = [["begin", 0, i]]
        self.elists = []
        possible_embed = False
        while i < len(self.sentence):
            letter = self.sentence[i]
            if letter == "-":
                bb = 8

            if letter == ")":
                count -= 1
                if embed and count == -1:
                    break

            elif letter == "(" and possible_embed:
                possible_embed = False
                list2, i = self.get_conn_chain(i, True)
                self.elists.append(list2)
                count -= 1

            elif letter == "(":
                count += 1

            elif letter in all_connectives:
                tconn_chain.append([letter, count, i])

            elif letter == "-":
                possible_embed = True

            elif letter.isupper() or letter.islower() or letter in non_literals:
                if possible_embed:
                    possible_embed = False
            i += 1

        if i == len(self.sentence) and embed: i -= 1
        z = 0 if embed else count
        tconn_chain.append(["end", z, i])
        if embed:
            return tconn_chain, i
        else:
            self.conn_chain = tconn_chain

    def embed_permitted_changes(self):
        self.remove_inner_edge()
        self.ad_hoc4()
        self.eliminate_successive_plurals()
        self.permitted_changes()

    def eliminate_successive_plurals(self):
        if not self.done:
            i = 2
            if len(self.conn_chain) == 4: return
            while i < len(self.conn_chain) - 1:
                if self.conn_chain[i - 2][0] == self.conn_chain[i - 1][0] == self.conn_chain[i][0] and \
                        self.conn_chain[i - 2][1] == self.conn_chain[i - 1][1] == self.conn_chain[i][1] and \
                        self.conn_chain[i][0] in plural_connectives:
                    del self.conn_chain[i - 1]
                else:
                    i += 1

            if self.conn_chain[-2][0] == cj and self.conn_chain[-2][1] == 0 and \
                    self.conn_chain[-3][0] == cj and self.conn_chain[-3][1] == 0:
                del self.conn_chain[-2]

            self.more_bad_adds()

        return

    def more_bad_adds(self):
        for back, front in zip(self.conn_chain[:-1], self.conn_chain[1:]):
            if front[0] == back[0] and front[1] == back[1] and \
                    front[0] in plural_connectives:
                self.bad_add.append(back[2] + 2)
                self.bad_add.append(back[2] - 2)
                self.bad_add.append(front[2] + 2)
                self.bad_add.append(front[2] - 2)
        return

    def permitted_changes(self):
        '''
        todo
        currently there is a mistake here
        'r ≡ ((q ≡ (p & o)) & (n ≡ (((m & (и₁)) → ~l) & (ж₂) & k)))'
        this sentence goes into 'ad_hoc2' because 'double' becomes
        true and it should not
        '''
        if not self.done:
            self.bad_del = []
            double_add = []
            on = False
            double = False
            if self.sentence[0] == "(" and self.sentence[1] != "(":
                on = True
                pos = -1
            if self.sentence[0] == "(" and self.sentence[1] == "(":
                double = True

            for e, letter in enumerate(self.sentence[2:len(self.sentence) - 2]):
                if letter == "-":
                    double = False
                    on = False

                trigram = self.sentence[e: e + 3]
                if trigram[0] != "(" and trigram[1] == "(" and trigram[2] != "(":
                    self.bad_del.append(e + 1)
                    on = True
                    pos = e
                elif on and trigram[0] == ")" and trigram[1] == ")":
                    on = False
                    self.bad_add.append(pos + 1)

                elif on and trigram[0] != ")" and trigram[1] == ")" and trigram[2] != ")":
                    double_add.append([pos + 1, e + 1])
                    pos = 0
                    on = False

                if trigram[0] != ")" and trigram[1] == ")" and trigram[2] != ")":
                    self.bad_del.append(e + 1)

                if trigram[1] == "(" and trigram[0] == "(":
                    double = True
                    pos = e
                elif double and trigram[0] == ")" and trigram[1] == ")":
                    if double: break
                elif double and trigram[0] != ")" and trigram[1] == ")" and trigram[2] != ")":
                    double = False
                    self.bad_add.append(e + 1)

            if double:
                self.ad_hoc2(e, pos)

            self.permitted_changes2()

    def remove_inner_edge(self):
        self.bad_add = []
        self.bad_add.append(self.conn_chain[1][2] - 2)
        self.bad_add.append(self.conn_chain[-2][2] + 2)
        if self.conn_chain[1][1] == 0 and self.conn_chain[1][0] == cj:
            pass
        else:
            self.paren_loc.add_oparen.append(self.conn_chain[0][2])
            if self.sentence[self.conn_chain[0][2]: self.conn_chain[0][2] + 2] == "((":
                self.paren_loc.del_oparen.append(self.conn_chain[0][2])

        if len(self.conn_chain) < 3:
            pass
        elif not self.sentence[self.conn_chain[-1][2] - 1].islower() \
                and self.conn_chain[-2][0] == cj:
            pass
        else:
            self.paren_loc.add_cparen.append(self.conn_chain[-1][2])
        if len(self.conn_chain) > 3 and self.sentence[self.conn_chain[-1][2] - 1] == ")":
            self.paren_loc.del_cparen.append(self.conn_chain[-1][2])

    def permitted_changes2(self):
        for itm in self.conn_chain[1:-1]:
            if itm[2] - 2 not in self.bad_add:
                self.paren_loc.add_cparen.append(itm[2] - 2)
            if itm[2] - 2 not in self.bad_del:
                self.paren_loc.del_cparen.append(itm[2] - 2)
            if itm[2] + 2 not in self.bad_add:
                self.paren_loc.add_oparen.append(itm[2] + 2)
            if itm[2] + 2 not in self.bad_del:
                self.paren_loc.del_oparen.append(itm[2] + 2)

        return

    # in this case there is a sentence of the form ((b)) & (c)
    def ad_hoc2(self, k, pos):
        if self.printcase: print(f"ad hoc 2")
        left_chunk = self.sentence[pos:pos + 3]
        right_chunk = self.sentence[k: k + 3]
        l = left_chunk.count("(")
        r = right_chunk.count(")")
        q = pos if l < r else k
        if l == r:
            new_sent = delete_at_i(k, self.sentence)
            rsent = replace_at_i(k, self.sentence, "]")
            new_sent = delete_at_i(pos, new_sent)
            rsent = replace_at_i(pos, rsent, "]")
        else:

            new_sent = delete_at_i(q, self.sentence)
            rsent = replace_at_i(q, self.sentence, "]")
        self.done = [[new_sent, rsent, 0]]

    # in this case we have a sentence of this form (b) & ((c)
    def ad_hoc4(self):
        if self.from_sentences: return
        idx = self.conn_chain[-2][2]
        if self.sentence[idx + 2:idx + 4] == "((":
            if self.printcase: print(f"ad_hoc 4")
            self.sentence = delete_at_i(idx + 2, self.sentence)
            rsent = add_at_i(idx + 2, self.sentence, "]")
            self.done = [[self.sentence, rsent, 0]]
            return

    def loop_check_errors(self):
        if not self.done:
            conn_chain2 = ujsonc(self.conn_chain)

            for self.conn_chain in self.elists:
                if len(self.conn_chain) > 1:
                    self.embed_permitted_changes()
                    self.embed = True
                    self.done = self.check_errors().begin(self)
                    self.embed = False
                    if self.done:
                        return

            self.conn_chain = conn_chain2
            self.done = self.check_errors().begin(self)

    class check_errors:
        def begin(self, cls):
            self.conn_chain = cls.conn_chain
            self.sentence = cls.sentence
            self.printcase = cls.printcase
            self.paren_loc = cls.paren_loc
            self.embed = cls.embed
            self.first = cls.first
            self.from_sentences = cls.from_sentences
            self.done = cls.done
            self.diff = cls.diff
            self.main()
            return self.done

        def main(self):
            self.get_mainc()

            self.divide_into_blocks()

            self.ad_hoc8()

            self.ad_hoc3()

            self.ad_hoc5()

            self.main_rule()

            self.ad_hoc9()

            self.ad_hoc7()

        def get_mainc(self):
            self.mainc = None
            for itm in self.conn_chain[1:]:
                if itm[1] == 0:
                    self.mainc = itm[0]
                    return

        def divide_into_blocks(self):
            self.blocks = []
            self.block = []
            if not self.done:
                isambiguous = self.ambiguous_mainc()
                if self.mainc in plural_connectives and not isambiguous:
                    for e, itm in enumerate(self.conn_chain):
                        self.block.append(itm)
                        if (itm[1] <= 0 and itm[0] != 'begin') or itm[0] == 'end':
                            self.blocks.append(self.block)
                            begin_count = self.block[-1][1]
                            begin_num = self.block[-1][2] + 2
                            self.block = [['begin', begin_count, begin_num]]

                else:
                    self.blocks.append(self.conn_chain)

        def ambiguous_mainc(self):
            cn = {x[0] for x in self.conn_chain if x[1] == 0 and x[0] != 'begin' and x[0] != 'end'}
            if len(cn) > 1:
                return True
            else:
                return False

        def ad_hoc8(self):
            for e, self.block in enumerate(self.blocks):
                b = len(self.block)
                if e == len(self.blocks) - 1:
                    b = -1
                if len([x for x in self.block[:b] if x[1] < 0]) > 0:
                    start = self.block[0][2]
                    stop = self.block[-1][2]
                    self.done = self.make_changes().main(self, start, stop, "", -1)
                    return

        # in this case the first sentence dips below 0,
        # we cannot have sentences of the form (b)) & (c)

        def ad_hoc3(self):
            if not self.done:
                for self.block in self.blocks:
                    self.remove_inner_edge2()
                    if self.block[1][1] == -1:
                        if self.printcase: print(f"ad hoc 3")
                        self.sentence = delete_at_i(self.block[1][2] - 2, self.sentence)
                        rsent = add_at_i(self.block[1][2] - 2, self.sentence, "]")
                        self.done = [[self.sentence, rsent, 0]]
                        return

        def remove_inner_edge2(self):
            if self.block[1][2] - 2 in self.paren_loc.add_cparen:
                self.paren_loc.add_cparen.remove(self.block[1][2] - 2)
            if self.block[-2][2] + 2 in self.paren_loc.add_oparen:
                self.paren_loc.add_oparen.remove(self.block[-2][2] + 2)

        # in this case the sentence is enclosed by redundant paren
        def ad_hoc5(self):
            if not self.done:
                if self.mainc == "end" and not self.embed and \
                        not "-" in self.sentence:
                    if self.printcase: print(f"ad_hoc 5")
                    current_counts = sorted({x[1] for x in self.conn_chain})
                    f = 0
                    for itm in current_counts[1:]:
                        if itm - current_counts[f] != 1:
                            break
                        f += 1

                    b = 1 if itm == current_counts[-1] else itm
                    self.sentence = self.sentence[b: -b]
                    str3 = b * "["
                    str4 = b * ']'
                    rsent = str3 + self.sentence + str4
                    self.done = [[self.sentence, rsent, 0]]
                elif self.from_sentences:
                    self.done = 'correct_paren'

        def main_rule(self):
            if not self.done:
                for self.block in self.blocks:
                    b = max([x[1] for x in self.block]) + 1
                    a = self.pot_ad7()
                    if len(self.block) > 2:
                        for num in range(a, b):
                            correct, kind = self.loop_level(num)
                            if not correct:
                                start, stop = self.get_start_stop()
                                self.done = self.make_changes().main(self, start, stop, kind, self.diff)
                                return

        # this rule was brought in so that those sentences which end with
        # an extra cparen can be easily identified.  this rule allows
        # the block to go through the main rule without errors
        def pot_ad7(self):
            c = 0
            if self.mainc == cj and self.diff < 0:
                b = [x[1] for x in self.block[1:] if x[1] == 0]
                if len(b) == 0:
                    return 1

            return c

        def loop_level(self, num):
            highest = 0
            found = False
            while highest < len(self.block):
                lst = self.block[highest]
                if lst[1] == num and lst[0] != 'begin':
                    conn = self.mainc if lst[0] == 'end' else lst[0]
                    if lst[0] == 'end':
                        bb = 8

                    found = True
                    lowest = highest - 1
                    highest += 1
                    correct, gap = self.loop_up(lowest, num, conn)
                    if not correct: return False, gap
                    correct, highest = self.loop_down(highest, num, conn)
                    if not correct: return False, highest

                highest += 1

            if not found:
                return False, ""
            return True, ""

        def loop_up(self, lowest, num, conn):
            i = lowest
            gr1 = False
            pl1 = False
            while self.block[i][1] >= num and self.block[i][0] != 'begin':

                if self.block[i][0] == conn and self.block[i][1] == num + 1 \
                        and self.block[i][0] in plural_connectives:
                    kind = 'delete' if num > 0 else "both"
                    return False, kind
                elif (self.block[i][1] - num) > 1 and not pl1:
                    gr1 = True
                elif (self.block[i][1] - num) == 1:
                    gr1 = False
                    pl1 = True
                i -= 1
            if gr1:
                return False, "delete"

            return True, ""

        def loop_down(self, highest, num, conn):
            i = highest
            gr1 = False
            pl1 = False
            while i < len(self.block) and self.block[i][1] >= num and self.block[i][0] != 'end':
                if self.block[i][0] == conn and self.block[i][1] == num \
                        and self.block[i][0] in plural_connectives:
                    pass
                elif self.block[i][1] == num:
                    return False, ""
                elif self.block[i][0] == conn and self.block[i][1] == num + 1 \
                        and self.block[i][0] in plural_connectives:
                    kind = 'delete' if num > 0 else "both"
                    return False, kind
                elif (self.block[i][1] - num) > 1 and not pl1:
                    gr1 = True
                elif (self.block[i][1] - num) == 1:
                    gr1 = False
                    pl1 = True
                i += 1
            if gr1:
                return False, "delete"

            return True, i

        def get_start_stop(self):
            if self.embed:
                return self.blocks[0][0][2], self.blocks[-1][-1][2]
            else:
                return self.block[0][2], self.block[-1][2]

        def ad_hoc9(self):
            if not self.done:
                if self.diff == 1 and self.conn_chain[-1][1] == self.diff:
                    if self.printcase: print(f"ad hoc 9")
                    self.sentence = self.sentence + ")"
                    # str2 = "]" * abs(self.diff)
                    rsent = self.sentence + "}"
                    self.done = [[self.sentence, rsent, 0]]

        # in this case the sentence ends with an extra closed paren
        def ad_hoc7(self):
            if not self.done:
                if self.diff < 0 and self.conn_chain[-1][1] == self.diff \
                        and self.sentence[-2:] == "))":
                    if self.printcase: print(f"ad hoc 7")
                    self.sentence = self.sentence[:self.diff]
                    str2 = "]" * abs(self.diff)
                    rsent = self.sentence + str2
                    self.done = [[self.sentence, rsent, 0]]
                    return

            if not self.embed and not self.done:
                if self.first:
                    self.done = 'correct paren'
                else:
                    self.done = [[self.sentence, 1, 0]]
            return

        class make_changes:
            def main(self, cls, start, stop, kind, tdiff):
                self.paren_loc = cls.paren_loc
                self.sentence = cls.sentence
                new_sents = []
                self.sort_class()
                if cls.embed:
                    self.addcparen(start, stop, new_sents)
                    self.deloparen(start, stop, new_sents)
                    self.addoparen(start, stop, new_sents)
                    self.delcparen(start, stop, new_sents)
                    self.del_paren(start, stop, new_sents)
                    self.add_paren(start, stop, new_sents)

                else:

                    if tdiff == 0 and kind == 'delete':
                        self.del_paren(start, stop, new_sents)
                    elif tdiff == 0 and kind == 'both':
                        self.add_paren(start, stop, new_sents)
                        self.del_paren(start, stop, new_sents)
                    elif tdiff == 0:
                        self.add_paren(start, stop, new_sents)

                    elif tdiff > 0:
                        self.addcparen(start, stop, new_sents)
                        self.deloparen(start, stop, new_sents)

                    # in this case we either add ) or delete (
                    elif tdiff < 0:
                        self.addoparen(start, stop, new_sents)
                        self.delcparen(start, stop, new_sents)

                if new_sents != []:
                    return new_sents
                else:
                    return [[self.sentence, 0, 0]]

            def sort_class(self):
                self.paren_loc.add_cparen = sorted(set(self.paren_loc.add_cparen))
                self.paren_loc.add_oparen = sorted(set(self.paren_loc.add_oparen))
                self.paren_loc.del_cparen = sorted(set(self.paren_loc.del_cparen))
                self.paren_loc.del_oparen = sorted(set(self.paren_loc.del_oparen))

            def del_paren(self, start, stop, new_sents):
                list2 = [self.paren_loc.del_oparen, self.paren_loc.del_cparen]
                lists = [i for i in product(*list2)]
                for opar, cpar in lists:
                    if opar >= start and opar <= stop and \
                            cpar >= start and cpar <= stop and \
                            opar < cpar:
                        new_sent = (delete_at_i(cpar, self.sentence))
                        rsent = (replace_at_i(cpar, self.sentence, "]"))
                        new_sent = (delete_at_i(opar, new_sent))
                        rsent = (replace_at_i(opar, rsent, "["))
                        new_sents.append([new_sent, rsent, 0])

            def add_paren(self, start, stop, new_sents):
                list2 = [self.paren_loc.add_oparen, self.paren_loc.add_cparen]
                lists = [i for i in product(*list2)]
                for opar, cpar in lists:
                    if opar >= start and opar <= stop and \
                            cpar >= start and cpar <= stop and \
                            opar < cpar:
                        new_sent = add_at_i(cpar, self.sentence, ")")
                        rsent = (add_at_i(cpar, self.sentence, "}"))
                        new_sent = add_at_i(opar, new_sent, "(")
                        rsent = (add_at_i(opar, rsent, "{"))
                        new_sents.append([new_sent, rsent, 0])

            def delcparen(self, start, stop, new_sents):
                for num in reversed(self.paren_loc.del_cparen):
                    if num >= start and num <= stop:
                        new_sent = self.sentence
                        rsent = self.sentence
                        new_sent = (delete_at_i(num, new_sent))
                        rsent = (replace_at_i(num, rsent, "]"))
                        new_sents.append([new_sent, rsent, 0])

            def addoparen(self, start, stop, new_sents):
                for num in reversed(self.paren_loc.add_oparen):
                    if num >= start and num <= stop:
                        new_sent = self.sentence
                        rsent = self.sentence
                        new_sent = add_at_i(num, new_sent, "(")
                        rsent = (add_at_i(num, rsent, "{"))
                        new_sents.append([new_sent, rsent, 0])

            def deloparen(self, start, stop, new_sents):
                for num in reversed(self.paren_loc.del_oparen):
                    if num >= start and num <= stop:
                        new_sent = self.sentence
                        rsent = self.sentence
                        new_sent = (delete_at_i(num, new_sent))
                        rsent = (replace_at_i(num, rsent, "["))
                        new_sents.append([new_sent, rsent, 0])

            def addcparen(self, start, stop, new_sents):
                for num in reversed(self.paren_loc.add_cparen):
                    if num >= start and num <= stop:
                        new_sent = self.sentence
                        rsent = self.sentence
                        new_sent = add_at_i(num, new_sent, ")")
                        rsent = (add_at_i(num, rsent, "}"))
                        new_sents.append([new_sent, rsent, 0])
