package engine;
import java.util.*;
import java.nio.file.*;
public final class SelfTest {
 static int checks;
 static void check(boolean b,String message){checks++;if(!b)throw new AssertionError(message);}
 public static void main(String[] a)throws Exception{
  check(!Checker.equal(1000000L,1000001L),"整数不能使用相对浮点容差");
  check(Checker.equal(1.00000001,1.0),"浮点允许误差");
  Object x=Json.parse("{\"a\":[1,null,true,\"中文\\n\\\"\"],\"b\":-2.5e2}");check(Checker.equal(x,Json.parse(Json.stringify(x))),"JSON往返");
  boolean fail=false;try{Json.parse("[1]junk");}catch(Exception e){fail=true;}check(fail,"JSON拒绝尾随内容");
  check(Checker.check(1,List.of(List.of(2,7,11),9),List.of(0,1),List.of(1,0)),"两数之和允许换序");
  check(!Checker.check(1,List.of(List.of(3,3),6),List.of(0,1),List.of(0,0)),"不允许重复下标");
  check(Checker.check(5,List.of("babad"),"bab","aba"),"最长回文不同合法答案");
  check(!Checker.check(5,List.of("babad"),"bab","bad"),"非回文不能通过");
  check(Checker.check(76,List.of("a","bb"),"",""),"无覆盖窗口返回空串");
  check(!Checker.check(76,List.of("aa","aa"),"aa","a"),"窗口检查重复字符数");
  check(Checker.check(210,List.of(3,List.of(List.of(2,0),List.of(2,1))),List.of(0,1,2),List.of(1,0,2)),"任意合法拓扑序");
  check(!Checker.check(210,List.of(3,List.of(List.of(2,0))),List.of(0,1,2),List.of(2,1,0)),"拓扑违反依赖");
  check(!Checker.check(210,List.of(2,List.of()),List.of(0,1),List.of()),"有解不能返回空");
  check(Checker.check(210,List.of(2,List.of(List.of(1,0),List.of(0,1))),List.of(),List.of()),"有环返回空");
  check(Checker.check(49,List.of(List.of("ab","ba","c")),List.of(List.of("ab","ba"),List.of("c")),List.of(List.of("c"),List.of("ba","ab"))),"分组忽略内外顺序");
  check(!Checker.check(49,List.of(List.of("a","a")),List.of(List.of("a","a")),List.of(List.of("a"))),"分组保留重复数量");
  List<Object> sql1=List.of(List.of("a","b"),List.of(Arrays.asList("1",null),List.of("2","x")));
  List<Object> sql2=List.of(List.of("B","A"),List.of(List.of("x","2"),Arrays.asList(null,"1")));
  check(SqlRunner.matches(sql1,sql2,false),"SQL按列名对齐且允许无序行");
  check(!SqlRunner.matches(sql1,sql2,true),"SQL有序结果必须比较顺序");
  check(!SqlRunner.matches(List.of(List.of("a"),List.of(List.of("1"),List.of("1"))),List.of(List.of("a"),List.of(List.of("1"))),false),"SQL不丢重复行");
  Path f=Files.createTempDirectory("algorithm-selftest-").resolve("record.json");Json.write(f,x);check(Checker.equal(x,Json.read(f)),"记录原子写入读取");Files.delete(f);Files.delete(f.getParent());
  System.out.println("ENGINE SELFTEST PASS: "+checks+" checks");
 }
}
