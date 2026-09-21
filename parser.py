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
        if tip == T.AT:
            return self.dekoratorlu_deyim()
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
        if tip == T.URET:
            return self.uret_deyimi()
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
        if tip == T.NONLOCAL:
            return self.nonlocal_deyimi()
        if tip == T.DOGRULA:
            return self.dogrula_deyimi()
        if tip == T.ESLESTIR:
            return self.eslestir_deyimi()
        if tip == T.ILE:
            return self.ile_deyimi()
        if tip == T.ESZAMANSIZ:
            return self.eszamansiz_deyimi()
        return self.atama_veya_ifade()

    def dekoratorlu_deyim(self):
        dekoratorler = []
        while self.tip() == T.AT:
            self.ilerle()  # @
            dekorator_ifadesi = self.erisim_zinciri()
            dekoratorler.append(dekorator_ifadesi)
            if self.tip() == T.YENISATIR:
                self.ilerle()
            self.bosluklari_atla()
        if self.tip() == T.ISLEV:
            node = self.islev_tanimi()
        elif self.tip() == T.SINIF:
            node = self.sinif_tanimi()
        elif self.tip() == T.ESZAMANSIZ:
            node = self.eszamansiz_deyimi()
        else:
            raise ParserHatasi(
                f"Satir {self.su_an().satir}: '@' sonrasi 'islev' veya 'sinif' bekleniyordu"
            )
        node.dekoratorler = dekoratorler
        return node

    def eszamansiz_deyimi(self):
        self.ilerle()  # eszamansiz
        if self.tip() != T.ISLEV:
            raise ParserHatasi(f"Satir {self.su_an().satir}: 'eszamansiz' sonrasi 'islev' bekleniyordu")
        node = self.islev_tanimi()
        node.eszamansiz = True
        return node

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
        param_tipleri = {}
        while self.tip() != T.PARANKAPA:
            yildiz = ""
            if self.tip() == T.CARPI:
                self.ilerle(); yildiz = "*"
            elif self.tip() == T.US:
                self.ilerle(); yildiz = "**"
            pisim = self.beklenen(T.IDENT).deger
            parametreler.append(yildiz + pisim)
            if self.tip() == T.IKINOKTA:
                self.ilerle()
                param_tipleri[pisim] = self.ifade()
            if self.tip() == T.ESIT:
                self.ilerle()
                varsayilanlar[pisim] = self.ifade()
            if self.tip() == T.VIRGUL:
                self.ilerle()
        self.beklenen(T.PARANKAPA)
        donus_tipi = None
        if self.tip() == T.OK:
            self.ilerle()
            donus_tipi = self.ifade()
        govde = self.blok()
        return IslevTanimi(isim, parametreler, govde, varsayilanlar, param_tipleri=param_tipleri, donus_tipi=donus_tipi)

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
            if self.tip() == T.PARANAC:
                self.ilerle()
                isimler = [self.beklenen(T.IDENT).deger]
                while self.tip() == T.VIRGUL:
                    self.ilerle()
                    isimler.append(self.beklenen(T.IDENT).deger)
                self.beklenen(T.PARANKAPA)
                hata_tipi = "(" + ", ".join(isimler) + ")"
                if self.tip() == T.IDENT:
                    isim = self.beklenen(T.IDENT).deger
            elif self.tip() == T.IDENT:
                hata_tipi = self.beklenen(T.IDENT).deger
                if self.tip() == T.IDENT:
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

    def uret_deyimi(self):
        self.ilerle()  # uret
        if self.tip() == T.IDENT and self.su_an().deger.lower() in ("hepsinden",):
            self.ilerle()
            ifade = self.ifade()
            return UretHepsindenDeyimi(ifade)
        if self.tip() in (T.YENISATIR, T.EOF, T.CIKINTI):
            return UretDeyimi(None)
        deger = self.ifade()
        if self.tip() == T.VIRGUL:
            elemanlar = [deger]
            while self.tip() == T.VIRGUL:
                self.ilerle()
                elemanlar.append(self.ifade())
            deger = TupleLiteral(elemanlar)
        return UretDeyimi(deger)

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

    def nonlocal_deyimi(self):
        self.ilerle()
        isimler = [self.beklenen(T.IDENT).deger]
        while self.tip() == T.VIRGUL:
            self.ilerle()
            isimler.append(self.beklenen(T.IDENT).deger)
        return NonlocalDeyimi(isimler)

    def dogrula_deyimi(self):
        self.ilerle()  # dogrula
        kosul = self.ifade()
        mesaj = None
        if self.tip() == T.VIRGUL:
            self.ilerle()
            mesaj = self.ifade()
        return DogrulaDeyimi(kosul, mesaj)

    def eslestir_deyimi(self):
        self.ilerle()  # eslestir
        deger = self.ifade()
        self.beklenen(T.IKINOKTA)
        self.beklenen(T.YENISATIR)
        self.bosluklari_atla()
        self.beklenen(T.GIRINTI, "Girinti bekleniyordu (eslestir bloğu)")
        durumlar = []
        while self.tip() == T.HAL:
            self.ilerle()
            desen = self.desen_ayristir()
            guard = None
            if self.tip() == T.EGER:
                self.ilerle()
                guard = self.ifade()
            govde = self.blok()
            durumlar.append((desen, guard, govde))
            self.bosluklari_atla()
        self.beklenen(T.CIKINTI)
        return EslestirDeyimi(deger, durumlar)

    def desen_ayristir(self):
        secenekler = [self._desen_temel()]
        while self.tip() == T.VEYA:
            self.ilerle()
            secenekler.append(self._desen_temel())
        if len(secenekler) == 1:
            return secenekler[0]
        return DesenVeya(secenekler)

    def _desen_temel(self):
        tok = self.su_an()
        if tok.tip == T.SAYI:
            self.ilerle(); return SayiLiteral(tok.deger)
        if tok.tip == T.STRING:
            self.ilerle(); return StringLiteral(tok.deger)
        if tok.tip == T.DOGRU:
            self.ilerle(); return BoolLiteral(True)
        if tok.tip == T.YANLIS:
            self.ilerle(); return BoolLiteral(False)
        if tok.tip == T.BOS:
            self.ilerle(); return NoneLiteral()
        if tok.tip == T.EKSI:
            self.ilerle()
            sayi_tok = self.beklenen(T.SAYI)
            return UnaryOp(T.EKSI, SayiLiteral(sayi_tok.deger))
        if tok.tip == T.IDENT:
            self.ilerle(); return DesenYakala(tok.deger)
        if tok.tip == T.PARANAC:
            self.ilerle()
            elemanlar = []
            while self.tip() != T.PARANKAPA:
                elemanlar.append(self.desen_ayristir())
                if self.tip() == T.VIRGUL:
                    self.ilerle()
            self.beklenen(T.PARANKAPA)
            return DesenDizi(elemanlar, True)
        if tok.tip == T.KOSEAC:
            self.ilerle()
            elemanlar = []
            while self.tip() != T.KOSEKAPA:
                elemanlar.append(self.desen_ayristir())
                if self.tip() == T.VIRGUL:
                    self.ilerle()
            self.beklenen(T.KOSEKAPA)
            return DesenDizi(elemanlar, False)
        raise ParserHatasi(f"Satir {tok.satir}: Gecersiz desen (pattern): {tok.tip}")

    def ile_deyimi(self):
        self.ilerle()  # ile
        ifadeler = []
        while True:
            ifade = self.ifade()
            isim = None
            if self.tip() == T.IDENT and self.su_an().deger == "olarak":
                self.ilerle()
                isim = self.beklenen(T.IDENT).deger
            ifadeler.append((ifade, isim))
            if self.tip() == T.VIRGUL:
                self.ilerle()
                continue
            break
        govde = self.blok()
        return IleDeyimi(ifadeler, govde)

    def atama_veya_ifade(self):
        ifade1 = self.ifade()

        # tip belirtecli tanim: isim: tur veya isim: tur = deger
        if self.tip() == T.IKINOKTA and isinstance(ifade1, Identifier):
            self.ilerle()
            tur = self.ifade()
            deger = None
            if self.tip() == T.ESIT:
                self.ilerle()
                deger = self.ifade()
            return TipliAtama(ifade1, tur, deger)

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
        sonuc = self.veya_ifadesi()
        if self.tip() == T.EGER:
            self.ilerle()
            kosul = self.veya_ifadesi()
            self.beklenen(T.DEGILSE, "kosullu ifade icin 'degilse' bekleniyordu")
            yanlis_deger = self.ifade()
            return KosulluIfade(sonuc, kosul, yanlis_deger)
        return sonuc

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
        zincir = []
        while self.tip() in karsilastirma_tipleri:
            op_tok = self.ilerle()
            sag = self.toplama()
            zincir.append((op_tok.tip, sag))
        if zincir:
            sol = KarsilastirmaZinciri(sol, zincir)
        if self.tip() == T.ICINDE:
            self.ilerle()
            sag = self.toplama()
            sol = IcindeOp(sol, sag, olumsuz=False)
        elif self._degil_icinde_mi():
            self.ilerle()  # degil
            self.ilerle()  # icinde
            sag = self.toplama()
            sol = IcindeOp(sol, sag, olumsuz=True)
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
        if self.tip() == T.BEKLE:
            self.ilerle()
            return BeklemeIfadesi(self.birli())
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
                    if self.tip() == T.CARPI:
                        self.ilerle()
                        argumanlar.append(YildizAcma(self.ifade()))
                    elif self.tip() == T.US:
                        self.ilerle()
                        argumanlar.append(CiftYildizAcma(self.ifade()))
                    elif self.tip() == T.IDENT and self.ileri_bak().tip == T.ESIT:
                        kw_isim = self.ilerle().deger
                        self.ilerle()  # =
                        kw_deger = self.ifade()
                        kw_argumanlar.append((kw_isim, kw_deger))
                    else:
                        arg_ifade = self.ifade()
                        if self.tip() == T.ICIN and len(argumanlar) == 0 and not kw_argumanlar:
                            hedef, iterable, kosul = self._comprehension_hedef_ve_iterable()
                            arg_ifade = GeneratorIfadesi(arg_ifade, hedef, iterable, kosul)
                        argumanlar.append(arg_ifade)
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
            if self.ileri_bak().tip == T.WALRUS:
                isim = self.ilerle().deger
                self.ilerle()  # :=
                deger = self.ifade()
                return YuruyenAtama(isim, deger)
            self.ilerle(); return Identifier(tok.deger)
        if tok.tip == T.PARANAC:
            self.ilerle()
            if self.tip() == T.PARANKAPA:
                self.ilerle(); return TupleLiteral([])
            ic = self.ifade()
            if self.tip() == T.ICIN:
                hedef, iterable, kosul = self._comprehension_hedef_ve_iterable()
                self.beklenen(T.PARANKAPA)
                return GeneratorIfadesi(ic, hedef, iterable, kosul)
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
            if self.tip() == T.KOSEKAPA:
                self.ilerle(); return ListeLiteral([])
            ilk = self.ifade()
            if self.tip() == T.ICIN:
                return self._liste_comprehension_tamamla(ilk)
            elemanlar = [ilk]
            while self.tip() == T.VIRGUL:
                self.ilerle()
                if self.tip() == T.KOSEKAPA:
                    break
                elemanlar.append(self.ifade())
            self.beklenen(T.KOSEKAPA)
            return ListeLiteral(elemanlar)
        if tok.tip == T.SUSLUAC:
            self.ilerle()
            if self.tip() == T.SUSLUKAPA:
                self.ilerle(); return SozlukLiteral([])
            ilk_ifade = self.ifade()
            if self.tip() == T.IKINOKTA:
                self.ilerle()
                ilk_deger = self.ifade()
                if self.tip() == T.ICIN:
                    return self._sozluk_comprehension_tamamla(ilk_ifade, ilk_deger)
                ciftler = [(ilk_ifade, ilk_deger)]
                while self.tip() == T.VIRGUL:
                    self.ilerle()
                    if self.tip() == T.SUSLUKAPA:
                        break
                    anahtar = self.ifade()
                    self.beklenen(T.IKINOKTA)
                    deger = self.ifade()
                    ciftler.append((anahtar, deger))
                self.beklenen(T.SUSLUKAPA)
                return SozlukLiteral(ciftler)
            elif self.tip() == T.ICIN:
                hedef, iterable, kosul = self._comprehension_hedef_ve_iterable()
                self.beklenen(T.SUSLUKAPA)
                return KumeComprehension(ilk_ifade, hedef, iterable, kosul)
            else:
                elemanlar = [ilk_ifade]
                while self.tip() == T.VIRGUL:
                    self.ilerle()
                    if self.tip() == T.SUSLUKAPA:
                        break
                    elemanlar.append(self.ifade())
                self.beklenen(T.SUSLUKAPA)
                return KumeLiteral(elemanlar)

        raise ParserHatasi(f"Satir {tok.satir}: Beklenmeyen token: {tok.tip} ({tok.deger!r})")

    def _comprehension_hedef_ve_iterable(self):
        self.ilerle()  # icin
        hedefler = [self.beklenen(T.IDENT).deger]
        while self.tip() == T.VIRGUL:
            self.ilerle()
            hedefler.append(self.beklenen(T.IDENT).deger)
        self.beklenen(T.ICINDE, "'icinde' bekleniyordu")
        iterable = self.veya_ifadesi()  # 'eger' ile celismesin diye ternary katmanini atla
        kosul = None
        if self.tip() == T.EGER:
            self.ilerle()
            kosul = self.veya_ifadesi()
        hedef = hedefler[0] if len(hedefler) == 1 else tuple(hedefler)
        return hedef, iterable, kosul

    def _liste_comprehension_tamamla(self, ifade):
        hedef, iterable, kosul = self._comprehension_hedef_ve_iterable()
        self.beklenen(T.KOSEKAPA)
        return ListeComprehension(ifade, hedef, iterable, kosul)

    def _sozluk_comprehension_tamamla(self, anahtar, deger):
        hedef, iterable, kosul = self._comprehension_hedef_ve_iterable()
        self.beklenen(T.SUSLUKAPA)
        return SozlukComprehension(anahtar, deger, hedef, iterable, kosul)
