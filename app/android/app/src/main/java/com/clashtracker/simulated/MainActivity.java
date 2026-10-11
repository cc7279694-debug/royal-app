package com.clashtracker.simulated;

import android.os.Bundle;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(AssistedSessionStorePlugin.class);
        super.onCreate(savedInstanceState);
    }
}
