package auth

import (
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        http.Header
		expectedKey    string
		expectedError  error
		checkErrorMsg  bool
		expectedErrMsg string
	}{
		{
			name:          "no authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "empty authorization header",
			headers:       http.Header{"Authorization": {""}},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:           "malformed header - no space",
			headers:        http.Header{"Authorization": {"ApiKeyabc123"}},
			expectedKey:    "",
			checkErrorMsg:  true,
			expectedErrMsg: "malformed authorization header",
		},
		{
			name:           "malformed header - wrong prefix",
			headers:        http.Header{"Authorization": {"Bearer abc123"}},
			expectedKey:    "",
			checkErrorMsg:  true,
			expectedErrMsg: "malformed authorization header",
		},
		{
			name:           "malformed header - only prefix",
			headers:        http.Header{"Authorization": {"ApiKey"}},
			expectedKey:    "",
			checkErrorMsg:  true,
			expectedErrMsg: "malformed authorization header",
		},
		{
			name:        "valid authorization header",
			headers:     http.Header{"Authorization": {"ApiKey abc123def456"}},
			expectedKey: "abc123def456",
		},
		{
			name:        "valid header with extra parts",
			headers:     http.Header{"Authorization": {"ApiKey mykey extra parts"}},
			expectedKey: "mykey",
		},
		{
			name:           "case sensitive prefix check",
			headers:        http.Header{"Authorization": {"apikey abc123"}},
			expectedKey:    "",
			checkErrorMsg:  true,
			expectedErrMsg: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			// Check the returned key using go-cmp
			if diff := cmp.Diff(tt.expectedKey, key); diff != "" {
				t.Errorf("GetAPIKey() key mismatch (-want +got):\n%s", diff)
			}

			// Check error cases
			if tt.expectedError != nil {
				// For specific error instances, use direct comparison
				if err != tt.expectedError {
					t.Errorf("GetAPIKey() error = %v, want %v", err, tt.expectedError)
				}
			} else if tt.checkErrorMsg {
				if err == nil {
					t.Errorf("GetAPIKey() expected error with message %q, got nil", tt.expectedErrMsg)
				} else {
					// Use go-cmp for string comparison of error messages
					if diff := cmp.Diff(tt.expectedErrMsg, err.Error()); diff != "" {
						t.Errorf("GetAPIKey() error message mismatch (-want +got):\n%s", diff)
					}
				}
			} else {
				if err != nil {
					t.Errorf("GetAPIKey() unexpected error = %v", err)
				}
			}
		})
	}
}
