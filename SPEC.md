# SPEC.md — t2-indep (t testi, iki bağımsız ortalama) Kabul Kriterleri

> Bu belge yalnızca LEDGER.md'deki kanıtlardan (`[DOK]` + `[REA]`) türetilir.
> `[AJAN]` etiketli, kanıtsız iddialar buraya **kabul kriteri olarak girmez**;
> yalnızca "doğrulanacak varsayım" notu olarak ASSUMPTIONS.md'de yer alır.
> Oturum 2 (temiz oda yazım) bu dosyayı, CONTRACT.md'yi ve
> oracle/public_vectors.jsonl'i görür; LEDGER.md'yi ya da Ghidra çıktısını
> görmez.

Sözleşme sürümü: CONTRACT.md 1.0.0. Test ailesi: `t2-indep`.

## Arka plan (klinik)

Araştırmacı iki bağımsız grubu (ör. ilaç ve plasebo) karşılaştırıyor.
Girdi/çıktı alan adları CONTRACT.md §4.1'dedir.

---

## Senaryo grupları

### A. a-priori mod — gerekli örneklem büyüklüğü

```gherkin
Senaryo: CONTRACT.md referans örneğiyle tam eşleşme
  Diyelim ki tails=1, d=0.5, alpha=0.05, power=0.95, ratio=1
  Motor a-priori modda çalıştırıldığında
  O zaman n1=88 ve n2=88 ve n_total=176 olmalı (tam eşleşme)
  Ve actual_power 0.9514254'e |fark|<=1e-6 ile eşit olmalı
  Ve ncp 3.3166248'e, critical_t 1.6536580'e, df 174'e eşit olmalı

Senaryo: Eşit olmayan oranda grup büyüklüğü dağıtımı
  Diyelim ki ratio=2 (n2 yaklaşık n1'in iki katı)
  Motor a-priori modda çalıştırıldığında
  O zaman n2/n1 oranı, G*Power'ın gözlenen protokolündeki n1,n2 çiftiyle
    (bkz. oracle/t2_indep_vectors.csv, id=apriori_ratio_2) tam eşleşmeli
  [REA kaynağı: LEDGER.md §3 (0x487300 admissible-range deseni) +
   oracle/reverse_rounding.py ampirik analizi: n1=ceil(x), n2=ceil(ratio*x),
   x = power(x, ratio*x)=target'ın kökü. 29 vektörlük oracle setinde bu kural
   ratio=1 için 100%, ratio≠1 için bazı sınır değerlerde ±1 sapma veriyor
   (bkz. ASSUMPTIONS.md) — CONTRACT.md §6 "Kapı"nın %90 (değil %100) eşik
   koymasının nedeni tam olarak budur.

Senaryo: Çok küçük etki büyüklüğü (d -> 0)
  Diyelim ki d=0.01
  Motor a-priori modda çalıştırıldığında
  O zaman n_total, G*Power'ın ürettiği değerle tam eşleşmeli
    (çok büyük bir N beklenir, taşma/sonsuz döngü OLMAMALI)

Senaryo: Çok büyük etki büyüklüğü (d -> büyük)
  Diyelim ki d=5.0
  Motor a-priori modda çalıştırıldığında
  O zaman n_total küçük ama df>=1 (geçerli) olmalı

Senaryo: Power alpha'ya çok yakın
  Diyelim ki power=0.06 ve alpha=0.05
  Motor a-priori modda çalıştırıldığında
  O zaman n1=2, n2=2 (CONTRACT.md §5 alt sınırı) üretilmeli — G*Power bu
    girdide dejenere/minimum örneklemi döndürüyor (oracle id=apriori_power_near_alpha)
  [REA kaynağı: CONTRACT.md §5 (n1,n2≥2 sınırı) + oracle gözlemi; motorun
   kendi kök-bulma mantığının x<2 bulduğu her durumda n1=n2=2'ye kenetlenmesi
   gerekir, aksi hâlde kökbulucu negatif/sıfır N'de patlar]
```

### B. post-hoc mod — ulaşılan güç

```gherkin
Senaryo: n1, n2 verildiğinde gücün hesaplanması
  Diyelim ki tails=1, d=0.5, alpha=0.05, n1=88, n2=88
  Motor post-hoc modda çalıştırıldığında
  O zaman power 0.9514254'e |fark|<=1e-6 ile eşit olmalı
  Ve ncp, critical_t, df a-priori örneğiyle birebir aynı olmalı
    (aynı n1/n2/d/alpha/tails -> aynı ncp/critical_t/df, mod farketmez)
```

