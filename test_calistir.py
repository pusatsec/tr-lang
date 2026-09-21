# -*- coding: utf-8 -*-
"""
Tr-lang Otomatik Test Calistirici

Kullanim:
    python3 test_calistir.py              -> tum testleri calistirir, karsilastirir
    python3 test_calistir.py --guncelle    -> mevcut ciktilari 'dogru cevap' olarak kaydeder

testler/ klasorundeki her .trl dosyasi icin, ayni isimde bir .beklenen dosyasi
tutuyoruz. Bu dosya o programin CIKTISININ ne olmasi gerektigini icerir.
Test calistiginda gercek cikti ile bu dosya karsilastirilir; farkli ise test
KIRMIZI (basarisiz) olur.
"""

import sys
import io
import os
import contextlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trlang import trlang_calistir

TESTLER_KLASORU = os.path.join(os.path.dirname(os.path.abspath(__file__)), "testler")


def test_dosyalarini_bul():
    dosyalar = []
    for isim in sorted(os.listdir(TESTLER_KLASORU)):
        if isim.endswith(".trl"):
            dosyalar.append(isim)
    return dosyalar


def programi_calistir_ve_yakala(trl_yolu):
    with open(trl_yolu, "r", encoding="utf-8") as f:
        kaynak_kod = f.read()
    yakalanan_cikti = io.StringIO()
    with contextlib.redirect_stdout(yakalanan_cikti):
        trlang_calistir(kaynak_kod, dosya_adi=trl_yolu)
    return yakalanan_cikti.getvalue()


def guncelle_modu():
    dosyalar = test_dosyalarini_bul()
    for trl_dosya in dosyalar:
        trl_yolu = os.path.join(TESTLER_KLASORU, trl_dosya)
        beklenen_yolu = trl_yolu[:-4] + ".beklenen"
        cikti = programi_calistir_ve_yakala(trl_yolu)
        with open(beklenen_yolu, "w", encoding="utf-8") as f:
            f.write(cikti)
        print(f"[GUNCELLENDI] {trl_dosya}")
    print(f"\n{len(dosyalar)} test dosyasinin beklenen ciktisi guncellendi.")


def test_modu():
    dosyalar = test_dosyalarini_bul()
    basarili = 0
    basarisiz = 0
    basarisiz_listesi = []

    print(f"Tr-lang Test Paketi calisiyor... ({len(dosyalar)} test bulundu)\n")

    for trl_dosya in dosyalar:
        trl_yolu = os.path.join(TESTLER_KLASORU, trl_dosya)
        beklenen_yolu = trl_yolu[:-4] + ".beklenen"

        if not os.path.exists(beklenen_yolu):
            print(f"[ATLANDI]  {trl_dosya}  (beklenen dosya yok, --guncelle ile olustur)")
            continue

        with open(beklenen_yolu, "r", encoding="utf-8") as f:
            beklenen_cikti = f.read()

        try:
            gercek_cikti = programi_calistir_ve_yakala(trl_yolu)
        except Exception as e:
            gercek_cikti = f"[TEST CALISTIRICI HATASI] {e}"

        if gercek_cikti == beklenen_cikti:
            print(f"[BASARILI] {trl_dosya}")
            basarili += 1
        else:
            print(f"[BASARISIZ] {trl_dosya}")
            basarisiz += 1
            basarisiz_listesi.append((trl_dosya, beklenen_cikti, gercek_cikti))

    print(f"\n{'='*50}")
    print(f"Sonuc: {basarili} basarili, {basarisiz} basarisiz")
    print(f"{'='*50}")

    if basarisiz_listesi:
        print("\nBASARISIZ TESTLERIN DETAYI:\n")
        for isim, beklenen, gercek in basarisiz_listesi:
            print(f"--- {isim} ---")
            print("Beklenen:")
            print(beklenen)
            print("Gercek:")
            print(gercek)
            print()
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    if "--guncelle" in sys.argv:
        guncelle_modu()
    else:
        test_modu()
