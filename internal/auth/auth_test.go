package auth

import (
	"net/http"
	"reflect"
	"testing"
)

// TestGetAPIKey uses the table-driven test idiom to ensure the function
// correctly extracts the API key under various conditions.
func TestGetAPIKey(t *testing.T) {
	// Define the test table structure
	tests := map[string]struct {
		// Input
		headers http.Header
		// Expected Output
		want string
		// Expected Error (non-nil is expected to fail)
		wantErr bool
	}{
		"ValidKey": {
			// Correctly formatted header with a key
			headers: map[string][]string{
				"Authorization": {"ApiKey my-valid-key"},
			},
			want:    "my-valid-key",
			wantErr: false,
		},
		"NoAuthHeader": {
			// Missing the Authorization header entirely
			headers: map[string][]string{},
			want:    "",
			wantErr: true,
		},
		"BadFormat": {
			// Header is present but not in "ApiKey {key}" format
			headers: map[string][]string{
				"Authorization": {"Bearer token"},
			},
			want:    "",
			wantErr: true,
		},
	}

	for name, tc := range tests {
		// Use t.Run to execute each test case as an independent subtest
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)

			// 1. Check for expected error
			if (err != nil) != tc.wantErr {
				t.Fatalf("GetAPIKey() error = %v, wantErr %v", err, tc.wantErr)
			}

			// 2. Check for expected result
			if !reflect.DeepEqual(tc.want, got) {
				t.Fatalf("GetAPIKey() got = %v, want %v", got, tc.want)
			}
		})
	}
}
