package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name               string
		headers            http.Header
		expectedKey        string
		expectedErrMessage string
	}{
		{
			name:               "no Authorization header",
			headers:            http.Header{},
			expectedKey:        "",
			expectedErrMessage: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name:               "empty Authorization header",
			headers:            http.Header{"Authorization": {""}},
			expectedKey:        "",
			expectedErrMessage: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name:               "malformed header missing scheme",
			headers:            http.Header{"Authorization": {"mykeyonly"}},
			expectedKey:        "",
			expectedErrMessage: "malformed authorization header",
		},
		{
			name:               "malformed header wrong scheme",
			headers:            http.Header{"Authorization": {"Bearer mykey"}},
			expectedKey:        "",
			expectedErrMessage: "malformed authorization header",
		},
		{
			name:               "valid ApiKey header",
			headers:            http.Header{"Authorization": {"ApiKey secret123"}},
			expectedKey:        "secret123",
			expectedErrMessage: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)
			// Check error
			if tt.expectedErrMessage != "" {
				if err == nil {
					t.Errorf("expected error '%s', got nil", tt.expectedErrMessage)
				} else if err.Error() != tt.expectedErrMessage {
					t.Errorf("expected error message '%s', got '%s'", tt.expectedErrMessage, err.Error())
				}
			} else {
				if err != nil {
					t.Errorf("expected no error, got '%s'", err.Error())
				}
			}

			// Check key
			if key != tt.expectedKey {
				t.Errorf("expected key '%s', got '%s'", tt.expectedKey, key)
			}
		})
	}
}
