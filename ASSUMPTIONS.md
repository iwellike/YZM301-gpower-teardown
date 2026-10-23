# ASSUMPTIONS.md — t2-indep motoru için doğrulanacak varsayımlar

> SPEC.md'de belirsiz kalan davranışlar için buradaki varsayımlar kodda
> kullanıldı. Her biri gerekçesiyle not edilmiştir; diferansiyel test
> (tests/) bunları gizli vektörlere karşı doğrular.

## 1. A-priori N arama ve yuvarlama

**SONUÇ (Oturum 3, kesin, LEDGER.md §2d):** `oracle/t2_indep_vectors.csv`'nin
**30 vektörünün TÜMÜNDE (%100)** tam eşleşen formül:

```
x = sürekli kök: actual_power(x, ratio*x) = power
n_total = 2 * ceil(x * (1+ratio) / 2)      # HER ZAMAN ÇİFT sayıya zorlanıyor
ratio >= 1:  n1 = ceil(x);         n2 = n_total - n1
ratio <  1:  n2 = ceil(ratio*x);   n1 = n_total - n2
```

Yani n1/n2 bağımsız ceil'lenmiyor: **n_total önce (yarıya bölüp ceil'leyip
ikiyle çarparak) ÇİFT bir tam sayıya zorlanıyor**, küçük grup (ratio'ya göre
hangisiyse) doğrudan ceil'leniyor, büyük grup `n_total - küçük_grup` ile
TÜRETİLİYOR (kendi başına yuvarlanmıyor).

**Kanıt (dinamik REA, iki bağımsız vakada):** CRT `ceil` thunk'ına hook
takılıp `apriori_ratio_3` (n1=43,n2=127) ve `apriori_gui_vs_mcp_q9`
(n1=32,n2=64) vektörleri GUI'de çalıştırıldı. Her ikisinde de İKİ ceil()
çağrısı yakalandı: biri (`0x496a92`) sürekli `x*(1+ratio)/2` değerini
taşıyor (47.1424=31.4283×3/2; 84.6923=42.3462×4/2), diğeri (`0x4d9d8d`)
DOĞRUDAN doğru n2 değerini (64, 127 — küsüratsız) taşıyor —
`ceil(ilk_değer)×2 − n1` formülüyle tam üretildiği doğrulandı. Detay ve
tüm ara denemeler: LEDGER.md §2b/§2c/§2d.

**Bu sonuca giden hipotez tarihçesi (hepsi daha düşük isabetliydi):**
- LEDGER.md §2/§4 `[REA]`: GPowerNT.exe'de `0x4a7140` gerçekten geometrik
  parantezleme + bisection ile sürekli bir değeri bulup sonra CRT `ceil()`
  çağırıyor — bu kod GERÇEKTEN VAR (REA ile kanıtlandı), ama **Oturum 3'te
  bu akışta HİÇ ÇAĞRILMADIĞI dinamik olarak doğrulandı** (LEDGER §2d) —
  yani "bu, t2-indep'in a-priori arama motorudur" teşhisi YANLIŞTI; bu
  fonksiyon G*Power'ın paylaşılan altyapısında başka bir yol için var
  olabilir, t2-indep a-priori onu kullanmıyor.
- Hangi değişkenin (n1 mi, n_total mi) doğrudan `ceil` edildiği ve ratio≠1
  durumunda ikinci değişkenin TAM olarak nasıl türetildiği sanal (vtable)
  çağrı olduğu için REA ile izlenemedi (LEDGER §2/§3 sınırlama notu).
- `oracle/reverse_rounding.py` ile pratik oracle vektörlerine
  (oracle/t2_indep_vectors.csv) karşı ampirik olarak üç hipotez test
  edildi (ilk iki alternatif script'ten silindi, sonuçları burada
  özetleniyor):
  1. `n1=ceil(x), n2=ceil(ratio*x)` (bağımsız ceil) → **23/30 (%76.7)**
     tam eşleşme (30. vektör: AI ajanı katmanından gerçek G*Power GUI'si
     ile doğrudan doğrulanan `docs/gui_vs_mcp_q9.json`, bkz. aşağıda).
     **ratio=1 olan TÜM 18 satırda %100 eşleşme**; sapmalar yalnızca
     ratio≠1 olan satırlarda (±1 birim).
  2. `n_total=ceil(x*(1+ratio))`, sonra `n1=round_half_up(n_total/(1+ratio))`,
     `n2=n_total-n1`, gerekirse n_total'i artırarak güç yetene kadar ara →
     16/29 (%55.2).
  3. `n1=round_half_up(x), n2=round_half_up(ratio*x)`, yetersizse minimal
     artışla düzelt → 15/29 (%51.7).
  **Seçilen: Hipotez 1** — en yüksek isabet, en basit, ve LEDGER'daki
  gerçek `ceil()` çağrısıyla doğrudan tutarlı.

