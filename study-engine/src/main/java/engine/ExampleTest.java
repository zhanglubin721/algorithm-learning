package engine;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Quick, editable cases. Never writes the full-suite pass record or timer state. */
public final class ExampleTest {
    private ExampleTest() {}

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            System.out.println("请运行题目入口里的 Test.java，或传入题目相对路径。");
            return;
        }
        runCurrent(args[0]);
    }

    public static Path prepare(Path question, Path attempt) throws Exception {
        Path local = attempt.resolve("本地用例.json");
        if (Files.exists(local)) return local;
        List<Object> all = Json.list(Json.read(question.resolve("测试/cases.json")));
        List<Object> selected = new ArrayList<>();
        for (Object entry : all) {
            Map<String, Object> c = Json.map(entry);
            if ("官方公开输入".equals(c.get("source")) || String.valueOf(c.get("name")).startsWith("公开示例")) {
                selected.add(new LinkedHashMap<>(c));
                if (selected.size() == 3) break;
            }
        }
        if (selected.isEmpty()) {
            for (Object entry : all) {
                if ("规模边界".equals(Json.map(entry).get("name"))) continue;
                selected.add(new LinkedHashMap<>(Json.map(entry)));
                if (selected.size() == 3) break;
            }
        }
        // The file is deliberately pretty-printed: it is part of the user's editing workflow.
        StringBuilder text = new StringBuilder("[\n");
        for (int i = 0; i < selected.size(); i++) {
            Map<String, Object> c = Json.map(selected.get(i));
            text.append("  {\n    \"name\": ").append(Json.stringify("示例 " + (i + 1)))
                .append(",\n    \"args\": ").append(Json.stringify(c.get("args")))
                .append(",\n    \"expected\": ").append(Json.stringify(c.get("expected")))
                .append("\n  }").append(i + 1 == selected.size() ? "\n" : ",\n");
        }
        text.append("]\n");
        Files.writeString(local, text.toString(), java.nio.file.StandardOpenOption.CREATE_NEW);
        return local;
    }

    public static void runCurrent(String relative) throws Exception {
        Path root = Main.root();
        Path question = root.resolve(relative).normalize();
        if (!question.startsWith(root) || !Files.isRegularFile(question.resolve("题目配置.json"))) {
            throw new IllegalArgumentException("题目路径无效");
        }
        Path pointer = question.resolve("作答/current.json");
        if (!Files.exists(pointer)) {
            System.out.println("还没有当前作答。请先运行同目录的 Start.java，选择 1 创建一轮。");
            return;
        }
        Path attempt = question.resolve(Json.map(Json.read(pointer)).get("path").toString()).normalize();
        if (!attempt.startsWith(question.resolve("作答")) || !Files.isRegularFile(attempt.resolve("session.json"))) {
            throw new IllegalArgumentException("当前作答已删除或路径无效，请通过 Start.java 新建一轮。");
        }
        run(root, question, attempt);
    }

    public static Map<String, Object> run(Path root, Path question, Path attempt) throws Exception {
        Path local = prepare(question, attempt);
        System.out.println("示例测试：" + attempt.resolve("Solution.java"));
        System.out.println("可编辑用例：" + local);
        List<Object> cases = Json.list(Json.read(local));
        Map<String, Object> report = Runner.runExamples(root, question, attempt, local);
        System.out.println();
        if (report.containsKey("results")) {
            for (Object entry : Json.list(report.get("results"))) {
                Map<String, Object> result = Json.map(entry);
                int i = ((Number) result.get("index")).intValue();
                Map<String, Object> c = Json.map(cases.get(i));
                System.out.println("【" + c.get("name") + "】" + (Boolean.TRUE.equals(result.get("passed")) ? "通过" : "未通过"));
                System.out.println("  输入：" + Json.stringify(c.get("args")));
                System.out.println("  预期：" + Json.stringify(c.get("expected")));
                System.out.println(result.containsKey("error") ? "  错误：" + result.get("error") : "  实际：" + Json.stringify(result.get("actual")));
            }
        }
        System.out.println("\n示例结果：" + report.get("status") + "，通过 "
            + report.getOrDefault("passedCount", 0) + "/" + report.getOrDefault("total", cases.size()));
        System.out.println("示例通过不等于完整测试通过。完成后回到 Start 控制台选择 3，再选择 5 结束计时。");
        return report;
    }
}
