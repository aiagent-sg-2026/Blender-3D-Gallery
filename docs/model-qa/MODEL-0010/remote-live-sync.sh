set -e
python3 - <<'PYINNER'
import subprocess
assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()=='34d008ba9f156c7f98ec58fc47f227f354f9dd81'
assert not subprocess.check_output(['git','diff','--name-only'],text=True).strip()
PYINNER
git fetch --depth=5 --filter=blob:none origin af8240b615ffeee5f2b43b35d08d0813453eb604
git merge-base --is-ancestor HEAD FETCH_HEAD
git merge --ff-only --quiet FETCH_HEAD
git diff --exit-code 34d008ba9f156c7f98ec58fc47f227f354f9dd81 HEAD -- scripts tests package.json package-lock.json models/catalog.json models/eight-ball-billiards
