package com.anthony.reperevocal.modules.stack.work

data class AppWorkerPolicy(
    val enableBackgroundCleanup: Boolean = true,
    val enableReminderChecks: Boolean = true,
    val enableDeferredSync: Boolean = false
)
