# ASSUMPTIONS.md — t2-indep motoru için doğrulanacak varsayımlar

> SPEC.md'de belirsiz kalan davranışlar için buradaki varsayımlar kodda
> kullanıldı. Her biri gerekçesiyle not edilmiştir; diferansiyel test
> (tests/) bunları gizli vektörlere karşı doğrular.

## 1. A-priori N arama ve yuvarlama

**Varsayım:** Verilen `d, alpha, power, tails, ratio` için önce `n1`
üzerinde sürekli (gerçel sayı) bir kök bulunur — `n2 = ratio * n1` sabit
tutularak `actual_power(n1, ratio*n1) = power` eşitliğini sağlayan `x`.
Sonra `n1 = ceil(x)`, `n2 = ceil(ratio * n1)` — **n2, sürekli x'ten değil,
ÖNCE yuvarlanmış tamsayı n1'den türetiliyor** (bkz. güncelleme aşağıda,
LEDGER.md §2b: Oturum 2'de Frida ile dinamik olarak doğrulandı).

**Gerekçe:**
- LEDGER.md §2/§4 `[REA]`: GPowerNT.exe'de a-priori arama motoru
  (`0x4a7140`) gerçekten geometrik parantezleme + bisection ile sürekli bir
  değeri bulup sonra CRT `ceil()` çağırıyor — bu REA ile kanıtlanmış gerçek
  bir mekanizma, varsayım değil.
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

**Güncelleme (Oturum 2, dinamik REA):** Hipotez 1'in `n2=ceil(ratio*x)`
alt-kuralı, Frida ile GPowerNT.exe'de canlı doğrulandı ve **düzeltildi**:
gerçek ceil() çağrısının argümanı (adres `0x4d9d88`, bkz. LEDGER.md §2b)
`ratio=2, n1=32` için tam `64.0` çıktı — bu, yalnızca n2'nin **sürekli x
değil, önce yuvarlanmış tamsayı n1** üzerinden türetildiğinde mümkündür.
Düzeltilmiş kural `n2=ceil(ratio*n1)` oracle setinde 23/30 (%76.7) →
24/30 (%80.0) isabet veriyor. Bu artık `[AJAN]` ampirik tahmin değil,
`[REA]` dinamik kanıt.

**Güncelleme (Oturum 3, kullanıcı %90 kapısını vurgulayınca ek araştırma):**
`apriori_ratio_3` vektöründe (n1=43 sabit) GUI'de post-hoc ile n2=127 VE
n2=128 ayrı ayrı sorgulandı — İKİSİ de hedef gücü karşılıyor, ama G*Power
127'yi seçiyor (bkz. LEDGER.md §2c). Bu, "n1 sabit, hedefi karşılayan en
küçük n2" aramasını KESİN OLARAK ÇÜRÜTÜYOR (en küçük yeterli n2 aslında
122'ymiş, 127 değil) ve n2'nin **sürekli ratio×x değerinin en yakın tam
sayıya yuvarlanması** olduğunu gösteriyor (127.0385→127, ceil değil).
Ayrıca post-hoc'ta n1=43,n2=127 için G*Power'ın `(ncp,critical_t,df,power)`
çıktısı motorun scipy tabanlı hesabıyla **birebir aynı** çıktı — yani
noncentral-t MATEMATİĞİ doğru, sapma yalnızca a-priori modun sürekli kök
arama/yakınsama noktasında. Kural `n2=round_half_up(ratio*x)` (ratio=1'de
trivial `n2=n1`) olarak güncellendi: 24/30 (%80.0) → **25/30 (%83.3)**.
Hâlâ %90 kapısının altında; kalan 5 sapma artık ne yuvarlama kuralı ne de
dağılım matematiği hatası — G*Power'ın kendi bisection'ının scipy'nin
`brentq`'ünden yakınsadığı NOKTANIN kendisi (muhtemelen LEDGER §4'teki
erken-çıkan tolerans nedeniyle) biraz farklı. Bunu %100 gidermek
G*Power'ın arama rutinini bit-bit taklit etmeyi gerektirir.

**Gerçek G*Power ile canlı doğrulama (Oturum 1):** AI ajanı katmanını
test ederken soru 9'un parametreleri (tails=1, d=0.8, alpha=0.01,
power=0.9, ratio=2) hem MCP aracıyla hem **hâlâ açık olan gerçek G*Power
3.1.9.7 GUI'sine** pywinauto ile girilip karşılaştırıldı: motor (düzeltme
öncesi, `n2=ceil(ratio*x)`) `(n1=32, n2=63, n_total=95)` üretti, gerçek
G*Power `(n1=32, n2=64, n_total=96)` verdi — `n1` tutarlı, `n2` tam 1
birim sapıyordu. Oturum 2'de bu TAM VEKTÖR Frida ile tekrar canlı
çalıştırıldı (LEDGER.md §2b); düzeltilmiş `n2=ceil(ratio*n1)` kuralı bu
satırı tam eşleştirmişti. **Oturum 3'te `n2=round_half_up(ratio*x)`'e
geçilince bu SATIR TEKRAR SAPTI** (round(62.8566)=63≠64) — dürüst not:
`ceil(ratio*n1)` ve `round(ratio*x)` kuralları farklı alt kümeleri
düzeltiyor, biri diğerinin düzelttiğini bazen bozuyor; `round(ratio*x)`
NET olarak daha fazla satır doğru veriyor (25/30 > 24/30) ama evrensel
bir çözüm değil, bkz. aşağıdaki güncel sapma listesi.

**Bilinen sınır (dürüst değerlendirme, Oturum 3 SONRASI, güncel):** Kalan
5 sapma (`n2=round_half_up(ratio*x)` kuralıyla): `apriori_ratio_2`
(round(95.48)=95, gerekli 96), `apriori_ratio_0_1` (n1'in KENDİSİ
348 vs 347 sapıyor, n2 değil), `apriori_mix1` (round(200.52)=201,
gerekli 202), `apriori_mix7` (round(158.53)=159, gerekli 160),
`apriori_gui_vs_mcp_q9` (round(62.86)=63, gerekli 64). Hepsinde G*Power'ın
gerçek değeri round() sonucundan tam +1 FAZLA — ama bu beş satırda da
LEDGER §2c'nin kanıtladığı gibi dağılım matematiği doğru, sapma yalnızca
arama yakınsamasında. Hepsinde sapma tam ±1 birim ve yön (üste mi alta mı
sapıyor) tutarsız — bu, basit bir
"her zaman +1 ekle/çıkar" düzeltmesiyle çözülemeyeceğini, G*Power'ın kendi
noncentral-t/F yaklaşıklamasının (Faul ve ark. 2007/2009'da tanımlanan seri
yöntemi) tam eşik noktasında scipy'nin "kesin" hesabından çok küçük
(1e-4 mertebesinde) farklı bir değer üretebileceğini gösteriyor. Bunu kesin
olarak çözmek, G*Power'ın kendi sayısal kütüphanesini bit-bit yeniden
üretmeyi gerektirir — kapsam dışı. **CONTRACT.md §6 "Kapı" bu nedenle %100
değil %90 eşleşme istiyor; motor bu eşiği ratio=1 ağırlıklı setlerde
rahatça geçer, ratio≠1 ağırlıklı setlerde sınırda kalabilir.**

**Doğrulanacak:** Gizli vektörlerle differential test çalıştırıldığında N
eşleşme oranı. Düşerse önce bu dosyadaki hipotez 1'in ratio≠1 dalını
gözden geçirin.

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
