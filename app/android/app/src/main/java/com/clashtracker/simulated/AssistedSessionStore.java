package com.clashtracker.simulated;

import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.DatabaseErrorHandler;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteDatabaseCorruptException;
import android.database.sqlite.SQLiteException;
import android.system.Os;
import android.system.OsConstants;
import java.io.File;
import java.io.FileDescriptor;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.text.ParsePosition;
import java.text.SimpleDateFormat;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.TimeZone;
import java.util.UUID;
import java.util.regex.Pattern;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

/** One private current session. Raw imported bytes are published before their SQLite pointer. */
final class AssistedSessionStore {
    private static final Object LOCK = new Object();
    private static final int VERSION = 1;
    private static final int PACKET_LIMIT = 24 * 1024 * 1024;
    private static final long MAX_REVISION = 9007199254740991L;
    private static final Pattern UUID_PATTERN = Pattern.compile("^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", Pattern.CASE_INSENSITIVE);
    private static final Pattern HASH_PATTERN = Pattern.compile("^[a-f0-9]{64}$");
    private static final Pattern DATE_PATTERN = Pattern.compile("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}\\.\\d{3}Z$");
    private static final Pattern PACKET_FILE_PATTERN = Pattern.compile("^packet-[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}\\.json$");
    private static final Pattern CANDIDATE_PATTERN = Pattern.compile("^[a-zA-Z0-9][a-zA-Z0-9._:-]{0,127}$");
    private static final Pattern CARD_PATTERN = Pattern.compile("^[a-z][a-z0-9_]{0,63}$");
    private static final String[] SESSION_KEYS = { "formatVersion", "sessionId", "revision", "createdAt", "updatedAt", "packetSha256", "packetJson", "reviews" };
    private static final String[] REVIEW_KEYS = { "candidateId", "cardId", "owner", "timestamp", "status", "decisionSource", "isManual" };
    private final File noBackup;
    private final File root;

    static final class StoreException extends Exception {
        final String code;
        StoreException(String code) { super(code); this.code = code; }
    }

    AssistedSessionStore(Context context) {
        noBackup = context.getNoBackupFilesDir();
        root = new File(noBackup, "assisted-session-store");
    }

    JSONObject load() throws StoreException {
        synchronized (LOCK) {
            try (SQLiteDatabase database = openDatabase()) {
                database.beginTransaction();
                try {
                    JSONObject session = readSession(database, true);
                    database.setTransactionSuccessful();
                    return session;
                } finally { database.endTransaction(); }
            } catch (Exception error) { throw publicError(error, true); }
        }
    }

    void replace(JSONObject input, String expectedSessionId, Long expectedRevision) throws StoreException {
        synchronized (LOCK) {
            try {
                exactKeys(input, SESSION_KEYS);
                validateMetadata(input);
                if (integer(input, "revision") != 1) throw new StoreException("INVALID_SESSION");
                JSONArray reviews = validateReviews(array(input, "reviews"));
                String packet = string(input, "packetJson");
                byte[] packetBytes = utf8(packet);
                String hash = string(input, "packetSha256");
                if (!hash.equals(digest(packetBytes))) throw new StoreException("PACKET_INTEGRITY");
                validateExpected(expectedSessionId, expectedRevision);
                try (SQLiteDatabase database = openDatabase()) {
                    database.beginTransaction();
                    try {
                        // Even a correct CAS token must never silently overwrite a damaged current record.
                        JSONObject current = readSession(database, false);
                        checkExpected(current, expectedSessionId, expectedRevision);
                        if (current != null && string(current, "sessionId").equalsIgnoreCase(string(input, "sessionId"))) {
                            throw new StoreException("INVALID_SESSION");
                        }
                        String packetFile = publishPacket(packetBytes, hash);
                        database.delete("sessions", null, null);
                        ContentValues values = metadataValues(input, reviews);
                        values.put("singleton", 1);
                        values.put("packet_file", packetFile);
                        database.insertOrThrow("sessions", null, values);
                        insertReviews(database, string(input, "sessionId"), reviews);
                        database.setTransactionSuccessful();
                    } finally { database.endTransaction(); }
                }
            } catch (Exception error) { throw publicError(error, false); }
        }
    }

