package engine;
import java.nio.file.*;
import java.sql.*;
import java.util.*;
import java.net.*;
import java.io.*;
public final class SqlRunner {
 static Connection connect(Path root)throws Exception{
  Path f=root.resolve("config/mysql.local.properties");if(!Files.exists(f))throw new IllegalStateException("请先复制config/mysql.example.properties为mysql.local.properties并填写本机MySQL8配置。");Properties p=new Properties();try(var in=Files.newInputStream(f)){p.load(in);}String host=p.getProperty("host","127.0.0.1");if(!Set.of("127.0.0.1","localhost","::1").contains(host)&&!Boolean.parseBoolean(p.getProperty("allowRemote","false")))throw new IllegalArgumentException("默认只连接本机练习实例");String db=p.getProperty("database","algorithm_practice");if(!db.matches("algorithm_practice[a-zA-Z0-9_]*"))throw new IllegalArgumentException("练习库名必须以algorithm_practice开头");String url="jdbc:mysql://"+host+":"+p.getProperty("port","3306")+"/"+db+"?useUnicode=true&characterEncoding=UTF-8&serverTimezone=Asia/Shanghai&allowMultiQueries=false&connectTimeout=5000&socketTimeout=15000";String password=System.getenv().getOrDefault("MYSQL_PASSWORD",p.getProperty("password",""));
  java.sql.Driver driver;
  try{driver=(java.sql.Driver)Class.forName("com.mysql.cj.jdbc.Driver").getDeclaredConstructor().newInstance();}catch(ClassNotFoundException e){Path jar=root.resolve(".cache/lib/mysql-connector-j-8.4.0.jar");if(!Files.exists(jar))throw new IllegalStateException("缺少MySQL JDBC驱动，请运行tools/setup.sh或在IDEA导入Maven依赖");URLClassLoader cl=new URLClassLoader(new URL[]{jar.toUri().toURL()},SqlRunner.class.getClassLoader());driver=(java.sql.Driver)cl.loadClass("com.mysql.cj.jdbc.Driver").getDeclaredConstructor().newInstance();}
  Properties auth=new Properties();auth.setProperty("user",p.getProperty("username"));auth.setProperty("password",password);Connection c=driver.connect(url,auth);if(c.getMetaData().getDatabaseMajorVersion()!=8){c.close();throw new IllegalArgumentException("本工程校验要求MySQL8，当前主版本不匹配");}return c;
 }
 static List<Object> query(Connection c,String sql)throws Exception{try(Statement st=c.createStatement()){st.setQueryTimeout(5);try(ResultSet rs=st.executeQuery(sql)){List<Object> rows=new ArrayList<>();int n=rs.getMetaData().getColumnCount();List<String>cols=new ArrayList<>();for(int i=1;i<=n;i++)cols.add(rs.getMetaData().getColumnLabel(i));while(rs.next()){List<Object> row=new ArrayList<>();for(int i=1;i<=n;i++){Object v=rs.getObject(i);if(v instanceof Number num)v=new java.math.BigDecimal(num.toString()).stripTrailingZeros().toPlainString();else if(v!=null)v=v.toString();row.add(v);}rows.add(row);}return List.of(cols,rows);}}}
 static void exec(Connection c,String s)throws Exception{try(Statement st=c.createStatement()){st.setQueryTimeout(5);st.execute(s);}}
 static String cleanSql(String text){String s=text.replaceAll("(?m)^\\s*(--|#).*?$","").trim();if(s.endsWith(";"))s=s.substring(0,s.length()-1).trim();return s;}
 static List<Object> evaluate(Connection c,Map<String,Object>cfg,Map<String,Object>data,String sql,boolean delete)throws Exception{
  String base=c.getCatalog();if(base==null||base.length()>35)throw new IllegalArgumentException("练习库名应短于36字符");String db=base+"_case_"+UUID.randomUUID().toString().replace("-","").substring(0,16);boolean created=false;
  try{exec(c,"CREATE DATABASE `"+db+"` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci");created=true;c.setCatalog(db);
   for(Object ddl:Json.list(cfg.get("ddl")))exec(c,ddl.toString());
   Map<String,Object>headers=Json.map(data.get("headers")),rows=Json.map(data.get("rows"));for(String table:headers.keySet()){
    if(!table.matches("[a-zA-Z_][a-zA-Z0-9_]*"))throw new IllegalArgumentException("表名非法");List<Object>cs=Json.list(headers.get(table));for(Object col:cs)if(!col.toString().matches("[a-zA-Z_][a-zA-Z0-9_]*"))throw new IllegalArgumentException("列名非法");
    String names=String.join(",",cs.stream().map(x->"`"+x+"`").toList());try(PreparedStatement ps=c.prepareStatement("INSERT INTO `"+table+"` ("+names+") VALUES ("+String.join(",",Collections.nCopies(cs.size(),"?"))+")")){
     for(Object row:Json.list(rows.get(table))){List<Object>rr=Json.list(row);for(int i=0;i<rr.size();i++)ps.setObject(i+1,rr.get(i));ps.addBatch();}ps.executeBatch();}
   }
   if(delete){exec(c,sql);return query(c,"SELECT id,email FROM Person");}return query(c,sql);
  }finally{if(created){c.setCatalog(base);exec(c,"DROP DATABASE `"+db+"`");}}
 }
 static boolean matches(List<Object>a,List<Object>b,boolean ordered){List<String>ac=Json.list(a.get(0)).stream().map(x->x.toString().toLowerCase(Locale.ROOT)).toList(),bc=Json.list(b.get(0)).stream().map(x->x.toString().toLowerCase(Locale.ROOT)).toList();if(ac.size()!=bc.size()||new HashSet<>(ac).size()!=ac.size()||!new HashSet<>(ac).equals(new HashSet<>(bc)))return false;List<Object>ar=new ArrayList<>(),br=new ArrayList<>(Json.list(b.get(1)));for(Object row:Json.list(a.get(1))){List<Object>old=Json.list(row),aligned=new ArrayList<>();for(String col:bc)aligned.add(old.get(ac.indexOf(col)));ar.add(aligned);}if(!ordered){ar.sort(Comparator.comparing(Json::stringify));br.sort(Comparator.comparing(Json::stringify));}return Checker.equal(ar,br);}
 public static Map<String,Object>run(Path root,Path q,Path attempt)throws Exception{
  Path answer=attempt.resolve("answer.sql");String sql=cleanSql(Files.readString(answer));
  if(sql.contains(";")||sql.matches("(?is).*\\b(create|drop|alter|truncate|use|grant|revoke|load|outfile|infile|call)\\b.*"))throw new IllegalArgumentException("只接受单条查询或本题要求的DELETE，禁止修改库结构/跨语句执行");
  Map<String,Object>cfg=Json.map(Json.read(q.resolve("题目配置.json")));boolean delete=Bridge.num(cfg.get("id"))==196;if(!(sql.matches("(?is)^(select|with)\\b.*")||delete&&sql.matches("(?is)^delete\\b.*")))throw new IllegalArgumentException("请填写SELECT/WITH查询，本题仅196允许DELETE");
  String reference=cleanSql(Files.readString(q.resolve("题解/参考答案.sql")));List<Object>cases=Json.list(Json.read(q.resolve("测试/sql-cases.json"))),results=new ArrayList<>();int passed=0;boolean ordered=Boolean.TRUE.equals(cfg.get("ordered"));
  // 先连接一次，配置缺失时只报告一次；不会把未执行当通过。
  try(Connection check=connect(root)){System.out.println("MySQL "+check.getMetaData().getDatabaseProductVersion()+"；每个用例在独立新建的练习子库执行并清理。");}
  for(Object obj:cases){Map<String,Object>tc=Json.map(obj),result=new LinkedHashMap<>();result.put("name",tc.get("name"));result.put("oracle",tc.get("oracle"));try(Connection c=connect(root)){
    Map<String,Object> data=Json.map(tc.get("data"));List<Object>expected=evaluate(c,cfg,data,reference,delete);
    if(tc.containsKey("expected")&&!matches(expected,Json.list(tc.get("expected")),ordered)){result.put("passed",false);result.put("status","ORACLE_DISAGREEMENT");result.put("referenceResult",expected);result.put("fixedExpected",tc.get("expected"));results.add(result);continue;}
    List<Object>actual=evaluate(c,cfg,data,sql,delete);boolean ok=matches(actual,expected,ordered);result.put("passed",ok);result.put("expected",expected);result.put("actual",actual);if(ok)passed++;
   }catch(Exception e){result.put("passed",false);result.put("error",e.getClass().getSimpleName()+": "+e.getMessage());}results.add(result);
  }
  Map<String,Object>report=new LinkedHashMap<>();boolean ok=!cases.isEmpty()&&passed==cases.size();report.put("passed",ok);report.put("status",ok?"LOCAL_PASS":"FAILED_OR_ORACLE_DISAGREEMENT");report.put("total",cases.size());report.put("passedCount",passed);report.put("results",results);report.put("sourceHash",Runner.hash(answer));report.put("testHash",Runner.hash(q.resolve("测试/sql-cases.json")));report.put("checkedAt",java.time.Instant.now().toString());Json.write(attempt.resolve("测试结果.json"),report);return report;
 }
}
