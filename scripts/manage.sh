#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$ROOT_DIR/VERSION"
README_FILE="$ROOT_DIR/README.md"
RUST_PROXY_MANIFEST="$ROOT_DIR/rust-proxy/Cargo.toml"
WEB_UI_DIR="$ROOT_DIR/data/web-ui"

usage() {
  cat <<'USAGE'
Usage: scripts/manage.sh <command> [args]

Commands:
  clean
      Remove build artifacts for web-ui and rust-proxy.

  build [dev|release]
      Build web-ui (if present) and rust-proxy.

  run <mode>
      Run in one of these modes:
        dev         Run rust-proxy in development mode
        prod        Run rust-proxy in production mode (release binary)
        proxy-dev   Same as dev
        proxy-prod  Same as prod
        web-dev     Run web-ui in development mode

  release
      Build release artifacts for web-ui and rust-proxy.

  version <bump|minor|major>
      Update VERSION and sync known version references.
USAGE
}

log() {
  printf '[manage] %s\n' "$*"
}

fail() {
  printf '[manage][error] %s\n' "$*" >&2
  exit 1
}

detect_node_pm() {
  if command -v pnpm >/dev/null 2>&1; then
    printf 'pnpm\n'
    return
  fi
  if command -v npm >/dev/null 2>&1; then
    printf 'npm\n'
    return
  fi
  printf '\n'
}

node_install() {
  local pm
  pm="$(detect_node_pm)"
  if [[ -z "$pm" ]] || [[ ! -f "$WEB_UI_DIR/package.json" ]]; then
    return 0
  fi

  if [[ "$pm" == "pnpm" ]]; then
    (cd "$WEB_UI_DIR" && pnpm install)
  else
    log "pnpm not found; falling back to npm"
    (cd "$WEB_UI_DIR" && npm install)
  fi
}

node_run_script() {
  local script="$1"
  local pm
  pm="$(detect_node_pm)"

  if [[ ! -f "$WEB_UI_DIR/package.json" ]]; then
    return 0
  fi
  if [[ -z "$pm" ]]; then
    fail "Neither pnpm nor npm is installed"
  fi

  if [[ "$pm" == "pnpm" ]]; then
    (cd "$WEB_UI_DIR" && pnpm run "$script")
  else
    log "pnpm not found; falling back to npm"
    (cd "$WEB_UI_DIR" && npm run "$script")
  fi
}

cargo_build() {
  local mode="$1"
  if ! command -v cargo >/dev/null 2>&1; then
    fail "cargo is required for rust-proxy commands"
  fi

  if [[ "$mode" == "release" ]]; then
    cargo build --manifest-path "$RUST_PROXY_MANIFEST" --release
  else
    cargo build --manifest-path "$RUST_PROXY_MANIFEST"
  fi
}

cmd_clean() {
  log "Cleaning rust-proxy artifacts"
  if command -v cargo >/dev/null 2>&1 && [[ -f "$RUST_PROXY_MANIFEST" ]]; then
    cargo clean --manifest-path "$RUST_PROXY_MANIFEST"
  else
    rm -rf "$ROOT_DIR/rust-proxy/target"
  fi

  if [[ -f "$WEB_UI_DIR/package.json" ]]; then
    log "Cleaning web-ui artifacts"
    rm -rf "$WEB_UI_DIR/.svelte-kit" "$WEB_UI_DIR/build" "$WEB_UI_DIR/dist"
  fi
}

cmd_build() {
  local mode="${1:-dev}"
  node_install
  node_run_script build

  if [[ "$mode" == "release" ]]; then
    cargo_build release
  else
    cargo_build dev
  fi
}

cmd_run() {
  local mode="${1:-dev}"

  case "$mode" in
    dev|proxy-dev)
      MMAIL_PROXY_MODE=development cargo run --manifest-path "$RUST_PROXY_MANIFEST"
      ;;
    prod|proxy-prod)
      MMAIL_PROXY_MODE=production cargo run --manifest-path "$RUST_PROXY_MANIFEST" --release
      ;;
    web-dev)
      node_install
      node_run_script dev
      ;;
    *)
      fail "Unknown run mode: $mode"
      ;;
  esac
}

semver_increment() {
  local current="$1"
  local mode="$2"

  if [[ ! "$current" =~ ^([0-9]+)\.([0-9]+)\.([0-9]+)$ ]]; then
    fail "Invalid semantic version in VERSION: $current"
  fi

  local major="${BASH_REMATCH[1]}"
  local minor="${BASH_REMATCH[2]}"
  local patch="${BASH_REMATCH[3]}"

  case "$mode" in
    bump)
      patch=$((patch + 1))
      ;;
    minor)
      minor=$((minor + 1))
      patch=0
      ;;
    major)
      major=$((major + 1))
      minor=0
      patch=0
      ;;
    *)
      fail "Unsupported version mode: $mode"
      ;;
  esac

  printf '%s.%s.%s\n' "$major" "$minor" "$patch"
}

sync_version_references() {
  local new_version="$1"

  if [[ -f "$README_FILE" ]]; then
    if grep -q '^\*\*Current Version:\*\* ' "$README_FILE"; then
      sed -i -E "s/^\*\*Current Version:\*\* .*/**Current Version:** ${new_version}/" "$README_FILE"
    fi
  fi

  if [[ -f "$RUST_PROXY_MANIFEST" ]]; then
    sed -i -E "0,/^version = \"[^\"]+\"/s//version = \"${new_version}\"/" "$RUST_PROXY_MANIFEST"
  fi

  if [[ -f "$WEB_UI_DIR/package.json" ]]; then
    python - "$WEB_UI_DIR/package.json" "$new_version" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
version = sys.argv[2]
obj = json.loads(path.read_text())
obj["version"] = version
path.write_text(json.dumps(obj, indent=2) + "\n")
PY
  fi
}

cmd_version() {
  local mode="${1:-}"
  [[ -n "$mode" ]] || fail "Missing version mode: bump|minor|major"

  if [[ ! -f "$VERSION_FILE" ]]; then
    printf '0.1.0\n' > "$VERSION_FILE"
  fi

  local current
  current="$(tr -d ' \n\r' < "$VERSION_FILE")"
  local next
  next="$(semver_increment "$current" "$mode")"

  printf '%s\n' "$next" > "$VERSION_FILE"
  sync_version_references "$next"
  log "Version updated: ${current} -> ${next}"
}

cmd_release() {
  cmd_build release
  log "Release build complete"
}

main() {
  local command="${1:-}"
  if [[ -z "$command" ]] || [[ "$command" == "-h" ]] || [[ "$command" == "--help" ]]; then
    usage
    exit 0
  fi

  shift || true

  case "$command" in
    clean)
      cmd_clean "$@"
      ;;
    build)
      cmd_build "$@"
      ;;
    run)
      cmd_run "$@"
      ;;
    release)
      cmd_release "$@"
      ;;
    version)
      cmd_version "$@"
      ;;
    *)
      usage
      fail "Unknown command: $command"
      ;;
  esac
}

main "$@"