    void save(String sessionId, long expectedRevision, long revision, String updatedAt, JSONArray inputReviews) throws StoreException {
        synchronized (LOCK) {
            try {
                validateExpected(sessionId, expectedRevision);
                if (sessionId == null || revision < 1 || revision > MAX_REVISION || expectedRevision >= MAX_REVISION || revision != expectedRevision + 1) {
                    throw new StoreException("INVALID_SESSION");
                }
                date(updatedAt);
                JSONArray reviews = validateReviews(inputReviews);
                try (SQLiteDatabase database = openDatabase()) {
                    database.beginTransaction();
                    try {
                        JSONObject current = readSession(database, false);
                        checkExpected(current, sessionId, expectedRevision);
                        if (date(updatedAt) < date(string(current, "updatedAt"))) throw new StoreException("INVALID_SESSION");
                        ContentValues values = new ContentValues();
                        values.put("revision", revision);
                        values.put("updated_at", updatedAt);
                        values.put("reviews_count", reviews.length());
                        values.put("reviews_sha256", digest(utf8(reviews.toString())));
                        if (database.update("sessions", values, "singleton=1 AND session_id=? AND revision=?", new String[] { sessionId, Long.toString(expectedRevision) }) != 1) {
                            throw new StoreException("SESSION_CONFLICT");
                        }
                        database.delete("reviews", "session_id=?", new String[] { sessionId });
                        insertReviews(database, sessionId, reviews);
                        database.setTransactionSuccessful();
                    } finally { database.endTransaction(); }
                }
            } catch (Exception error) { throw publicError(error, false); }
        }
    }

    private SQLiteDatabase openDatabase() throws StoreException {
        SQLiteDatabase database = null;
        try {
            if (!root.getCanonicalFile().equals(new File(noBackup.getCanonicalFile(), "assisted-session-store"))) {
                throw new StoreException("STORAGE_CORRUPT");
            }
            if (!root.exists()) {
                if (!root.mkdir()) throw new StoreException("STORAGE_IO");
                syncDirectory(noBackup);
            }
            if (!root.isDirectory()) throw new StoreException("STORAGE_IO");
            File databaseFile = ownedFile("session.sqlite");
            boolean existing = databaseFile.exists();
            if (!existing) {
                String[] survivors = root.list();
                if (survivors == null) throw new StoreException("STORAGE_IO");
                // Packets/journals are recovery evidence, never an invitation to create an empty DB.
                if (survivors.length != 0) throw new StoreException("STORAGE_CORRUPT");
            }
            if (existing) {
                // Android may treat an existing zero-byte file as a new DB. Never recreate it.
                byte[] header = new byte[16];
                try (FileInputStream input = new FileInputStream(databaseFile)) {
                    if (input.read(header) != header.length || !Arrays.equals(header, "SQLite format 3\u0000".getBytes(StandardCharsets.US_ASCII))) {
                        throw new StoreException("STORAGE_CORRUPT");
                    }
                }
            }
            DatabaseErrorHandler preserveCorruption = corruptDatabase -> {
                // DefaultDatabaseErrorHandler deletes DB/journals. Recovery needs the original bytes.
            };
            int flags = SQLiteDatabase.OPEN_READWRITE | (existing ? 0 : SQLiteDatabase.CREATE_IF_NECESSARY);
            database = SQLiteDatabase.openDatabase(databaseFile.getPath(), null, flags, preserveCorruption);
            if (existing && database.getVersion() != VERSION) throw new StoreException("STORAGE_VERSION");
            database.execSQL("PRAGMA foreign_keys=ON");
            try (Cursor mode = database.rawQuery("PRAGMA journal_mode=DELETE", null)) {
                if (!mode.moveToFirst() || !"delete".equalsIgnoreCase(mode.getString(0))) throw new StoreException("STORAGE_IO");
            }
            database.execSQL("PRAGMA synchronous=FULL");
            if (!existing) {
                database.beginTransaction();
                try {
                    if (database.getVersion() == 0) {
                        database.execSQL("CREATE TABLE sessions (singleton INTEGER PRIMARY KEY CHECK(singleton=1), format_version INTEGER NOT NULL CHECK(format_version=1), session_id TEXT NOT NULL UNIQUE, revision INTEGER NOT NULL CHECK(revision>=1), created_at TEXT NOT NULL, updated_at TEXT NOT NULL, packet_sha256 TEXT NOT NULL, packet_file TEXT NOT NULL, reviews_count INTEGER NOT NULL CHECK(reviews_count>=0 AND reviews_count<=5000), reviews_sha256 TEXT NOT NULL)");
                        database.execSQL("CREATE TABLE reviews (candidate_id TEXT PRIMARY KEY NOT NULL, session_id TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE, ordinal INTEGER NOT NULL UNIQUE CHECK(ordinal>=0), card_id TEXT, owner TEXT NOT NULL CHECK(owner IN ('own','opponent','unknown')), timestamp REAL NOT NULL CHECK(timestamp>=0 AND timestamp<=86400), status TEXT NOT NULL CHECK(status IN ('pending','confirmed','excluded')), decision_source TEXT CHECK(decision_source IS NULL OR decision_source IN ('user_choice','manual')), is_manual INTEGER NOT NULL CHECK(is_manual IN (0,1)))");
                        database.setVersion(VERSION);
                    } else if (database.getVersion() != VERSION) { throw new StoreException("STORAGE_VERSION"); }
                    database.setTransactionSuccessful();
                } finally { database.endTransaction(); }
                syncDirectory(root);
            }
            if (database.getVersion() != VERSION) throw new StoreException("STORAGE_VERSION");
            try (Cursor integrity = database.rawQuery("PRAGMA quick_check(1)", null)) {
                if (!integrity.moveToFirst() || !"ok".equals(integrity.getString(0))) throw new StoreException("STORAGE_CORRUPT");
            }
            try (Cursor foreignKeys = database.rawQuery("PRAGMA foreign_key_check", null)) {
                if (foreignKeys.moveToFirst()) throw new StoreException("STORAGE_CORRUPT");
            }
            return database;
        } catch (Exception error) {
            if (database != null) database.close();
            throw publicError(error, true);
        }
    }

