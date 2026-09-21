# -*- coding: utf-8 -*-
"""
Tr-lang Lexer
Bu modul, Tr-lang kaynak kodunu token (kelime/sembol) dizisine ayirir.
Ornek: "eger x > 5:" -> [EGER, IDENT(x), GT, SAYI(5), IKINOKTA]
"""

# ---- Token tipleri ----
class TokenType:
    # Anahtar kelimeler
    EGER = "EGER"
    DEGILSE = "DEGILSE"
    YOKSA_EGER = "YOKSA_EGER"
    IKEN = "IKEN"          # while
    ICIN = "ICIN"          # for
    ICINDE = "ICINDE"      # in
    ISLEV = "ISLEV"        # def
    DONDUR = "DONDUR"      # return
    DOGRU = "DOGRU"        # True
    YANLIS = "YANLIS"      # False
    BOS = "BOS"            # None
    VE = "VE"              # and
    VEYA = "VEYA"          # or
    DEGIL = "DEGIL"        # not
    SINIF = "SINIF"        # class
    DENE = "DENE"          # try
    YAKALA = "YAKALA"      # except
    SONUNDA = "SONUNDA"    # finally
    DEVAM = "DEVAM"        # continue
    DUR = "DUR"            # break
    IMPORT = "IMPORT"      # import (aynen kalabilir ya da "getir")
    GETIR = "GETIR"        # import
    GLOBAL = "GLOBAL"      # global
    LAMBDA = "LAMBDA"      # lambda -> "kisa_islev"
    PASS = "PASS"          # gec
    ILE = "ILE"            # with
    URET = "URET"          # yield
    DOGRULA = "DOGRULA"    # assert
    NONLOCAL = "NONLOCAL"  # nonlocal
    ESLESTIR = "ESLESTIR"  # match
    HAL = "HAL"            # case
    WALRUS = "WALRUS"      # :=
    ESZAMANSIZ = "ESZAMANSIZ"  # async
    BEKLE = "BEKLE"        # await
    FIRLAT = "FIRLAT"      # raise

    # Temel
    IDENT = "IDENT"
    SAYI = "SAYI"
    STRING = "STRING"
    FSTRING = "FSTRING"
    YENISATIR = "YENISATIR"
    GIRINTI = "GIRINTI"      # INDENT
    CIKINTI = "CIKINTI"      # DEDENT
    EOF = "EOF"

    # Semboller / operatorler
    ARTI = "ARTI"
    EKSI = "EKSI"
    CARPI = "CARPI"
    BOL = "BOL"
    TAMBOL = "TAMBOL"     # //
    MOD = "MOD"           # %
    US = "US"             # **
    ESIT = "ESIT"         # =
    ARTI_ESIT = "ARTI_ESIT"    # +=
    EKSI_ESIT = "EKSI_ESIT"    # -=
    CARPI_ESIT = "CARPI_ESIT"  # *=
    BOL_ESIT = "BOL_ESIT"      # /=
    ESITESIT = "ESITESIT" # ==
    FARKLI = "FARKLI"     # !=
    BUYUK = "BUYUK"       # >
    KUCUK = "KUCUK"       # <
    BUYUKESIT = "BUYUKESIT"  # >=
    KUCUKESIT = "KUCUKESIT"  # <=
    PARANAC = "PARANAC"   # (
    PARANKAPA = "PARANKAPA"  # )
    KOSEAC = "KOSEAC"     # [
    KOSEKAPA = "KOSEKAPA" # ]
    SUSLUAC = "SUSLUAC"   # {
    SUSLUKAPA = "SUSLUKAPA"  # }
    VIRGUL = "VIRGUL"     # ,
    IKINOKTA = "IKINOKTA" # :
    NOKTA = "NOKTA"       # .
    AT = "AT"             # @
    OK = "OK"             # ->


KEYWORDS = {
    "eger": TokenType.EGER,
    "degilse": TokenType.DEGILSE,
    "yoksa_eger": TokenType.YOKSA_EGER,
    "iken": TokenType.IKEN,
    "icin": TokenType.ICIN,
    "icinde": TokenType.ICINDE,
    "islev": TokenType.ISLEV,
    "dondur": TokenType.DONDUR,
    "dogru": TokenType.DOGRU,
    "yanlis": TokenType.YANLIS,
    "bos": TokenType.BOS,
    "ve": TokenType.VE,
    "veya": TokenType.VEYA,
    "degil": TokenType.DEGIL,
    "sinif": TokenType.SINIF,
    "dene": TokenType.DENE,
    "yakala": TokenType.YAKALA,
    "sonunda": TokenType.SONUNDA,
    "devam": TokenType.DEVAM,
    "dur": TokenType.DUR,
    "getir": TokenType.GETIR,
    "global": TokenType.GLOBAL,
    "gec": TokenType.PASS,
    "ile": TokenType.ILE,
    "uret": TokenType.URET,
    "dogrula": TokenType.DOGRULA,
    "nonlocal": TokenType.NONLOCAL,
    "eslestir": TokenType.ESLESTIR,
    "hal": TokenType.HAL,
    "eszamansiz": TokenType.ESZAMANSIZ,
    "bekle": TokenType.BEKLE,
    "firlat": TokenType.FIRLAT,
}


