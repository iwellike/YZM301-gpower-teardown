# HALLUCINATIONS.md — Ajanın Yanlış Çıkarımları

Bu dosya, ajanın (ben) kanıtsız ama kendinden emin biçimde ileri sürdüğü ve
sonradan yanlış çıktığı ortaya çıkan en az 2 iddiayı belgeler. Amaç:
"Bunun kanıtı hangi fonksiyonda?" sorusunun önemini somutlaştırmak.

Format: her kayıt için (1) ajanın ilk iddiası, (2) hangi `[AJAN]` satırından
geldiği, (3) nasıl fark edildi, (4) hangi test/REA bulgusu yakaladı, (5)
düzeltme.

---

## 1. "A-priori N araması N=1'den başlayıp 1'er artırıyor"

**İlk iddia:** LEDGER.md §4'ün ilk taslağı, a-priori modun gerekli N'yi
"tipik güç analizi algoritması" varsayımıyla — küçük bir N'den başlayıp
`actual_power >= power` olana kadar N'yi teker teker artırarak — bulduğunu
öne sürdü. Bu, gözleme değil "böyle genelde yapılır" sezgisine dayanıyordu.
**Kaynak:** LEDGER.md §4 (Oturum 1 başlangıcındaki `[AJAN]` satırı).
**Nasıl fark edildi:** GPowerNT.exe'de REA ile `FUN_004a7140` (adres
`0x4a7140`) decompile edildiğinde, kodun doğrusal/+1 bir tarama değil,
**geometrik parantezleme (×1.2 / ÷1.2) + bisection** uyguladığı görüldü —
tamamen farklı bir algoritma ailesi.
**Yakalayan test/kanıt:** `procedure_pseudo_code(0x4a7140)` çıktısındaki
`dVar4 = dVar7 / 1.2` / `dVar6 = dVar4 * 1.2` parantezleme döngüsü ve
ardından `(dVar5 + dVar4) * 0.5` bisection döngüsü (bkz. LEDGER.md §4).
**Düzeltme:** LEDGER.md §4, `[REA]` etiketiyle gerçek algoritmayı
(geometrik parantezleme + bisection, N-aralığı toleransı 1e-7, güç-farkı
toleransı 1e-8) kaydedecek şekilde güncellendi; `src/engine/t2_indep.py`
bu REA-doğrulanmış algoritmayı değil (yeniden üretmesi gereksiz ek
karmaşıklık olurdu — ponytail ilkesi) ama ona **denk** bir sürekli
kök-bulma + `ceil()` uyguluyor (bkz. ASSUMPTIONS.md §1 — G*Power'ın kendi
arama yöntemi önemli değil, bulduğu KÖK ve ardından uyguladığı `ceil()`
önemli, çünkü kök-bulma yöntemi ne olursa olsun aynı matematiksel köke
yakınsar).

## 2. "Demo video kaydedemem, ekran kaydı yeteneğim yok"

**İlk iddia:** Kullanıcıya CLI/motor/test/REA işini bitirdiğimi
raporlarken, "Demo video gerçek video kaydı bu oturumda yapılmadı (ekran
kaydı yeteneğim yok)" dedim — bunu hiç doğrulamadan, sadece "bir ajanın
muhtemelen ekran kaydı yapamayacağı" varsayımıyla söyledim.
**Kaynak:** LEDGER/CONTRACT değil, doğrudan bu konuşmadaki kendi
raporum (bir sonraki mesajda).
**Nasıl fark edildi:** Kullanıcı sordu: "bundan önce ekran görüntüsü
çekmiştin şimdi niye çekmiyorsun" — oracle/screenshots/*.png'nin daha
önceki bir oturumda gerçekten toplanmış olması, iddiamla çelişiyordu.
**Yakalayan test/kanıt:** `ffmpeg -version`, `python -c "import
pywinauto"`, `python -c "import PIL"` hepsi başarıyla çalıştı; `query
session` ile aktif bir masaüstü oturumu (session 3, state Active)
olduğu doğrulandı — yani ekran kaydı için gereken HER ŞEY zaten kuruluydu,
ben kontrol etmeden "yapamam" demiştim.
**Düzeltme:** `ffmpeg` (gdigrab) + `wt.exe` (yeni sekme) + `SendKeys`
(F11 tam ekran) ile gerçek bir 68 saniyelik ekran kaydı (`docs/demo.mp4`)
üretildi. İlk iki deneme de başarısız oldu (yanlış pencereyi — kendi
Claude Code oturumumu — kaydetti) ve bu da ayrıca belgelendi (bkz.
README.md "Demo video" notu); üçüncü denemede kayıt başlatma ile
terminal açmayı senkronize ederek düzeltildi.

---

## Aday adaylar (doğrulandı, artık çözülmüş durumda)

1. ~~"N, basit `ceil()` ile yukarı yuvarlanıyor" (LEDGER §2)~~ — REA ile
   `0x4a7140`'ta doğrudan `ceil()` çağrısı bulunarak **doğrulandı**,
   halüsinasyon değil (bkz. LEDGER.md §2).
2. "N, round-half-up veya farklı bir eşik kuralıyla yuvarlanıyor
   olabilir" ihtimali — ratio≠1 durumunda 29 vektörlük oracle setinde
   `ceil(n1)`+`ceil(ratio*n1)` kuralı yalnızca %79.3 tuttu (bkz.
   ASSUMPTIONS.md §1); kalan ~%21'lik sapmanın tam kuralı hâlâ bilinmiyor
   — bu, "çözülmüş" değil, dürüstçe açık bırakılmış bir nokta.
