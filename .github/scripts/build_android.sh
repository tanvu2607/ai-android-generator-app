#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR=${1:-generated}
LOG_DIR="build-logs"
mkdir -p "$LOG_DIR"

run_gradle() {
  (cd "$PROJECT_DIR" && ./gradlew --version >/dev/null 2>&1 || true)
  (cd "$PROJECT_DIR" && ./gradlew --no-daemon --stacktrace --warning-mode all assembleDebug) | tee "$LOG_DIR/build_attempt_${1}.log"
}

apply_fixes() {
  echo "[fix] Applying common fixes..."
  # Increase Gradle JVM heap
  echo 'org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8' >> "$PROJECT_DIR/gradle.properties" || true
  # Refresh dependencies and clean
  (cd "$PROJECT_DIR" && ./gradlew --no-daemon --refresh-dependencies clean) || true
}

max_attempts=3
attempt=1

# Ensure gradlew exists; if not, initialize wrapper
if [ ! -f "$PROJECT_DIR/gradlew" ]; then
  echo "[init] Gradle wrapper not found, initializing..."
  (cd "$PROJECT_DIR" && gradle wrapper) || true
  chmod +x "$PROJECT_DIR/gradlew" || true
fi

while [ $attempt -le $max_attempts ]; do
  echo "[build] Attempt $attempt/$max_attempts"
  if run_gradle "$attempt"; then
    echo "[build] Success on attempt $attempt"
    exit 0
  fi
  if [ $attempt -lt $max_attempts ]; then
    apply_fixes
  fi
  attempt=$((attempt+1))
 done

echo "[build] Failed after $max_attempts attempts"
exit 1