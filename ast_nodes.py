# -*- coding: utf-8 -*-
"""
Tr-lang AST (Soyut Sozdizim Agaci) Dugumleri
Parser bu siniflardan bir agac olusturur, codegen bu agaci gercek Python koduna cevirir.
"""

class Node:
    pass

# ---- Ifadeler (Expressions) ----
class SayiLiteral(Node):
    def __init__(self, deger): self.deger = deger

class StringLiteral(Node):
    def __init__(self, deger): self.deger = deger

class FStringLiteral(Node):
    def __init__(self, ham_metin): self.ham_metin = ham_metin

class BoolLiteral(Node):
    def __init__(self, deger): self.deger = deger

class KosulluIfade(Node):  # ternary: X eger kosul degilse Y
    def __init__(self, dogru_deger, kosul, yanlis_deger):
        self.dogru_deger, self.kosul, self.yanlis_deger = dogru_deger, kosul, yanlis_deger

class NoneLiteral(Node):
    pass

class Identifier(Node):
    def __init__(self, isim): self.isim = isim

class ListeLiteral(Node):
    def __init__(self, elemanlar): self.elemanlar = elemanlar

class ListeComprehension(Node):
    def __init__(self, ifade, degisken, iterable, kosul=None):
        self.ifade, self.degisken, self.iterable, self.kosul = ifade, degisken, iterable, kosul

class SozlukComprehension(Node):
    def __init__(self, anahtar, deger, degisken, iterable, kosul=None):
        self.anahtar, self.deger = anahtar, deger
        self.degisken, self.iterable, self.kosul = degisken, iterable, kosul

class GeneratorIfadesi(Node):  # (x for x in liste)
    def __init__(self, ifade, degisken, iterable, kosul=None):
        self.ifade, self.degisken, self.iterable, self.kosul = ifade, degisken, iterable, kosul

class KumeLiteral(Node):  # {1, 2, 3}
    def __init__(self, elemanlar): self.elemanlar = elemanlar

class KumeComprehension(Node):  # {x for x in liste}
    def __init__(self, ifade, degisken, iterable, kosul=None):
        self.ifade, self.degisken, self.iterable, self.kosul = ifade, degisken, iterable, kosul

class SozlukLiteral(Node):
    def __init__(self, ciftler): self.ciftler = ciftler  # [(key, value), ...]

class TupleLiteral(Node):
    def __init__(self, elemanlar): self.elemanlar = elemanlar

class BinOp(Node):
    def __init__(self, sol, op, sag):
        self.sol, self.op, self.sag = sol, op, sag

class KarsilastirmaZinciri(Node):  # a < b < c gibi zincirleme karsilastirmalar
    def __init__(self, ilk, zincir):
        self.ilk = ilk
        self.zincir = zincir  # [(op_tip, operand_node), ...]

class UnaryOp(Node):
    def __init__(self, op, ifade):
        self.op, self.ifade = op, ifade

class BoolOp(Node):
    def __init__(self, op, degerler):  # op: 've' / 'veya'
        self.op, self.degerler = op, degerler

class NotOp(Node):
    def __init__(self, ifade): self.ifade = ifade

class IcindeOp(Node):  # membership test: x icinde y  ->  x in y
    def __init__(self, eleman, koleksiyon, olumsuz=False):
        self.eleman, self.koleksiyon, self.olumsuz = eleman, koleksiyon, olumsuz

class Cagri(Node):  # function call
    def __init__(self, fonksiyon, argumanlar, kw_argumanlar=None):
        self.fonksiyon = fonksiyon
        self.argumanlar = argumanlar
        self.kw_argumanlar = kw_argumanlar or []  # [(isim, deger), ...]

class Oznitelik(Node):  # attribute access: obj.attr
    def __init__(self, obje, isim): self.obje, self.isim = obje, isim

class Indeksleme(Node):  # obj[expr]
    def __init__(self, obje, indeks): self.obje, self.indeks = obje, indeks

class DilimlemeIndeks(Node):  # obj[a:b:c]
    def __init__(self, baslangic, bitis, adim):
        self.baslangic, self.bitis, self.adim = baslangic, bitis, adim

class LambdaIfade(Node):
    def __init__(self, parametreler, govde):
        self.parametreler, self.govde = parametreler, govde

class YuruyenAtama(Node):  # walrus: (x := ifade)
    def __init__(self, isim, deger): self.isim, self.deger = isim, deger

class BeklemeIfadesi(Node):  # await ifade
    def __init__(self, ifade): self.ifade = ifade