    private JSONObject readSession(SQLiteDatabase database, boolean includePacket) throws StoreException {
        try (Cursor metadata = database.rawQuery("SELECT format_version,session_id,revision,created_at,updated_at,packet_sha256,packet_file,reviews_count,reviews_sha256 FROM sessions WHERE singleton=1", null)) {
            if (!metadata.moveToFirst()) {
                if (countReviews(database) != 0) throw new StoreException("STORAGE_CORRUPT");
                return null;
            }
            if (storedInteger(metadata, 0) != VERSION) throw new StoreException("STORAGE_VERSION");
            JSONObject session = new JSONObject().put("formatVersion", VERSION).put("sessionId", storedString(metadata, 1, false))
                .put("revision", storedInteger(metadata, 2)).put("createdAt", storedString(metadata, 3, false)).put("updatedAt", storedString(metadata, 4, false))
                .put("packetSha256", storedString(metadata, 5, false));
            validateMetadata(session);
            long count = storedInteger(metadata, 7);
            String reviewsHash = storedString(metadata, 8, false);
            if (count < 0 || count > 5000 || reviewsHash == null || !HASH_PATTERN.matcher(reviewsHash).matches() || countReviews(database) != count) {
                throw new StoreException("STORAGE_CORRUPT");
            }
            JSONArray reviews = new JSONArray();
            try (Cursor rows = database.rawQuery("SELECT candidate_id,card_id,owner,timestamp,status,decision_source,is_manual,ordinal FROM reviews WHERE session_id=? ORDER BY ordinal", new String[] { metadata.getString(1) })) {
                while (rows.moveToNext()) {
                    long manual = storedInteger(rows, 6);
                    if (storedInteger(rows, 7) != reviews.length() || manual < 0 || manual > 1 || reviews.length() >= 5000
                        || (rows.getType(3) != Cursor.FIELD_TYPE_INTEGER && rows.getType(3) != Cursor.FIELD_TYPE_FLOAT)) {
                        throw new StoreException("STORAGE_CORRUPT");
                    }
                    String card = storedString(rows, 1, true);
                    String source = storedString(rows, 5, true);
                    reviews.put(new JSONObject().put("candidateId", storedString(rows, 0, false)).put("cardId", card == null ? JSONObject.NULL : card)
                        .put("owner", storedString(rows, 2, false)).put("timestamp", rows.getDouble(3)).put("status", storedString(rows, 4, false))
                        .put("decisionSource", source == null ? JSONObject.NULL : source).put("isManual", manual == 1));
                }
            }
            reviews = validateReviews(reviews);
            if (reviews.length() != count || !digest(utf8(reviews.toString())).equals(reviewsHash)) throw new StoreException("STORAGE_CORRUPT");
            String packet = readPacket(storedString(metadata, 6, false), string(session, "packetSha256"), includePacket);
            session.put("packetJson", includePacket ? packet : JSONObject.NULL).put("reviews", reviews);
            return session;
        } catch (StoreException error) {
            if ("INVALID_SESSION".equals(error.code)) throw new StoreException("STORAGE_CORRUPT");
            throw error;
        } catch (Exception error) { throw publicError(error, true); }
    }

