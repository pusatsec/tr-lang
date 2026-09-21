# -*- coding: utf-8 -*-
"""
Tr-lang Yerlesik Fonksiyonlar (Builtins)
Turkce fonksiyon isimlerini gercek Python karsiliklarina baglar.
Bu sozluk, uretilen kodun calisma ortamina (globals) enjekte edilir.
"""

TURKCE_HATA_ISIMLERI = {
    "ZeroDivisionError": "SifiraBolmeHatasi",
    "ValueError": "DegerHatasi",
    "TypeError": "TipHatasi",
    "IndexError": "IndeksHatasi",
    "KeyError": "AnahtarHatasi",
    "AttributeError": "OznitelikHatasi",
    "FileNotFoundError": "DosyaBulunamadiHatasi",
    "NameError": "IsimHatasi",
    "ImportError": "IceAktarmaHatasi",
    "StopIteration": "YinelemeDurdu",
    "RecursionError": "OzyinelemeHatasi",
    "OverflowError": "TasmaHatasi",
    "MemoryError": "BellekHatasi",
    "NotImplementedError": "UygulanmamisHatasi",
    "PermissionError": "IzinHatasi",
    "TimeoutError": "ZamanAsimiHatasi",
    "UnicodeError": "KarakterKodlamaHatasi",
    "AssertionError": "DogrulamaHatasi",
}

TURKCE_HATA_ACIKLAMALARI = {
    "ZeroDivisionError": "Bir sayi sifira bolunmeye calisildi",
    "IndexError": "Listede/dizide olmayan bir sira numarasina erisilmeye calisildi",
    "KeyError": "Sozlukte olmayan bir anahtara erisilmeye calisildi",
    "TypeError": "Yanlis veri tipiyle islem yapilmaya calisildi",
    "ValueError": "Fonksiyona uygun olmayan bir deger verildi",
    "AttributeError": "Nesnede olmayan bir ozellik/metod cagrildi",
    "NameError": "Tanimlanmamis bir degisken kullanildi",
    "FileNotFoundError": "Belirtilen dosya bulunamadi",
    "RecursionError": "Fonksiyon kendini cok fazla kez cagirdi (sonsuz dongu olabilir)",
}


def _turkce_mesaj_olustur(ingilizce_isim, detay):
    turkce_isim = TURKCE_HATA_ISIMLERI.get(ingilizce_isim, ingilizce_isim)
    aciklama = TURKCE_HATA_ACIKLAMALARI.get(ingilizce_isim)
    if aciklama:
        if detay:
            return f"{turkce_isim}: {aciklama} ({detay})"
        return f"{turkce_isim}: {aciklama}"
    if detay:
        return f"{turkce_isim}: {detay}"
    return turkce_isim


def turkce_hata_mesaji(exc):
    """Bir Python exception'ini Turkce, ogrenci-dostu bir mesaja cevirir."""
    return _turkce_mesaj_olustur(type(exc).__name__, str(exc))


class TrlangHataSarici:
    """Eskiden kullanilan sarma sinifi; artik _trhata dogrudan __class__
    degistirerek calisiyor ama geriye donuk uyumluluk icin birakildi."""

    def __init__(self, orijinal):
        object.__setattr__(self, "_orijinal", orijinal)

    def __str__(self):
        return turkce_hata_mesaji(self._orijinal)

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, isim):
        return getattr(self._orijinal, isim)

    def __eq__(self, other):
        return self._orijinal == other

    @property
    def orijinal_hata(self):
        return self._orijinal


_TURKCE_HATA_SINIF_ONBELLEGI = {}


def _trhata(exc):
    """Yakalanan hatayla ayni bilgilere sahip, ama str()/repr() cagrildiginda
    Turkce mesaj gosteren yeni bir hata nesnesi olusturur. tur(hata) ve
    ornek_mi(hata, X) hala dogru sonuc verir, cunku yeni sinif orijinalin
    alt sinifidir (Python yerlesik exception'larda __class__ degistirmeye
    izin vermedigi icin bu sekilde yapiyoruz)."""
    orijinal_sinif = type(exc)
    yeni_sinif = _TURKCE_HATA_SINIF_ONBELLEGI.get(orijinal_sinif)
    if yeni_sinif is None:
        def _yeni_str(self, _osinif=orijinal_sinif):
            return _turkce_mesaj_olustur(_osinif.__name__, _osinif.__str__(self))

        yeni_sinif = type(
            orijinal_sinif.__name__,
            (orijinal_sinif,),
            {
                "__str__": _yeni_str,
                "__repr__": _yeni_str,
            },
        )
        _TURKCE_HATA_SINIF_ONBELLEGI[orijinal_sinif] = yeni_sinif
    try:
        yeni_hata = yeni_sinif(*exc.args)
        yeni_hata.__dict__.update(getattr(exc, "__dict__", {}))
        yeni_hata.__traceback__ = exc.__traceback__
        yeni_hata.__cause__ = exc.__cause__
        return yeni_hata
    except Exception:
        return exc  # olusturulamazsa orijinal hatayi oldugu gibi don


