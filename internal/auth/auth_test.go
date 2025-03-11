package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name                string
		headers             http.Header
		expectedKey         string
		expectedErrCategory string
	}{
		{
			name:                "No Authorization header",
			headers:             http.Header{}, // no headers set
			expectedKey:         "",
			expectedErrCategory: "noauth",
		},
		{
			name:                "Malformed header: missing API key part",
			headers:             http.Header{"Authorization": []string{"ApiKey"}},
			expectedKey:         "",
			expectedErrCategory: "malformed",
		},
		{
			name:                "Malformed header: wrong scheme",
			headers:             http.Header{"Authorization": []string{"Bearer sometoken"}},
			expectedKey:         "",
			expectedErrCategory: "malformed",
		},
		{
			name:                "Valid header",
			headers:             http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			expectedKey:         "my-secret-key",
			expectedErrCategory: "none",
		},
		{
			name:                "Valid header but empty API key",
			headers:             http.Header{"Authorization": []string{"ApiKey "}},
			expectedKey:         "",
			expectedErrCategory: "none",
		},
	}

	// Run each test case as a subtest.
	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tc.headers)

			// Check error based on expected error category.
			switch tc.expectedErrCategory {
			case "none":
				if err != nil {
					t.Fatalf("unexpected error, got: %v", err)
				}
			case "noauth":
				if !errors.Is(err, ErrNoAuthHeaderIncluded) {
					t.Fatalf("expected ErrNoAuthHeaderIncluded, got: %v", err)
				}
			case "malformed":
				if err == nil {
					t.Fatalf("expected an error but got nil")
				}
				// The error should be something other than ErrNoAuthHeaderIncluded.
				if errors.Is(err, ErrNoAuthHeaderIncluded) {
					t.Fatalf("unexpected ErrNoAuthHeaderIncluded; expected a different error")
				}
			default:
				t.Fatalf("unknown error category %q", tc.expectedErrCategory)
			}

			// If an error was expected, we don't care about the key.
			if tc.expectedErrCategory != "none" {
				return
			}

			// Check the returned API key.
			if gotKey != tc.expectedKey {
				t.Fatalf("expected key %q, got %q", tc.expectedKey, gotKey)
			}
		})
	}
}
