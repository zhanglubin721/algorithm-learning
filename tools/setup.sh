#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
./tools/compile.sh
if [ ! -f config/mysql.local.properties ]; then cp config/mysql.example.properties config/mysql.local.properties; fi
printf '%s\n' 'Java引擎已编译，配置模板已准备。' '请在IDEA选择JDK21，或运行 tools/start.sh 1。' 'MySQL尚未安装时可正常练习算法；SQL待安装MySQL8并填写本机配置后使用。'