def _yazdir(*args, **kwargs):
    print(*args, **kwargs)

def _tur(x):
    return type(x)

def _tamsayi(x=0):
    return int(x)

def _ondalik(x=0.0):
    return float(x)

def _metin(x=""):
    return str(x)

def _liste(*args):
    if len(args) == 0:
        return []
    return list(args[0])

def _sozluk(*args, **kwargs):
    if args:
        return dict(args[0])
    return dict(kwargs)

def _demet(*args):
    if len(args) == 0:
        return tuple()
    return tuple(args[0])

def _kume(*args):
    if len(args) == 0:
        return set()
    return set(args[0])

TRLANG_BUILTINS = {
    "_trhata": _trhata,

    # Girdi / cikti
    "yazdir": _yazdir,
    "girdi": input,

    # Tip donusumleri
    "tamsayi": _tamsayi,
    "ondalik": _ondalik,
    "metin": _metin,
    "liste": _liste,
    "sozluk": _sozluk,
    "demet": _demet,
    "kume": _kume,
    "tur": _tur,
    "bool_yap": bool,

    # Sayisal
    "mutlak": abs,
    "topla": sum,
    "maksimum": max,
    "minimum": min,
    "yuvarla": round,
    "us": pow,

    # Dizi / koleksiyon islemleri
    "uzunluk": len,
    "aralik": range,
    "siralanmis": sorted,
    "tersine": reversed,
    "numarali": enumerate,
    "birlikte": zip,
    "hepsi": all,
    "herhangi": any,
    "filtrele": filter,
    "esle": map,

    # Nesne / sinif
    "ornek_mi": isinstance,
    "alt_sinif_mi": issubclass,
    "ozellik_var_mi": hasattr,
    "ozellik_al": getattr,
    "ozellik_ayarla": setattr,

    # Genel
    "acik": open,
    "id_al": id,
    "girdi_al": input,

    # Sabitler
    "Dogru": True,
    "Yanlis": False,
    "Bos": None,

    # Yaygin hata (exception) tipleri - Turkce isimlerle de yakalanabilsin
    "Hata": Exception,
    "DegerHatasi": ValueError,
    "TipHatasi": TypeError,
    "IndeksHatasi": IndexError,
    "AnahtarHatasi": KeyError,
    "SifiraBolmeHatasi": ZeroDivisionError,
    "OznitelikHatasi": AttributeError,
    "DosyaBulunamadiHatasi": FileNotFoundError,
}

# Standart kutuphane modul isimlerinin Turkce karsiliklari.
# "getir matematik" dedigin zaman arka planda "import math as matematik"
# calisir, yani kod icinde de Turkce isimle (matematik.sqrt(16) gibi)
# erisebilirsin. Gercek Ingilizce ismiyle de (getir math) calismaya devam eder.
TURKCE_MODUL_ISIMLERI = {
    "matematik": "math",
    "rastgele": "random",
    "zaman": "time",
    "tarih": "datetime",
    "sistem": "sys",
    "isletim_sistemi": "os",
    "regex": "re",
    "duzenli_ifade": "re",
    "koleksiyonlar": "collections",
    "fonksiyonel_araclar": "functools",
    "yinelemeler": "itertools",
    "istatistik": "statistics",
    "kopyala": "copy",
    "dosya_yolu": "pathlib",
    "json_verisi": "json",
    "tablo_verisi": "csv",
    "veritabani": "sqlite3",
    "agirlik_kodlama": "hashlib",
    "kripto": "hashlib",
    "soket": "socket",
    "iplik": "threading",
    "surec": "multiprocessing",
    "test": "unittest",
    "hata_ayikla": "pdb",
    "komut_satiri": "argparse",
    "ortam_degiskenleri": "os",
    "sikistirma": "zipfile",
    "web_istek": "urllib",
    "e_posta": "email",
    "turkce_karakter": "locale",
}

