package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedErr error
		expectedKey string
	}{
		{
			name:        "valid header",
			headers:     http.Header{"Authorization": []string{"ApiKey my-api-key"}},
			expectedKey: "my-api-key",
			expectedErr: nil,
		},
		{
			name:        "malformed header",
			headers:     http.Header{"Authorization": []string{"apiKey my-api-key"}},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name:        "missign header",
			headers:     http.Header{"Authorization": []string{""}},
			expectedErr: errors.New("no authorization header included"),
			expectedKey: "",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.headers)
			if gotKey != tc.expectedKey {
				t.Errorf("expected key %q, got %q", tc.expectedKey, gotKey)
			}
			if tc.expectedErr == nil {
				if gotErr != nil {
					t.Errorf("expected no error, got %v", gotErr)
				}
			} else {
				if gotErr == nil || gotErr.Error() != tc.expectedErr.Error() {
					t.Errorf("expected error %q, got %v", tc.expectedErr.Error(), gotErr)
				}
			}
		})
	}
}
