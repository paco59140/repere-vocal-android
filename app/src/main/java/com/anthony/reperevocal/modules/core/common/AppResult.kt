package com.anthony.reperevocal.modules.core.common

sealed class AppResult<out T> {
    data class Success<T>(val data: T) : AppResult<T>()
    data class Error(val message: String, val throwable: Throwable? = null) : AppResult<Nothing>()
    object Loading : AppResult<Nothing>()
}
