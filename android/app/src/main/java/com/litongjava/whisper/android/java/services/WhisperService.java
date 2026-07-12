package com.litongjava.whisper.android.java.services;

import android.os.Build;
import android.os.Handler;
import android.widget.TextView;

import androidx.annotation.RequiresApi;

import com.litongjava.jfinal.aop.Aop;
import com.litongjava.whisper.android.java.single.LocalWhisper;
import com.litongjava.whisper.android.java.utils.WaveEncoder;

import java.io.File;
import java.io.IOException;
import java.util.List;
import java.util.concurrent.ExecutionException;

public class WhisperService {

    @RequiresApi(api = Build.VERSION_CODES.O)
    public void loadModel(
        TextView outputView,
        File modelFile
    ) {
        outputMsg(
            outputView,
            "در حال بارگذاری مدل: "
                + modelFile.getName()
        );

        long start = System.currentTimeMillis();

        LocalWhisper.INSTANCE.loadModel(
            modelFile
        );

        long elapsed =
            System.currentTimeMillis() - start;

        outputMsg(
            outputView,
            "مدل با موفقیت بارگذاری شد ("
                + elapsed
                + " ms)"
        );
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    public void transcribeSample(
        TextView outputView,
        File audioFile
    ) {
        if (!LocalWhisper.INSTANCE.isLoaded()) {
            throw new IllegalStateException(
                "ابتدا مدل را بارگذاری کنید"
            );
        }

        outputMsg(
            outputView,
            "در حال خواندن فایل صوتی: "
                + audioFile.getName()
        );

        float[] audioData;

        try {
            audioData =
                WaveEncoder.decodeWaveFile(
                    audioFile
                );
        } catch (IOException error) {
            throw new IllegalStateException(
                "فایل WAV قابل خواندن نیست",
                error
            );
        }

        try {
            List transcription =
                LocalWhisper.INSTANCE
                    .transcribeDataWithTime(
                        audioData
                    );

            if (transcription == null) {
                throw new IllegalStateException(
                    "موتور Whisper خروجی نداد"
                );
            }

            outputMsg(
                outputView,
                transcription.toString()
            );
        } catch (
            ExecutionException
            | InterruptedException error
        ) {
            Thread.currentThread().interrupt();

            throw new IllegalStateException(
                "رونویسی ناموفق بود",
                error
            );
        }
    }

    private void outputMsg(
        TextView outputView,
        String message
    ) {
        if (outputView == null) {
            return;
        }

        Aop.get(Handler.class).post(
            () -> outputView.append(
                message + "\n"
            )
        );
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    public void release() {
        // Native context release is not exposed
        // by the current Java wrapper.
    }
}