**Ara adımlar (kısaca, hepsi yukarıdaki kesin formülle aşıldı):** Oturum 2
`n2=ceil(ratio*n1)`'e geçip 23/30→24/30 çıkardı (Frida ile `0x4d9d88`'de
`64.0` küsüratsız argüman gözlendi). Oturum 3 önce `apriori_ratio_3`'te
n1=43 sabitken n2=127 VE n2=128'in İKİSİNİN de hedefi karşıladığını
(dolayısıyla "en küçük yeterli n2" aramasının yanlış olduğunu) canlı
gösterdi, `n2=round_half_up(ratio*x)`'e geçip 24/30→25/30 çıkardı — ama
hâlâ %90 kapısının altındaydı. Kullanıcı bunu kabul etmeyip bit-bit arama
replikasyonuna devam edilmesini isteyince, `FUN_004a7140`'ın bu akışta
HİÇ ÇAĞRILMADIĞI (Oturum 1/2'nin fonksiyon teşhisi yanlışmış) fark edildi;
ceil-thunk hook'u ratio_3 vektöründe TEKRAR çalıştırılınca yukarıdaki
kesin `n_total`-tabanlı formül bulundu ve **30/30'a (%100)** çıktı. Tüm
ara hipotezlerin REA kanıtı ve puanları LEDGER.md §2b/§2c/§2d'de.

**CONTRACT.md §6 "Kapı" notu:** Sözleşme bilinçli olarak %100 değil %90
eşik koymuştu (o zamanki belirsizlik payı için); motor artık pratik
oracle setinin tamamında tam eşleşiyor, dolayısıyla gizli vektör setinde
de güçlü bir performans bekleniyor — ama "gizli set farklı bir sınır
durumu içerebilir" riski sıfırlanmış değil, yalnızca ÇOK daha düşük.

## 2. Ratio admissible aralığı

**Varsayım:** `ratio` için ayrı bir alt/üst sınır uygulanmıyor; CONTRACT.md
§5'teki genel kural (`ratio > 0`) kullanılıyor.

**Gerekçe:** LEDGER §3 `[REA]`, GPowerNT.exe'nin Proportions ailesinde
`ratio ∈ [0.01, 100]` aralığını REA ile doğruladı (`0x487300`,
`L=0x3f847ae147ae147b`=0.01), ama t2-indep (Means) için kendi `L` sabiti
sanal çağrı nedeniyle izlenemedi. Oturum 1'de toplanan oracle verisi
ratio=0.1 ve ratio=10'u BAŞARIYLA hesapladığına göre (bkz.
oracle/t2_indep_vectors.csv id=apriori_ratio_0_1, apriori_ratio_10),
t2-indep'in `L` sabiti en az 0.1 kadar gevşek. CONTRACT.md §5 zaten
`ratio>0` dışında bir sınır tanımlamıyor; bu nedenle motor ek bir "admissible
range" reddi uygulamıyor — sözleşmeye birebir uyum önceliklendirildi.

## 3. alpha/tails için OUT_OF_RANGE

**Varsayım:** `alpha<=0`, `alpha>=1`, `tails` ∉ {1,2} → `OUT_OF_RANGE`.

**Gerekçe:** REA ile GPowerNT.exe'de bu alanlar için açık bir runtime
doğrulayıcı bulunamadı (muhtemelen GUI spin-button/combobox seviyesinde
kısıtlanıyor, motor seviyesinde ayrı bir hata yolu yok). CONTRACT.md §5
bu aralığı zaten tanımladığı için motor doğrudan sözleşmeyi uyguluyor.

## 4. Diğer modların (post-hoc/compromise/criterion/sensitivity) kök bulma

**Varsayım:** Bu modlarda `n1,n2` girdi olduğu için N-yuvarlama sorunu
yok; `alpha`/`power`/`d` için kök bulma scipy `brentq` ile yapılıyor,
CONTRACT.md §6'daki 1e-6 ondalık tolerans ile karşılaştırılıyor (tam
eşleşme gerekmiyor).

**Gerekçe:** CONTRACT.md §4.1 tablosu bu modlarda n1/n2'yi girdi listesine
koyuyor; dolayısıyla LEDGER §2/§3/§4'teki N-arama bulguları bu modları
etkilemiyor. Tolerans zaten CONTRACT.md §6'da tanımlı.
