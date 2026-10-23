# AGENT_COST.md — Ajan Maliyet ve Süreç Günlüğü

## Kullanılan ajan

Claude Code (Sonnet 5), tek bir sürekli oturumda hem ortam kurulumu hem
kod/doküman üretimi için kullanıldı.

**Dürüst not — "iki ayrı oturum" tam olarak uygulanmadı.**
`prompts/session1_first_prompt.txt` ve `session2_first_prompt.txt`
tasarımı iki AYRI ajan çağrısı/konuşması öngörüyor (Oturum 2'nin Oturum
1'in Ghidra çıktısını ve konuşma geçmişini GÖRMEMESİ gerekiyor — gerçek
"temiz oda"). Fiilen bu çalıştırmada her ikisi de **aynı sürekli Claude
Code konuşmasında** yapıldı: REA/Ghidra bulgularını üreten ben (ajan),
hemen ardından SPEC.md/ASSUMPTIONS.md/motor/CLI'yi de aynı bağlamda
yazdım. Yani motoru yazarken LEDGER.md'deki `[REA]` bulgularını (örn.
`ceil()` kuralı) zaten görüyordum — bu, ödevin istediği "ayrım testi"
(iki bağımsız ajanın aynı sonuca ulaşıp ulaşmadığı) açısından **daha
zayıf bir kanıt**: motor LEDGER'a göz atarak değil ama LEDGER'ı bilerek
yazıldı. Gerçek bir iki-oturum ayrımı için `src/engine`/`src/cli`'nin
SPEC.md+CONTRACT.md+oracle/public_vectors.jsonl'den başka hiçbir şey
görmeyen taze bir Agent çağrısıyla (`subagent_type` yeni, sıfır bağlam)
yeniden yazılması ve sonucun karşılaştırılması gerekir — bu sprintte
yapılmadı.

## Ortam kurulum maliyeti (bu çalıştırma)

| Adım | Araç | Not |
|---|---|---|
| ffmpeg | winget | ~90 sn, tek komut |
| pywinauto/pillow/pywin32 | pip | ~30 sn |
| Ghidra 12.1.4 | GitHub Releases (zip, ~400+MB) | indirme ağ hızına bağlı, ~15-25 dk |
| G*Power 3.1.9.7 | resmi sayfa (zip, ~14MB) | ~5 sn |
| statsmodels/pandas/pytest | pip | ~30 sn |

## İterasyon sayısı / token tahmini

Tam token sayacı tutulmadı (bu bilgiye erişimim yok); aşağıdaki sayılar
yalnızca tool-call SAYISININ kaba mertebesi, gerçek ölçüm değil:

| Katman | Yaklaşık tool-call sayısı | Not |
|---|---|---|
| REA/Ghidra analizi (LEDGER.md) | ~15-20 | search_strings/xrefs/pseudo_code zinciri |
| SPEC.md + ASSUMPTIONS.md | ~5 | REA bulgularını Gherkin'e çevirme |
| Yuvarlama kuralı ampirik testi | ~5 (3 hipotez scripti + çalıştırma) | oracle/reverse_rounding.py |
| Motor + CLI (src/engine, src/cli) | ~10 | yazma + CONTRACT örnekleriyle doğrulama |
| Testler (tests/) | ~8 | engine/cli/differential/mcp/agent |
| MCP + AI ajanı (src/mcp, src/agent) | ~12 | server, classifier, run_eval, düzeltme |

Toplam kabaca 55-60 tool-call, tek bir sürekli oturumda.

## Neyi farklı yapardım

- pywinauto UIA çağrıları (select/set_edit_text/click) her biri 2-4 saniye
  sürdü — bu VM'de UI Automation gözlemci zinciri yavaş; ileride win32
  (MFC mesaj pompası) backend'i ya da doğrudan `WM_SETTEXT`/`BM_CLICK`
  mesajları ile 5-10x hızlanabilirdi.
