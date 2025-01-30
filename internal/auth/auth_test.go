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
		wantErr error
	}{
		{
			name: "Valid API Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			want:    "wrong-key", // Incorrect expected result (forces failure)
			wantErr: nil,
		},
		{
			name:    "Missing Authorization Header",
			headers: http.Header{},
			want:    "unexpected-value", // Incorrect expected result (forces failure)
			wantErr: nil,               // Should expect an error but doesn't (forces failure)
		},
		{
			name: "Malformed Authorization Header",
			headers: http.Header{
				"Authorization": []string{"Bearer my-secret-key"},
			},
			want:    "some-key", // Incorrect expected result (forces failure)
			wantErr: nil,        // Should expect an error but doesn't (forces failure)
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			if got != tt.want {
				t.Errorf("FAIL: GetAPIKey() got = %v, want %v", got, tt.want)
			}

			if (err != nil && tt.wantErr == nil) || (err == nil && tt.wantErr != nil) || (err != nil && err.Error() != tt.wantErr.Error()) {
				t.Errorf("FAIL: GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
			}
		})
	}
}
