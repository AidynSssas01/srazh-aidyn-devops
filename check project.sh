#!/usr/bin/env bash
# ------------------------------------------------------------------
# check_project.sh — project structure check (Jenkins "Test" stage)
# Exit code 0 = all checks passed, 1 = at least one check failed.
# If this script fails, Jenkins marks the Test stage red and stops.
# ------------------------------------------------------------------
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR" || exit 1

FAILED=0
ok()   { echo "  [OK]   $1"; }
fail() { echo "  [FAIL] $1"; FAILED=1; }

echo "== Checking project structure in $PROJECT_DIR"
for d in app scripts config logs; do
    [ -d "$d" ] && ok "directory $d/" || fail "directory $d/ is missing"
done

for f in Srazh_Aidyn_info.txt config/app.conf app/app.py scripts/Srazh_Aidyn_system.sh \
         Dockerfile docker-compose.yml Jenkinsfile .gitignore README.md; do
    [ -f "$f" ] && ok "file $f" || fail "file $f is missing"
done

echo "== Checking student information file"
for field in "Name: Aidyn" "Surname: Srazh" "Group: IT2-2308" "Student ID:" "Course: DevOps"; do
    grep -q "^$field" Srazh_Aidyn_info.txt 2>/dev/null && ok "'$field'" || fail "'$field' not found"
done

echo "== Checking Bash script"
[ -x scripts/Srazh_Aidyn_system.sh ] && ok "script is executable" || fail "script is not executable"
bash -n scripts/Srazh_Aidyn_system.sh && ok "script syntax is valid" || fail "script syntax error"
scripts/Srazh_Aidyn_system.sh | grep -q "Student information file exists." \
    && ok "script finds Srazh_Aidyn_info.txt" || fail "script does not find the info file"

echo "== Checking Dockerfile instructions"
for instr in FROM WORKDIR COPY RUN EXPOSE CMD; do
    grep -q "^$instr " Dockerfile && ok "$instr" || fail "$instr is missing in Dockerfile"
done

echo "== Checking .gitignore rules"
for rule in '*.log' 'backup/' '.env'; do
    grep -qxF "$rule" .gitignore && ok "$rule is ignored" || fail "$rule is not in .gitignore"
done

if [ "$FAILED" -eq 0 ]; then
    echo "== RESULT: all checks passed"
else
    echo "== RESULT: some checks FAILED"
fi
exit "$FAILED"
