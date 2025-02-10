package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name:          "no authorization header",
			headers:       http.Header{},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "malformed header (missing space)",
			headers:       http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "malformed header (wrong prefix)",
			headers:       http.Header{"Authorization": []string{"Bearer token"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "valid api key",
			headers:       http.Header{"Authorization": []string{"ApiKey 12345"}},
			expectedKey:   "12345",
			expectedError: nil,
		},
		{
			name:          "valid api key with spaces",
			headers:       http.Header{"Authorization": []string{"ApiKey 123 456"}},
			expectedKey:   "123 456",
			expectedError: nil,
		},
		{
			name:          "case-sensitive prefix check",
			headers:       http.Header{"Authorization": []string{"apikey 12345"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "multiple authorization headers",
			headers:       http.Header{"Authorization": []string{"ApiKey valid", "Bearer invalid"}},
			expectedKey:   "valid",
			expectedError: nil,
		},
		{
			name:          "valid api key with leading spaces",
			headers:       http.Header{"Authorization": []string{"   ApiKey 12345"}},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"), // Since prefix is not exactly "ApiKey"
		},
		{
			name:          "empty API key value",
			headers:       http.Header{"Authorization": []string{"ApiKey "}},
			expectedKey:   "",
			expectedError: nil, // Should this be an error?
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)
			assertError(t, err, tt.expectedError)
			if key != tt.expectedKey {
				t.Errorf("expected key %q, got %q", tt.expectedKey, key)
			}
		})
	}
}

func assertError(t *testing.T, gotErr, wantErr error) {
	t.Helper()
	if wantErr == nil {
		if gotErr != nil {
			t.Fatalf("expected no error, got %v", gotErr)
		}
		return
	}

	if gotErr == nil {
		t.Fatal("expected error, got nil")
	}

	// Handle sentinel error comparison
	if errors.Is(wantErr, ErrNoAuthHeaderIncluded) {
		if !errors.Is(gotErr, wantErr) {
			t.Fatalf("expected error %v, got %v", wantErr, gotErr)
		}
		return
	}

	// Compare error messages for dynamic errors
	if gotErr.Error() != wantErr.Error() {
		t.Fatalf("expected error %q, got %q", wantErr, gotErr)
	}
}
