package com.clashtracker.simulated;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Context;
import android.content.ContextWrapper;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.json.JSONArray;
import org.json.JSONObject;

/** Runs real platform SQLite/file checks without adding a test-framework dependency. */
public final class AssistedSessionStoreInstrumentation extends Instrumentation {
    private static final String FIRST_ID = "11111111-1111-4111-8111-111111111111";
    private static final String SECOND_ID = "22222222-2222-4222-8222-222222222222";
    private static final String CREATED = "2026-10-11T01:00:00.000Z";
    private static final String UPDATED = "2026-10-11T01:01:00.000Z";
    private static final String PACKET = "{\"images\":[\"data:image/jpeg;base64,/9j/2Q==\"],\"label\":\"卡牌\"}";
    private Context context;

    @Override public void onCreate(Bundle arguments) {
        super.onCreate(arguments);
        start();
    }

    @Override public void onStart() {
        // Instrumentation runs with the target UID. Isolate every fixture below a synthetic child.
        context = new ContextWrapper(getTargetContext()) {
            @Override public File getNoBackupFilesDir() {
                try {
                    File base = super.getNoBackupFilesDir().getCanonicalFile();
                    File synthetic = new File(base, "assisted-session-store-instrumentation");
                    if (!synthetic.getCanonicalFile().equals(synthetic)) throw new IllegalStateException("Synthetic test root escaped its private base");
                    if (!synthetic.isDirectory() && !synthetic.mkdir()) throw new IllegalStateException("Synthetic test root unavailable");
                    if (!synthetic.getCanonicalFile().equals(synthetic)) throw new IllegalStateException("Synthetic test root changed");
                    return synthetic;
                } catch (java.io.IOException error) { throw new IllegalStateException("Synthetic test root unavailable"); }
            }
        };
        List<String> failures = new ArrayList<>();
        int passed = 0;
        for (Method test : getClass().getDeclaredMethods()) {
            if (!test.getName().startsWith("test")) continue;
            try {
                // Only the synthetic test directory is cleared; actual session data is untouched.
                clearSyntheticRoot();
                test.invoke(this);
                passed++;
                status(test.getName(), "PASS");
            } catch (Throwable error) {
                Throwable cause = error instanceof InvocationTargetException ? error.getCause() : error;
                failures.add(test.getName() + ": " + cause.getClass().getSimpleName() + " " + cause.getMessage());
                status(test.getName(), "FAIL " + cause.getClass().getSimpleName() + " " + cause.getMessage());
            }
        }
        Bundle result = new Bundle();
        result.putInt("passed", passed);
        result.putInt("failed", failures.size());
        result.putString("stream", "\nNative store checks: " + passed + " passed, " + failures.size() + " failed\n" + String.join("\n", failures) + "\n");
        finish(failures.isEmpty() ? Activity.RESULT_OK : Activity.RESULT_CANCELED, result);
    }

    public void testFreshStoreIsEmpty() throws Exception {
        equal(null, invoke(store(), "load", new Class<?>[0]));
    }

    public void testReopenRestoresExactPacketAndReviewedRows() throws Exception {
        JSONObject session = session(FIRST_ID, PACKET);
        invokeReplace(store(), session, null, null);
        JSONObject restored = (JSONObject) invoke(store(), "load", new Class<?>[0]);
        equal(FIRST_ID, restored.getString("sessionId"));
        equal(PACKET, restored.getString("packetJson"));
        equal(sha(PACKET.getBytes(StandardCharsets.UTF_8)), restored.getString("packetSha256"));
        equal(1L, restored.getLong("revision"));
        equal("candidate:1", restored.getJSONArray("reviews").getJSONObject(0).getString("candidateId"));
        check(root().getCanonicalPath().startsWith(context.getNoBackupFilesDir().getCanonicalPath() + File.separator), "storage must remain in no-backup private directory");
    }