    private static long storedInteger(Cursor cursor, int column) throws StoreException {
        if (cursor.getType(column) != Cursor.FIELD_TYPE_INTEGER) throw new StoreException("STORAGE_CORRUPT");
        return cursor.getLong(column);
    }

    private static String storedString(Cursor cursor, int column, boolean nullable) throws StoreException {
        if (nullable && cursor.getType(column) == Cursor.FIELD_TYPE_NULL) return null;
        if (cursor.getType(column) != Cursor.FIELD_TYPE_STRING) throw new StoreException("STORAGE_CORRUPT");
        return cursor.getString(column);
    }

    private int countReviews(SQLiteDatabase database) {
        try (Cursor rows = database.rawQuery("SELECT COUNT(*) FROM reviews", null)) { rows.moveToFirst(); return rows.getInt(0); }
    }

    private ContentValues metadataValues(JSONObject session, JSONArray reviews) throws Exception {
        ContentValues values = new ContentValues();
        values.put("format_version", VERSION);
        values.put("session_id", string(session, "sessionId"));
        values.put("revision", integer(session, "revision"));
        values.put("created_at", string(session, "createdAt"));
        values.put("updated_at", string(session, "updatedAt"));
        values.put("packet_sha256", string(session, "packetSha256"));
        values.put("reviews_count", reviews.length());
        values.put("reviews_sha256", digest(utf8(reviews.toString())));
        return values;
    }

    private void insertReviews(SQLiteDatabase database, String sessionId, JSONArray reviews) throws JSONException {
        for (int i = 0; i < reviews.length(); i++) {
            JSONObject row = reviews.getJSONObject(i);
            ContentValues values = new ContentValues();
            values.put("candidate_id", row.getString("candidateId"));
            values.put("session_id", sessionId);
            values.put("ordinal", i);
            if (row.isNull("cardId")) values.putNull("card_id"); else values.put("card_id", row.getString("cardId"));
            values.put("owner", row.getString("owner"));
            values.put("timestamp", row.getDouble("timestamp"));
            values.put("status", row.getString("status"));
            if (row.isNull("decisionSource")) values.putNull("decision_source"); else values.put("decision_source", row.getString("decisionSource"));
            values.put("is_manual", row.getBoolean("isManual") ? 1 : 0);
            database.insertOrThrow("reviews", null, values);
        }
    }

    private String publishPacket(byte[] bytes, String expectedHash) throws Exception {
        String token = UUID.randomUUID().toString();
        File temporary = ownedFile("packet-" + token + ".tmp");
        File published = ownedFile("packet-" + token + ".json");
        if (!temporary.createNewFile()) throw new StoreException("STORAGE_IO");
        try (FileOutputStream output = new FileOutputStream(temporary)) { output.write(bytes); output.getFD().sync(); }
        if (published.exists() || !temporary.renameTo(published)) throw new StoreException("STORAGE_IO");
        syncDirectory(root);
        readPacket(published.getName(), expectedHash, false);
        // Failures leave the newly published file for recovery. Previous packets are never removed.
        return published.getName();
    }

    private String readPacket(String filename, String expectedHash, boolean includeContent) throws StoreException {
        if (filename == null || !PACKET_FILE_PATTERN.matcher(filename).matches()) throw new StoreException("STORAGE_CORRUPT");
        try {
            File packet = ownedFile(filename);
            if (!packet.exists()) throw new StoreException("PACKET_MISSING");
            long length = packet.length();
            if (!packet.isFile() || length <= 0 || length > PACKET_LIMIT) throw new StoreException("PACKET_INTEGRITY");
            MessageDigest sha = MessageDigest.getInstance("SHA-256");
            StringBuilder text = includeContent ? new StringBuilder((int) Math.min(length, 65536)) : null;
            try (FileInputStream file = new FileInputStream(packet);
                 DigestInputStream input = new DigestInputStream(file, sha);
                 InputStreamReader reader = new InputStreamReader(input, StandardCharsets.UTF_8.newDecoder()
                     .onMalformedInput(CodingErrorAction.REPORT).onUnmappableCharacter(CodingErrorAction.REPORT))) {
                char[] chunk = new char[8192];
                int count;
                while ((count = reader.read(chunk)) != -1) {
                    if (file.getChannel().position() > PACKET_LIMIT) throw new StoreException("PACKET_INTEGRITY");
                    if (text != null) text.append(chunk, 0, count);
                }
                if (file.getChannel().position() != length) throw new StoreException("PACKET_INTEGRITY");
            }
            if (!hex(sha.digest()).equals(expectedHash)) throw new StoreException("PACKET_INTEGRITY");
            return text == null ? null : text.toString();
        } catch (StoreException error) { throw error; }
        catch (java.nio.charset.CharacterCodingException error) { throw new StoreException("PACKET_INTEGRITY"); }
        catch (Exception error) { throw new StoreException("STORAGE_IO"); }
    }

