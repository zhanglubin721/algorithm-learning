#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ $# -lt 1 ]; then echo '用法：tools/start.sh 题号，例如 tools/start.sh 1'; exit 1; fi
./tools/compile.sh
question_path=$(python3 -c 'import json,sys;print(json.load(open("catalog/canonical.json"))[str(int(sys.argv[1]))])' "$1")
if [ -n "${ALGORITHM_JAVA_HOME:-}" ]; then java_cmd="$ALGORITHM_JAVA_HOME/bin/java"; elif [ "$(uname)" = Darwin ]; then java_cmd="$(/usr/libexec/java_home -v 21)/bin/java"; else java_cmd=java; fi
exec "$java_cmd" -cp .cache/engine engine.Main "$question_path"
