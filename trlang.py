# -*- coding: utf-8 -*-
"""
Tr-lang Ana Calistirici
Kullanim: python3 trlang.py dosya.trl
"""

import sys
import traceback

from lexer import Lexer, LexerHatasi
from parser import Parser, ParserHatasi
from codegen import python_koduna_cevir, CodeGenHatasi
from trlang_builtins import TRLANG_BUILTINS, turkce_hata_mesaji


def trlang_calistir(kaynak_kod, dosya_adi="<trlang>", python_ciktisini_goster=False):
    try:
        lexer = Lexer(kaynak_kod)
        tokenlar = lexer.calistir()
    except LexerHatasi as e:
        print(f"[Sozcuk Hatasi] {e}")
        return

    try:
        parser = Parser(tokenlar)
        ast_agaci = parser.ayristir()
    except ParserHatasi as e:
        print(f"[Sozdizim Hatasi] {e}")
        return

    try:
        python_kodu = python_koduna_cevir(ast_agaci)
    except CodeGenHatasi as e:
        print(f"[Cevirme Hatasi] {e}")
        return

    if python_ciktisini_goster:
        print("---- Uretilen Python Kodu ----")
        print(python_kodu)
        print("-------------------------------")

    calisma_ortami = dict(TRLANG_BUILTINS)
    calisma_ortami["__name__"] = "__main__"

    try:
        derlenmis = compile(python_kodu, dosya_adi, "exec")
        exec(derlenmis, calisma_ortami)
    except Exception as e:
        print(f"[Calisma Zamani Hatasi] {turkce_hata_mesaji(e)}")
        # Hata ayiklama icin tam izleme istenirse:
        # traceback.print_exc()


def main():
    if len(sys.argv) < 2:
        print("Kullanim: python3 trlang.py dosya.trl [--python-goster]")
        sys.exit(1)

    dosya_yolu = sys.argv[1]
    python_goster = "--python-goster" in sys.argv

    with open(dosya_yolu, "r", encoding="utf-8") as f:
        kaynak_kod = f.read()

    trlang_calistir(kaynak_kod, dosya_adi=dosya_yolu, python_ciktisini_goster=python_goster)


if __name__ == "__main__":
    main()