    private File ownedFile(String filename) throws Exception {
        File file = new File(root, filename);
        if (!file.getCanonicalFile().equals(new File(root.getCanonicalFile(), filename))) {
            throw new StoreException("STORAGE_CORRUPT");
        }
        return file;
    }

    private static void syncDirectory(File directory) throws Exception {
        FileDescriptor descriptor = Os.open(directory.getPath(), OsConstants.O_RDONLY, 0);
        try {
            if (!OsConstants.S_ISDIR(Os.fstat(descriptor).st_mode)) throw new StoreException("STORAGE_IO");
            Os.fsync(descriptor);
        } finally { Os.close(descriptor); }
    }

    private static void validateMetadata(JSONObject session) throws StoreException {
        if (integer(session, "formatVersion") != VERSION || !UUID_PATTERN.matcher(string(session, "sessionId")).matches()
            || !HASH_PATTERN.matcher(string(session, "packetSha256")).matches()) throw new StoreException("INVALID_SESSION");
        integer(session, "revision");
        if (date(string(session, "updatedAt")) < date(string(session, "createdAt"))) throw new StoreException("INVALID_SESSION");
    }

    private static JSONArray validateReviews(JSONArray input) throws StoreException {
        if (input == null || input.length() > 5000) throw new StoreException("INVALID_SESSION");
        Set<String> seen = new HashSet<>();
        JSONArray reviews = new JSONArray();
        try {
            for (int i = 0; i < input.length(); i++) {
                if (!(input.opt(i) instanceof JSONObject)) throw new StoreException("INVALID_SESSION");
                JSONObject row = input.getJSONObject(i);
                exactKeys(row, REVIEW_KEYS);
                String id = string(row, "candidateId");
                String card = nullableString(row, "cardId");
                String owner = string(row, "owner");
                String status = string(row, "status");
                String source = nullableString(row, "decisionSource");
                Object timestamp = row.opt("timestamp");
                Object manual = row.opt("isManual");
                if (!CANDIDATE_PATTERN.matcher(id).matches() || !seen.add(id) || !(manual instanceof Boolean)
                    || !(timestamp instanceof Number) || !Double.isFinite(((Number) timestamp).doubleValue())
                    || ((Number) timestamp).doubleValue() < 0 || ((Number) timestamp).doubleValue() > 86400
                    || (card != null && (card.equals("unknown") || !CARD_PATTERN.matcher(card).matches()))
                    || !(owner.equals("own") || owner.equals("opponent") || owner.equals("unknown"))
                    || !(status.equals("pending") || status.equals("confirmed") || status.equals("excluded"))
                    || (source != null && !(source.equals("manual") || source.equals("user_choice")))) throw new StoreException("INVALID_SESSION");
                boolean isManual = (Boolean) manual;
                if ((isManual && (!"manual".equals(source) || !id.matches("^manual:[1-9]\\d*$")))
                    || (!isManual && "manual".equals(source))
                    || (status.equals("confirmed") && (card == null || !owner.equals("opponent") || source == null))
                    || (status.equals("excluded") && source == null)
                    || (!isManual && source == null && !status.equals("pending"))) throw new StoreException("INVALID_SESSION");
                // Fixed key order and numeric normalization bind SQLite rows to their committed digest.
                reviews.put(new JSONObject().put("candidateId", id).put("cardId", card == null ? JSONObject.NULL : card)
                    .put("owner", owner).put("timestamp", ((Number) timestamp).doubleValue()).put("status", status)
                    .put("decisionSource", source == null ? JSONObject.NULL : source).put("isManual", isManual));
            }
        } catch (JSONException error) { throw new StoreException("INVALID_SESSION"); }
        return reviews;
    }

