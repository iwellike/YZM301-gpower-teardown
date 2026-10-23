# Ajan Değerlendirme Seti — 10 Soru (Türkçe) + İngilizce Çeviri

Her soru kurgusal bir araştırma senaryosudur (gerçek hasta verisi yoktur).
"Jev" (Sistem 1 sınıflandırıcı) her soru için şu etiketlerden birini,
0-1 arası bir güvenle üretir: `t2-indep`, `t-paired`, `anova-oneway`,
`chi2-contingency`, `multireg-r2`, `ambiguous`, `unsupported`.
Güven < 0.75 ya da etiket `ambiguous`/`unsupported` ise araştırmacıya
sorulur; Jev sayı üretmez (N, güç, etki büyüklüğü asla Jev'den gelmez).

| # | Soru (TR) | Question (EN) | Beklenen aile | Beklenen parametreler (not) |
|---|---|---|---|---|
| 1 | Yeni bir ağrı kesicinin plasebodan daha iyi olduğunu göstermek istiyorum. Orta büyüklükte bir etki bekliyorum, α=0.05, güç 0.80. Kaç hastaya ihtiyacım var? | I want to show a new painkiller is better than placebo. I expect a medium effect, α=0.05, power 0.80. How many patients do I need? | `t2-indep` | tails=1 (yönlü iddia: "daha iyi"), d=0.5 (orta, Cohen), alpha=0.05, power=0.80, ratio=1 (varsayım — araştırmacıya sorulmalı) |
| 2 | Aynı hastalarda tedavi öncesi ve sonrası tansiyonu karşılaştıracağım, fark olup olmadığını (yön iddia etmeden) test edeceğim. Küçük-orta bir etki, α=0.05, güç 0.90. | I will compare blood pressure before/after treatment in the same patients, testing for any difference (no direction). Small-medium effect, α=0.05, power 0.90. | `t-paired` | tails=2 (yönsüz "fark var"), dz≈0.35 (küçük-orta arası — belirsiz, sorulmalı), alpha=0.05, power=0.90 |
| 3 | Üç farklı tedavi kolunu (A, B, C) karşılaştıracağım, en az ikisi arasında fark olup olmadığına bakacağım. Orta etki büyüklüğü, α=0.05, güç 0.95. | I will compare three treatment arms (A, B, C) for any difference between at least two. Medium effect, α=0.05, power 0.95. | `anova-oneway` | f=0.25 (orta), groups=3, alpha=0.05, power=0.95 |
| 4 | Yeni tedaviye yanıt oranı ile standart tedaviye yanıt oranını 2x2 bir tabloda karşılaştırmak istiyorum, orta etki, α=0.05, güç 0.80. | I want to compare response rate to new vs standard treatment in a 2x2 table, medium effect, α=0.05, power 0.80. | `chi2-contingency` | w=0.3 (orta), df=1 (2x2 tablo), alpha=0.05, power=0.80 |
| 5 | Üç risk faktörünün (yaş, kilo, sigara) hastalık riskindeki varyansı ne kadar açıkladığını göstermek istiyorum, orta etki (R²≈0.13), α=0.05, güç 0.80. | I want to show how much variance three risk factors (age, weight, smoking) explain in disease risk, medium effect (R²≈0.13), α=0.05, power 0.80. | `multireg-r2` | f2=0.15 (orta), predictors=3, alpha=0.05, power=0.80 |
| 6 | Elimde 60 hasta var, yarısı ilaç yarısı plasebo aldı; orta büyüklükte bir etki varsa bunu yakalama gücüm nedir? | I have 60 patients, half drug half placebo; if there's a medium effect, what's my power to detect it? | `t2-indep` | post-hoc, n1=30, n2=30, d=0.5, alpha=0.05 (varsayılan — sorulmalı), tails belirsiz (sorulmalı) |
| 7 | Hastalarımı iki gruba ayırıp bir anket puanını karşılaştıracağım ama kaç kişi gerektiğini bilmiyorum, bana standart bir sayı söyler misin? | I'll split patients into two groups and compare a survey score, but I don't know sample size — can you just give me a standard number? | `ambiguous` | Etki büyüklüğü, alpha, power verilmemiş — Jev araştırmacıya sormalı, varsayılan "standart" sayı üretmemeli |
| 8 | Hastaların genetik profiline göre 5 farklı tedaviye verdikleri yanıtı makine öğrenmesiyle kümeleyip kaç kümeye ihtiyacım olduğunu bulmak istiyorum. | I want to cluster patients' response to 5 treatments by genetic profile using machine learning and find how many clusters I need. | `unsupported` | Bu bir güç analizi sorusu değil (kümeleme/ML) — Jev `unsupported` demeli, uydurma bir aile seçmemeli |
| 9 | İki bağımsız grupta (deney/kontrol) ortalama iyileşme süresini karşılaştıracağım, etkinin büyük olduğunu düşünüyorum (d=0.8), tek yönlü, α=0.01, güç 0.90, kontrol grubunun deney grubunun iki katı olmasını planlıyorum. | I'll compare mean recovery time in two independent groups (experimental/control), I expect a large effect (d=0.8), one-sided, α=0.01, power 0.90, and I plan the control group to be twice the size of the experimental group. | `t2-indep` | tails=1, d=0.8, alpha=0.01, power=0.90, ratio=2 (tüm parametreler net — yüksek güven beklenir) |
| 10 | Dört tedavi grubunda yan etki görülme oranlarını karşılaştırıp aralarında fark olup olmadığına bakacağım, etkiyi küçük-orta varsayıyorum, standart α ve güç kullanacağım. | I'll compare side-effect rates across four treatment groups for any difference, assuming a small-medium effect, standard α and power. | `chi2-contingency` | w≈0.2-0.3 (belirsiz, "küçük-orta" bir kategori, sayı değil — sorulmalı), df=3, "standart α/power" da netleştirilmeli (0.05/0.80 mi?) |

## Değerlendirme yöntemi

- Her soru için Jev'in verdiği `(etiket, güven)` çifti kaydedilir
  (`logs/jev_eval.jsonl`).
- Doğru seçim oranı = (etiket beklenenle eşleşen soru sayısı) / 10.
- Kalibrasyon: "güven >= 0.75" dediği sorularda gerçek doğruluk yüzdesi
  ayrıca raporlanır (örn. "0.75+ güvenle cevapladığı 6 sorunun 5'i doğru:
  kalibre güven ≈ %83").
- Aynı 10 soru İngilizce çeviriyle de çalıştırılır (tablo 3. sütun); TR/EN
  doğruluk ve ortalama güven karşılaştırılır — Türkçe için yayımlanmış bir
  kalibrasyon ölçümü olmadığından bu çalışmanın kendisi bir veri noktasıdır.
- "Orta etki" gibi kategorik ifadelerin sessizce sayıya çevrilmediği
  (CONTRACT.md §10 uyarısı) ayrıca kontrol edilir: 1, 2, 6, 10 numaralı
  sorular bu yüzden kasıtlı olarak tam sayı vermiyor.
