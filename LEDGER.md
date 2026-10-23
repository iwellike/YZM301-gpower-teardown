# Kanıt Defteri — t2-indep (t testi, iki bağımsız ortalama)

Etiketler: `[DOK]` kılavuzda/makalede yazıyor · `[REA]` binary'den kanıtlandı
(fonksiyon adresi/dize referansı) · `[AJAN]` ajan çıkarımı, kanıtsız.

**Puan yalnızca `[REA]` satırlarına verilir.**

GPowerNT.exe SHA-256: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc81`
(kaynak: psychologie.hhu.de resmi GPowerWin_3.1.9.7.zip, bkz. README.md)

---

## 1. Dağılım ve test istatistiği

- `[DOK]` t2-indep testi, iki bağımsız grup ortalaması farkı için merkezi
  olmayan (noncentral) t dağılımını kullanır; test istatistiği merkezsizlik
  parametresi δ (ncp) ile karakterize edilir. Kaynak: Faul, Erdfelder, Lang &
  Buchner (2007), *G\*Power 3: A flexible statistical power analysis program*,
  Behavior Research Methods, 39(2), 175-191; G*Power El Kitabı (GPowerManual.pdf).
- `[DOK]` Etki büyüklüğü d (Cohen's d), ncp = d · sqrt(n1·n2/(n1+n2)) formülüyle
  örneklem büyüklüğüne bağlanır (standart Cohen 1988 tanımı).

## 2. Yuvarlama kuralı

- `[AJAN]` (doğrulanacak) G*Power'ın a-priori modda gerekli N'yi tam sayıya
  **yukarı yuvarladığı** (ceil) gözlemi: statsmodels.stats.power ile aynı
  girdi (d=0.5, α=0.05, power=0.95, tails=1, ratio=1) için kesirli N=87.2626
  hesaplanıyor; G*Power protokolünde n1=n2=88 görünüyor (CONTRACT.md §9).
  `ceil(87.2626)=88` ile tutarlı ama REA ile fonksiyon seviyesinde
  doğrulanmadı (round-half-up veya farklı bir eşik kuralı da aynı sonucu
  verebilir; ayrım ancak sınır değerlerde — örn. kesirli kısım tam 0.5'e
  yakınken — ortaya çıkar).
- `[REA]` _(Oturum 1'de doldurulacak: ceil fonksiyonunun çağrıldığı adres/
  dize referansı, ya da alternatif bir yuvarlama rutini)_

## 3. Eşit olmayan oran (ratio ≠ 1) dağıtımı

- `[AJAN]` (doğrulanacak) `ratio` = N2/N1 girildiğinde G*Power'ın önce n1'i
  mi yoksa n2'yi mi yuvarladığı, ardından diğerinin `round(n1*ratio)` ile mi
  yoksa `ceil` ile mi türetildiği kılavuzda yazmıyor.
- `[REA]` _(Oturum 1'de doldurulacak)_

## 4. İterasyon durma koşulu (a-priori N arama)

- `[AJAN]` (doğrulanacak) a-priori modda G*Power olası N üzerinde arama
  yaparak `actual_power >= power` koşulunu sağlayan en küçük N'yi buluyor
  gibi görünüyor (tipik güç analizi algoritması), ancak arama yönteminin
  (ikili arama mı, N'yi 1'er 1'er artırma mı) ve durma toleransının kanıtı yok.
- `[REA]` _(Oturum 1'de doldurulacak)_

## 5. Geçersiz girdiye tepki

- `[AJAN]` (doğrulanacak) GUI üzerinden α=0 veya d<0 gibi değerler
  girildiğinde G*Power'ın davranışı (sessiz reddetme, hata mesaj kutusu,
  alanın kırmızıya dönmesi vb.) henüz REA ile incelenmedi, yalnızca GUI
  gözlemi planlanıyor (oracle/collect_vectors.py'nin geçersiz-girdi seti).
- `[REA]` _(Oturum 1'de doldurulacak)_

## 6. Ondalık gösterim / hassasiyet

- `[DOK]` G*Power protokol çıktısında değerleri 7 ondalık basamakla
  gösterir (CONTRACT.md §6'da da belirtilmiş, gösterim G*Power'ın kendi
  arayüzünden gözlemlenebilir — örn. `ncp = 3.3166248`).

---

## Oturum 1 ilerleme notu

Bu defter, REA+Ghidra statik analizi GPowerNT.exe üzerinde çalıştırıldıktan
sonra `[REA]` satırlarıyla güncellenecektir. Şu an yalnızca `[DOK]` (yayımlanmış
kaynak) ve `[AJAN]` (GUI gözlemine dayalı, henüz ikili dosyada doğrulanmamış
hipotez) satırları doludur — bu, tam olarak ödevin istediği ayrımı yansıtır:
"Ajanınız kendinden emin bir açıklama yaptığında sorun: bunun kanıtı hangi
fonksiyonda?" Şu anki haliyle 2-5. bölümlerdeki iddiaların hiçbirinin
`[REA]` kanıtı yok; bu yüzden hiçbiri puanlanmaz.
