package engine;
import java.nio.file.*;
import java.nio.channels.*;
import java.time.*;
import java.time.format.*;
import java.util.*;
public final class Main {
 static final ZoneId STUDY_ZONE=ZoneId.of(System.getProperty("study.timezone","Asia/Shanghai"));
 static Path root(){Path p=Path.of(System.getProperty("user.dir")).toAbsolutePath();while(p!=null){if(Files.isRegularFile(p.resolve("catalog/plans.json")))return p;p=p.getParent();}throw new IllegalStateException("请将工作目录设置为algorithm-learning或其子目录");}
 public static void main(String[]a)throws Exception{if(a.length==0){System.out.println("请从题目Start.java启动，或传入题目相对路径。");return;}launch(a[0]);}
 public static void launch(String relative)throws Exception{
  Path r=root(),q=r.resolve(relative).normalize();if(!q.startsWith(r)||!Files.isRegularFile(q.resolve("题目配置.json")))throw new IllegalArgumentException("题目路径无效");
  Map<String,Object>cfg=Json.map(Json.read(q.resolve("题目配置.json")));Files.createDirectories(q.resolve("作答"));
  try(FileChannel ch=FileChannel.open(q.resolve("作答/.lock"),StandardOpenOption.CREATE,StandardOpenOption.WRITE);FileLock lock=ch.tryLock()){
   if(lock==null){System.out.println("这道题已在另一个窗口运行，请先退出。");return;}
   Scanner in=new Scanner(System.in);Path active=null;long resumed=0;Map<String,Object>s=null;
   System.out.println("\nLC"+cfg.get("id")+" "+cfg.get("titleCn")+" · "+cfg.get("difficulty"));
   while(true){
    System.out.println("\n1开始新一轮  2继续  3测试  4暂停/恢复  5结束  6历史  7导出AI复核  8调试  0退出");
    if(!in.hasNextLine())break;String op=in.nextLine().trim();
    try{
     if(op.equals("0"))break;
     if(op.equals("1")){
      if(s!=null){if(resumed>0){accrue(s,resumed);resumed=0;}s.put("status","PAUSED");Json.write(active.resolve("session.json"),s);}
      String stamp="a"+LocalDateTime.now(STUDY_ZONE).format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"))+"_"+UUID.randomUUID().toString().substring(0,6);String pkg="practice."+cfg.get("namespace")+".attempts."+stamp;
      active=q.resolve("作答/src/main/java").resolve(pkg.replace('.','/'));Files.createDirectories(active);boolean sql="sql".equals(cfg.get("kind"));String file=sql?"answer.sql":"Solution.java";String template=Files.readString(q.resolve("模板/"+file+".template"));String header=(sql?"-- ":"// ")+"LC"+cfg.get("id")+" "+cfg.get("titleCn")+" | 创建时间 "+OffsetDateTime.now(STUDY_ZONE)+"\n";
      Files.writeString(active.resolve(file),header+(sql?"":"package "+pkg+";\n")+template);
      Path support=q.resolve("模板/Support.java.template");if(!sql&&Files.exists(support))Files.writeString(active.resolve("Support.java"),"package "+pkg+";\n"+Files.readString(support));
      s=new LinkedHashMap<>();s.put("attemptId",stamp);s.put("questionId",cfg.get("id"));s.put("package",pkg);s.put("createdAt",Instant.now().toString());s.put("status","ACTIVE");s.put("activeMillis",0);s.put("templateHash",Runner.hash(q.resolve("模板/"+file+".template")));s.put("questionHash",Runner.hash(q.resolve("题目配置.json")));Json.write(active.resolve("session.json"),s);Json.write(q.resolve("作答/current.json"),Map.of("path",q.relativize(active).toString()));Files.writeString(active.resolve("本轮复盘.md"),"# 本轮复盘\n\n- 解题思路：\n- 时间/空间复杂度：\n- 卡点与修正：\n- 是否用了提示：\n- 复做重点：\n");resumed=System.nanoTime();System.out.println("已创建并开始计时：\n"+active.resolve(file));
     }else if(op.equals("2")){
      if(s!=null&&resumed>0){System.out.println("本轮正在计时");continue;}Path pointer=q.resolve("作答/current.json");if(!Files.exists(pointer)){System.out.println("没有当前练习，请选1。");continue;}Path next=q.resolve(Json.map(Json.read(pointer)).get("path").toString()).normalize();if(!next.startsWith(q.resolve("作答"))||!Files.exists(next.resolve("session.json"))){System.out.println("上轮目录已删除，请选1重做。");continue;}
      active=next;s=Json.map(Json.read(active.resolve("session.json")));if("FINISHED".equals(s.get("status"))){System.out.println("该轮已结束，请选1复做。");s=null;continue;}if("ACTIVE".equals(s.get("status"))){System.out.println("上次可能异常退出；请补录未记录的有效分钟（输入0表示不追加）：");long minutes=Long.parseLong(in.nextLine().trim());if(minutes<0||minutes>1440)throw new IllegalArgumentException("分钟范围0—1440");s.put("activeMillis",((Number)s.get("activeMillis")).longValue()+minutes*60000);s.put("interruptionAdjustedAt",Instant.now().toString());}s.put("status","ACTIVE");Json.write(active.resolve("session.json"),s);resumed=System.nanoTime();System.out.println("继续："+active);
     }else if(op.equals("6")){
      try(var walk=Files.walk(q.resolve("作答"))){for(Path f:walk.filter(x->x.getFileName().toString().equals("session.json")).sorted().toList())System.out.println(Files.readString(f));}
     }else if(s==null){System.out.println("请先开始或继续一轮。");}
     else if(op.equals("4")){
      if(resumed>0){accrue(s,resumed);resumed=0;s.put("status","PAUSED");}else{resumed=System.nanoTime();s.put("status","ACTIVE");}Json.write(active.resolve("session.json"),s);System.out.println(s.get("status"));
     }else if(op.equals("3")||op.equals("8")){
      Map<String,Object> result=Runner.run(r,q,active,op.equals("8"));System.out.println(result.get("status")+" "+result.getOrDefault("passedCount",0)+"/"+result.getOrDefault("total",0));if(Boolean.TRUE.equals(result.get("passed"))&&!s.containsKey("firstLocalPassAt")){s.put("firstLocalPassAt",Instant.now().toString());s.put("firstLocalPassMillis",((Number)s.get("activeMillis")).longValue()+(resumed>0?(System.nanoTime()-resumed)/1000000:0));}Json.write(active.resolve("session.json"),s);System.out.println("详情："+active.resolve("测试结果.json"));
     }else if(op.equals("5")){
      if(resumed>0){accrue(s,resumed);resumed=0;}System.out.println("完成方式：1独立 2看提示 3看题解 4未完成");String mode=in.nextLine().trim();if(!Set.of("1","2","3","4").contains(mode)){s.put("status","PAUSED");Json.write(active.resolve("session.json"),s);throw new IllegalArgumentException("请选择1—4，本轮已暂停");}boolean passed=false;Path rp=active.resolve("测试结果.json");if(Files.exists(rp)){Map<String,Object>report=Json.map(Json.read(rp));Path src=active.resolve("sql".equals(cfg.get("kind"))?"answer.sql":"Solution.java");passed=Boolean.TRUE.equals(report.get("passed"))&&Runner.hash(src).equals(report.get("sourceHash"))&&Runner.hash(q.resolve("sql".equals(cfg.get("kind"))?"测试/sql-cases.json":"测试/cases.json")).equals(report.get("testHash"));}s.put("status","FINISHED");s.put("finishedAt",Instant.now().toString());s.put("mode",mode);s.put("localPassed",passed);s.put("wallMillis",Duration.between(Instant.parse(s.get("createdAt").toString()),Instant.now()).toMillis());Json.write(active.resolve("session.json"),s);System.out.println("有效用时："+(((Number)s.get("activeMillis")).longValue()/60000.0)+"分钟；本地通过="+passed);export(q,active,s);s=null;active=null;
     }else if(op.equals("7")){export(q,active,s);}
    }catch(Exception e){System.out.println("操作未完成："+e.getMessage());}
   }
   if(s!=null){if(resumed>0)accrue(s,resumed);s.put("status","PAUSED");Json.write(active.resolve("session.json"),s);}Progress.write(r);System.out.println("已保存。暂停期间不计有效用时。进度见progress/学习进度.md。");
  }
 }
 static void accrue(Map<String,Object>s,long start){s.put("activeMillis",((Number)s.get("activeMillis")).longValue()+(System.nanoTime()-start)/1000000);}
 static void export(Path q,Path a,Map<String,Object>s)throws Exception{Path code=a.resolve(Files.exists(a.resolve("answer.sql"))?"answer.sql":"Solution.java");String text="# 独立AI复核材料\n\n题号：LC"+s.get("questionId")+"\n\n请独立检查正确性、复杂度和遗漏边界，尝试构造反例。不要因为本地测试通过就假定正确。\n\n"+Files.readString(q.resolve("题目.md"))+"\n\n## 我的代码\n\n```"+(code.toString().endsWith(".sql")?"sql":"java")+"\n"+Files.readString(code)+"\n```\n\n## 本地测试\n"+(Files.exists(a.resolve("测试结果.json"))?Files.readString(a.resolve("测试结果.json")):"未运行");Files.writeString(a.resolve("AI复核材料.md"),text);System.out.println("复核材料："+a.resolve("AI复核材料.md"));}
}
