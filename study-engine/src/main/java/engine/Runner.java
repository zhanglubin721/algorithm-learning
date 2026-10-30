package engine;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import javax.tools.*;
import java.security.*;
public final class Runner {
 public static String hash(Path p)throws Exception{return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(Files.readAllBytes(p)));}
 public static Map<String,Object> run(Path root,Path question,Path attempt,boolean debug)throws Exception{
  Map<String,Object>cfg=Json.map(Json.read(question.resolve("题目配置.json")));Map<String,Object>session=Json.map(Json.read(attempt.resolve("session.json")));
  if("sql".equals(cfg.get("kind")))return SqlRunner.run(root,question,attempt);
  Path source=attempt.resolve("Solution.java"),classes=attempt.resolve(".build");Files.createDirectories(classes);
  try(var paths=Files.walk(classes)){for(Path f:paths.filter(Files::isRegularFile).toList())Files.delete(f);}
  JavaCompiler compiler=ToolProvider.getSystemJavaCompiler();if(compiler==null)throw new IllegalStateException("需要完整JDK 21，不是JRE");List<String> args=new ArrayList<>(List.of("-encoding","UTF-8","-g","-proc:none","-d",classes.toString()));try(var paths=Files.list(attempt)){paths.filter(x->x.toString().endsWith(".java")).forEach(x->args.add(x.toString()));}
  Path report=attempt.resolve("测试结果.json");int rc=compiler.run(null,System.out,System.err,args.toArray(String[]::new));if(rc!=0){Map<String,Object> r=Map.of("status","COMPILE_ERROR","passed",false,"sourceHash",hash(source));Json.write(report,r);return r;}
  Path cases=question.resolve("测试/cases.json"),out=attempt.resolve(".worker-result.json");Files.deleteIfExists(out);
  List<String>cmd=new ArrayList<>(List.of(Path.of(System.getProperty("java.home"),"bin","java").toString(),"-Xmx256m","-Xss4m"));
  if(debug){cmd.add("-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=127.0.0.1:5005");System.out.println("已等待调试器：运行 IDEA 的 Attach-练习 配置，然后继续。端口5005，仅本机。");}
  cmd.addAll(List.of("-cp",System.getProperty("java.class.path"),"engine.Worker",classes.toString(),question.resolve("题目配置.json").toString(),cases.toString(),out.toString(),session.get("package").toString()));
  Path console=attempt.resolve("运行输出.log");Process proc=new ProcessBuilder(cmd).redirectErrorStream(true).redirectOutput(console.toFile()).start();boolean finished=proc.waitFor(debug?600:30,TimeUnit.SECONDS);if(!finished){proc.destroyForcibly();proc.waitFor();}
  List<Object>results=Files.exists(out)?Json.list(Json.read(out)):List.of();int total=Json.list(Json.read(cases)).size(),passed=0;for(Object x:results)if(Boolean.TRUE.equals(Json.map(x).get("passed")))passed++;
  boolean ok=finished&&proc.exitValue()==0&&total>0&&results.size()==total&&passed==total;
  Map<String,Object>r=new LinkedHashMap<>();r.put("status",!finished?"TIMEOUT":ok?"LOCAL_PASS":"FAILED");r.put("passed",ok);r.put("total",total);r.put("passedCount",passed);r.put("results",results);r.put("sourceHash",hash(source));r.put("testHash",hash(cases));r.put("checkedAt",java.time.Instant.now().toString());Json.write(report,r);return r;
 }
}
