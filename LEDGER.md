# Kanıt Defteri — t2-indep (t testi, iki bağımsız ortalama)

Etiketler: `[DOK]` kılavuzda/makalede yazıyor · `[REA]` binary'den kanıtlandı
(fonksiyon adresi/dize referansı) · `[AJAN]` ajan çıkarımı, kanıtsız.

**Puan yalnızca `[REA]` satırlarına verilir.**

GPowerNT.exe SHA-256: `c63e6a133eb6372932f810c08cc33dc35a06d1ddb658f897bd6c34a754efc812`
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
- `[REA]` `FUN_004a7140` (adres `0x4a7140`), GPowerNT.exe'nin a-priori N-arama
  motorunun (bkz. §4) ikinci çağrısında (arama tamamlanıp sürekli/kesirli N
  bulunduktan sonra) doğrudan CRT `ceil()` (import `API-MS-WIN-CRT-MATH-L1-1-0.DLL::ceil`,
  thunk `0x5ac047`) çağırıyor: `dVar7 = ceil(param_3 * *(double *)(in_ECX + 0xa6));`.
  Yani bulunan kesirli N, bir çarpan (`in_ECX+0xa6`, muhtemelen 1 ya da ratio'ya
  bağlı bir ölçek faktörü) ile çarpılıp **yukarı yuvarlanıyor** — `round`/`floor`
  değil, `ceil`. Bu, aynı `ceil` import'unun 34 farklı çağrı adresinden
  (`0x481980`…`0x567520`, `procedure_callers` ile listelendi) kullanıldığını da
  doğruluyor; yani ceil-ile-yukarı-yuvarlama G*Power'ın örneklem-büyüklüğü
  motorlarında genel bir desen. **Sınır:** `0x4a7140`'ın doğrudan çağıranı
  Ghidra tarafından çözülemedi (sanal/vtable çağrısı, `procedure_callers`
  0 sonuç döndürdü) — bu fonksiyonun t2-indep'in vtable yuvasına ait olduğu
  değil, G*Power'ın a-priori arama altyapısının (t2-indep'in de kullandığı)
  parçası olduğu kanıtlanmıştır.

## 3. Eşit olmayan oran (ratio ≠ 1) dağıtımı

- `[AJAN]` (doğrulanacak) `ratio` = N2/N1 girildiğinde G*Power'ın önce n1'i
  mi yoksa n2'yi mi yuvarladığı, ardından diğerinin `round(n1*ratio)` ile mi
  yoksa `ceil` ile mi türetildiği kılavuzda yazmıyor.
- `[REA]` `FUN_00487300` (adres `0x487300`) genel bir "ratio admissible range"
  doğrulayıcısı: `dVar4 = 1.0 / param_2; if ((param_2 <= param_1) && (param_1 <= dVar4)) return 1;`
  — yani `ratio` (param_1), `[L, 1/L]` aralığının (L=param_2, çağıran tarafından
  sabit geçiliyor) DIŞINDAYSA, G*Power N'leri sessizce kırpmıyor/düzeltmiyor,
  bunun yerine `"The allocation ratio falls outside the admissible range (...)"`
  (adres `0x5c679c`) metnini oluşturup başarısız dönüyor (return 0). Çözülebilen
  tek çağıran `FUN_004ad3a0` (`0x4ad3a0`, Proportions/iki-oran test ailesinin
  dağıtıcısı) `L=0x3f847ae147ae147b` = **0.01** sabitiyle çağırıyor → Proportions
  için admissible ratio aralığı `[0.01, 100]`. **Sınır:** t2-indep (Means) için
  bu doğrulayıcıyı çağıran spesifik adres sanal çağrı olduğundan çözülemedi;
  dolayısıyla t2-indep'in kendi L sabiti (oracle'daki 0.1–10 aralığının G*Power
  tarafından kabul edilmiş olmasından `L_means ≤ 0.1` çıkarımı yapılabilir, ama
  bu `[AJAN]` seviyesinde kalır — REA ile doğrulanan şey, **mekanizmanın
  kendisi** (`[L,1/L]` simetrik aralık + açık hata mesajı, sessiz düzeltme değil).

## 4. İterasyon durma koşulu (a-priori N arama)

