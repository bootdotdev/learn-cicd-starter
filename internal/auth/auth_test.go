package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		name          string
		input         http.Header
		expected      string
		expectedError string
	}

	tests := []test{
		{"No auth header", http.Header{}, "", "no authorization header included"},
		{"No ApiKey in auth header", http.Header{"Authorization": []string{"Bearer fakekey"}}, "", "malformed authorization header"},
		{"Less than 2 keys", http.Header{"Authorization": []string{"ApiKey"}}, "", "malformed authorization header"},
		{"Correct ApiKey", http.Header{"Authorization": []string{"ApiKey fakekey"}}, "fakekey", ""},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)
			switch {
			case tc.expectedError != "":
				if err == nil || (err != nil && err.Error() != tc.expectedError) {
					t.Fatalf("GetAPIKey(%q) expected error: %v, got: %v", tc.input, tc.expectedError, err)
				}
			case err != nil && err.Error() != "":
				t.Fatalf("GetAPIKey(%q) returned unexpected error: %v, want: %q", tc.input, err, tc.expected)
			case got != tc.expected:
				t.Fatalf("GetAPIKey(%q)\n got: %v\nwant: %v", tc.input, got, tc.expected)
			}
		})
	}
}
