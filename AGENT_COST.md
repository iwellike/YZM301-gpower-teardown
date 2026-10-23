# AGENT_COST.md — Ajan Maliyet ve Süreç Günlüğü

## Kullanılan ajan

Claude Code (Sonnet 5), tek bir sürekli oturumda hem ortam kurulumu hem
kod/doküman üretimi için kullanıldı. Ödevin önerdiği "iki ayrı oturum"
yapısı şu şekilde uygulandı: _(doldurulacak — fiilen ayrı bir Agent
çağrısıyla mı yoksa prompts/ dosyalarıyla mı ayrıldığı netleştirilecek)_

## Ortam kurulum maliyeti (bu çalıştırma)

| Adım | Araç | Not |
|---|---|---|
| ffmpeg | winget | ~90 sn, tek komut |
| pywinauto/pillow/pywin32 | pip | ~30 sn |
| Ghidra 12.1.4 | GitHub Releases (zip, ~400+MB) | indirme ağ hızına bağlı, ~15-25 dk |
| G*Power 3.1.9.7 | resmi sayfa (zip, ~14MB) | ~5 sn |
| statsmodels/pandas/pytest | pip | ~30 sn |

## İterasyon sayısı / token tahmini

_(doldurulacak — bu oturumun toplam tool-call sayısı ve kabaca token
kullanımı; CLI/MCP/ajan katmanlarının her biri için ayrı satır)_

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

_(doldurulacak — AI ajanı katmanı bitince: aynı 10 soru hem MCP aracı
üzerinden hem G*Power ekran görüntüsü alıp okuyarak çözülecek, iki yolun
toplam token, süre ve doğruluğu karşılaştırılacak)_
