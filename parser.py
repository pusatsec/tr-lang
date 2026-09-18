# -*- coding: utf-8 -*-
"""
Tr-lang Parser (Recursive Descent)
Token dizisini alir, ast_nodes.py'deki siniflardan bir agac kurar.
"""

from lexer import TokenType as T
from ast_nodes import *


class ParserHatasi(Exception):
    pass


class Parser:
    def __init__(self, tokenlar):
        self.tokenlar = tokenlar
        self.pos = 0

    # ---- yardimci fonksiyonlar ----
    def su_an(self):
        return self.tokenlar[self.pos]

    def ileri_bak(self, ofset=1):
        i = self.pos + ofset
        if i < len(self.tokenlar):
            return self.tokenlar[i]
        return self.tokenlar[-1]

    def tip(self):
        return self.su_an().tip

    def ilerle(self):
        t = self.su_an()
        if t.tip != T.EOF:
            self.pos += 1
        return t

    def beklenen(self, tip, mesaj=None):
        if self.tip() != tip:
            hata_mesaji = mesaj or f"{tip} bekleniyordu ama {self.tip()} bulundu"
            raise ParserHatasi(f"Satir {self.su_an().satir}: {hata_mesaji}")
        return self.ilerle()

    def uyuyor_mu(self, *tipler):
        return self.tip() in tipler

    def bosluklari_atla(self):
        while self.tip() == T.YENISATIR:
            self.ilerle()

    # ---- giris noktasi ----
    def ayristir(self):
        govde = []
        self.bosluklari_atla()
        while self.tip() != T.EOF:
            govde.append(self.deyim())
            self.bosluklari_atla()
        return Program(govde)

    # ---- blok (indent/dedent yonetimi) ----
    def blok(self):
        self.beklenen(T.IKINOKTA, "':' bekleniyordu")
        # Ayni satirda tek deyim de olabilir: "eger x: yazdir(1)"
        if self.tip() != T.YENISATIR:
            return [self.deyim()]
        self.ilerle()  # NEWLINE
        self.bosluklari_atla()
        self.beklenen(T.GIRINTI, "Girinti (indentation) bekleniyordu")
        govde = []
        while self.tip() != T.CIKINTI and self.tip() != T.EOF:
            govde.append(self.deyim())
            self.bosluklari_atla()
        self.beklenen(T.CIKINTI, "Cikinti (dedent) bekleniyordu")
        return govde

    # ---- deyimler ----
    def deyim(self):
        tip = self.tip()
        if tip == T.EGER:
            return self.eger_deyimi()
        if tip == T.IKEN:
            return self.iken_deyimi()
        if tip == T.ICIN:
            return self.icin_deyimi()
        if tip == T.ISLEV:
            return self.islev_tanimi()
        if tip == T.SINIF:
            return self.sinif_tanimi()
        if tip == T.DENE:
            return self.dene_deyimi()
        if tip == T.DONDUR:
            return self.dondur_deyimi()
        if tip == T.DUR:
            self.ilerle(); return DurDeyimi()
        if tip == T.DEVAM:
            self.ilerle(); return DevamDeyimi()
        if tip == T.PASS:
            self.ilerle(); return GecDeyimi()
        if tip == T.GETIR:
            return self.getir_deyimi()
        if tip == T.GLOBAL:
            return self.global_deyimi()
        return self.atama_veya_ifade()

    def eger_deyimi(self):
        self.ilerle()  # eger
        kosul = self.ifade()
        govde = self.blok()
        elif_dallari = []
        while self.tip() == T.YOKSA_EGER:
            self.ilerle()
            elif_kosul = self.ifade()
            elif_govde = self.blok()
            elif_dallari.append((elif_kosul, elif_govde))
        else_govde = None
        if self.tip() == T.DEGILSE:
            self.ilerle()
            else_govde = self.blok()
        return EgerDeyimi(kosul, govde, elif_dallari, else_govde)

    def iken_deyimi(self):
        self.ilerle()  # iken
        kosul = self.ifade()
        govde = self.blok()
        return IkenDeyimi(kosul, govde)

    def icin_deyimi(self):
        self.ilerle()  # icin
        degisken = self.beklenen(T.IDENT).deger
        # tuple hedef de olabilir: icin a, b icinde ...
        hedefler = [degisken]
        while self.tip() == T.VIRGUL:
            self.ilerle()
            hedefler.append(self.beklenen(T.IDENT).deger)
        self.beklenen(T.ICINDE, "'icinde' bekleniyordu")
        iterable = self.ifade()
        govde = self.blok()
        hedef = hedefler[0] if len(hedefler) == 1 else tuple(hedefler)
        return IcinDeyimi(hedef, iterable, govde)

    def islev_tanimi(self):
        self.ilerle()  # islev
        isim = self.beklenen(T.IDENT).deger
        self.beklenen(T.PARANAC)
        parametreler = []
        varsayilanlar = {}
        while self.tip() != T.PARANKAPA:
            pisim = self.beklenen(T.IDENT).deger
            parametreler.append(pisim)
            if self.tip() == T.ESIT:
                self.ilerle()
                varsayilanlar[pisim] = self.ifade()
            if self.tip() == T.VIRGUL:
                self.ilerle()
        self.beklenen(T.PARANKAPA)
        govde = self.blok()
        return IslevTanimi(isim, parametreler, govde, varsayilanlar)

    def sinif_tanimi(self):
        self.ilerle()  # sinif
        isim = self.beklenen(T.IDENT).deger
        ustler = []
        if self.tip() == T.PARANAC:
            self.ilerle()
            while self.tip() != T.PARANKAPA:
                ustler.append(self.beklenen(T.IDENT).deger)
                if self.tip() == T.VIRGUL:
                    self.ilerle()
            self.beklenen(T.PARANKAPA)
        govde = self.blok()
        return SinifTanimi(isim, ustler, govde)

    def dene_deyimi(self):
        self.ilerle()  # dene
        govde = self.blok()
        yakalamalar = []
        while self.tip() == T.YAKALA:
            self.ilerle()
            hata_tipi = None
            isim = None
            if self.tip() == T.IDENT:
                hata_tipi = self.beklenen(T.IDENT).deger
                if self.tip() == T.IDENT:  # "yakala Hata olarak h" -> basitlik icin "yakala Hata h"
                    isim = self.beklenen(T.IDENT).deger
            y_govde = self.blok()
            yakalamalar.append((hata_tipi, isim, y_govde))
        sonunda_govde = None
        if self.tip() == T.SONUNDA:
            self.ilerle()
            sonunda_govde = self.blok()
        return DeneDeyimi(govde, yakalamalar, sonunda_govde)

    def dondur_deyimi(self):
        self.ilerle()  # dondur
        if self.tip() in (T.YENISATIR, T.EOF, T.CIKINTI):
            return DondurDeyimi(None)
        deger = self.ifade()
        # coklu deger: dondur a, b
        if self.tip() == T.VIRGUL:
            elemanlar = [deger]
            while self.tip() == T.VIRGUL:
                self.ilerle()
                elemanlar.append(self.ifade())
            deger = TupleLiteral(elemanlar)
        return DondurDeyimi(deger)

    def getir_deyimi(self):
        self.ilerle()  # getir
        modul = self.beklenen(T.IDENT).deger
        while self.tip() == T.NOKTA:
            self.ilerle()
            modul += "." + self.beklenen(T.IDENT).deger
        takma_ad = None
        if self.tip() == T.IDENT and self.su_an().deger == "olarak":
            self.ilerle()
            takma_ad = self.beklenen(T.IDENT).deger
        return GetirDeyimi(modul, takma_ad)

    def global_deyimi(self):
        self.ilerle()
        isimler = [self.beklenen(T.IDENT).deger]
        while self.tip() == T.VIRGUL:
            self.ilerle()
            isimler.append(self.beklenen(T.IDENT).deger)
        return GlobalDeyimi(isimler)

    def atama_veya_ifade(self):
        ifade1 = self.ifade()
        # coklu atama: a, b = 1, 2
        if self.tip() == T.VIRGUL:
            hedefler = [ifade1]
            konum = self.pos
            gecici = []
            while self.tip() == T.VIRGUL:
                self.ilerle()
                gecici.append(self.ifade())
            if self.tip() == T.ESIT:
                self.ilerle()
                hedefler.extend(gecici)
                deger1 = self.ifade()
                degerler = [deger1]
                while self.tip() == T.VIRGUL:
                    self.ilerle()
                    degerler.append(self.ifade())
                deger = degerler[0] if len(degerler) == 1 else TupleLiteral(degerler)
                return CokluAtama(hedefler, deger)
            else:
                # aslinda tuple ifadesiymis (ornek: dondur olmadan a, b kullanimi nadir), geri sar
                self.pos = konum

        atama_op_map = {
            T.ESIT: "=",
            T.ARTI_ESIT: "+=",
            T.EKSI_ESIT: "-=",
            T.CARPI_ESIT: "*=",
            T.BOL_ESIT: "/=",
        }
        if self.tip() in atama_op_map:
            op = atama_op_map[self.tip()]
            self.ilerle()
            deger = self.ifade()
            return Atama(ifade1, deger, op)

        return IfadeDeyimi(ifade1)

    # ---- ifadeler (expression) - operator onceligine gore ----
    def ifade(self):
        return self.veya_ifadesi()

    def veya_ifadesi(self):
        sol = self.ve_ifadesi()
        if self.tip() == T.VEYA:
            degerler = [sol]
            while self.tip() == T.VEYA:
                self.ilerle()
                degerler.append(self.ve_ifadesi())
            return BoolOp("veya", degerler)
        return sol

    def ve_ifadesi(self):
        sol = self.degil_ifadesi()
        if self.tip() == T.VE:
            degerler = [sol]
            while self.tip() == T.VE:
                self.ilerle()
                degerler.append(self.degil_ifadesi())
            return BoolOp("ve", degerler)
        return sol

    def degil_ifadesi(self):
        if self.tip() == T.DEGIL:
            self.ilerle()
            return NotOp(self.degil_ifadesi())
        return self.karsilastirma()

    def karsilastirma(self):
        sol = self.toplama()
        karsilastirma_tipleri = (T.ESITESIT, T.FARKLI, T.BUYUK, T.KUCUK, T.BUYUKESIT, T.KUCUKESIT)
        while self.tip() in karsilastirma_tipleri or self.tip() == T.ICINDE or self._degil_icinde_mi():
            if self.tip() == T.ICINDE:
                self.ilerle()
                sag = self.toplama()
                sol = IcindeOp(sol, sag, olumsuz=False)
            elif self._degil_icinde_mi():
                self.ilerle()  # degil
                self.ilerle()  # icinde
                sag = self.toplama()
                sol = IcindeOp(sol, sag, olumsuz=True)
            else:
                op_tok = self.ilerle()
                sag = self.toplama()
                sol = BinOp(sol, op_tok.tip, sag)
        return sol

    def _degil_icinde_mi(self):
        return self.tip() == T.DEGIL and self.ileri_bak().tip == T.ICINDE

    def toplama(self):
        sol = self.carpma()
        while self.tip() in (T.ARTI, T.EKSI):
            op_tok = self.ilerle()
            sag = self.carpma()
            sol = BinOp(sol, op_tok.tip, sag)
        return sol

    def carpma(self):
        sol = self.birli()
        while self.tip() in (T.CARPI, T.BOL, T.TAMBOL, T.MOD):
            op_tok = self.ilerle()
            sag = self.birli()
            sol = BinOp(sol, op_tok.tip, sag)
        return sol

    def birli(self):
        if self.tip() in (T.EKSI, T.ARTI):
            op_tok = self.ilerle()
            return UnaryOp(op_tok.tip, self.birli())
        return self.us_alma()

    def us_alma(self):
        taban = self.erisim_zinciri()
        if self.tip() == T.US:
            self.ilerle()
            us = self.birli()  # sagdan sola bagliligi basitlestirdik
            return BinOp(taban, T.US, us)
        return taban

    def erisim_zinciri(self):
        ifade = self.temel()
        while True:
            if self.tip() == T.NOKTA:
                self.ilerle()
                isim = self.beklenen(T.IDENT).deger
                ifade = Oznitelik(ifade, isim)
            elif self.tip() == T.PARANAC:
                self.ilerle()
                argumanlar = []
                kw_argumanlar = []
                while self.tip() != T.PARANKAPA:
                    if self.tip() == T.IDENT and self.ileri_bak().tip == T.ESIT:
                        kw_isim = self.ilerle().deger
                        self.ilerle()  # =
                        kw_deger = self.ifade()
                        kw_argumanlar.append((kw_isim, kw_deger))
                    else:
                        argumanlar.append(self.ifade())
                    if self.tip() == T.VIRGUL:
                        self.ilerle()
                self.beklenen(T.PARANKAPA)
                ifade = Cagri(ifade, argumanlar, kw_argumanlar)
            elif self.tip() == T.KOSEAC:
                self.ilerle()
                # dilimleme destegi: [a:b:c]
                baslangic = None
                bitis = None
                adim = None
                if self.tip() != T.IKINOKTA:
                    baslangic = self.ifade()
                if self.tip() == T.IKINOKTA:
                    self.ilerle()
                    if self.tip() not in (T.KOSEKAPA, T.IKINOKTA):
                        bitis = self.ifade()
                    if self.tip() == T.IKINOKTA:
                        self.ilerle()
                        if self.tip() != T.KOSEKAPA:
                            adim = self.ifade()
                    self.beklenen(T.KOSEKAPA)
                    ifade = Indeksleme(ifade, DilimlemeIndeks(baslangic, bitis, adim))
                else:
                    self.beklenen(T.KOSEKAPA)
                    ifade = Indeksleme(ifade, baslangic)
            else:
                break
        return ifade

    def temel(self):
        tok = self.su_an()

        if tok.tip == T.SAYI:
            self.ilerle(); return SayiLiteral(tok.deger)
        if tok.tip == T.STRING:
            self.ilerle(); return StringLiteral(tok.deger)
        if tok.tip == T.FSTRING:
            self.ilerle(); return FStringLiteral(tok.deger)
        if tok.tip == T.DOGRU:
            self.ilerle(); return BoolLiteral(True)
        if tok.tip == T.YANLIS:
            self.ilerle(); return BoolLiteral(False)
        if tok.tip == T.BOS:
            self.ilerle(); return NoneLiteral()
        if tok.tip == T.IDENT:
            self.ilerle(); return Identifier(tok.deger)
        if tok.tip == T.PARANAC:
            self.ilerle()
            if self.tip() == T.PARANKAPA:
                self.ilerle(); return TupleLiteral([])
            ic = self.ifade()
            if self.tip() == T.VIRGUL:
                elemanlar = [ic]
                while self.tip() == T.VIRGUL:
                    self.ilerle()
                    if self.tip() == T.PARANKAPA:
                        break
                    elemanlar.append(self.ifade())
                self.beklenen(T.PARANKAPA)
                return TupleLiteral(elemanlar)
            self.beklenen(T.PARANKAPA)
            return ic
        if tok.tip == T.KOSEAC:
            self.ilerle()
            elemanlar = []
            while self.tip() != T.KOSEKAPA:
                elemanlar.append(self.ifade())
                if self.tip() == T.VIRGUL:
                    self.ilerle()
            self.beklenen(T.KOSEKAPA)
            return ListeLiteral(elemanlar)
        if tok.tip == T.SUSLUAC:
            self.ilerle()
            ciftler = []
            while self.tip() != T.SUSLUKAPA:
                anahtar = self.ifade()
                self.beklenen(T.IKINOKTA)
                deger = self.ifade()
                ciftler.append((anahtar, deger))
                if self.tip() == T.VIRGUL:
                    self.ilerle()
            self.beklenen(T.SUSLUKAPA)
            return SozlukLiteral(ciftler)

        raise ParserHatasi(f"Satir {tok.satir}: Beklenmeyen token: {tok.tip} ({tok.deger!r})")
