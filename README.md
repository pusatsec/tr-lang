# Tr-lang

Python'un üzerine inşa edilmiş, **Türkçe anahtar kelimelerle kod yazmanı sağlayan** bir programlama dili.

> 🚧 Bu proje aktif olarak geliştiriliyor (work in progress).

**💬 Hata mı buldun? Bir özellik mi eksik? [Issues sekmesinden](https://github.com/pusatsec/tr-lang/issues/new) yazabilirsin — her türlü geri bildirim, öneri ve soru için açık.**

## Örnek

```
islev selamla(isim):
    dondur f"Merhaba, {isim}!"

yazdir(selamla("Dünya"))

sayilar = [1, 2, 3, 4, 5]
toplam = topla(s * s icin s icinde sayilar eger s % 2 == 0)
yazdir(f"Cift sayilarin kareleri toplami: {toplam}")

eslestir toplam:
    hal 0:
        yazdir("Sifir")
    hal x eger x > 50:
        yazdir("Buyuk bir sayi")
    hal _:
        yazdir("Normal bir sayi")
```

## Nasıl çalışıyor?

Tr-lang, Python'u yeniden yazmıyor. Türkçe kodunu okuyup gerçek Python koduna çeviriyor
(bir "transpiler"), sonra Python'un kendi motoruyla çalıştırıyor. Bu sayede Python'un
gücünden (hız, kütüphaneler, veri yapıları) doğrudan faydalanıyoruz.

```
Tr-lang kodu → Lexer (tokenlara ayırma) → Parser (AST oluşturma) → Codegen (Python kodu üretme) → exec()
```

## Kurulum ve Çalıştırma

Python 3.10+ önerilir (match/case için), başka bağımlılık yok.

```bash
# Bir dosya çalıştırmak için:
python3 trlang.py ornekler/01_temel_yapilar.trl

# Üretilen Python kodunu da görmek için:
python3 trlang.py dosya.trl --python-goster

# İnteraktif kabuk (REPL):
python3 repl.py

# Otomatik test paketini çalıştırmak için:
python3 test_calistir.py
```

## Desteklenen Özellikler

| Türkçe | Karşılığı |
|---|---|
| `eger` / `yoksa_eger` / `degilse` | if / elif / else |
| `iken` | while |
| `icin ... icinde` | for ... in |
| `islev` | def |
| `dondur` | return |
| `uret` / `uret hepsinden` | yield / yield from |
| `sinif` | class |
| `dene` / `yakala` / `sonunda` | try / except / finally |
| `dur` / `devam` / `gec` | break / continue / pass |
| `dogru` / `yanlis` / `bos` | True / False / None |
| `ve` / `veya` / `degil` | and / or / not |
| `icinde` / `degil icinde` | in / not in |
| `getir` | import |
| `ile ... olarak` | with ... as |
| `dogrula` | assert |
| `nonlocal` | nonlocal |
| `eslestir` / `hal` | match / case |
| `eszamansiz` / `bekle` | async / await |
| `X eger K degilse Y` | X if K else Y (ternary) |
| `:=` | walrus operatörü |

Ayrıca: listeler, sözlükler, tuple'lar, set'ler, dilimleme (`liste[1:3]`), comprehension
(liste/sözlük/set/generator), `+=`/`-=`/`*=`/`/=`, `*args`/`**kwargs`, decorator (`@...`),
çoklu kalıtım + `super()`, çoklu exception yakalama, f-string (format belirteçleri dahil,
`{x:.2f}`), type hinting, Türkçeleştirilmiş hata mesajları, ve standart kütüphanenin
popüler modüllerine Türkçe isim (`getir matematik`, `getir rastgele`, `getir zaman` vb.
tam liste için `trlang_builtins.py`).

## Testler

`testler/` klasöründe her `.trl` dosyasının bir `.beklenen` (beklenen çıktı) eşi var.
Yeni bir özellik eklediğinde veya bir şeyi değiştirdiğinde:

```bash
python3 test_calistir.py            # tum testleri calistir, kirmizi/yesil goster
python3 test_calistir.py --guncelle # yeni davranisi 'dogru cevap' olarak kaydet
```

## Henüz Eklenmedi

- Metaclass, `__slots__` gibi çok ileri seviye OOP özellikleri
- `async for` / `async with` (sadece `async def` / `await` var)
- Tam standart kütüphane kapsamı (şu an ~30 popüler modül Türkçeleştirildi)

## Proje Yapısı

```
lexer.py             - kaynak kodu token'lara ayırır
ast_nodes.py          - AST (soyut sözdizim ağacı) düğüm tanımları
parser.py             - token'lardan AST oluşturur
codegen.py            - AST'den gerçek Python kodu üretir
trlang_builtins.py    - Türkçe yerleşik fonksiyonlar, hata mesajları, modül isimleri
trlang.py             - ana çalıştırıcı (dosya çalıştırma)
repl.py               - interaktif kabuk
test_calistir.py      - otomatik test paketi
testler/              - test programları + beklenen çıktıları
ornekler/             - örnek .trl programları
```

## Katkıda Bulunma

Bu bir öğrenme projesi olarak başladı, ama gerçek katkılara açık.
[Issue açabilir](https://github.com/pusatsec/tr-lang/issues/new) (hata bildirimi, özellik
isteği, soru — hepsi olur) ya da pull request gönderebilirsin.

## Lisans

MIT — [LICENSE](LICENSE) dosyasına bak.

