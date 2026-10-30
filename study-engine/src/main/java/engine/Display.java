package engine;

/** Human-facing formatting; persistent timing stays in milliseconds. */
public final class Display {
    private Display() {}

    public static String elapsed(long millis) {
        long seconds = Math.max(0, millis) / 1000;
        return (seconds / 60) + " 分 " + String.format(java.util.Locale.ROOT, "%02d", seconds % 60) + " 秒";
    }
}
