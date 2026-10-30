package engine;

import java.nio.channels.FileChannel;
import java.nio.channels.FileLock;
import java.nio.channels.OverlappingFileLockException;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.TimeUnit;
import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;

public final class Runner {
    public static String hash(Path path) throws Exception {
        return digest(Files.readAllBytes(path));
    }

    private static String digest(byte[] bytes) throws Exception {
        return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    public static Map<String, Object> run(Path root, Path question, Path attempt, boolean debug) throws Exception {
        return lockedRun(root, question, attempt, debug, null);
    }

    public static Map<String, Object> runExamples(Path root, Path question, Path attempt, Path cases) throws Exception {
        List<Object> entries = Json.list(Json.read(cases));
        if (entries.isEmpty()) throw new IllegalArgumentException("本地用例不能为空");
        for (Object entry : entries) {
            Map<String, Object> c = Json.map(entry);
            if (!(c.get("args") instanceof List<?>) || !c.containsKey("expected")) {
                throw new IllegalArgumentException("每个本地用例需要 args 数组和 expected 字段（expected可以为null）");
            }
        }
        return lockedRun(root, question, attempt, false, cases);
    }

    private static Map<String, Object> lockedRun(Path root, Path question, Path attempt,
                                                 boolean debug, Path examples) throws Exception {
        // Start can keep its timer running while Test.java runs in another process.
        // Only the compilation/test operation itself is exclusive.
        try (FileChannel channel = FileChannel.open(attempt.resolve(".test.lock"),
                StandardOpenOption.CREATE, StandardOpenOption.WRITE)) {
            FileLock lock;
            try { lock = channel.tryLock(); }
            catch (OverlappingFileLockException e) { lock = null; }
            if (lock == null) throw new IllegalStateException("当前轮正在测试，请等待这次测试结束");
            try (FileLock held = lock) {
                Map<String, Object> cfg = Json.map(Json.read(question.resolve("题目配置.json")));
                if ("sql".equals(cfg.get("kind"))) {
                    if (examples != null) throw new IllegalArgumentException("SQL请通过Start菜单3运行数据库测试");
                    return SqlRunner.run(root, question, attempt);
                }
                return execute(question, attempt, debug, examples);
            }
        }
    }

    private static Map<String, Object> execute(Path question, Path attempt, boolean debug,
                                               Path examples) throws Exception {
        boolean sample = examples != null;
        String scope = sample ? "EXAMPLES" : "FULL";
        Path source = attempt.resolve("Solution.java");
        String sourceHash = hash(source);
        Path cases = sample ? examples : question.resolve("测试/cases.json");
        byte[] caseBytes = Files.readAllBytes(cases);
        String testHash = digest(caseBytes);
        int total = Json.list(Json.parse(new String(caseBytes, java.nio.charset.StandardCharsets.UTF_8))).size();
        Path classes = attempt.resolve(sample ? ".build-examples" : ".build");
        Files.createDirectories(classes);
        try (var paths = Files.walk(classes)) {
            for (Path file : paths.filter(Files::isRegularFile).toList()) Files.delete(file);
        }
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        if (compiler == null) throw new IllegalStateException("需要完整JDK 21，不是JRE");
        List<String> arguments = new ArrayList<>(List.of("-encoding", "UTF-8", "-g", "-proc:none", "-d", classes.toString()));
        try (var paths = Files.list(attempt)) {
            paths.filter(path -> path.toString().endsWith(".java")).forEach(path -> arguments.add(path.toString()));
        }
        Path report = attempt.resolve(sample ? "示例测试结果.json" : "测试结果.json");
        int code = compiler.run(null, System.out, System.err, arguments.toArray(String[]::new));
        if (code != 0) {
            Map<String, Object> result = Map.of("status", "COMPILE_ERROR", "passed", false,
                    "sourceHash", sourceHash, "testHash", testHash, "testScope", scope, "total", total);
            Json.write(report, result);
            return result;
        }
        Path snapshot = classes.resolve("cases.json");
        Files.write(snapshot, caseBytes);
        Path out = attempt.resolve(sample ? ".worker-examples.json" : ".worker-result.json");
        Files.deleteIfExists(out);
        Map<String, Object> session = Json.map(Json.read(attempt.resolve("session.json")));
        List<String> command = new ArrayList<>(List.of(
                Path.of(System.getProperty("java.home"), "bin", "java").toString(), "-Xmx256m", "-Xss4m"));
        if (debug) {
            command.add("-agentlib:jdwp=transport=dt_socket,server=y,suspend=y,address=127.0.0.1:5005");
            System.out.println("已等待调试器：运行 IDEA 的 Attach-练习 配置，然后继续。端口5005，仅本机。");
        }
        command.addAll(List.of("-cp", System.getProperty("java.class.path"), "engine.Worker",
                classes.toString(), question.resolve("题目配置.json").toString(), snapshot.toString(),
                out.toString(), session.get("package").toString()));
        Path console = attempt.resolve(sample ? "示例运行输出.log" : "运行输出.log");
        Process process = new ProcessBuilder(command).redirectErrorStream(true).redirectOutput(console.toFile()).start();
        boolean finished = process.waitFor(debug ? 600 : 30, TimeUnit.SECONDS);
        if (!finished) { process.destroyForcibly(); process.waitFor(); }
        List<Object> results = Files.exists(out) ? Json.list(Json.read(out)) : List.of();
        int passed = 0;
        for (Object entry : results) if (Boolean.TRUE.equals(Json.map(entry).get("passed"))) passed++;
        boolean unchanged = sourceHash.equals(hash(source)) && testHash.equals(hash(cases));
        boolean ok = finished && process.exitValue() == 0 && total > 0
                && results.size() == total && passed == total && unchanged;
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("status", !finished ? "TIMEOUT" : !unchanged ? "INPUT_CHANGED_RETEST"
                : ok ? (sample ? "EXAMPLE_PASS" : "LOCAL_PASS") : "FAILED");
        result.put("passed", ok);
        result.put("testScope", scope);
        result.put("total", total);
        result.put("passedCount", passed);
        result.put("results", results);
        result.put("sourceHash", sourceHash);
        result.put("testHash", testHash);
        result.put("checkedAt", java.time.Instant.now().toString());
        Json.write(report, result);
        return result;
    }
}
