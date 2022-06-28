import add_path
from settings import *
from general import *
# import general_functions as gf
from dictionary.split_sentences import split_sentencescl


class calculate_statments:
    def __init__(self):
        self.temp11()
        claims = pi.open_pickle("claims")
        self.claims = claims[2]
        for self.claim in self.claims:
            self.main()

    def main(self):
        self.enclose()
        self.sp_sent = split_sentencescl().main(self.claim)
        bb = 8

    def enclose(self):
        b = len(self.claim) - 1
        while b > -1:
            let = self.claim[b]
            if let.isalpha():
                self.claim = replace_at_i(b + 1, self.claim, ")")
                self.claim = replace_at_i(b - 1, self.claim, "(")
                b -= 2
            else:
                b -= 1

    def unenclose(self):
        b = len(self.claim) - 1
        while b > -1:
            let = self.claim[b]
            if let.isalpha():
                self.claim = delete_at_i(b + 1, self.claim)
                self.claim = delete_at_i(b - 1, self.claim, "(")
            else:
                b -= 1


    def temp11(self):
        d = "(b C c)"
        e = "(~b C c)"
        f = "(b C ~c)"
        g = "(~b C ~c)"
        h = "~(b C c)"
        i = "~(~b C c)"
        j = "~(b C ~c)"
        k = "~(~b C ~c)"

        lst = [d,e,f,g,h,i,j,k]
        lst2 = list(combinations(lst,2))
        for x, y in lst2:
            p(f"{x} {cj} {y}")
        return




calculate_statments()