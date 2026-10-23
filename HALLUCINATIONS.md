# HALLUCINATIONS.md — Ajanın Yanlış Çıkarımları

Bu dosya, ajanın (ben) kanıtsız ama kendinden emin biçimde ileri sürdüğü ve
sonradan yanlış çıktığı ortaya çıkan en az 2 iddiayı belgeler. Amaç:
"Bunun kanıtı hangi fonksiyonda?" sorusunun önemini somutlaştırmak.

Format: her kayıt için (1) ajanın ilk iddiası, (2) hangi `[AJAN]` satırından
geldiği, (3) nasıl fark edildi, (4) hangi test/REA bulgusu yakaladı, (5)
düzeltme.

---

## 1. _(Oturum 1/2 tamamlandıkça doldurulacak)_

**İlk iddia:**
**Kaynak:** LEDGER.md §_
**Nasıl fark edildi:**
**Yakalayan test/kanıt:**
**Düzeltme:**

## 2. _(doldurulacak)_

---

## Aday adaylar (şu ana kadar gözlemlenen riskli varsayımlar)

Bunlar henüz "halüsinasyon" olarak doğrulanmadı ama LEDGER.md'de `[AJAN]`
etiketiyle işaretli, REA ile henüz teyit/çürütme yapılmamış iddialar —
Oturum 1 tamamlandığında bu listeden gerçek halüsinasyonlar seçilecek:

1. "N, basit `ceil()` ile yukarı yuvarlanıyor" (LEDGER §2) — statsmodels'in
   kesirli N'siyle G*Power'ın tam sayısı tek bir örnekte (87.26 -> 88)
   tutarlı ama bu, round-half-up veya farklı bir eşik kuralını ekarte etmez.
2. "a-priori N araması N=1'den başlayıp 1'er artırıyor" (LEDGER §4) —
   gözleme değil, tipik güç analizi algoritmalarına dayalı bir varsayım.
