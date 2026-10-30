"""Portable maintenance-tool paths; normal practice does not run import tools."""
import pathlib,os,subprocess,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/source'
java_home=os.environ.get('ALGORITHM_JAVA_HOME')
if not java_home and pathlib.Path('/usr/libexec/java_home').exists():
 java_home=subprocess.check_output(['/usr/libexec/java_home','-v','21'],text=True).strip()
if not java_home:java_home=os.environ.get('JAVA_HOME')
JAVA_BIN=str(pathlib.Path(java_home)/'bin')+os.sep if java_home else ''
