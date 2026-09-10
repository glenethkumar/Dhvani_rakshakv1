package com.dhvanirakshak.app.ui;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.CheckBox;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import com.dhvanirakshak.app.R;
import com.google.android.material.button.MaterialButton;

public class VerificationFragment extends Fragment {

    private CheckBox chkSecretPhrase;
    private CheckBox chkCallback;
    private MaterialButton btnVerifyIdentity;

    @Nullable
    @Override
    public View onCreateView(@NonNull LayoutInflater inflater, @Nullable ViewGroup container, @Nullable Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_verification, container, false);

        chkSecretPhrase = view.findViewById(R.id.chk_secret_phrase);
        chkCallback = view.findViewById(R.id.chk_callback);
        btnVerifyIdentity = view.findViewById(R.id.btn_verify_identity);

        btnVerifyIdentity.setOnClickListener(v -> {
            if (chkSecretPhrase.isChecked() || chkCallback.isChecked()) {
                Toast.makeText(getContext(), "✅ Verification Complete: Caller Identity Verified", Toast.LENGTH_LONG).show();
                // Return to Home Fragment
                getParentFragmentManager()
                        .beginTransaction()
                        .replace(R.id.fragment_container, new HomeFragment())
                        .commit();
            } else {
                Toast.makeText(getContext(), "Please complete at least one verification check above.", Toast.LENGTH_SHORT).show();
            }
        });

        return view;
    }
}
