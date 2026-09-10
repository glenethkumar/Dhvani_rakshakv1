package com.dhvanirakshak.app;

import android.Manifest;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;

import com.getcapacitor.JSObject;
import com.getcapacitor.PermissionState;
import com.getcapacitor.Plugin;
import com.getcapacitor.PluginCall;
import com.getcapacitor.PluginMethod;
import com.getcapacitor.annotation.CapacitorPlugin;
import com.getcapacitor.annotation.Permission;

@CapacitorPlugin(
    name = "CallDetector",
    permissions = {
        @Permission(strings = {Manifest.permission.READ_PHONE_STATE, Manifest.permission.READ_CALL_LOG}, alias = "phone"),
        @Permission(strings = {Manifest.permission.RECORD_AUDIO}, alias = "microphone")
    }
)
public class CallDetectorPlugin extends Plugin {

    @PluginMethod
    public void requestCallPermissions(PluginCall call) {
        if (getPermissionState("phone") != PermissionState.GRANTED ||
            getPermissionState("microphone") != PermissionState.GRANTED) {
            requestAllPermissions(call, "permissionCallback");
        } else {
            checkOverlayPermission(call);
        }
    }

    @PluginMethod
    public void permissionCallback(PluginCall call) {
        checkOverlayPermission(call);
    }

    private void checkOverlayPermission(PluginCall call) {
        JSObject ret = new JSObject();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M && !Settings.canDrawOverlays(getContext())) {
            Intent intent = new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:" + getContext().getPackageName()));
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            getContext().startActivity(intent);
            ret.put("overlayRequested", true);
            ret.put("status", "OVERLAY_PERMISSION_REQUIRED");
        } else {
            ret.put("status", "PERMISSIONS_GRANTED");
        }
        call.resolve(ret);
    }

    @PluginMethod
    public void startMonitoring(PluginCall call) {
        JSObject ret = new JSObject();
        ret.put("status", "ACTIVE_MONITORING_ENABLED");
        call.resolve(ret);
    }

    @PluginMethod
    public void stopMonitoring(PluginCall call) {
        Intent intent = new Intent(getContext(), CallDetectionService.class);
        intent.putExtra("ACTION", "STOP_DETECTION");
        getContext().stopService(intent);
        JSObject ret = new JSObject();
        ret.put("status", "MONITORING_DISABLED");
        call.resolve(ret);
    }
}
