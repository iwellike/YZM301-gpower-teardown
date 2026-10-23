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
  [REA kaynağı: LEDGER.md §3 — doldurulacak]

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
  O zaman motor G*Power ile aynı davranışı sergilemeli: ya küçük bir N
    üretmeli ya da G*Power'ın kendisi de hata veriyorsa aynı error+code
    döndürülmeli
  [REA kaynağı: LEDGER.md §5 — doldurulacak]
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

## Bekleyen kalemler (LEDGER.md tamamlanınca doldurulacak)

- [ ] Yuvarlama kuralının kesin formu (LEDGER §2 `[REA]`)
- [ ] ratio≠1 dağıtım kuralı (LEDGER §3 `[REA]`)
- [ ] a-priori N arama algoritması / durma koşulu (LEDGER §4 `[REA]`)
- [ ] Geçersiz girdiye GUI/motor tepkisi (LEDGER §5 `[REA]`)

Bu kalemler `[REA]` kanıtı olmadan kesinleştirilemez; Oturum 2'ye
ASSUMPTIONS.md üzerinden "doğrulanacak varsayım" olarak geçecekler.
