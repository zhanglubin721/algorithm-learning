package engine;
import java.nio.file.*;
import java.net.*;
import java.util.*;
/** 独立JVM工作进程：结果写文件，用户stdout不影响判题协议。 */
public final class Worker {
 static final class Limited extends java.io.OutputStream {final java.io.OutputStream out;long count;Limited(java.io.OutputStream o){out=o;}public void write(int b)throws java.io.IOException{if(count++<1048576)out.write(b);}public void flush()throws java.io.IOException{out.flush();}}
 public static void main(String[] a)throws Exception{
  System.setOut(new java.io.PrintStream(new Limited(System.out),true,java.nio.charset.StandardCharsets.UTF_8));System.setErr(new java.io.PrintStream(new Limited(System.err),true,java.nio.charset.StandardCharsets.UTF_8));
  Path classes=Path.of(a[0]),config=Path.of(a[1]),cases=Path.of(a[2]),out=Path.of(a[3]);String pkg=a[4];
  Map<String,Object> cfg=Json.map(Json.read(config));int id=Bridge.num(cfg.get("id"));Map<String,Object> meta=Json.map(cfg.get("meta"));List<Object> results=new ArrayList<>();
  try(URLClassLoader l=new URLClassLoader(new URL[]{classes.toUri().toURL()},ClassLoader.getPlatformClassLoader())){
   int index=0;for(Object cc:Json.list(Json.read(cases))){Map<String,Object> c=Json.map(cc);Map<String,Object> res=new LinkedHashMap<>();res.put("index",index++);res.put("name",c.get("name"));long start=System.nanoTime();try{Object value=new Bridge(l,pkg,id).run(meta,Json.list(c.get("args")));res.put("actual",value);res.put("passed",!c.containsKey("expected")?null:Checker.check(id,Json.list(c.get("args")),c.get("expected"),value));}catch(Throwable t){Throwable e=t.getCause()==null?t:t.getCause();res.put("passed",false);res.put("error",e.getClass().getSimpleName()+": "+e.getMessage());}res.put("elapsedNs",System.nanoTime()-start);results.add(res);Json.write(out,results);}
  }
 }
}
