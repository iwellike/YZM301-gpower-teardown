# 60 saniyelik CLI demo script

Bu dosya video kaydı değil — kaydı (ekran kaydı) kendin alman gerekiyor,
burada yalnızca sırayla çalıştırman gereken komutlar ve beklenen çıktılar
var (terminalde ~45-60 saniyede biter).

```bash
# 1) Kurulum (5 sn)
pip install -r src/requirements.txt

# 2) Sürüm sorgusu (CONTRACT.md §2.2)
./gpower-clone --version
# {"contract_version": "1.0.0", "name": "melike-tikir-k1", "engine": "python 3.x"}

# 3) a-priori: CONTRACT.md §9 referans örneği
./gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
# {"ncp": 3.3166247903554, "critical_t": 1.6536580165162147, "df": 174,
#  "n1": 88, "n2": 88, "n_total": 176, "actual_power": 0.9514254482775333}

# 4) post-hoc: aynı n1/n2 ile gücü doğrula
./gpower-clone --test t2-indep --mode post-hoc --tails 1 --d 0.5 --alpha 0.05 --n1 88 --n2 88
# {"ncp": ..., "critical_t": ..., "df": 174, "power": 0.9514254...}

# 5) Geçersiz girdi: alpha=0 -> OUT_OF_RANGE, çıkış kodu 2
./gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0 --power 0.95 --ratio 1
echo "exit=$?"
# {"error": "...", "code": "OUT_OF_RANGE", "field": "alpha"}
# exit=2

# 6) Test paketi (33+ test)
python -m pytest tests/ -q
```

Ekran kaydı için: terminalde yukarıdaki 6 adımı art arda çalıştır, her
çıktının stdout'ta tek satır JSON olduğunu göster.
