package com.anthony.reperevocal.modules.stack.service

import android.app.Notification
import android.app.Service
import android.content.Intent
import android.os.IBinder

class NavigationForegroundService : Service() {
    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = Notification.Builder(this, "navigation_channel")
            .setContentTitle("Navigation active")
            .setContentText("Le guidage vocal fonctionne en arrière-plan.")
            .setSmallIcon(android.R.drawable.ic_dialog_map)
            .build()

        startForeground(1001, notification)
        return START_STICKY
    }
}
