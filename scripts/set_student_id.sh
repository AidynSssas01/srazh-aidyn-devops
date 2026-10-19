#!/usr/bin/env bash
# Change the Student ID in every project file.
# The current ID is read from Srazh_Aidyn_info.txt.
# Usage: ./scripts/set_student_id.sh 123456
set -e
NEW_ID="$1"
if [ -z "$NEW_ID" ]; then
    echo "Usage: $0 <student-id>"; exit 1
fi
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"
OLD_ID=$(grep '^Student ID:' Srazh_Aidyn_info.txt | awk '{print $3}')
if [ "$OLD_ID" = "$NEW_ID" ]; then
    echo "Student ID is already $NEW_ID"; exit 0
fi
for f in $(grep -rl --exclude-dir=.git --exclude=set_student_id.sh "$OLD_ID" .); do
    sed -i.bak "s/${OLD_ID}/${NEW_ID}/g" "$f" && rm -f "$f.bak"
    echo "updated: $f"
done
echo "Student ID changed: $OLD_ID -> $NEW_ID"
