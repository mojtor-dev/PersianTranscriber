package com.litongjava.whisper.android.java.single;

import android.os.Build;

import androidx.annotation.RequiresApi;

import com.whispercpp.java.whisper.WhisperContext;

import java.io.File;
import java.util.List;
import java.util.concurrent.ExecutionException;

@RequiresApi(api = Build.VERSION_CODES.O)
public enum LocalWhisper {
    INSTANCE;

    private WhisperContext whisperContext;
    private String loadedModelPath;

    public synchronized void loadModel(File modelFile) {
        if (modelFile == null || !modelFile.isFile()) {
            throw new IllegalArgumentException(
                "Model file does not exist"
            );
        }

        whisperContext = WhisperContext.createContextFromFile(
            modelFile.getAbsolutePath()
        );

        loadedModelPath = modelFile.getAbsolutePath();
    }

    public synchronized boolean isLoaded() {
        return whisperContext != null;
    }

    public synchronized String getLoadedModelPath() {
        return loadedModelPath;
    }

    public synchronized String transcribeData(float[] data)
        throws ExecutionException, InterruptedException {
        ensureLoaded();
        return whisperContext.transcribeData(data);
    }

    public synchronized List transcribeDataWithTime(float[] data)
        throws ExecutionException, InterruptedException {
        ensureLoaded();
        return whisperContext.transcribeDataWithTime(data);
    }

    private void ensureLoaded() {
        if (whisperContext == null) {
            throw new IllegalStateException(
                "Model is not loaded"
            );
        }
    }

    public void init() {
        // Kept for backward compatibility.
    }
}
