import pathlib,json,html
R=pathlib.Path(__file__).resolve().parents[1];roots=json.loads((R/'catalog/source-roots.json').read_text());index=json.loads((R/'catalog/index.json').read_text())
esc=html.escape
sources='\n'.join('          <source>'+esc(p)+'</source>' for p in roots)
pom=f'''<project xmlns="http://maven.apache.org/POM/4.0.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
 <modelVersion>4.0.0</modelVersion><groupId>local.study</groupId><artifactId>algorithm-learning</artifactId><version>1.0.0</version>
 <properties><maven.compiler.release>21</maven.compiler.release><project.build.sourceEncoding>UTF-8</project.build.sourceEncoding></properties>
 <dependencies><dependency><groupId>com.mysql</groupId><artifactId>mysql-connector-j</artifactId><version>8.4.0</version><scope>runtime</scope></dependency></dependencies>
 <build><sourceDirectory>study-engine/src/main/java</sourceDirectory><plugins>
  <plugin><groupId>org.codehaus.mojo</groupId><artifactId>build-helper-maven-plugin</artifactId><version>3.6.1</version><executions><execution><id>study-sources</id><phase>generate-sources</phase><goals><goal>add-source</goal></goals><configuration><sources>
{sources}
  </sources></configuration></execution></executions></plugin>
  <plugin><groupId>org.apache.maven.plugins</groupId><artifactId>maven-compiler-plugin</artifactId><version>3.14.1</version><configuration><includes><include>engine/**/*.java</include><include>**/Start.java</include></includes><compilerArgs><arg>-proc:none</arg></compilerArgs></configuration></plugin>
 </plugins></build>
</project>''';(R/'pom.xml').write_text(pom)
sourcefolders='\n'.join('    <sourceFolder url="file://$MODULE_DIR$/'+esc(p)+'" isTestSource="false" />' for p in ['study-engine/src/main/java']+roots)
(R/'algorithm-learning.iml').write_text(f'''<?xml version="1.0" encoding="UTF-8"?>
<module type="JAVA_MODULE" version="4"><component name="NewModuleRootManager" inherit-compiler-output="false"><output url="file://$MODULE_DIR$/.cache/idea-classes"/><exclude-output/><content url="file://$MODULE_DIR$">
{sourcefolders}
<excludeFolder url="file://$MODULE_DIR$/.cache"/><excludeFolder url="file://$MODULE_DIR$/target"/>
</content><orderEntry type="inheritedJdk"/><orderEntry type="sourceFolder" forTests="false"/></component></module>''')
(R/'.idea/modules.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><project version="4"><component name="ProjectModuleManager"><modules><module fileurl="file://$PROJECT_DIR$/algorithm-learning.iml" filepath="$PROJECT_DIR$/algorithm-learning.iml"/></modules></component></project>')
(R/'.idea/misc.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><project version="4"><component name="ProjectRootManager" version="2" languageLevel="JDK_21" project-jdk-name="21" project-jdk-type="JavaSDK"><output url="file://$PROJECT_DIR$/.cache/idea-classes"/></component></project>')
excludes=''.join('<directory url="file://$PROJECT_DIR$/'+esc(x['path'])+'/作答" includeSubdirectories="true"/>' for x in index)
(R/'.idea/compiler.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><project version="4"><component name="CompilerConfiguration"><excludeFromCompile>'+excludes+'</excludeFromCompile><bytecodeTargetLevel target="21"/></component></project>')
(R/'.run/Attach-练习.run.xml').write_text('''<component name="ProjectRunConfigurationManager"><configuration default="false" name="Attach-练习" type="Remote" factoryName="Remote JVM Debug"><option name="USE_SOCKET_TRANSPORT" value="true"/><option name="SERVER_MODE" value="false"/><option name="HOST" value="127.0.0.1"/><option name="PORT" value="5005"/><method v="2"/></configuration></component>''')
(R/'.mvn/maven.config').write_text('-Dmaven.repo.local=.cache/m2\n')
(R/'tools/maven-settings.xml').write_text('<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"><mirrors><mirror><id>study-central</id><mirrorOf>*</mirrorOf><url>https://repo.maven.apache.org/maven2</url></mirror></mirrors></settings>')
# Synchronize validated cases to repeated study-plan entries without touching attempts.
canonical=json.loads((R/'catalog/canonical.json').read_text())
import shutil
for x in index:
 src=R/canonical[str(x['id'])]/'测试';dst=R/x['path']/'测试'
 if src!=dst:shutil.copytree(src,dst,dirs_exist_ok=True)
print('IDEA/Maven source roots',len(roots),'questions',len(index))
