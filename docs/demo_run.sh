#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit 1
step() { echo; echo "### $1"; sleep 1; }

clear
echo "gpower-clone -- t2-indep CLI demo"
sleep 2

step "1) Surum sorgusu"
echo '$ ./gpower-clone --version'
./gpower-clone --version
sleep 4

step "2) a-priori: CONTRACT.md referans ornegi (d=0.5, alpha=0.05, power=0.95)"
echo '$ ./gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1'
./gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0.05 --power 0.95 --ratio 1
sleep 5

step "3) post-hoc: ayni n1/n2 ile gucu dogrula"
echo '$ ./gpower-clone --test t2-indep --mode post-hoc --tails 1 --d 0.5 --alpha 0.05 --n1 88 --n2 88'
./gpower-clone --test t2-indep --mode post-hoc --tails 1 --d 0.5 --alpha 0.05 --n1 88 --n2 88
sleep 5

step "4) Gecersiz girdi: alpha=0 -> OUT_OF_RANGE, exit 2"
echo '$ ./gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0 --power 0.95 --ratio 1'
./gpower-clone --test t2-indep --mode a-priori --tails 1 --d 0.5 --alpha 0 --power 0.95 --ratio 1
echo "exit=$?"
sleep 5

step "5) Test paketi"
echo '$ python -m pytest tests/ -q'
python -m pytest tests/ -q
sleep 8

echo
echo "Demo bitti."
sleep 4
