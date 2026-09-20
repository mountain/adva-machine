#!/bin/bash
# Run the host-dependent machine checks on the resident Linux guest.
#
# Some checks declare a per-child address-space limit (RLIMIT_AS). That limit is
# Linux-only: on macOS a child launched under it dies inside preexec_fn. This
# syncs the working tree into a Lima guest, builds the native binary there when
# it is missing, runs the acceptance and (by default) the host-dependent tests.
#
#   scripts/linux_host_check.sh                 acceptance + host-limit tests
#   scripts/linux_host_check.sh --full          the whole python suite
#   scripts/linux_host_check.sh --retain NAME   also retain toolchain/evidence/NAME
#
# The guest and its state are described in docs/maintenance/LINUX_HOST_FIXTURE.md.
set -u

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
LIMA_HOME="${LIMA_HOME:-$(dirname "$REPO")/.lima-adva}"
INSTANCE="${ADVA_LIMA_INSTANCE:-adva}"
GUEST_DIR="${ADVA_LIMA_DIR:-adva-machine}"
export LIMA_HOME

MODE="host-limit"
RETAIN=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    --full) MODE="full" ;;
    --retain) shift; RETAIN="${1:-}" ;;
    *) echo "usage: $0 [--full] [--retain NAME]" >&2; exit 2 ;;
  esac
  shift
done

if ! command -v limactl >/dev/null 2>&1; then
  echo "limactl is not installed; see docs/maintenance/LINUX_HOST_FIXTURE.md" >&2
  exit 2
fi
if [ "$(limactl list --format '{{.Status}}' "$INSTANCE" 2>/dev/null)" != "Running" ]; then
  echo "guest '$INSTANCE' is not running; run: limactl start $INSTANCE --tty=false" >&2
  exit 2
fi

TARGETS="tests/python/test_phase_runner.py tests/python/test_triadic_free.py \
tests/python/test_pascal_commutator_certificate.py tests/python/test_machine_toolchain_evidence.py"
if [ "$MODE" = "full" ]; then
  TARGETS="tests/python"
fi

limactl shell "$INSTANCE" -- bash -lc "
set -e
rsync -a --delete --exclude target --exclude .venv --exclude .venv-linux \
  --exclude .cargo-adva --exclude .lima-adva '$REPO/' \"\$HOME/$GUEST_DIR/\"
cd \"\$HOME/$GUEST_DIR\"
test -x target/release/adva || cargo build --locked --release -p adva-witness --bin adva
echo '--- conform ---'
.venv-linux/bin/python adva-machine conform --output /tmp/adva-conform-\$\$ | \
  .venv-linux/bin/python -c 'import json,sys; d=json.load(sys.stdin); print(d[\"status\"], d.get(\"case_count\"), d.get(\"host\"), d[\"cost\"][\"limits\"].get(\"address_space_limit_installed\"))'
echo '--- pytest ---'
.venv-linux/bin/python -m pytest -q $TARGETS
$([ -n "$RETAIN" ] && echo "rm -rf toolchain/evidence/$RETAIN && .venv-linux/bin/python adva-machine conform --output toolchain/evidence/$RETAIN >/dev/null && .venv-linux/bin/python -m toolchain.archive toolchain/evidence/$RETAIN" || echo ":")
"
STATUS=$?

if [ -n "$RETAIN" ]; then
  GUEST_HOME="$(limactl shell "$INSTANCE" -- bash -lc 'echo "$HOME"' | tr -d '\r')"
  mkdir -p "$REPO/toolchain/evidence/$RETAIN"
  limactl copy -r "$INSTANCE:$GUEST_HOME/$GUEST_DIR/toolchain/evidence/$RETAIN/." \
    "$REPO/toolchain/evidence/$RETAIN/" >/dev/null
  echo "retained toolchain/evidence/$RETAIN in the working tree; commit it deliberately"
fi
exit $STATUS