class TipliAtama(Node):  # isim: tur = deger  (type hint'li atama/tanim)
    def __init__(self, hedef, tur, deger=None):
        self.hedef, self.tur, self.deger = hedef, tur, deger

class YildizAcma(Node):  # *args kullanimda acma: fonksiyon(*liste)
    def __init__(self, ifade): self.ifade = ifade

class CiftYildizAcma(Node):  # **kwargs kullanimda acma: fonksiyon(**sozluk)
    def __init__(self, ifade): self.ifade = ifade

# ---- Deyimler (Statements) ----
class Program(Node):
    def __init__(self, govde): self.govde = govde

class Atama(Node):
    def __init__(self, hedef, deger, op="="):
        self.hedef, self.deger, self.op = hedef, deger, op

class CokluAtama(Node):  # a, b = 1, 2
    def __init__(self, hedefler, deger):
        self.hedefler, self.deger = hedefler, deger

class IfadeDeyimi(Node):  # bare expression as statement (e.g. function call)
    def __init__(self, ifade): self.ifade = ifade

class EgerDeyimi(Node):
    def __init__(self, kosul, govde, elif_dallari, else_govde):
        self.kosul = kosul
        self.govde = govde
        self.elif_dallari = elif_dallari  # [(kosul, govde), ...]
        self.else_govde = else_govde

class IkenDeyimi(Node):  # while
    def __init__(self, kosul, govde):
        self.kosul, self.govde = kosul, govde

class IcinDeyimi(Node):  # for
    def __init__(self, degisken, iterable, govde):
        self.degisken, self.iterable, self.govde = degisken, iterable, govde

class IslevTanimi(Node):  # def
    def __init__(self, isim, parametreler, govde, varsayilanlar=None, dekoratorler=None, eszamansiz=False, param_tipleri=None, donus_tipi=None):
        self.isim = isim
        self.parametreler = parametreler
        self.govde = govde
        self.varsayilanlar = varsayilanlar or {}
        self.dekoratorler = dekoratorler or []
        self.eszamansiz = eszamansiz
        self.param_tipleri = param_tipleri or {}
        self.donus_tipi = donus_tipi

class DondurDeyimi(Node):  # return
    def __init__(self, deger): self.deger = deger

class UretDeyimi(Node):  # yield
    def __init__(self, deger): self.deger = deger

class UretHepsindenDeyimi(Node):  # yield from
    def __init__(self, ifade): self.ifade = ifade

class SinifTanimi(Node):  # class
    def __init__(self, isim, ustler, govde, dekoratorler=None):
        self.isim, self.ustler, self.govde = isim, ustler, govde
        self.dekoratorler = dekoratorler or []

class DeneDeyimi(Node):  # try/except/finally
    def __init__(self, govde, yakalamalar, sonunda_govde):
        self.govde = govde
        self.yakalamalar = yakalamalar  # [(hata_tipi, isim, govde), ...]
        self.sonunda_govde = sonunda_govde

class DurDeyimi(Node):  # break
    pass

class DevamDeyimi(Node):  # continue
    pass

class GecDeyimi(Node):  # pass
    pass

class GetirDeyimi(Node):  # import
    def __init__(self, modul, takma_ad=None):
        self.modul, self.takma_ad = modul, takma_ad

class GlobalDeyimi(Node):
    def __init__(self, isimler): self.isimler = isimler

class NonlocalDeyimi(Node):
    def __init__(self, isimler): self.isimler = isimler

class DogrulaDeyimi(Node):  # assert
    def __init__(self, kosul, mesaj=None):
        self.kosul, self.mesaj = kosul, mesaj

class EslestirDeyimi(Node):  # match
    def __init__(self, deger, durumlar):
        self.deger = deger
        self.durumlar = durumlar  # [(desen, guard_veya_None, govde), ...]

class DesenYakala(Node):  # match icinde: degisken yakalama veya '_' joker
    def __init__(self, isim): self.isim = isim

class DesenDizi(Node):  # match icinde: (a, b) veya [a, b] desen
    def __init__(self, elemanlar, parantez_mi):
        self.elemanlar, self.parantez_mi = elemanlar, parantez_mi

class DesenVeya(Node):  # match icinde: desen1 veya desen2
    def __init__(self, secenekler): self.secenekler = secenekler

class IleDeyimi(Node):  # with
    def __init__(self, ifadeler, govde):
        self.ifadeler = ifadeler  # [(ifade, isim_veya_None), ...]
        self.govde = govde