### C. Geçersiz girdi

```gherkin
Senaryo: Eksik zorunlu alan
  Diyelim ki a-priori modda "power" alanı verilmedi
  Motor çalıştırıldığında
  O zaman {"error":..., "code":"MISSING_PARAM", "field":"power"} dönmeli
  Ve çıkış kodu 2 olmalı

Senaryo: Aralık dışı değer
  Diyelim ki alpha=0 verildi (0 < alpha < 1 şartını sağlamıyor)
  Motor çalıştırıldığında
  O zaman {"error":..., "code":"OUT_OF_RANGE", "field":"alpha"} dönmeli
  Ve çıkış kodu 2 olmalı

Senaryo: Negatif etki büyüklüğü
  Diyelim ki d=-0.5 verildi
  Motor çalıştırıldığında
  O zaman {"error":..., "code":"OUT_OF_RANGE", "field":"d"} dönmeli
  Ve çıkış kodu 2 olmalı

Senaryo: Bilinmeyen alan
  Diyelim ki post-hoc modda "power" alanı da verildi (bu modda power çıktıdır, girdi değil)
  Motor çalıştırıldığında
  O zaman {"error":..., "code":"UNKNOWN_PARAM", "field":"power"} dönmeli
  Ve çıkış kodu 2 olmalı
```

### D. Sayısal hassasiyet ve tutarlılık

```gherkin
Senaryo: Deterministik çıktı
  Diyelim ki aynı girdi iki kez verildi
  O zaman iki çalıştırmanın çıktısı birebir aynı olmalı (bit-bit, tolerans olmadan)

Senaryo: Tam sayı alanları JSON tam sayı olarak döner
  Diyelim ki a-priori modda n1, n2, n_total, df hesaplandı
  O zaman bu alanlar JSON'da "88" değil 88 olarak (ondalık noktasız) yazılmalı
```

---

## Çözülen kalemler (LEDGER.md Oturum 1 `[REA]` bulgularından)

- [x] Yuvarlama kuralının kesin formu: `ceil()` (LEDGER §2, `0x4a7140`)
- [x] a-priori N arama algoritması / durma koşulu: geometrik parantezleme
  (×1.2/÷1.2) + bisection, toleranslar 1e-7 (N aralığı) / 1e-8 (güç farkı)
  (LEDGER §4, `0x4a7140`)
- [x] Geçersiz girdiye motor tepkisi (effect size için): `|d|<1e-5` → açık
  hata, sessiz düzeltme yok (LEDGER §5, `0x4d4bd0` + 3 kardeş adres)
- [x] ratio≠1 dağıtımının GENEL deseni: `[L,1/L]` admissible aralık +
  açık hata (sessiz kırpma yok) (LEDGER §3, `0x487300`)

## Hâlâ açık (ASSUMPTIONS.md'de "doğrulanacak varsayım")

- [ ] t2-indep'in kendi ratio admissible-range sabiti `L` (Proportions
  ailesi için L=0.01 doğrulandı, Means için REA ile doğrulanamadı — sanal
  çağrı)
- [ ] ratio≠1'de n1/n2'nin TAM hangi tamsayıya yuvarlandığı — ampirik
  olarak (oracle/reverse_rounding*.py) `n1=ceil(x), n2=ceil(ratio*x)`
  kuralının ratio=1'de %100, ratio≠1'de ~%80 isabet ettiği gözlendi; kalan
  sapmalar G*Power'ın kendi noncentral-t yaklaşıklamasının sınır
  değerlerindeki küçük farklardan kaynaklanıyor olabilir (bkz.
  ASSUMPTIONS.md). CONTRACT.md §6 "Kapı" bilinçli olarak %100 değil %90
  eşik koyuyor — bu tam da bu belirsizliği hesaba katıyor.
- [ ] `alpha=0/1`, `tails=3` gibi girdiler için motor-seviyesi doğrulayıcı
  REA ile bulunamadı (muhtemelen GUI spin-button/combobox kısıtlaması,
  runtime validator yok); CONTRACT.md §5 aralıklarına göre `OUT_OF_RANGE`
  ile reddedilecek şekilde varsayıldı.