class Token:
    def __init__(self, tip, deger, satir):
        self.tip = tip
        self.deger = deger
        self.satir = satir

    def __repr__(self):
        return f"Token({self.tip}, {self.deger!r}, satir={self.satir})"


class LexerHatasi(Exception):
    pass


def turkce_normalize(s):
    """Turkce karakterleri anahtar kelime karsilastirmasi icin normalize eder.
    Kullanicinin 'eğer', 'değilse' gibi Turkce harflerle yazmasina izin verir."""
    donusum = {
        "ğ": "g", "Ğ": "G",
        "ü": "u", "Ü": "U",
        "ş": "s", "Ş": "S",
        "ı": "i", "İ": "I",
        "ö": "o", "Ö": "O",
        "ç": "c", "Ç": "C",
    }
    for k, v in donusum.items():
        s = s.replace(k, v)
    return s


class Lexer:
    def __init__(self, kaynak):
        self.kaynak = kaynak
        self.pos = 0
        self.satir = 1
        self.tokenlar = []
        self.girinti_yigin = [0]  # indent stack
        self.paren_derinlik = 0   # ( [ { icindeyken yeni satir onemsiz

    def hata(self, mesaj):
        raise LexerHatasi(f"Satir {self.satir}: {mesaj}")

    def peek(self, ofset=0):
        i = self.pos + ofset
        if i < len(self.kaynak):
            return self.kaynak[i]
        return "\0"

    def ilerle(self):
        c = self.peek()
        self.pos += 1
        if c == "\n":
            self.satir += 1
        return c

    def token_ekle(self, tip, deger=None):
        self.tokenlar.append(Token(tip, deger, self.satir))

    def calistir(self):
        satir_basi = True
        while self.peek() != "\0":
            if satir_basi and self.paren_derinlik == 0:
                self._girinti_isle()
                satir_basi = False
                continue

            c = self.peek()

            if c == "\n":
                self.ilerle()
                if self.paren_derinlik == 0:
                    self.token_ekle(TokenType.YENISATIR)
                    satir_basi = True
                continue

            if c in " \t":
                self.ilerle()
                continue

            if c == "#":
                while self.peek() not in ("\n", "\0"):
                    self.ilerle()
                continue

            if c.isdigit():
                self._sayi_oku()
                continue

            if c in ('"', "'"):
                self._string_oku()
                continue

            if c in ("f", "F") and self.peek(1) in ('"', "'"):
                self.ilerle()  # 'f' harfini gec
                self._fstring_oku()
                continue

            if c.isalpha() or c == "_" or c in "ğüşıöçĞÜŞİÖÇ":
                self._kimlik_oku()
                continue

            self._sembol_oku()

        # Dosya sonunda acik kalan girintileri kapat
        while self.girinti_yigin[-1] > 0:
            self.girinti_yigin.pop()
            self.token_ekle(TokenType.CIKINTI)
        self.token_ekle(TokenType.EOF)
        return self.tokenlar

    def _girinti_isle(self):
        # Bos satirlari ve sadece-yorum iceren satirlari atlayarak,
        # girinti hesabini gercek icerigi olan bir sonraki satira gore yap.
        while True:
            sayac = 0
            while self.peek() in (" ", "\t"):
                sayac += 1 if self.peek() == " " else 4  # tab = 4 bosluk say
                self.ilerle()

            if self.peek() == "#":
                while self.peek() not in ("\n", "\0"):
                    self.ilerle()

            if self.peek() == "\n":
                self.ilerle()
                continue  # bos/yorum satiri idi, bir sonraki satira gec

            break  # gercek icerik iceren bir satira ulastik

        if self.peek() == "\0":
            return

        mevcut = self.girinti_yigin[-1]
        if sayac > mevcut:
            self.girinti_yigin.append(sayac)
            self.token_ekle(TokenType.GIRINTI)
        elif sayac < mevcut:
            while self.girinti_yigin[-1] > sayac:
                self.girinti_yigin.pop()
                self.token_ekle(TokenType.CIKINTI)
            if self.girinti_yigin[-1] != sayac:
                self.hata("Girinti (indentation) uyumsuz")

    def _sayi_oku(self):
        baslangic = self.pos
        while self.peek().isdigit():
            self.ilerle()
        if self.peek() == "." and self.peek(1).isdigit():
            self.ilerle()
            while self.peek().isdigit():
                self.ilerle()
        metin = self.kaynak[baslangic:self.pos]
        deger = float(metin) if "." in metin else int(metin)
        self.token_ekle(TokenType.SAYI, deger)

    def _string_oku(self):
        tirnak = self.ilerle()  # ' veya "
        baslangic = self.pos
        parcalar = []
        while self.peek() != tirnak:
            if self.peek() == "\0":
                self.hata("Kapatilmamis string")
            if self.peek() == "\\":
                self.ilerle()
                kacis = self.ilerle()
                escape_map = {"n": "\n", "t": "\t", "\\": "\\", "'": "'", '"': '"'}
                parcalar.append(escape_map.get(kacis, kacis))
            else:
                parcalar.append(self.ilerle())
        self.ilerle()  # kapanis tirnagi
        self.token_ekle(TokenType.STRING, "".join(parcalar))

    def _fstring_oku(self):
        """f\"...{ifade}...\" bicimli string'leri okur. {} icindeki metni
        oldugu gibi (ham) saklar, codegen asamasinda islenir."""
        tirnak = self.ilerle()  # ' veya "
        parcalar = []
        while self.peek() != tirnak:
            if self.peek() == "\0":
                self.hata("Kapatilmamis f-string")
            if self.peek() == "\\":
                self.ilerle()
                kacis = self.ilerle()
                escape_map = {"n": "\n", "t": "\t", "\\": "\\", "'": "'", '"': '"'}
                parcalar.append(escape_map.get(kacis, kacis))
            elif self.peek() == "{":
                parcalar.append(self.ilerle())  # '{'
                derinlik = 1
                while derinlik > 0:
                    ch = self.peek()
                    if ch == "\0":
                        self.hata("Kapatilmamis f-string ifadesi ({...})")
                    if ch == "{":
                        derinlik += 1
                    elif ch == "}":
                        derinlik -= 1
                    parcalar.append(self.ilerle())
            else:
                parcalar.append(self.ilerle())
        self.ilerle()  # kapanis tirnagi
        self.token_ekle(TokenType.FSTRING, "".join(parcalar))

    def _kimlik_oku(self):
        baslangic = self.pos
        while self.peek().isalnum() or self.peek() == "_" or self.peek() in "ğüşıöçĞÜŞİÖÇ":
            self.ilerle()
        metin = self.kaynak[baslangic:self.pos]
        normalize = turkce_normalize(metin).lower()
        if normalize in KEYWORDS:
            self.token_ekle(KEYWORDS[normalize], metin)
        else:
            self.token_ekle(TokenType.IDENT, metin)

    def _sembol_oku(self):
        c = self.ilerle()
        n = self.peek()

        iki_karakter = {
            ("=", "="): TokenType.ESITESIT,
            ("!", "="): TokenType.FARKLI,
            (">", "="): TokenType.BUYUKESIT,
            ("<", "="): TokenType.KUCUKESIT,
            ("/", "/"): TokenType.TAMBOL,
            ("*", "*"): TokenType.US,
            ("+", "="): TokenType.ARTI_ESIT,
            ("-", "="): TokenType.EKSI_ESIT,
            ("*", "="): TokenType.CARPI_ESIT,
            ("/", "="): TokenType.BOL_ESIT,
            (":", "="): TokenType.WALRUS,
            ("-", ">"): TokenType.OK,
        }
        if (c, n) in iki_karakter:
            self.ilerle()
            self.token_ekle(iki_karakter[(c, n)])
            return

        tek_karakter = {
            "+": TokenType.ARTI,
            "-": TokenType.EKSI,
            "*": TokenType.CARPI,
            "/": TokenType.BOL,
            "%": TokenType.MOD,
            "=": TokenType.ESIT,
            ">": TokenType.BUYUK,
            "<": TokenType.KUCUK,
            ",": TokenType.VIRGUL,
            ":": TokenType.IKINOKTA,
            ".": TokenType.NOKTA,
            "@": TokenType.AT,
        }
        if c in tek_karakter:
            self.token_ekle(tek_karakter[c])
            return

        parantezler = {
            "(": TokenType.PARANAC, ")": TokenType.PARANKAPA,
            "[": TokenType.KOSEAC, "]": TokenType.KOSEKAPA,
            "{": TokenType.SUSLUAC, "}": TokenType.SUSLUKAPA,
        }
        if c in parantezler:
            if c in "([{":
                self.paren_derinlik += 1
            else:
                self.paren_derinlik -= 1
            self.token_ekle(parantezler[c])
            return

        self.hata(f"Bilinmeyen karakter: {c!r}")


if __name__ == "__main__":
    ornek = '''
eger x > 5:
    yazdir("buyuk")
degilse:
    yazdir("kucuk")
'''
    lex = Lexer(ornek)
    for t in lex.calistir():
        print(t)
