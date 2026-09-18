# Tr-lang

Python'un üzerine inşa edilmiş, **Türkçe anahtar kelimelerle kod yazmanı sağlayan** bir programlama dili.

> 🚧 Bu proje aktif olarak geliştiriliyor (work in progress). Temel özellikler çalışıyor, bazı ileri seviye özellikler henüz eklenmedi. Aşağıda hem neyin çalıştığını hem de eksikleri şeffafça listeliyoruz.

## Örnek

```
islev selamla(isim):
    dondur f"Merhaba, {isim}!"

yazdir(selamla("Dünya"))

sayilar = [1, 2, 3, 4, 5]
toplam = 0
icin s icinde sayilar:
    eger s % 2 == 0:
        toplam += s
yazdir(f"Cift sayilarin toplami: {toplam}")
```

## Nasıl çalışıyor?

Tr-lang, Python'u yeniden yazmıyor. Türkçe kodunu okuyup gerçek Python koduna çeviriyor
(bir "transpiler"), sonra Python'un kendi motoruyla çalıştırıyor. Bu sayede Python'un
gücünden (hız, kütüphaneler, veri yapıları) doğrudan faydalanıyoruz.

```
Tr-lang kodu → Lexer (tokenlara ayırma) → Parser (AST oluşturma) → Codegen (Python kodu üretme) → exec()
```

## Kurulum ve Çalıştırma

Python 3.8+ gerekli, başka bağımlılık yok.

```bash
# Bir dosya çalıştırmak için:
python3 trlang.py ornekler/01_temel_yapilar.trl

# Üretilen Python kodunu da görmek için:
python3 trlang.py dosya.trl --python-goster

# İnteraktif kabuk (REPL):
python3 repl.py
```

## Desteklenen Özellikler

| Türkçe | Karşılığı |
|---|---|
| `eger` / `yoksa_eger` / `degilse` | if / elif / else |
| `iken` | while |
| `icin ... icinde` | for ... in |
| `islev` | def |
| `dondur` | return |
| `sinif` | class |
| `dene` / `yakala` / `sonunda` | try / except / finally |
| `dur` / `devam` / `gec` | break / continue / pass |
| `dogru` / `yanlis` / `bos` | True / False / None |
| `ve` / `veya` / `degil` | and / or / not |
| `icinde` | in |
| `getir` | import |

Ayrıca: listeler, sözlükler, tuple'lar, dilimleme (`liste[1:3]`), `+=`/`-=`/`*=`/`/=`,
f-string (`f"Değer: {x}"`), Türkçeleştirilmiş hata mesajları, ve yaygın yerleşik
fonksiyonlar (`yazdir`, `uzunluk`, `aralik`, `tur`, `tamsayi` vb. — tam liste için
`trlang_builtins.py`).

## Henüz Eklenmedi

Şeffaf olalım — bunlar bilinen eksikler, katkıda bulunmak istersen iyi başlangıç noktaları:

- List/dict comprehension (`[x*x for x in liste]` gibi kısa yazımlar)
- Decorator desteği (`@bir_şey`)
- `with` deyimi (bağlam yöneticileri)
- `yield` / generator desteği
- `dene/yakala` içinde yakalanan hatanın kendisi hâlâ İngilizce mesaj veriyor
- f-string içinde iç içe tırnak kullanımı (`f"{sozluk['anahtar']}"`) sorunlu olabilir
- Standart kütüphane modül isimleri Türkçeleştirilmedi (`getir math` çalışır, `getir matematik` çalışmaz)
- Otomatik/düzenli test paketi yok, şu ana kadar elle test edildi

## Proje Yapısı

```
lexer.py            - kaynak kodu token'lara ayırır
ast_nodes.py         - AST (soyut sözdizim ağacı) düğüm tanımları
parser.py            - token'lardan AST oluşturur
codegen.py           - AST'den gerçek Python kodu üretir
trlang_builtins.py   - Türkçe yerleşik fonksiyonlar ve hata mesajları
trlang.py            - ana çalıştırıcı (dosya çalıştırma)
repl.py              - interaktif kabuk
ornekler/            - örnek .trl programları
```

## Katkıda Bulunma

Bu bir öğrenme projesi olarak başladı, ama gerçek katkılara açık. Issue açabilir,
pull request gönderebilirsin.

## Lisans

MIT — [LICENSE](LICENSE) dosyasına bak.