- `[AJAN]` (doğrulanacak) a-priori modda G*Power olası N üzerinde arama
  yaparak `actual_power >= power` koşulunu sağlayan en küçük N'yi buluyor
  gibi görünüyor (tipik güç analizi algoritması), ancak arama yönteminin
  (ikili arama mı, N'yi 1'er 1'er artırma mı) ve durma toleransının kanıtı yok.
- `[REA]` `FUN_004a7140` (adres `0x4a7140`) iki aşamalı bir arama uyguluyor:
  (1) **geometrik sınırlama** — hedef güce ulaşılana kadar adayı `×1.2` (güç
  yetersizse) veya `÷1.2` (güç fazlaysa) ile büyütüp/küçültüyor, alt sınır
  `1e-10`/`2e-10` epsilon ile korunuyor (`dVar7 = 2e-10; if (2e-10 <= dVar4) dVar7 = dVar4;`
  ve `while (1e-10 < dVar7) {...}`); (2) ardından bulunan aralıkta **ikiye
  bölerek arama (bisection)** — `dVar4 = (dVar5 + dVar4) * 0.5;` — aralık
  genişliği `1e-7`'nin altına düşene kadar (`while (1e-07 < dVar3)`) veya
  güç farkı `1e-8`'in altına düşene kadar (`if (ABS((double)fVar2 - *(double *)(in_ECX + 0x2e)) < 1e-08) break;`)
  devam ediyor. Yani durma koşulu ne saf `actual_power >= power` ne de sabit
  adımlı tarama; **geometrik parantezleme + bisection**, N-aralığı toleransı
  `1e-7`, güç-farkı toleransı `1e-8`. Bulunan kesirli N, §2'de açıklanan `ceil`
  adımına gidiyor. **Sınır:** bu rutinin t2-indep'e özgü vtable yuvasına
  bağlandığı sanal çağrı nedeniyle doğrudan izlenemedi; yukarıdaki algoritma
  G*Power'ın paylaşılan a-priori arama motorunda REA ile doğrulanmıştır.

## 5. Geçersiz girdiye tepki

- `[AJAN]` (doğrulanacak) GUI üzerinden α=0 veya d<0 gibi değerler
  girildiğinde G*Power'ın davranışı (sessiz reddetme, hata mesaj kutusu,
  alanın kırmızıya dönmesi vb.) henüz REA ile incelenmedi, yalnızca GUI
  gözlemi planlanıyor (oracle/collect_vectors.py'nin geçersiz-girdi seti).
- `[REA]` Etki büyüklüğü (`d`) için: `FUN_004d4bd0` (adres `0x4d4bd0`,
  `effect size must be greater than 0.00001.` dizesine 4 referanstan biri —
  diğerleri `0x4d9287`, `0x4dd1d6`, `0x4df7e7`, aynı deseni taşıyan kardeş
  doğrulayıcılar): `if ((param_1 == 0) && (ABS(param_2) <= 1e-05 && ABS(param_2) != 1e-05)) { /* hata string'i oluştur, başarısız dön */ }`.
  Yani `|d| < 1e-05` ise G*Power **sessizce düzeltmiyor**, açık bir hata
  mesajı üretip işlemi durduruyor; kontrol `d`'nin işaretine değil
  **mutlak değerine** bakıyor (bu fonksiyon için negatif `d`'nin tek başına
  reddedilip reddedilmediği ayrı bir sorudur, bu REA bulgusu sadece
  `|d| < 1e-5` eşiğini kanıtlıyor). Benzer desen ratio için §3'te: admissible
  aralık dışına çıkan ratio da sessizce kırpılmıyor, açık hata metni
  üretiyor. `alpha=0`, `alpha=1`, `tails=3` için eşdeğer bir doğrulayıcı
  Oturum 1'de bulunamadı — hâlâ açık.

## 6. Ondalık gösterim / hassasiyet

- `[DOK]` G*Power protokol çıktısında değerleri 7 ondalık basamakla
  gösterir (CONTRACT.md §6'da da belirtilmiş, gösterim G*Power'ın kendi
  arayüzünden gözlemlenebilir — örn. `ncp = 3.3166248`).

---

## Oturum 1 ilerleme notu

REA + Ghidra 12.1.4 ile GPowerNT.exe üzerinde statik analiz yapıldı (x86 PE,
9116 fonksiyon, 2570 string, Ghidra `rea-workflow` aracılığıyla). Bulgu
yöntemi: ilgili GUI dizelerinden (`search_strings`) başlayıp `xrefs` ve
`resolve_containing_procedure` ile üretici fonksiyona inilip
`procedure_pseudo_code` ile kısa alıntı çıkarıldı.

**Doğrulanan (`[REA]`):** ceil-ile-yuvarlama deseni (§2), ratio için
`[L,1/L]` admissible-aralık doğrulaması + sessiz-değil açık hata deseni (§3),
a-priori N aramasının geometrik parantezleme + bisection algoritması ve
toleransları (§4), effect-size `|d|<1e-5` eşiği ve açık hata deseni (§5).

**Önemli sınırlama:** GPowerNT.exe C++ (STL `std::basic_ostream` kullanımı
gözlemlendi, Delphi değil) ile yazılmış ve test aileleri aşırı derecede
**sanal fonksiyon tablosu (vtable) üzerinden** çağrılıyor. Bu yüzden
`procedure_callers` çoğu kritik fonksiyon için 0 çözülmüş çağıran döndürdü
(örn. `0x4a7140`, `0x4d9a00`) — Ghidra statik analizi indirekt/sanal çağrıları
çözemiyor. Bu nedenle yukarıdaki algoritmaların **G*Power'ın paylaşılan
a-priori/doğrulama altyapısında** (tüm örneklem-büyüklüğü testlerinin
kullandığı ortak motor) doğrulandığı söylenebilir, ama "bu adres, t2-indep'in
kendi vtable yuvasıdır" iddiası REA ile kanıtlanamadı — bu ayrım ilgili her
maddede açıkça belirtildi. `alpha`/`tails` geçersiz girdi davranışı ve
ratio'nun t2-indep'e özgü `L` sabiti hâlâ açık (`[AJAN]` kalıyor).
