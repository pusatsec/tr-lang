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


def turkce_hata_mesaji(exc):
    """Bir Python exception'ini Turkce, ogrenci-dostu bir mesaja cevirir."""
    ingilizce_isim = type(exc).__name__
    turkce_isim = TURKCE_HATA_ISIMLERI.get(ingilizce_isim, ingilizce_isim)
    aciklama = TURKCE_HATA_ACIKLAMALARI.get(ingilizce_isim)
    detay = str(exc)
    if aciklama:
        if detay:
            return f"{turkce_isim}: {aciklama} ({detay})"
        return f"{turkce_isim}: {aciklama}"
    if detay:
        return f"{turkce_isim}: {detay}"
    return turkce_isim


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
