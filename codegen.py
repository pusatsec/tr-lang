# -*- coding: utf-8 -*-
"""
Tr-lang Code Generator
AST agacini alir, calisabilir Python kaynak kodu (string) uretir.
"""

from ast_nodes import *
from lexer import TokenType as T
import re

BINOP_MAP = {
    T.ARTI: "+", T.EKSI: "-", T.CARPI: "*", T.BOL: "/",
    T.TAMBOL: "//", T.MOD: "%", T.US: "**",
    T.ESITESIT: "==", T.FARKLI: "!=",
    T.BUYUK: ">", T.KUCUK: "<", T.BUYUKESIT: ">=", T.KUCUKESIT: "<=",
}

_FSTRING_KELIME_HARITASI = {
    "dogru": "True", "yanlis": "False", "bos": "None",
    "ve": "and", "veya": "or", "degil": "not", "icinde": "in",
}
_KIMLIK_DESENI = re.compile(r"[A-Za-zÇĞİÖŞÜçğıöşü_][A-Za-zÇĞİÖŞÜçğıöşü_0-9]*")


def _fstring_ic_donustur(ham_metin):
    """f-string icindeki {ifade} bloklarinda kullanilan birkac Turkce anahtar
    kelimeyi (dogru/yanlis/ve/veya/degil/icinde) Python karsiligina cevirir.
    NOT: Tam bir Tr-lang ifadesini parse etmez; sadece yaygin kelimeleri degistirir.
    Bilinen sinirlama: {} icinde tirnak isareti (nested string) kullanimi desteklenmez.
    """
    sonuc = []
    i, n = 0, len(ham_metin)
    while i < n:
        if ham_metin[i] == "{":
            j = ham_metin.find("}", i)
            if j == -1:
                sonuc.append(ham_metin[i:])
                break
            ic = ham_metin[i+1:j]

            def repl(m):
                kelime = m.group(0)
                normalize = kelime.lower()
                return _FSTRING_KELIME_HARITASI.get(normalize, kelime)

            ic_donustu = _KIMLIK_DESENI.sub(repl, ic)
            sonuc.append("{" + ic_donustu + "}")
            i = j + 1
        else:
            sonuc.append(ham_metin[i])
            i += 1
    return "".join(sonuc)


class CodeGenHatasi(Exception):
    pass


