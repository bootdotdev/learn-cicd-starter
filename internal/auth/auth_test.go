	package auth

	import (
		"net/http"
		"testing"
	)

	func TestGetAPIKey(t *testing.T) {
		tests := []struct {
			name        string
			header      string
			expectedKey string
			expectErr   bool
		}{
			{
				name:        "valid API key",
				header:      "ApiKey 12345",
				expectedKey: "12345",
				expectErr:   false,
			},
			{
				name:      "missing header",
				header:    "",
				expectErr: true,
			},
			{
				name:      "wrong prefix",
				header:    "Bearer 12345",
				expectErr: true,
			},
			{
				name:      "missing key",
				header:    "ApiKey",
				expectErr: true,
			},
		}

		for _, tt := range tests {
			t.Run(tt.name, func(t *testing.T) {
				headers := http.Header{}
				if tt.header != "" {
					headers.Set("Authorization", tt.header)
				}

				got, err := GetAPIKey(headers)

				if tt.expectErr {
					if err == nil {
						t.Fatalf("expected error, got nil")
					}
					return
				}

				if err != nil {
					t.Fatalf("unexpected error: %v", err)
				}

				if got != tt.expectedKey {
					t.Errorf("got %s, want %s", got, tt.expectedKey)
				}
			})
		}
	}