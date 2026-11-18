package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headerValue string
		wantKey     string
		wantErr     bool
	}{
		{
			name:        "valid api key",
			headerValue: "ApiKey abcd",
			wantKey:     "abcd",
			wantErr:     false,
		},
		{
			name:        "no authorization header",
			headerValue: "",
			wantErr:     true,
		},
		{
			name:        "malformed header - missing prefix",
			headerValue: "abcd",
			wantErr:     true,
		},
		{
			name:        "malformed header - wrong prefix",
			headerValue: "Bearer abcd",
			wantErr:     true,
		},
		{
			name:        "empty key but no error (current behavior)",
			headerValue: "ApiKey ",
			wantKey:     "",
			wantErr:     false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			header := http.Header{}
			if tc.headerValue != "" {
				header.Set("Authorization", tc.headerValue)
			}

			got, err := GetAPIKey(header)

			if tc.wantErr {
				if err == nil {
					t.Fatalf("expected error, got nil (key: %q)", got)
				}
				return
			}

			if err != nil {
				t.Fatalf("did not expect error, got: %v", err)
			}

			if got != tc.wantKey {
				t.Fatalf("expected key %q, got %q", tc.wantKey, got)
			}
		})
	}
}
