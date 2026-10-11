package com.clashtracker.simulated;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import org.json.JSONArray;
import org.json.JSONObject;

@CapacitorPlugin(name = "AssistedSessionStore")
public final class AssistedSessionStorePlugin extends Plugin {
    @PluginMethod
    public void load(PluginCall call) {
        try {
            JSONObject session = new AssistedSessionStore(getContext()).load();
            call.resolve(new JSObject().put("session", session == null ? JSONObject.NULL : session));
        } catch (Exception error) { reject(call, error); }
    }

    @PluginMethod
    public void replace(PluginCall call) {
        try {
            JSONObject data = call.getData();
            Object session = data.opt("session");
            if (!(session instanceof JSONObject) || !data.has("expectedRevision")) throw new AssistedSessionStore.StoreException("INVALID_SESSION");
            String expectedId = AssistedSessionStore.nullableString(data, "expectedSessionId");
            Long expectedRevision = data.isNull("expectedRevision") ? null : AssistedSessionStore.integer(data, "expectedRevision");
            new AssistedSessionStore(getContext()).replace((JSONObject) session, expectedId, expectedRevision);
            call.resolve(new JSObject());
        } catch (Exception error) { reject(call, error); }
    }

    @PluginMethod
    public void save(PluginCall call) {
        try {
            JSONObject data = call.getData();
            Object reviews = data.opt("reviews");
            if (!(reviews instanceof JSONArray)) throw new AssistedSessionStore.StoreException("INVALID_SESSION");
            new AssistedSessionStore(getContext()).save(AssistedSessionStore.string(data, "sessionId"),
                AssistedSessionStore.integer(data, "expectedRevision"), AssistedSessionStore.integer(data, "revision"),
                AssistedSessionStore.string(data, "updatedAt"), (JSONArray) reviews);
            call.resolve(new JSObject());
        } catch (Exception error) { reject(call, error); }
    }

    private static void reject(PluginCall call, Exception error) {
        String code = error instanceof AssistedSessionStore.StoreException ? ((AssistedSessionStore.StoreException) error).code : "STORAGE_IO";
        // Error text/code are public constants; private paths, causes and stacks never reach the WebView.
        call.reject("本地审核记录读取或保存失败，原记录已保留。", code);
    }
}
