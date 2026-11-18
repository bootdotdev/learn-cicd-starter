package auth_test

import (
	"errors"
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectErr   error
	}{
		{
			name:        "Valid API Key",
			headers:     http.Header{"Authorization": []string{"ApiKey test-key"}},
			expectedKey: "test-key",
			expectErr:   nil,
		},
		{
			name:      "No Authorization Header",
			headers:   http.Header{},
			expectErr: auth.ErrNoAuthHeaderIncluded,
		},
		{
			name:      "Malformed Authorization Header",
			headers:   http.Header{"Authorization": []string{"InvalidHeader"}},
			expectErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := auth.GetAPIKey(tt.headers)
			keyDiff := cmp.Diff(tt.expectedKey, key)
			if keyDiff != "" {
				t.Errorf("API Key mismatch (-want +got):\n%s", keyDiff)
			}

			var (
				errMsg       string
				expectErrMsg string
			)

			if err != nil {
				errMsg = err.Error()
			}

			if tt.expectErr != nil {
				expectErrMsg = tt.expectErr.Error()
			}

			if errDiff := cmp.Diff(expectErrMsg, errMsg); errDiff != "" {
				t.Errorf("error mismatch (-want +got):\n%s", errDiff)
			}
		})
	}
}