- Ghidra indirmesini daha en başta, diğer kurulumlarla eşzamanlı başlatmak
  (yapıldı) doğru karardı; büyük indirmeler her zaman en başta tetiklenmeli.
- 4 kişilik takım ödevini tek başıma yaparken REA/Ghidra ile GUI toplamayı
  aynı anda yürütmek yerine önce REA bulgularını tamamlayıp SPEC.md'yi
  kilitlemek, sonra GUI oracle toplamayı paralel koşturmak daha temiz bir
  "önce kanıt, sonra spec" sırası olurdu.

## Token/süre/doğruluk karşılaştırması (MCP vs GUI ekran görüntüsü)

**MCP tarafı tamamlandı:** `src/agent/run_eval.py`, 10 kurgusal sorunun
hepsini "Jev" sınıflandırıcısı + `power_analysis` MCP aracıyla çözdü —
10/10 doğru aile sınıflandırması, güven≥0.75 olan 9 sorunun 9'unda
doğru, log `logs/agent_calls.jsonl`'de. Bu yol gerçek bir LLM API çağrısı
içermediği için (deterministik Python sınıflandırıcı) token tüketimi
gerçekten **0** — uydurma bir placeholder değil, ölçülen gerçek.

**GUI tarafı: tek soru için gerçek, ölçülmüş karşılaştırma yapıldı
(soru 9, `oracle/gui_vs_mcp_q9.py`, sonuç `docs/gui_vs_mcp_q9.json`).**
G*Power 3.1.9.7 bu oturumda zaten açık kalmıştı; pywinauto ile canlı
GUI'ye soru 9'un parametreleri (tails=1, d=0.8, alpha=0.01, power=0.9,
ratio=2) girildi, Calculate'a basıldı, çıktı alanları okundu — tıpkı
MCP aracının yaptığı gibi, ama GUI üzerinden (ekran görüntüsü:
`docs/gui_vs_mcp_q9.png`):

| Yol | Süre | n1 | n2 | n_total | actual_power |
|---|---|---|---|---|---|
| MCP (`power_analysis`) | **1.4 ms** | 32 | 63 | 95 | 0.9040607 |
| GUI (pywinauto, combobox+edit+click) | **40.9 s** | 32 | 64 | 96 | 0.9057807 |

Yaklaşık **29000×** hız farkı — beklenen sonuç, çünkü GUI yolu her
combobox seçimi/alan yazımı arasında UI Automation'ın gözlemci zincirini
bekliyor (bkz. yukarıdaki "Neyi farklı yapardım" notu, aynı yavaşlık
oracle toplama sırasında da gözlendi). Token tarafında MCP yolu burada
da **0** (deterministik Python), GUI yolu ise bir vizyon modeliyle
okunsaydı ekran görüntüsü başına ~1-2K token gerektirirdi (tahmini,
ölçülmedi — bu adımda ekran görüntüsünü ben doğrudan okudum, ayrı bir
vizyon API çağrısı yapılmadı).

**Doğruluk tarafında beklenmeyen ama değerli bir bulgu:** GUI'nin gerçek
çıktısı (n1=32, n2=64) motorun çıktısından (n1=32, n2=63) 1 birim farklı
çıktı — ASSUMPTIONS.md §1'de zaten belgelenen "ratio≠1'de ±1 sapma"
sınırının canlı bir örneği; bu sonuç `oracle/t2_indep_vectors.csv`'ye
30. vektör olarak eklendi (N eşleşme oranı 23/29'dan 23/30'a güncellendi,
bkz. README.md).

**Kalan 9 soru için GUI karşılaştırması yapılmadı** (kategorik etki
büyüklüğü içerdikleri için zaten MCP tarafı da aracı çağırmıyordu, bkz.
`logs/agent_calls.jsonl` — karşılaştırılacak bir "GUI sonucu" da anlamlı
olmazdı, çünkü girilecek net bir sayı yok).