class CodeGen:
    def __init__(self):
        self.girinti_seviyesi = 0

    def girinti(self):
        return "    " * self.girinti_seviyesi

    def uret(self, node):
        return self._uret(node)

    def _uret(self, node):
        yontem = getattr(self, f"_{type(node).__name__}", None)
        if yontem is None:
            raise CodeGenHatasi(f"Bilinmeyen AST dugumu: {type(node).__name__}")
        return yontem(node)

    # ---- program / bloklar ----
    def _Program(self, node):
        satirlar = []
        for deyim in node.govde:
            satirlar.append(self._deyim_satiri(deyim))
        return "\n".join(satirlar)

    def _blok_uret(self, govde):
        self.girinti_seviyesi += 1
        satirlar = [self._deyim_satiri(d) for d in govde]
        self.girinti_seviyesi -= 1
        if not satirlar:
            satirlar = [self.girinti() + "    gec"]
        return "\n".join(satirlar)

    def _deyim_satiri(self, node):
        kod = self._uret(node)
        return kod  # her deyim metodu kendi girintisini ekliyor

    # ---- deyimler ----
    def _Atama(self, node):
        hedef = self._uret(node.hedef)
        deger = self._uret(node.deger)
        return f"{self.girinti()}{hedef} {node.op} {deger}"

    def _CokluAtama(self, node):
        hedefler = ", ".join(self._uret(h) for h in node.hedefler)
        deger = self._uret(node.deger)
        return f"{self.girinti()}{hedefler} = {deger}"

    def _IfadeDeyimi(self, node):
        return f"{self.girinti()}{self._uret(node.ifade)}"

    def _EgerDeyimi(self, node):
        satirlar = [f"{self.girinti()}if {self._uret(node.kosul)}:"]
        satirlar.append(self._blok_uret(node.govde))
        for elif_kosul, elif_govde in node.elif_dallari:
            satirlar.append(f"{self.girinti()}elif {self._uret(elif_kosul)}:")
            satirlar.append(self._blok_uret(elif_govde))
        if node.else_govde is not None:
            satirlar.append(f"{self.girinti()}else:")
            satirlar.append(self._blok_uret(node.else_govde))
        return "\n".join(satirlar)

    def _IkenDeyimi(self, node):
        satirlar = [f"{self.girinti()}while {self._uret(node.kosul)}:"]
        satirlar.append(self._blok_uret(node.govde))
        return "\n".join(satirlar)

    def _IcinDeyimi(self, node):
        if isinstance(node.degisken, tuple):
            hedef = ", ".join(node.degisken)
        else:
            hedef = node.degisken
        satirlar = [f"{self.girinti()}for {hedef} in {self._uret(node.iterable)}:"]
        satirlar.append(self._blok_uret(node.govde))
        return "\n".join(satirlar)

    def _IslevTanimi(self, node):
        parcalar = []
        for p in node.parametreler:
            if p in node.varsayilanlar:
                parcalar.append(f"{p}={self._uret(node.varsayilanlar[p])}")
            else:
                parcalar.append(p)
        params = ", ".join(parcalar)
        satirlar = [f"{self.girinti()}def {node.isim}({params}):"]
        satirlar.append(self._blok_uret(node.govde))
        return "\n".join(satirlar)

    def _SinifTanimi(self, node):
        ustler = f"({', '.join(node.ustler)})" if node.ustler else ""
        satirlar = [f"{self.girinti()}class {node.isim}{ustler}:"]
        satirlar.append(self._blok_uret(node.govde))
        return "\n".join(satirlar)

    def _DeneDeyimi(self, node):
        satirlar = [f"{self.girinti()}try:"]
        satirlar.append(self._blok_uret(node.govde))
        for hata_tipi, isim, y_govde in node.yakalamalar:
            baslik = "except"
            if hata_tipi:
                baslik += f" {hata_tipi}"
                if isim:
                    baslik += f" as {isim}"
            satirlar.append(f"{self.girinti()}{baslik}:")
            satirlar.append(self._blok_uret(y_govde))
        if node.sonunda_govde is not None:
            satirlar.append(f"{self.girinti()}finally:")
            satirlar.append(self._blok_uret(node.sonunda_govde))
        return "\n".join(satirlar)

    def _DondurDeyimi(self, node):
        if node.deger is None:
            return f"{self.girinti()}return"
        return f"{self.girinti()}return {self._uret(node.deger)}"

    def _DurDeyimi(self, node):
        return f"{self.girinti()}break"

    def _DevamDeyimi(self, node):
        return f"{self.girinti()}continue"

    def _GecDeyimi(self, node):
        return f"{self.girinti()}pass"

    def _GetirDeyimi(self, node):
        if node.takma_ad:
            return f"{self.girinti()}import {node.modul} as {node.takma_ad}"
        return f"{self.girinti()}import {node.modul}"

    def _GlobalDeyimi(self, node):
        return f"{self.girinti()}global {', '.join(node.isimler)}"

    # ---- ifadeler ----
    def _SayiLiteral(self, node):
        return repr(node.deger)

    def _StringLiteral(self, node):
        return repr(node.deger)

    def _FStringLiteral(self, node):
        donusturulmus = _fstring_ic_donustur(node.ham_metin)
        # Suslu parantez disindaki metni Python string literal'i icin kacisla.
        kacisli = self._fstring_kacisla(donusturulmus)
        return f'f"{kacisli}"'

    def _fstring_kacisla(self, metin):
        """{} disindaki duz metin kisimlarini escape eder, {} icini oldugu gibi birakir
        (icinde ifade var, kacislanirsa bozulur)."""
        sonuc = []
        i, n = 0, len(metin)
        while i < n:
            if metin[i] == "{":
                j = metin.find("}", i)
                if j == -1:
                    sonuc.append(metin[i:].replace("\\", "\\\\").replace('"', '\\"'))
                    break
                sonuc.append(metin[i:j+1])  # ifade kismi, dokunma
                i = j + 1
            else:
                j = metin.find("{", i)
                if j == -1:
                    j = n
                duz = metin[i:j].replace("\\", "\\\\").replace('"', '\\"')
                sonuc.append(duz)
                i = j
        return "".join(sonuc)

    def _BoolLiteral(self, node):
        return "True" if node.deger else "False"

    def _NoneLiteral(self, node):
        return "None"

    def _Identifier(self, node):
        return node.isim

    def _ListeLiteral(self, node):
        return "[" + ", ".join(self._uret(e) for e in node.elemanlar) + "]"

    def _SozlukLiteral(self, node):
        ciftler = [f"{self._uret(k)}: {self._uret(v)}" for k, v in node.ciftler]
        return "{" + ", ".join(ciftler) + "}"

    def _TupleLiteral(self, node):
        if len(node.elemanlar) == 1:
            return f"({self._uret(node.elemanlar[0])},)"
        return "(" + ", ".join(self._uret(e) for e in node.elemanlar) + ")"

    def _BinOp(self, node):
        op = BINOP_MAP[node.op]
        return f"({self._uret(node.sol)} {op} {self._uret(node.sag)})"

    def _UnaryOp(self, node):
        op = "-" if node.op == T.EKSI else "+"
        return f"({op}{self._uret(node.ifade)})"

    def _BoolOp(self, node):
        op = "and" if node.op == "ve" else "or"
        return "(" + f" {op} ".join(self._uret(d) for d in node.degerler) + ")"

    def _NotOp(self, node):
        return f"(not {self._uret(node.ifade)})"

    def _IcindeOp(self, node):
        op = "not in" if node.olumsuz else "in"
        return f"({self._uret(node.eleman)} {op} {self._uret(node.koleksiyon)})"

    def _Cagri(self, node):
        argumanlar = [self._uret(a) for a in node.argumanlar]
        for isim, deger in node.kw_argumanlar:
            argumanlar.append(f"{isim}={self._uret(deger)}")
        return f"{self._uret(node.fonksiyon)}({', '.join(argumanlar)})"

    def _Oznitelik(self, node):
        return f"{self._uret(node.obje)}.{node.isim}"

    def _Indeksleme(self, node):
        return f"{self._uret(node.obje)}[{self._uret(node.indeks)}]"

    def _DilimlemeIndeks(self, node):
        b = self._uret(node.baslangic) if node.baslangic is not None else ""
        s = self._uret(node.bitis) if node.bitis is not None else ""
        a = self._uret(node.adim) if node.adim is not None else ""
        if node.adim is not None:
            return f"{b}:{s}:{a}"
        return f"{b}:{s}"

    def _LambdaIfade(self, node):
        params = ", ".join(node.parametreler)
        return f"lambda {params}: {self._uret(node.govde)}"


def python_koduna_cevir(ast_agaci):
    gen = CodeGen()
    return gen.uret(ast_agaci)
