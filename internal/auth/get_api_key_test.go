package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	tests := []struct {
		name        string
		header      string
		expectedKey string
		expectedErr error
	}{
		{
			name:        "valid api key",
			header:      "ApiKey abc123",
			expectedKey: "abc123",
			expectedErr: nil,
		},
		{
			name:        "missing authorization header",
			header:      "",
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:        "wrong authorization scheme",
			header:      "Bearer abc123",
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name:        "missing api key",
			header:      "ApiKey",
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			// Sesuai implementasi GetAPIKey saat ini (strings.Split),
			// "ApiKey " dianggap valid dan menghasilkan key kosong.
			name:        "empty api key",
			header:      "ApiKey ",
			expectedKey: "",
			expectedErr: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}
			key, err := GetAPIKey(headers)
			if key != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, key)
			}
			if tt.expectedErr == nil {
				if err != nil {
					t.Fatalf("expected no error, got %v", err)
				}
				return
			}
			if err == nil {
				t.Fatalf("expected error %v, got nil", tt.expectedErr)
			}
			if err.Error() != tt.expectedErr.Error() {
				t.Errorf("expected error %q, got %q", tt.expectedErr.Error(), err.Error())
			}
		})
	}

}
