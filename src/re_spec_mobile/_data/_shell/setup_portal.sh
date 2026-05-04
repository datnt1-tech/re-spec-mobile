#!/usr/bin/env bash
# setup_portal.sh — one-time setup of droidrun Portal APK on the connected device.
#
# Steps:
#  1. Verify adb + exactly one device connected (or use $SPEC_PROFILE.serial)
#  2. Download pinned Portal APK release (version in portal_version.txt) if not cached
#  3. Install (reinstall if needed) + grant runtime permissions
#  4. Detect whether accessibility service is enabled; if not, instruct manual enable
#  5. Set up TCP port forwarding for Portal HTTP (8080)
#  6. Probe `content://com.droidrun.portal/state` to confirm Portal is live
#  7. Disable element-inspect overlay (best-effort broadcast; manual fallback printed)
#  8. Print success banner

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Cache APK in user dir; site-packages may be read-only when pip-installed.
CACHE_DIR="${RE_SPEC_CACHE:-$HOME/.cache/re-spec-mobile}"
VERSION_FILE="$SCRIPT_DIR/portal_version.txt"
PORTAL_VERSION=$(cat "$VERSION_FILE" | tr -d ' \n\r')
PORTAL_VERSION_NUMERIC="${PORTAL_VERSION#v}"
PORTAL_PKG="com.droidrun.portal"
PORTAL_APK_URL="https://github.com/droidrun/droidrun-portal/releases/download/${PORTAL_VERSION}/com.droidrun.portal-${PORTAL_VERSION_NUMERIC}-debug.apk"
PORTAL_APK_PATH="$CACHE_DIR/com.droidrun.portal-${PORTAL_VERSION_NUMERIC}-debug.apk"

banner() { printf "\n\033[1;36m=== %s ===\033[0m\n" "$*"; }
ok()     { printf "\033[1;32m✓\033[0m %s\n" "$*"; }
warn()   { printf "\033[1;33m!\033[0m %s\n" "$*"; }
fail()   { printf "\033[1;31m✗\033[0m %s\n" "$*"; exit 1; }

banner "1. adb + device check"
command -v adb >/dev/null || fail "adb not on PATH"
DEVICES=$(adb devices | awk 'NR>1 && $2=="device" {print $1}')
DEVICE_COUNT=$(echo "$DEVICES" | grep -c . || true)
[[ "$DEVICE_COUNT" == "1" ]] || fail "Expected exactly 1 device online, got $DEVICE_COUNT: $DEVICES"
SERIAL="$DEVICES"
ok "Device: $SERIAL"

banner "2. Portal APK"
mkdir -p "$CACHE_DIR"
if [[ ! -f "$PORTAL_APK_PATH" ]]; then
  warn "Downloading pinned Portal ${PORTAL_VERSION}"
  curl -fsSL -o "$PORTAL_APK_PATH" "$PORTAL_APK_URL" || fail "Download failed from $PORTAL_APK_URL"
fi
ok "APK cached: $PORTAL_APK_PATH"

banner "3. Install"
INSTALLED_VERSION=$(adb -s "$SERIAL" shell "dumpsys package $PORTAL_PKG | grep versionName | head -1" 2>/dev/null | sed 's/.*versionName=//' | tr -d '\r\n' || true)
if [[ "$INSTALLED_VERSION" == "${PORTAL_VERSION#v}" ]]; then
  ok "Portal already at $INSTALLED_VERSION"
else
  warn "Installing (current: '${INSTALLED_VERSION:-none}', target: ${PORTAL_VERSION#v})"
  adb -s "$SERIAL" install -r -g "$PORTAL_APK_PATH" >/dev/null || fail "adb install failed"
  ok "Installed"
fi

banner "4. Accessibility service"
A11Y_ENABLED=$(adb -s "$SERIAL" shell "settings get secure enabled_accessibility_services" 2>/dev/null | tr -d '\r\n')
if [[ "$A11Y_ENABLED" == *"$PORTAL_PKG"* ]]; then
  ok "Portal accessibility enabled"
else
  warn "Portal accessibility NOT enabled. Attempting adb-side toggle..."
  CURRENT="${A11Y_ENABLED}"
  NEW_SERVICE="$PORTAL_PKG/com.droidrun.portal.DroidrunAccessibilityService"
  if [[ -z "$CURRENT" || "$CURRENT" == "null" ]]; then
    NEW_LIST="$NEW_SERVICE"
  else
    NEW_LIST="${CURRENT}:${NEW_SERVICE}"
  fi
  adb -s "$SERIAL" shell "settings put secure enabled_accessibility_services '$NEW_LIST'" 2>/dev/null || true
  adb -s "$SERIAL" shell "settings put secure accessibility_enabled 1" 2>/dev/null || true
  sleep 1
  A11Y_CHECK=$(adb -s "$SERIAL" shell "settings get secure enabled_accessibility_services" 2>/dev/null | tr -d '\r\n')
  if [[ "$A11Y_CHECK" == *"$PORTAL_PKG"* ]]; then
    ok "Enabled via adb"
  else
    cat <<EOF

\033[1;33m⚠ adb-side toggle blocked (common on Pixel/AOSP).\033[0m

Please enable the accessibility service manually (ONE TIME):
  1. On the device: \033[1mSettings → Accessibility → Installed apps → droidrun Portal\033[0m
  2. Toggle the service ON and confirm the system warning
  3. Re-run: \033[1mbash $0\033[0m

Or open directly:
  adb -s $SERIAL shell am start -a android.settings.ACCESSIBILITY_SETTINGS

EOF
    exit 2
  fi
fi

banner "5. TCP forward (Portal HTTP on 8080)"
adb -s "$SERIAL" forward tcp:8080 tcp:8080 >/dev/null && ok "Forward 8080 → device 8080"

banner "6. Portal probe"
PROBE=$(adb -s "$SERIAL" shell "content query --uri content://com.droidrun.portal/state" 2>&1 | head -c 400 || true)
if [[ "$PROBE" == *'"status":"success"'* ]] || [[ "$PROBE" == *'"a11y_tree"'* ]]; then
  ok "Portal responding (v0.6.x: success+result envelope)"
elif [[ "$PROBE" == *'Accessibility service not available'* ]]; then
  cat <<EOF

\033[1;33m⚠ Portal package is installed but its accessibility service is NOT bound.\033[0m

Open: \033[1mSettings → Accessibility → droidrun Portal → toggle ON → confirm dialog\033[0m

  adb -s $SERIAL shell am start -a android.settings.ACCESSIBILITY_SETTINGS

Then re-run this script.
EOF
  exit 3
else
  warn "Content provider output: $PROBE"
  fail "Portal not responding."
fi

banner "7. Disable element-inspect overlay"
adb -s "$SERIAL" shell "am broadcast -a com.droidrun.portal.TOGGLE_OVERLAY --ez overlay_visible false" >/dev/null && ok "Overlay broadcast sent"
warn "If screenshots still show bounding boxes, manually toggle:"
echo "    adb -s $SERIAL shell monkey -p com.droidrun.portal -c android.intent.category.LAUNCHER 1"
echo "    # scroll to Controls section, tap 'Overlay' switch"
echo "    adb -s $SERIAL shell input keyevent KEYCODE_HOME"
echo "    # then re-launch your target app"

banner "DONE"
cat <<EOF
Portal \033[1m${PORTAL_VERSION}\033[0m is ready on device \033[1m$SERIAL\033[0m.

Next: use \`re-spec-capture\` to grab screens (requires .spec-profile.yml in CWD or parent).
  \$ re-spec-capture <feature> <screen_name> [--from <parent_id>] [--via "<action>"]

EOF
