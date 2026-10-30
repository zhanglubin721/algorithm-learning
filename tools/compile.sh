#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -n "${ALGORITHM_JAVA_HOME:-}" ]; then
  JAVAC="$ALGORITHM_JAVA_HOME/bin/javac"
elif [ "$(uname)" = Darwin ]; then
  JAVAC="$(/usr/libexec/java_home -v 21)/bin/javac"
else
  JAVAC=javac
fi
mkdir -p .cache/engine
find study-engine/src/main/java -name '*.java' > .cache/sources.txt
"$JAVAC" -encoding UTF-8 -d .cache/engine @.cache/sources.txt
