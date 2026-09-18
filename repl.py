# -*- coding: utf-8 -*-
"""
Tr-lang REPL (Read-Eval-Print Loop)
Kullanim: python3 repl.py
Interaktif olarak Tr-lang kodu yazip aninda sonucunu gorebilirsin.
"""

from lexer import Lexer, LexerHatasi
from parser import Parser, ParserHatasi
from codegen import python_koduna_cevir, CodeGenHatasi
from trlang_builtins import TRLANG_BUILTINS, turkce_hata_mesaji

BANNER = """
Tr-lang REPL'ine hos geldin! (cikmak icin 'cik' veya 'exit' yaz)
Ornek: yazdir("Merhaba Dunya")
"""


def tek_ifade_mi_dene(kaynak_kod):
    """Girilen tek satirin bir ifade mi (deger dondurup ekrana basilmali) yoksa
    bir deyim mi (atama, if, def vs.) oldugunu anlamaya calisir. Basitce:
    ayristirip tek bir IfadeDeyimi ise deger olarak yazdiracagiz."""
    from ast_nodes import IfadeDeyimi
    lexer = Lexer(kaynak_kod)
    tokenlar = lexer.calistir()
    parser = Parser(tokenlar)
    ast_agaci = parser.ayristir()
    if len(ast_agaci.govde) == 1 and isinstance(ast_agaci.govde[0], IfadeDeyimi):
        return ast_agaci.govde[0].ifade
    return None


def coklu_satir_gerekli_mi(satir):
    """Satir ':' ile bitiyorsa (eger/icin/islev/sinif/iken/dene) daha fazla
    satir bekleniyor demektir - kullanicidan blok bitene kadar devam istenir."""
    satir_temiz = satir.rstrip()
    return satir_temiz.endswith(":")


def main():
    print(BANNER)
    calisma_ortami = dict(TRLANG_BUILTINS)
    calisma_ortami["__name__"] = "__main__"

    while True:
        try:
            satir = input("tr-lang> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGorusuruz!")
            break

        if satir.strip() in ("cik", "exit", "quit", "q"):
            print("Gorusuruz!")
            break
        if not satir.strip():
            continue

        tam_kod = satir
        # Blok gerektiren yapilar icin (eger/icin/islev/vs.) ek satirlar iste
        if coklu_satir_gerekli_mi(satir):
            girinti_seviyesi = 1
            while True:
                try:
                    ek_satir = input("......  ")
                except (EOFError, KeyboardInterrupt):
                    break
                if ek_satir.strip() == "":
                    break
                # Kullanici kendi girintisini yazmadiysa otomatik ekle
                if ek_satir[:1] not in (" ", "\t"):
                    ek_satir = ("    " * girinti_seviyesi) + ek_satir
                tam_kod += "\n" + ek_satir
                if ek_satir.rstrip().endswith(":"):
                    girinti_seviyesi += 1

        try:
            deger_ifadesi = None
            try:
                deger_ifadesi = tek_ifade_mi_dene(tam_kod)
            except Exception:
                pass

            if deger_ifadesi is not None:
                # Tek bir ifade girildiyse (ör: 2+2, x, faktoriyel(5)) sonucu yazdir
                from codegen import CodeGen
                gen = CodeGen()
                py_ifade = gen.uret(deger_ifadesi)
                sonuc = eval(py_ifade, calisma_ortami)
                if sonuc is not None:
                    print(repr(sonuc))
            else:
                lexer = Lexer(tam_kod)
                tokenlar = lexer.calistir()
                parser = Parser(tokenlar)
                ast_agaci = parser.ayristir()
                python_kodu = python_koduna_cevir(ast_agaci)
                derlenmis = compile(python_kodu, "<repl>", "exec")
                exec(derlenmis, calisma_ortami)

        except LexerHatasi as e:
            print(f"[Sozcuk Hatasi] {e}")
        except ParserHatasi as e:
            print(f"[Sozdizim Hatasi] {e}")
        except CodeGenHatasi as e:
            print(f"[Cevirme Hatasi] {e}")
        except Exception as e:
            print(f"[Calisma Zamani Hatasi] {turkce_hata_mesaji(e)}")


if __name__ == "__main__":
    main()
