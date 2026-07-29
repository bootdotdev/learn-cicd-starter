package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr bool
	}{
		{
			name:    "Valid API Key",
			headers: http.Header{"Authorization": []string{"ApiKey my-super-secret-key"}},
			want:    "my-super-secret-key",
			wantErr: false,
		},
		{
			name:    "Missing Header",
			headers: http.Header{},
			want:    "",
			wantErr: true,
		},
		{
			name:    "Wrong Authorization Type",
			headers: http.Header{"Authorization": []string{"Bearer my-super-secret-key"}},
			want:    "",
			wantErr: true,
		},
		{
			name:    "Malformed Header (No key provided)",
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			want:    "",
			wantErr: true,
		},
	}

	// 2. Loop through the test cases
	for _, tc := range tests {
		// t.Run creates a sub-test for each case, making output much easier to read
		t.Run(tc.name, func(t *testing.T) {

			got, err := GetAPIKey(tc.headers)

			// Check if the error status matches our expectation
			if (err != nil) != tc.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tc.wantErr)
				return // stop testing this specific case if the error state is wrong
			}

			// Check if the returned string matches our expectation
			if got != tc.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tc.want)
			}
		})
	}
}