    public void testReviewSavePersistsRevisionWithoutChangingRawPacket() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        JSONArray reviews = new JSONArray().put(review("candidate:1", "confirmed", "user_choice", false))
            .put(review("manual:2", "confirmed", "manual", true));
        invokeSave(store(), FIRST_ID, 1L, 2L, reviews);
        JSONObject restored = (JSONObject) invoke(store(), "load", new Class<?>[0]);
        equal(2L, restored.getLong("revision"));
        equal(UPDATED, restored.getString("updatedAt"));
        equal(PACKET, restored.getString("packetJson"));
        equal(2, restored.getJSONArray("reviews").length());
        equal("manual", restored.getJSONArray("reviews").getJSONObject(1).getString("decisionSource"));
        check(restored.getJSONArray("reviews").getJSONObject(1).getBoolean("isManual"), "manual provenance must survive reopening");
        equal(1, packetFiles().length);
    }

    public void testStaleSaveCannotOverwriteLatestReview() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(review("candidate:1", "confirmed", "user_choice", false)));
        expectCode("SESSION_CONFLICT", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray()));
        JSONObject restored = (JSONObject) invoke(store(), "load", new Class<?>[0]);
        equal(2L, restored.getLong("revision"));
        equal("confirmed", restored.getJSONArray("reviews").getJSONObject(0).getString("status"));
    }

    public void testStaleReplacementPreservesCurrentSession() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        expectCode("SESSION_CONFLICT", () -> invokeReplace(store(), session(SECOND_ID, "{}"), null, null));
        equal(FIRST_ID, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getString("sessionId"));
        equal(1, packetFiles().length);
    }

    public void testReplacementKeepsOldImmutablePacket() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        File first = packetFiles()[0];
        byte[] before = read(first);
        invokeReplace(store(), session(SECOND_ID, "{\"new\":true}"), FIRST_ID, 1L);
        equal(SECOND_ID, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getString("sessionId"));
        check(Arrays.equals(before, read(first)), "replacement cannot overwrite or remove the previous packet");
        equal(2, packetFiles().length);
    }

    public void testReplacementCannotReuseCurrentSessionIdentity() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        expectCode("INVALID_SESSION", () -> invokeReplace(store(), session(FIRST_ID, "{\"other\":true}"), FIRST_ID, 1L));
        equal(PACKET, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getString("packetJson"));
        equal(1, packetFiles().length);
    }

    public void testSqlFailureRollsBackReviewsAndMetadata() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) {
            database.execSQL("CREATE TRIGGER reject_review BEFORE INSERT ON reviews WHEN NEW.candidate_id = 'reject-row' BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END");
        }
        JSONArray rows = new JSONArray().put(review("candidate:1", "confirmed", "user_choice", false))
            .put(review("reject-row", "pending", null, false));
        expectCode("STORAGE_IO", () -> invokeSave(store(), FIRST_ID, 1L, 2L, rows));
        JSONObject restored = (JSONObject) invoke(store(), "load", new Class<?>[0]);
        equal(1L, restored.getLong("revision"));
        equal(CREATED, restored.getString("updatedAt"));
        equal(1, restored.getJSONArray("reviews").length());
        equal("pending", restored.getJSONArray("reviews").getJSONObject(0).getString("status"));
    }

    public void testFailedReplaceRetainsOldSessionAndPublishedPacket() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        byte[] original = read(packetFiles()[0]);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) {
            database.execSQL("CREATE TRIGGER reject_session BEFORE INSERT ON sessions WHEN NEW.session_id = '" + SECOND_ID + "' BEGIN SELECT RAISE(ABORT, 'synthetic failure'); END");
        }
        expectCode("STORAGE_IO", () -> invokeReplace(store(), session(SECOND_ID, "{\"new\":true}"), FIRST_ID, 1L));
        equal(FIRST_ID, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getString("sessionId"));
        equal(2, packetFiles().length);
        boolean originalRetained = false;
        for (File file : packetFiles()) if (Arrays.equals(original, read(file))) originalRetained = true;
        check(originalRetained, "failed replacement must retain original bytes");
    }

    public void testMissingPacketReportsErrorInsteadOfEmptySession() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        check(packetFiles()[0].delete(), "synthetic packet removal failed");
        expectCode("PACKET_MISSING", () -> invoke(store(), "load", new Class<?>[0]));
        expectCode("PACKET_MISSING", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray()));
        check(databaseFile().exists(), "database must survive missing packet");
    }

    public void testPacketTamperingReportsIntegrityFailure() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        File packet = packetFiles()[0];
        write(packet, "{\"tampered\":true}".getBytes(StandardCharsets.UTF_8));
        expectCode("PACKET_INTEGRITY", () -> invoke(store(), "load", new Class<?>[0]));
        expectCode("PACKET_INTEGRITY", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray()));
        equal("{\"tampered\":true}", new String(read(packet), StandardCharsets.UTF_8));
    }

    public void testUnknownSchemaVersionPreservesDatabase() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) { database.setVersion(2); }
        expectCode("STORAGE_VERSION", () -> invoke(store(), "load", new Class<?>[0]));
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) { equal(2, database.getVersion()); }
        equal(1, packetFiles().length);
    }

    public void testCorruptDatabaseIsNeverDeletedOrRecreated() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        byte[] corrupt = "this is intentionally not SQLite; preserve it".getBytes(StandardCharsets.UTF_8);
        write(databaseFile(), corrupt);
        expectCode("STORAGE_CORRUPT", () -> invoke(store(), "load", new Class<?>[0]));
        check(Arrays.equals(corrupt, read(databaseFile())), "default SQLite corruption deletion must never run");
        expectCode("STORAGE_CORRUPT", () -> invokeReplace(store(), session(SECOND_ID, "{}"), FIRST_ID, 1L));
        check(Arrays.equals(corrupt, read(databaseFile())), "retry must preserve corrupted bytes");
    }

    public void testPlatformDetectedPageCorruptionNeverDeletesDatabase() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        byte[] corrupt = read(databaseFile());
        check(corrupt.length > 101, "synthetic SQLite database must have a first page");
        corrupt[100] = (byte) 0xff; // Preserve the SQLite header while corrupting the first B-tree page.
        write(databaseFile(), corrupt);
        expectCode("STORAGE_CORRUPT", () -> invoke(store(), "load", new Class<?>[0]));
        check(Arrays.equals(corrupt, read(databaseFile())), "platform corruption recovery must not delete the database");
        equal(1, packetFiles().length);
    }

    public void testInvalidHashAndRevisionLeaveExistingSessionUntouched() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        JSONObject bad = session(SECOND_ID, "{}");
        bad.put("packetSha256", "0000000000000000000000000000000000000000000000000000000000000000");
        expectCode("PACKET_INTEGRITY", () -> invokeReplace(store(), bad, FIRST_ID, 1L));
        expectCode("INVALID_SESSION", () -> invokeSave(store(), FIRST_ID, 1L, 4L, new JSONArray()));
        equal(FIRST_ID, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getString("sessionId"));
        equal(1, packetFiles().length);
    }

    public void testInvalidReviewProvenanceIsRejected() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        JSONArray duplicate = new JSONArray().put(review("candidate:1", "pending", null, false)).put(review("candidate:1", "pending", null, false));
        expectCode("INVALID_SESSION", () -> invokeSave(store(), FIRST_ID, 1L, 2L, duplicate));
        expectCode("INVALID_SESSION", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(review("manual:2", "pending", null, true))));
        JSONObject own = review("candidate:1", "confirmed", "user_choice", false).put("owner", "own");
        expectCode("INVALID_SESSION", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(own)));
        equal(1L, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getLong("revision"));
    }

    public void testReviewBoundsPreventOversizedAndInvalidRows() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        JSONArray oversized = new JSONArray();
        for (int i = 0; i < 5001; i++) oversized.put(review("candidate:" + i, "pending", null, false));
        expectCode("INVALID_SESSION", () -> invokeSave(store(), FIRST_ID, 1L, 2L, oversized));
        JSONObject longId = review(new String(new char[129]).replace('\0', 'a'), "pending", null, false);
        expectCode("INVALID_SESSION", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(longId)));
        JSONObject badTime = review("candidate:1", "pending", null, false).put("timestamp", 86400.001);
        expectCode("INVALID_SESSION", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(badTime)));
        equal(1L, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getLong("revision"));
    }

    public void testOversizedPacketAndInvalidUnicodeNeverPublishFiles() throws Exception {
        String oversized = new String(new char[24 * 1024 * 1024 + 1]).replace('\0', 'a');
        expectCode("INVALID_SESSION", () -> invokeReplace(store(), session(FIRST_ID, oversized), null, null));
        expectCode("INVALID_SESSION", () -> invokeReplace(store(), session(FIRST_ID, "\ud800"), null, null));
        equal(0, packetFiles().length);
    }

    public void testRestartSavesPendingReviewsOnTheSamePacket() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(review("candidate:1", "confirmed", "user_choice", false)));
        invokeSave(store(), FIRST_ID, 2L, 3L, new JSONArray().put(review("candidate:1", "pending", null, false)));
        JSONObject restored = (JSONObject) invoke(store(), "load", new Class<?>[0]);
        equal(3L, restored.getLong("revision"));
        equal(PACKET, restored.getString("packetJson"));
        equal("pending", restored.getJSONArray("reviews").getJSONObject(0).getString("status"));
        equal(1, packetFiles().length);
    }

    public void testMalformedPersistedReviewCannotRestoreAsValid() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) {
            database.execSQL("PRAGMA ignore_check_constraints=ON");
            database.execSQL("UPDATE reviews SET owner='alien'");
        }
        expectCode("STORAGE_CORRUPT", () -> invoke(store(), "load", new Class<?>[0]));
        expectCode("STORAGE_CORRUPT", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray()));
        check(databaseFile().exists(), "invalid stored metadata must remain available for recovery");
    }

    public void testDeletedStoredReviewCannotBeSilentlyRepopulated() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        invoke(store(), "load", new Class<?>[0]);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) {
            database.execSQL("DELETE FROM reviews");
        }
        expectCode("STORAGE_CORRUPT", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(review("candidate:1", "confirmed", "user_choice", false))));
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE);
             android.database.Cursor rows = database.rawQuery("SELECT COUNT(*) FROM reviews", null)) {
            rows.moveToFirst();
            equal(0, rows.getInt(0));
        }
    }

    public void testPlausibleStoredReviewMutationIsDetectedBeforeSave() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        invoke(store(), "load", new Class<?>[0]);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) {
            database.execSQL("UPDATE reviews SET card_id='witch'");
        }
        expectCode("STORAGE_CORRUPT", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray().put(review("candidate:1", "confirmed", "user_choice", false))));
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE);
             android.database.Cursor rows = database.rawQuery("SELECT card_id FROM reviews", null)) {
            rows.moveToFirst();
            equal("witch", rows.getString(0));
        }
    }

    public void testReplacementMustStartAtRevisionOne() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        JSONObject fresh = session(SECOND_ID, "{}").put("revision", 2);
        expectCode("INVALID_SESSION", () -> invokeReplace(store(), fresh, FIRST_ID, 1L));
        equal(FIRST_ID, ((JSONObject) invoke(store(), "load", new Class<?>[0])).getString("sessionId"));
        equal(1, packetFiles().length);
    }

    public void testMissingDatabaseWithCommittedPacketCannotBecomeEmpty() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        File packet = packetFiles()[0];
        byte[] original = read(packet);
        check(databaseFile().getCanonicalFile().getParentFile().equals(root().getCanonicalFile()), "synthetic deletion escaped the test-owned directory");
        check(databaseFile().delete(), "synthetic database must be removable");
        expectCode("STORAGE_CORRUPT", () -> invoke(store(), "load", new Class<?>[0]));
        expectCode("STORAGE_CORRUPT", () -> invokeReplace(store(), session(SECOND_ID, "{}"), null, null));
        check(!databaseFile().exists(), "a missing prior database must never be silently recreated");
        check(Arrays.equals(original, read(packet)), "original packet must remain available for recovery");
        equal(1, packetFiles().length);
    }

    public void testFractionalStoredReviewCountIsNotTruncated() throws Exception {
        assertStoredNumberIsRejected("sessions", "reviews_count", 1.5);
    }

    public void testFractionalStoredOrdinalIsNotTruncated() throws Exception {
        assertStoredNumberIsRejected("reviews", "ordinal", 0.5);
    }

    public void testFractionalStoredRevisionIsNotTruncated() throws Exception {
        assertStoredNumberIsRejected("sessions", "revision", 1.5);
    }

    public void testFractionalStoredFormatVersionIsNotTruncated() throws Exception {
        assertStoredNumberIsRejected("sessions", "format_version", 1.5);
    }

    public void testFractionalStoredManualFlagIsNotTruncated() throws Exception {
        assertStoredNumberIsRejected("reviews", "is_manual", 0.5);
    }

    public void testBlobStoredTextIsNotDecodedAsValidMetadata() throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) {
            database.execSQL("UPDATE sessions SET created_at=CAST(created_at AS BLOB)");
        }
        expectCode("STORAGE_CORRUPT", () -> invoke(store(), "load", new Class<?>[0]));
        expectCode("STORAGE_CORRUPT", () -> invokeReplace(store(), session(SECOND_ID, "{}"), FIRST_ID, 1L));
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE);
             android.database.Cursor rows = database.rawQuery("SELECT created_at FROM sessions", null)) {
            check(rows.moveToFirst(), "damaged metadata must remain present");
            equal(android.database.Cursor.FIELD_TYPE_BLOB, rows.getType(0));
        }
    }

    private void assertStoredNumberIsRejected(String table, String column, double value) throws Exception {
        invokeReplace(store(), session(FIRST_ID, PACKET), null, null);
        invoke(store(), "load", new Class<?>[0]);
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE)) {
            database.execSQL("PRAGMA ignore_check_constraints=ON");
            database.execSQL("UPDATE " + table + " SET " + column + "=?", new Object[] { value });
        }
        expectCode("STORAGE_CORRUPT", () -> invoke(store(), "load", new Class<?>[0]));
        expectCode("STORAGE_CORRUPT", () -> invokeSave(store(), FIRST_ID, 1L, 2L, new JSONArray()));
        try (SQLiteDatabase database = SQLiteDatabase.openDatabase(databaseFile().getPath(), null, SQLiteDatabase.OPEN_READWRITE);
             android.database.Cursor rows = database.rawQuery("SELECT " + column + " FROM " + table, null)) {
            check(rows.moveToFirst(), "damaged synthetic record must still exist");
            equal(android.database.Cursor.FIELD_TYPE_FLOAT, rows.getType(0));
            equal(value, rows.getDouble(0));
        }
    }

    private Object store() throws Exception {
        Class<?> type;
        try {
            type = Class.forName("com.clashtracker.simulated.AssistedSessionStore");
        } catch (ClassNotFoundException missing) {
            throw new AssertionError("Native session persistence is not implemented");
        }
        java.lang.reflect.Constructor<?> constructor = type.getDeclaredConstructor(Context.class);
        constructor.setAccessible(true);
        return constructor.newInstance(context);
    }

    private static Object invoke(Object target, String name, Class<?>[] types, Object... args) throws Exception {
        try {
            Method method = target.getClass().getDeclaredMethod(name, types);
            method.setAccessible(true);
            return method.invoke(target, args);
        } catch (InvocationTargetException error) {
            Throwable cause = error.getCause();
            if (cause instanceof Exception) throw (Exception) cause;
            throw error;
        }
    }

    private static void invokeReplace(Object store, JSONObject session, String id, Long revision) throws Exception {
        invoke(store, "replace", new Class<?>[] { JSONObject.class, String.class, Long.class }, session, id, revision);
    }

    private static void invokeSave(Object store, String id, long expected, long revision, JSONArray rows) throws Exception {
        invoke(store, "save", new Class<?>[] { String.class, long.class, long.class, String.class, JSONArray.class }, id, expected, revision, UPDATED, rows);
    }

    private static JSONObject session(String id, String packet) throws Exception {
        return new JSONObject().put("formatVersion", 1).put("sessionId", id).put("revision", 1).put("createdAt", CREATED)
            .put("updatedAt", CREATED).put("packetSha256", sha(packet.getBytes(StandardCharsets.UTF_8)))
            .put("packetJson", packet).put("reviews", new JSONArray().put(review("candidate:1", "pending", null, false)));
    }

    private static JSONObject review(String id, String status, String source, boolean manual) throws Exception {
        return new JSONObject().put("candidateId", id).put("cardId", "hog_rider").put("owner", "opponent").put("timestamp", 6.25)
            .put("status", status).put("decisionSource", source == null ? JSONObject.NULL : source).put("isManual", manual);
    }

    private File root() { return new File(context.getNoBackupFilesDir(), "assisted-session-store"); }
    private File databaseFile() { return new File(root(), "session.sqlite"); }
    private File[] packetFiles() {
        File[] files = root().listFiles((dir, name) -> name.startsWith("packet-") && name.endsWith(".json"));
        return files == null ? new File[0] : files;
    }
    private void clearSyntheticRoot() throws Exception {
        File testRoot = root().getCanonicalFile();
        check(testRoot.equals(new File(context.getNoBackupFilesDir().getCanonicalFile(), "assisted-session-store")), "synthetic cleanup escaped app-owned test directory");
        removeSynthetic(testRoot, testRoot);
    }
    private static void removeSynthetic(File file, File checkedRoot) throws Exception {
        File resolved = file.getCanonicalFile();
        check(resolved.equals(file.getAbsoluteFile()), "synthetic cleanup refuses path aliases and symlinks");
        check(resolved.equals(checkedRoot) || resolved.getPath().startsWith(checkedRoot.getPath() + File.separator), "synthetic cleanup escaped its validated root");
        File[] children = file.listFiles();
        if (children != null) for (File child : children) removeSynthetic(child, checkedRoot);
        if (file.exists() && !file.delete()) throw new Exception("Could not clear synthetic test data");
    }
    private static byte[] read(File file) throws Exception {
        try (FileInputStream input = new FileInputStream(file)) { return input.readAllBytes(); }
    }
    private static void write(File file, byte[] bytes) throws Exception {
        try (FileOutputStream output = new FileOutputStream(file)) { output.write(bytes); output.getFD().sync(); }
    }
    private static String sha(byte[] bytes) throws Exception {
        byte[] digest = MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder hex = new StringBuilder();
        for (byte value : digest) hex.append(String.format(java.util.Locale.US, "%02x", value & 0xff));
        return hex.toString();
    }
    private static void equal(Object expected, Object actual) {
        if (!java.util.Objects.equals(expected, actual)) throw new AssertionError("Expected " + expected + ", got " + actual);
    }
    private static void check(boolean condition, String message) { if (!condition) throw new AssertionError(message); }
    private interface Action { void run() throws Exception; }
    private static void expectCode(String code, Action action) throws Exception {
        try { action.run(); } catch (Exception error) {
            java.lang.reflect.Field field = error.getClass().getDeclaredField("code");
            field.setAccessible(true);
            equal(code, field.get(error));
            return;
        }
        throw new AssertionError("Expected failure " + code);
    }
    private void status(String name, String outcome) {
        Bundle status = new Bundle();
        status.putString("stream", name + ": " + outcome + "\n");
        sendStatus(0, status);
    }
}
