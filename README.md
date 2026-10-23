# gpower-clone — t2-indep (YZM301 Teardown Sprint)

Melike Tıkır · 231118022 · Bireysel çalışma (4 kişilik takım ödevi, tek
başına tamamlandı)

**Yapılan katmanlar:** _(doldurulacak — CLI / +MCP / +AI ajanı)_

G*Power 3.1.9.7'nin "t tests – Means: Difference between two independent
means (two groups)" hesabının ters mühendislik, kanıt, temiz oda yeniden
yazım ve ajan katmanı çalışması. Atıf: Faul, F., Erdfelder, E., Lang, A.-G.,
& Buchner, A. (2007, 2009). G\*Power 3: A flexible statistical power
analysis program. *Behavior Research Methods*.

## Etik not

Bu, G\*Power'ın yazarlarının bilim dünyasına ücretsiz sunduğu emeğe saygıyla
yürütülen bir eğitim çalışmasıdır. G\*Power değiştirilmez, dağıtılmaz,
satılmaz; hiçbir çıktı G\*Power olarak sunulmaz (bkz. CONTRACT.md "Etik
niyet"). `GPowerNT.exe` repoya **konmamıştır** (.gitignore).

## Kurulum kanıtı (REA + Ghidra erişimi)

`npx rea-agents setup` çıktısı ve Ghidra provider doğrulaması: _(ekran
görüntüsü eklenecek — docs/rea_setup_check.png)_

## G\*Power sürüm bilgisi

- Sürüm: 3.1.9.7 (Windows)
- Kaynak: resmi sayfa, https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower
- Dosya: `GPowerWin_3.1.9.7.zip`
- `GPowerNT.exe` SHA-256: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc81`

## Kurulum ve çalıştırma

```bash
pip install -r src/requirements.txt
python -m src.cli --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
```

_(gpower-clone adlı çalıştırılabilir sarmalayıcı — doldurulacak)_

## Diferansiyel test sonucu

_(doldurulacak — tests/ altındaki uyum raporuna bağlanacak)_

## Demo video

_(doldurulacak — 60 saniyelik CLI demosu linki)_

## Takım / Yazarlar

Melike Tıkır (231118022) — tüm katmanlar.

## Kaynakça

- Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G\*Power 3: A
  flexible statistical power analysis program for the social, behavioral,
  and biomedical sciences. *Behavior Research Methods*, 39(2), 175-191.
- Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical
  power analyses using G\*Power 3.1: Tests for correlation and regression
  analyses. *Behavior Research Methods*, 41(4), 1149-1160.