    private static void validateExpected(String id, Long revision) throws StoreException {
        if ((id == null) != (revision == null) || (id != null && (!UUID_PATTERN.matcher(id).matches() || revision < 1 || revision > MAX_REVISION))) {
            throw new StoreException("INVALID_SESSION");
        }
    }

    private static void checkExpected(JSONObject current, String id, Long revision) throws StoreException {
        if (current == null ? id != null || revision != null : id == null || !string(current, "sessionId").equals(id) || integer(current, "revision") != revision) {
            throw new StoreException("SESSION_CONFLICT");
        }
    }

    static long integer(JSONObject object, String key) throws StoreException {
        Object value = object == null ? null : object.opt(key);
        if (!(value instanceof Number)) throw new StoreException("INVALID_SESSION");
        double number = ((Number) value).doubleValue();
        long whole = ((Number) value).longValue();
        if (!Double.isFinite(number) || number != whole || whole < 1 || whole > MAX_REVISION) throw new StoreException("INVALID_SESSION");
        return whole;
    }

    static String string(JSONObject object, String key) throws StoreException {
        Object value = object == null ? null : object.opt(key);
        if (!(value instanceof String)) throw new StoreException("INVALID_SESSION");
        return (String) value;
    }

    static String nullableString(JSONObject object, String key) throws StoreException {
        if (object == null || !object.has(key)) throw new StoreException("INVALID_SESSION");
        return object.isNull(key) ? null : string(object, key);
    }

    private static JSONArray array(JSONObject object, String key) throws StoreException {
        Object value = object.opt(key);
        if (!(value instanceof JSONArray)) throw new StoreException("INVALID_SESSION");
        return (JSONArray) value;
    }

    private static void exactKeys(JSONObject object, String[] keys) throws StoreException {
        if (object == null || object.length() != keys.length) throw new StoreException("INVALID_SESSION");
        for (String key : keys) if (!object.has(key)) throw new StoreException("INVALID_SESSION");
    }

    private static long date(String value) throws StoreException {
        if (value == null || !DATE_PATTERN.matcher(value).matches()) throw new StoreException("INVALID_SESSION");
        SimpleDateFormat format = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'", Locale.US);
        format.setTimeZone(TimeZone.getTimeZone("UTC"));
        format.setLenient(false);
        ParsePosition position = new ParsePosition(0);
        java.util.Date parsed = format.parse(value, position);
        if (parsed == null || position.getIndex() != value.length() || !format.format(parsed).equals(value)) throw new StoreException("INVALID_SESSION");
        return parsed.getTime();
    }

    private static byte[] utf8(String value) throws StoreException {
        if (value == null || value.length() == 0 || value.length() > PACKET_LIMIT) throw new StoreException("INVALID_SESSION");
        long bytes = 0;
        for (int i = 0; i < value.length(); i++) {
            char character = value.charAt(i);
            if (Character.isHighSurrogate(character)) {
                if (++i >= value.length() || !Character.isLowSurrogate(value.charAt(i))) throw new StoreException("INVALID_SESSION");
                bytes += 4;
            } else if (Character.isLowSurrogate(character)) { throw new StoreException("INVALID_SESSION"); }
            else bytes += character < 0x80 ? 1 : character < 0x800 ? 2 : 3;
            if (bytes > PACKET_LIMIT) throw new StoreException("INVALID_SESSION");
        }
        return value.getBytes(StandardCharsets.UTF_8);
    }

    private static String digest(byte[] bytes) throws Exception { return hex(MessageDigest.getInstance("SHA-256").digest(bytes)); }
    private static String hex(byte[] bytes) {
        char[] alphabet = "0123456789abcdef".toCharArray();
        StringBuilder value = new StringBuilder(64);
        for (byte part : bytes) { value.append(alphabet[(part & 0xff) >>> 4]); value.append(alphabet[part & 0x0f]); }
        return value.toString();
    }

    private static StoreException publicError(Exception error, boolean reading) {
        if (error instanceof StoreException) return (StoreException) error;
        if (error instanceof SQLiteDatabaseCorruptException || (reading && error instanceof SQLiteException)) return new StoreException("STORAGE_CORRUPT");
        return new StoreException("STORAGE_IO");
    }
}
