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
  echo 'org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8' >> "$PROJECT_DIR/gradle.properties" || true
  (cd "$PROJECT_DIR" && ./gradlew --no-daemon --refresh-dependencies clean) || true
}

regenerate_from_templates() {
  echo "[ai-fix] Regenerating project from updated templates..."
  rm -rf "$PROJECT_DIR"_new
  python -m backend.cli \
    -n "${APP_NAME}" \
    -p "${PKG_NAME}" \
    -r "${PROMPT_TEXT}" \
    -o android-project.zip
  rm -rf "$PROJECT_DIR"
  mkdir -p "$PROJECT_DIR"
  unzip -q android-project.zip -d "$PROJECT_DIR"
}

max_attempts=3
attempt=1

# Inputs carried via environment (set by workflow step)
APP_NAME=${APP_NAME:-GeneratedApp}
PKG_NAME=${PKG_NAME:-com.example.generatedapp}
PROMPT_TEXT=${PROMPT_TEXT:-Generated screen}

# Ensure gradlew exists; if not, initialize wrapper
if [ ! -f "$PROJECT_DIR/gradlew" ]; then
  echo "[init] Gradle wrapper not found, initializing..."
  (cd "$PROJECT_DIR" && gradle wrapper --gradle-version 8.7) || true
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
    # Call AI fixer if GEMINI_API_KEY is present
    if [ -n "${GEMINI_API_KEY:-}" ]; then
      echo "[ai-fix] Invoking Gemini fixer..."
      python backend/ai_fixer.py --generated "$PROJECT_DIR" --log "$LOG_DIR/build_attempt_${attempt}.log" || true
      regenerate_from_templates
      # Ensure wrapper exists again
      if [ ! -f "$PROJECT_DIR/gradlew" ]; then
        (cd "$PROJECT_DIR" && gradle wrapper --gradle-version 8.7) || true
        chmod +x "$PROJECT_DIR/gradlew" || true
      fi
    fi
  fi

  attempt=$((attempt+1))
 done

echo "[build] Failed after $max_attempts attempts"
exit 1