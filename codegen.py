# -*- coding: utf-8 -*-
"""
Tr-lang Code Generator
AST agacini alir, calisabilir Python kaynak kodu (string) uretir.
"""

from ast_nodes import *
from lexer import TokenType as T
from trlang_builtins import TURKCE_MODUL_ISIMLERI
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
        icin_kelimesi = "async for" if node.eszamansiz else "for"
        satirlar = [f"{self.girinti()}{icin_kelimesi} {hedef} in {self._uret(node.iterable)}:"]
        satirlar.append(self._blok_uret(node.govde))
        return "\n".join(satirlar)

    def _IslevTanimi(self, node):
        satirlar = [f"{self.girinti()}@{self._uret(d)}" for d in node.dekoratorler]
        parcalar = []
        for p in node.parametreler:
            duz_isim = p.lstrip("*")
            yildiz = p[:len(p) - len(duz_isim)]
            parca = duz_isim
            if duz_isim in node.param_tipleri:
                parca += f": {self._uret(node.param_tipleri[duz_isim])}"
            if duz_isim in node.varsayilanlar:
                parca += f" = {self._uret(node.varsayilanlar[duz_isim])}"
            parcalar.append(yildiz + parca)
        params = ", ".join(parcalar)
        tanim_kelimesi = "async def" if node.eszamansiz else "def"
        donus_str = f" -> {self._uret(node.donus_tipi)}" if node.donus_tipi is not None else ""
        satirlar.append(f"{self.girinti()}{tanim_kelimesi} {node.isim}({params}){donus_str}:")
        satirlar.append(self._blok_uret(node.govde))
        return "\n".join(satirlar)

    def _SinifTanimi(self, node):
        satirlar = [f"{self.girinti()}@{self._uret(d)}" for d in node.dekoratorler]
        ustler = f"({', '.join(node.ustler)})" if node.ustler else ""
        satirlar.append(f"{self.girinti()}class {node.isim}{ustler}:")
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
            if isim:
                # Yakalanan hatayi Turkce mesaj gosterecek sekilde sar
                self.girinti_seviyesi += 1
                sarma_satiri = f"{self.girinti()}{isim} = _trhata({isim})"
                self.girinti_seviyesi -= 1
                govde_kodu = self._blok_uret(y_govde)
                satirlar.append(sarma_satiri + "\n" + govde_kodu)
            else:
                satirlar.append(self._blok_uret(y_govde))
        if node.sonunda_govde is not None:
            satirlar.append(f"{self.girinti()}finally:")
            satirlar.append(self._blok_uret(node.sonunda_govde))
        return "\n".join(satirlar)

    def _DondurDeyimi(self, node):
        if node.deger is None:
            return f"{self.girinti()}return"
        return f"{self.girinti()}return {self._uret(node.deger)}"

    def _UretDeyimi(self, node):
        if node.deger is None:
            return f"{self.girinti()}yield"
        return f"{self.girinti()}yield {self._uret(node.deger)}"

    def _UretHepsindenDeyimi(self, node):
        return f"{self.girinti()}yield from {self._uret(node.ifade)}"

    def _DurDeyimi(self, node):
        return f"{self.girinti()}break"

    def _DevamDeyimi(self, node):
        return f"{self.girinti()}continue"

    def _GecDeyimi(self, node):
        return f"{self.girinti()}pass"

    def _GetirDeyimi(self, node):
        # Turkce modul ismi verilmisse (ör. "matematik"), gercek Python
        # modulune (math) baglan ama Turkce isimle erisilebilir sekilde birak.
        ilk_parca, *kalan_parcalar = node.modul.split(".")
        gercek_ilk_parca = TURKCE_MODUL_ISIMLERI.get(ilk_parca, ilk_parca)
        gercek_modul = ".".join([gercek_ilk_parca] + kalan_parcalar)

        if node.takma_ad:
            return f"{self.girinti()}import {gercek_modul} as {node.takma_ad}"
        if gercek_modul != node.modul:
            # Turkce isim, kullanicinin yazdigi Turkce adla erisebilsin diye takma ad
            return f"{self.girinti()}import {gercek_modul} as {node.modul}"
        return f"{self.girinti()}import {gercek_modul}"

    def _GlobalDeyimi(self, node):
        return f"{self.girinti()}global {', '.join(node.isimler)}"

    def _NonlocalDeyimi(self, node):
        return f"{self.girinti()}nonlocal {', '.join(node.isimler)}"

    def _DogrulaDeyimi(self, node):
        if node.mesaj is not None:
            return f"{self.girinti()}assert {self._uret(node.kosul)}, {self._uret(node.mesaj)}"
        return f"{self.girinti()}assert {self._uret(node.kosul)}"

    def _FirlatDeyimi(self, node):
        if node.ifade is None:
            return f"{self.girinti()}raise"
        satir = f"{self.girinti()}raise {self._uret(node.ifade)}"
        if node.kaynaktan is not None:
            satir += f" from {self._uret(node.kaynaktan)}"
        return satir

    def _EslestirDeyimi(self, node):
        satirlar = [f"{self.girinti()}match {self._uret(node.deger)}:"]
        self.girinti_seviyesi += 1
        for desen, guard, govde in node.durumlar:
            baslik = f"{self.girinti()}case {self._desen_uret(desen)}"
            if guard is not None:
                baslik += f" if {self._uret(guard)}"
            satirlar.append(baslik + ":")
            satirlar.append(self._blok_uret(govde))
        self.girinti_seviyesi -= 1
        return "\n".join(satirlar)

    def _desen_uret(self, desen):
        if isinstance(desen, DesenYakala):
            return desen.isim
        if isinstance(desen, DesenDizi):
            ic = ", ".join(self._desen_uret(e) for e in desen.elemanlar)
            return f"({ic})" if desen.parantez_mi else f"[{ic}]"
        if isinstance(desen, DesenVeya):
            return " | ".join(self._desen_uret(s) for s in desen.secenekler)
        return self._uret(desen)

    def _IleDeyimi(self, node):
        parcalar = []
        for ifade, isim in node.ifadeler:
            parca = self._uret(ifade)
            if isim:
                parca += f" as {isim}"
            parcalar.append(parca)
        ile_kelimesi = "async with" if node.eszamansiz else "with"
        satirlar = [f"{self.girinti()}{ile_kelimesi} {', '.join(parcalar)}:"]
        satirlar.append(self._blok_uret(node.govde))
        return "\n".join(satirlar)

    # ---- ifadeler ----
    def _SayiLiteral(self, node):
        return repr(node.deger)

    def _StringLiteral(self, node):
        return repr(node.deger)

    def _FStringLiteral(self, node):
        donusturulmus = _fstring_ic_donustur(node.ham_metin)
        # Icerikte hangi tirnak turleri kullanilmis, ona gore disaridaki
        # tirnagi cakismayacak sekilde secelim.
        cift_var = '"' in donusturulmus
        tek_var = "'" in donusturulmus
        if not cift_var:
            disari = '"'
        elif not tek_var:
            disari = "'"
        else:
            disari = '"""'  # ikisi de kullanilmissa uclu tirnaga gecelim
        kacisli = self._fstring_kacisla(donusturulmus, disari)
        return f"f{disari}{kacisli}{disari}"

    def _fstring_kacisla(self, metin, disari):
        """{} disindaki duz metin kisimlarinda SADECE disaridaki tirnak
        karakterini kacislar, {} icini oldugu gibi birakir (ifade var, dokunulmaz).
        disari secimi zaten iceriginde bulunmayan bir tirnak turu oldugu icin
        {} icinde kacislama gerekmez."""
        tirnak_karakteri = disari[0]  # '"""' icin de '"' yeterli tek karakter kontrolu
        sonuc = []
        i, n = 0, len(metin)
        while i < n:
            if metin[i] == "{":
                j = metin.find("}", i)
                if j == -1:
                    sonuc.append(metin[i:])
                    break
                sonuc.append(metin[i:j+1])  # ifade kismi, dokunma
                i = j + 1
            else:
                j = metin.find("{", i)
                if j == -1:
                    j = n
                duz = metin[i:j]
                if disari != '"""':
                    duz = duz.replace("\\", "\\\\").replace(tirnak_karakteri, "\\" + tirnak_karakteri)
                sonuc.append(duz)
                i = j
        return "".join(sonuc)

    def _BoolLiteral(self, node):
        return "True" if node.deger else "False"

    def _KosulluIfade(self, node):
        return f"({self._uret(node.dogru_deger)} if {self._uret(node.kosul)} else {self._uret(node.yanlis_deger)})"

    def _NoneLiteral(self, node):
        return "None"

    def _Identifier(self, node):
        return node.isim

    def _ListeLiteral(self, node):
        return "[" + ", ".join(self._uret(e) for e in node.elemanlar) + "]"

    def _ListeComprehension(self, node):
        hedef = ", ".join(node.degisken) if isinstance(node.degisken, tuple) else node.degisken
        kosul_str = f" if {self._uret(node.kosul)}" if node.kosul is not None else ""
        return f"[{self._uret(node.ifade)} for {hedef} in {self._uret(node.iterable)}{kosul_str}]"

    def _SozlukComprehension(self, node):
        hedef = ", ".join(node.degisken) if isinstance(node.degisken, tuple) else node.degisken
        kosul_str = f" if {self._uret(node.kosul)}" if node.kosul is not None else ""
        return f"{{{self._uret(node.anahtar)}: {self._uret(node.deger)} for {hedef} in {self._uret(node.iterable)}{kosul_str}}}"

    def _GeneratorIfadesi(self, node):
        hedef = ", ".join(node.degisken) if isinstance(node.degisken, tuple) else node.degisken
        kosul_str = f" if {self._uret(node.kosul)}" if node.kosul is not None else ""
        return f"({self._uret(node.ifade)} for {hedef} in {self._uret(node.iterable)}{kosul_str})"

    def _KumeLiteral(self, node):
        return "{" + ", ".join(self._uret(e) for e in node.elemanlar) + "}"

    def _KumeComprehension(self, node):
        hedef = ", ".join(node.degisken) if isinstance(node.degisken, tuple) else node.degisken
        kosul_str = f" if {self._uret(node.kosul)}" if node.kosul is not None else ""
        return f"{{{self._uret(node.ifade)} for {hedef} in {self._uret(node.iterable)}{kosul_str}}}"

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

    def _KarsilastirmaZinciri(self, node):
        parcalar = [self._uret(node.ilk)]
        for op_tip, operand in node.zincir:
            parcalar.append(BINOP_MAP[op_tip])
            parcalar.append(self._uret(operand))
        return "(" + " ".join(parcalar) + ")"

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

    def _YuruyenAtama(self, node):
        return f"({node.isim} := {self._uret(node.deger)})"

    def _BeklemeIfadesi(self, node):
        return f"await {self._uret(node.ifade)}"

    def _TipliAtama(self, node):
        hedef = self._uret(node.hedef)
        tur = self._uret(node.tur)
        if node.deger is not None:
            return f"{self.girinti()}{hedef}: {tur} = {self._uret(node.deger)}"
        return f"{self.girinti()}{hedef}: {tur}"

    def _YildizAcma(self, node):
        return f"*{self._uret(node.ifade)}"

    def _CiftYildizAcma(self, node):
        return f"**{self._uret(node.ifade)}"


def python_koduna_cevir(ast_agaci):
    gen = CodeGen()
    return gen.uret(ast_agaci)
