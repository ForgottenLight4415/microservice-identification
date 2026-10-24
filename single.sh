#!/usr/bin/env bash
# Runs main.py on ONE monolith, the same way batch.sh does, then prints a quick
# check of how many dependencies cross services in the parsed output.
# Output: runs/<datetime>/<name>/run.txt and runs/<datetime>/<name>/results/... (same layout as batch.sh)
# Usage, inside the container:
#   ./single.sh <name-under-$MONO_ROOT | /path/to/monolith> [extra main.py args, e.g. -k 8 -m]
# Examples:
#   ./single.sh piggymetrics-united
#   ./single.sh /monoliths/train-ticket-united -k 12
# Set ALLOW_STALE_JAR=1 to run even if the parser jar is older than the Java sources.
set -u

if [ $# -lt 1 ]; then
  echo "Usage: $0 <monolith name or path> [extra main.py args]"; exit 1
fi

REPO="${REPO:-/workspace}"
MONO_ROOT="${MONO_ROOT:-/monoliths}"
LOG_DIR="${LOG_DIR:-$REPO/runs}"
WORK_ROOT="${WORK_ROOT:-/tmp/msid-jobs}"

# Accept either a bare name (looked up under $MONO_ROOT) or a path
target="$1"; shift
if [ -d "$target" ]; then dir="$target"; else dir="$MONO_ROOT/$target"; fi
dir="${dir%/}"
if [ ! -d "$dir" ]; then echo "Not found: $dir"; exit 1; fi
if ! find "$dir" -name '*.java' -print -quit | grep -q .; then
  echo "No .java files under $dir"; exit 1
fi

JAR="$REPO/symbolsolver/target/symbolsolver-1.0.jar"
if [ ! -f "$JAR" ]; then
  echo "Missing $JAR. Build it first: cd $REPO/symbolsolver && mvn package -DskipTests"; exit 1
fi
# Stop if the jar is older than the Java sources, since the point is usually to test a parser change
if [ -n "$(find "$REPO/symbolsolver/src" "$REPO/symbolsolver/pom.xml" -newer "$JAR" -print -quit 2>/dev/null)" ]; then
  if [ "${ALLOW_STALE_JAR:-0}" != "1" ]; then
    echo "Java sources changed after the jar was built. Rebuild: cd $REPO/symbolsolver && mvn package -DskipTests"
    echo "(or set ALLOW_STALE_JAR=1 to run anyway)"; exit 1
  fi
  echo "WARNING: running with a jar older than the Java sources (ALLOW_STALE_JAR=1)"
fi

name="$(basename "$dir")"
out="$LOG_DIR/$(date +%Y%m%d_%H%M%S)/$name"   # runs/<datetime>/<name>/, same as batch.sh
log="$out/run.txt"
results="$out/results"
mkdir -p "$WORK_ROOT"
# Unique job folder per run, so two runs of the same project can run at the same time
job="$(mktemp -d "$WORK_ROOT/$name.XXXXXX")"
mkdir -p "$results"

# Private copy of the repo, skipping .git, earlier runs and the ~500 MB build output
(cd "$REPO" && tar cf - --exclude=./.git --exclude=./runs --exclude=./symbolsolver/target \
    --exclude='__pycache__' .) | (cd "$job" && tar xf -)
# Link the parser jar instead of copying it. Java still runs from inside the job copy,
# because Constants.getRootPath() works out the repo root from the current directory.
mkdir -p "$job/symbolsolver/target"
ln -s "$JAR" "$job/symbolsolver/target/symbolsolver-1.0.jar"
touch "$job/.start"

echo ">>> [$name] started  ->  $log"
# tee so progress is visible live and still saved
(cd "$job/app" && python -u main.py -p "$dir" "$@") 2>&1 | tee "$log"
rc=${PIPESTATUS[0]}

# Keep every file the run created or changed (paths kept, e.g. results/data/output.json)
(cd "$job" && find . -type f -newer .start ! -name .start -exec cp --parents {} "$results/" \;)
rm -rf "$job"

if [ $rc -eq 0 ]; then echo ">>> [$name] OK"; else echo ">>> [$name] FAILED (exit $rc), see $log"; fi

# Quick check: dependencies between classes of different original services.
# Service = the package segment after com.micro2mono.unified; anything else is grouped by its first 3 segments.
OUTPUT_JSON="$results/data/output.json"
if [ -f "$OUTPUT_JSON" ]; then
  python - "$OUTPUT_JSON" <<'EOF'
import json, sys, collections
out = json.load(open(sys.argv[1]))
def svc(c):
    p = c.split('.')
    return p[3] if p[:3] == ['com', 'micro2mono', 'unified'] and len(p) > 3 else '.'.join(p[:3])
deps = [(c, d) for c, v in out.items() for d in v.get('dependencies', []) if d in out]
cross = collections.Counter((svc(c), svc(d)) for c, d in deps if svc(c) != svc(d))
print()
print(f"Classes parsed:            {len(out)}")
print(f"Services (by package):     {len(set(map(svc, out)))}")
print(f"Internal dependencies:     {len(deps)}")
print(f"Cross-service dependencies: {sum(cross.values())}")
for (a, b), n in cross.most_common(10):
    print(f"   {a} -> {b}: {n}")
EOF
else
  echo "No output.json in results (the run failed before it was saved). See $log"
fi

echo "Logs and results in: $out"
exit $rc
