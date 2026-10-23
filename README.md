# gpower-clone — t2-indep (YZM301 Teardown Sprint)

Melike Tıkır · 231118022 · Bireysel çalışma (4 kişilik takım ödevi, tek
başına tamamlandı)

**Yapılan katmanlar:** CLI (zorunlu, 5/5 mod) + MCP (`power_analysis`
aracı, CLI ile aynı motoru çağırıyor) + AI ajanı ("Jev" sınıflandırıcı,
10 kurgusal senaryoda 10/10 doğru aile tahmini, MCP aracını çağırıyor,
loglar `logs/agent_calls.jsonl`). Demo video `docs/demo.mp4` olarak
kaydedildi (bkz. aşağıda).

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

`npx rea-agents setup`/`doctor` çıktısı ve Ghidra provider doğrulaması:
`docs/rea_setup_check.txt` (ham JSON/YAML çıktı — ekran görüntüsü değil,
komut çıktısının kendisi: Ghidra 12.1.4, `GHIDRA_INSTALL_DIR` ayarlı,
tüm `ghidra-*` kontrolleri `ok:true`). LEDGER.md Oturum 1'de bu kurulum
fiilen kullanılarak GPowerNT.exe üzerinde REA ile canlı analiz yapıldı
(bkz. LEDGER.md `[REA]` satırları, adres+alıntı kanıtlı).

## G\*Power sürüm bilgisi

- Sürüm: 3.1.9.7 (Windows)
- Kaynak: resmi sayfa, https://www.psychologie.hhu.de/arbeitsgruppen/allgemeine-psychologie-und-arbeitspsychologie/gpower
- Dosya: `GPowerWin_3.1.9.7.zip`
- `GPowerNT.exe` SHA-256: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`

## Kurulum ve çalıştırma

```bash
pip install -r src/requirements.txt
./gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
# eşdeğer: python -m src.cli --test t2-indep --mode a-priori ...
```

```json
{"ncp": 3.3166247903554, "critical_t": 1.6536580165162147, "df": 174, "n1": 88, "n2": 88, "n_total": 176, "actual_power": 0.9514254482775333}
```

Testler: `pip install pytest && python -m pytest tests/ -q` → **42/42 geçti**
(motor, CLI, MCP eşdeğerliği, ajan sınıflandırıcısı, diferansiyel).

MCP sunucusunu çalıştırmak için: `python -m src.mcp.server` (stdio).
Ajan değerlendirmesini çalıştırmak için: `python -m src.agent.run_eval`.

## Diferansiyel test sonucu

- **CONTRACT.md §9'daki 5 t2-indep referans vektörü** (a-priori, post-hoc,
  compromise, criterion, sensitivity): tüm alanlar ≤1e-6 tolerans içinde
  **tam eşleşme** (`tests/test_differential.py::test_public_vector`).
- **30 vektörlük pratik oracle seti** (`oracle/t2_indep_vectors.csv`, 29'u
  G*Power 3.1.9.7 GUI'sinden doğrudan toplandı, 1'i Oturum 1'de ajan
  değerlendirmesi sırasında canlı G*Power'a karşı ek doğrulandı — sınır
  değerler ve ratio≠1 dahil): n1/n2/n_total **tam eşleşme oranı 24/30 =
  %80.0** (Oturum 2'de Frida ile dinamik REA sonucu `n2=ceil(ratio*n1)`
  kuralına düzeltildi, bkz. LEDGER.md §2b; önceki `n2=ceil(ratio*x)`
  kuralı 23/30 = %76.7 veriyordu). ratio=1 olan 18 vektörün **tamamında
  %100** eşleşme; kalan sapmalar ratio≠1 vektörlerinin bir kısmında ±1
  birim. Kök sebep ve hipotez karşılaştırması ASSUMPTIONS.md §1'de;
  CONTRACT.md §6 "Kapı"nın bilerek %100 değil %90 eşik koyması bu
  belirsizliği zaten hesaba katıyor — %80 ile gizli vektör setine bağlı
  olarak kapı hâlâ riskli (ratio=1 ağırlıklı ise geçer, ratio≠1 ağırlıklı
  ise sınırda kalabilir).
- Yuvarlanan N ne olursa olsun, ncp/critical_t/actual_power o N için her
  zaman iç tutarlı (ayrı bir regresyon testiyle korunuyor).
- **CLI/MCP eşdeğerliği** (CONTRACT.md §7, 5 t2-indep vektörü): tam
  eşleşme — ikisi de aynı `src/cli/core.run()` fonksiyonunu çağırıyor,
  eşdeğerlik tasarımla garanti, ayrıca testle de doğrulandı.
- **AI ajanı** (CONTRACT.md §8, `src/agent/eval_questions.md`'nin 10
  kurgusal senaryosu): "Jev" sınıflandırıcısı 10/10 doğru aile tahmini
  yaptı; güven≥0.75 dediği 9 sorunun 9'unda doğru (kalibre doğruluk
  %100, küçük örneklem — tek bir ölçüm). Etki büyüklüğü yalnızca
  kategori kelimesiyle ("orta", "küçük-orta") verilen 7 soruda ajan
  **sayıyı sessizce varsaymadı**, netleştirme gerektiğini logladı
  (CONTRACT.md §10 uyarısı); sadece açık sayı verilen soru 9'da aracı
  gerçekten çağırdı (`logs/agent_calls.jsonl`).

## Demo video

`docs/demo.mp4` — 68 saniyelik gerçek ekran kaydı (ffmpeg + Windows
Terminal, `docs/demo_run.sh` çalıştırılarak kaydedildi): sürüm sorgusu,
CONTRACT.md referans örneği (a-priori), post-hoc doğrulama, geçersiz
girdi (`alpha=0` → `OUT_OF_RANGE`, exit 2) ve `pytest` çalışması.
Kozmetik not: Windows Terminal'in "Termination behavior..." bilgi
banner'ı köşede görünüyor, otomasyonla kapatılamadı — işlevsel bir sorun
değil. Kendi kaydını almak istersen `docs/demo_script.md`'deki komutları
kullanabilirsin.

## Takım / Yazarlar

Melike Tıkır (231118022) — tüm katmanlar.

## Kaynakça

- Faul, F., Erdfelder, E., Lang, A.-G., & Buchner, A. (2007). G\*Power 3: A
  flexible statistical power analysis program for the social, behavioral,
  and biomedical sciences. *Behavior Research Methods*, 39(2), 175-191.
- Faul, F., Erdfelder, E., Buchner, A., & Lang, A.-G. (2009). Statistical
  power analyses using G\*Power 3.1: Tests for correlation and regression
  analyses. *Behavior Research Methods*, 41(4), 1149-1160.
