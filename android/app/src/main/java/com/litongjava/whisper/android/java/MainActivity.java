package com.litongjava.whisper.android.java;

import android.content.ContentResolver;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.OpenableColumns;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import com.blankj.utilcode.util.ThreadUtils;
import com.litongjava.jfinal.aop.Aop;
import com.litongjava.jfinal.aop.AopManager;
import com.litongjava.whisper.android.java.services.WhisperService;
import com.litongjava.whisper.android.java.task.LoadModelTask;
import com.litongjava.whisper.android.java.task.TranscriptionTask;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;

public class MainActivity extends AppCompatActivity {
    private EditText outputText;
    private TextView selectedFileText;
    private TextView statusText;
    private ProgressBar progressBar;
    private Button transcribeBtn;
    private File selectedAudioFile;
    private File selectedModelFile;

    private final WhisperService whisperService =
        Aop.get(WhisperService.class);

    private ActivityResultLauncher<String[]> audioPicker;
    private ActivityResultLauncher<String[]> modelPicker;
    private ActivityResultLauncher<String> saveTextLauncher;

    @RequiresApi(api = Build.VERSION_CODES.O)
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.activity_main);

        AopManager.me().addSingletonObject(
            new Handler(Looper.getMainLooper())
        );

        outputText = findViewById(R.id.sample_text);
        selectedFileText = findViewById(R.id.selectedFileText);
        statusText = findViewById(R.id.statusText);
        progressBar = findViewById(R.id.progressBar);
        transcribeBtn = findViewById(R.id.transcribeBtn);

        configurePickers();
        configureButtons();
    }

    private void configurePickers() {
        modelPicker = registerForActivityResult(
            new ActivityResultContracts.OpenDocument(),
            uri -> {
                if (uri == null) return;

                try {
                    String name = getDisplayName(uri);

                    if (!name.toLowerCase().endsWith(".bin")) {
                        message("فایل مدل باید پسوند bin داشته باشد.");
                        return;
                    }

                    selectedModelFile = copyToCache(
                        uri,
                        "selected_model.bin"
                    );

                    statusText.setText(
                        "مدل انتخاب شد: " + name
                    );

                    loadSelectedModel();
                } catch (Exception error) {
                    message(
                        "خطا در خواندن مدل: "
                            + error.getMessage()
                    );
                }
            }
        );

        audioPicker = registerForActivityResult(
            new ActivityResultContracts.OpenDocument(),
            uri -> {
                if (uri == null) return;

                try {
                    String name = getDisplayName(uri);

                    if (!name.toLowerCase().endsWith(".wav")) {
                        message("در این نسخه فقط فایل WAV پشتیبانی می‌شود.");
                        return;
                    }

                    selectedAudioFile = copyToCache(
                        uri,
                        "selected_audio.wav"
                    );

                    selectedFileText.setText(
                        "فایل انتخاب‌شده: " + name
                    );
                    transcribeBtn.setEnabled(true);
                    statusText.setText("فایل آماده تبدیل است");
                } catch (Exception error) {
                    message("خطا در خواندن فایل: " + error.getMessage());
                }
            }
        );

        saveTextLauncher = registerForActivityResult(
            new ActivityResultContracts.CreateDocument("text/plain"),
            uri -> {
                if (uri == null) return;

                try (OutputStream output =
                         getContentResolver().openOutputStream(uri)) {
                    if (output == null) {
                        throw new IllegalStateException(
                            "فایل خروجی قابل نوشتن نیست"
                        );
                    }

                    output.write(
                        outputText.getText().toString()
                            .getBytes("UTF-8")
                    );
                    message("فایل TXT ذخیره شد");
                } catch (Exception error) {
                    message("خطا در ذخیره: " + error.getMessage());
                }
            }
        );
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    private void configureButtons() {
        findViewById(R.id.loadModelBtn)
            .setOnClickListener(view ->
                modelPicker.launch(
                    new String[] {
                        "application/octet-stream",
                        "*/*"
                    }
                )
            );

        findViewById(R.id.selectAudioBtn)
            .setOnClickListener(view ->
                audioPicker.launch(
                    new String[] {
                        "audio/wav",
                        "audio/x-wav",
                        "audio/*"
                    }
                )
            );

        transcribeBtn.setOnClickListener(
            view -> transcribeSelected()
        );

        findViewById(R.id.clearBtn)
            .setOnClickListener(view -> {
                outputText.setText("");
                statusText.setText("متن پاک شد");
            });

        findViewById(R.id.shareBtn)
            .setOnClickListener(view -> shareText());

        findViewById(R.id.saveBtn)
            .setOnClickListener(view -> {
                if (outputText.getText().toString().trim().isEmpty()) {
                    message("هنوز متنی برای ذخیره وجود ندارد");
                    return;
                }
                saveTextLauncher.launch("PersianTranscriber.txt");
            });
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    private void loadSelectedModel() {
        if (
            selectedModelFile == null
            || !selectedModelFile.isFile()
        ) {
            message("ابتدا فایل مدل را انتخاب کنید");
            return;
        }

        busy(true, "در حال بارگذاری مدل...");

        ThreadUtils.executeByIo(
            new LoadModelTask(
                outputText,
                selectedModelFile
            ) {
                @Override
                public void onSuccess(Object result) {
                    busy(false, "مدل آماده است");
                }

                @Override
                public void onFail(Throwable error) {
                    busy(
                        false,
                        "بارگذاری مدل ناموفق بود"
                    );

                    message(
                        "خطای مدل: "
                            + error.getMessage()
                    );
                }
            }
        );
    }

    private void transcribeSelected() {
        if (selectedAudioFile == null
            || !selectedAudioFile.isFile()) {
            message("ابتدا فایل WAV را انتخاب کنید");
            return;
        }

        outputText.setText("");
        busy(true, "در حال تبدیل صوت به متن...");

        ThreadUtils.executeByIo(
            new TranscriptionTask(
                outputText,
                selectedAudioFile
            ) {
                @Override
                public void onSuccess(Object result) {
                    busy(false, "تبدیل به پایان رسید");
                }

                @Override
                public void onFail(Throwable error) {
                    busy(false, "تبدیل ناموفق بود");
                    message("خطای تبدیل: " + error.getMessage());
                }
            }
        );
    }

    private void shareText() {
        String text = outputText.getText().toString().trim();

        if (text.isEmpty()) {
            message("هنوز متنی برای اشتراک وجود ندارد");
            return;
        }

        Intent intent = new Intent(Intent.ACTION_SEND);
        intent.setType("text/plain");
        intent.putExtra(Intent.EXTRA_TEXT, text);

        startActivity(
            Intent.createChooser(
                intent,
                "اشتراک متن رونویسی"
            )
        );
    }

    private File copyToCache(Uri uri, String filename)
        throws Exception {
        File target = new File(getCacheDir(), filename);
        ContentResolver resolver = getContentResolver();

        try (
            InputStream input = resolver.openInputStream(uri);
            FileOutputStream output = new FileOutputStream(target)
        ) {
            if (input == null) {
                throw new IllegalStateException(
                    "فایل قابل خواندن نیست"
                );
            }

            byte[] buffer = new byte[8192];
            int count;

            while ((count = input.read(buffer)) != -1) {
                output.write(buffer, 0, count);
            }
        }

        return target;
    }

    private String getDisplayName(Uri uri) {
        String name = "audio.wav";

        try (Cursor cursor = getContentResolver().query(
            uri,
            new String[] {OpenableColumns.DISPLAY_NAME},
            null,
            null,
            null
        )) {
            if (cursor != null && cursor.moveToFirst()) {
                int index = cursor.getColumnIndex(
                    OpenableColumns.DISPLAY_NAME
                );

                if (index >= 0) {
                    name = cursor.getString(index);
                }
            }
        }

        return name;
    }

    private void busy(boolean value, String text) {
        runOnUiThread(() -> {
            progressBar.setVisibility(
                value ? View.VISIBLE : View.GONE
            );
            transcribeBtn.setEnabled(
                !value && selectedAudioFile != null
            );
            statusText.setText(text);
        });
    }

    private void message(String text) {
        runOnUiThread(() ->
            Toast.makeText(
                this,
                text,
                Toast.LENGTH_LONG
            ).show()
        );
    }

    @RequiresApi(api = Build.VERSION_CODES.O)
    @Override
    protected void onDestroy() {
        whisperService.release();
        super.onDestroy();
    }
}
