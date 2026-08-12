package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		wantKey       string
		wantErrString string
	}{
		{
			name: "Success: Valid ApiKey header",
			headers: http.Header{
				"Authorization": []string{"ApiKey secret-token-123"},
			},
			wantKey: "secret-token-123",
		},
		{
			name:          "Error: No Authorization header",
			headers:       http.Header{},
			wantErrString: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "Error: Malformed header (missing prefix)",
			headers: http.Header{
				"Authorization": []string{"secret-token-123"},
			},
			wantErrString: "malformed authorization header",
		},
		{
			name: "Error: Malformed header (wrong prefix)",
			headers: http.Header{
				"Authorization": []string{"Bearer some-token"},
			},
			wantErrString: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// Check for expected error
			if tt.wantErrString != "" {
				if err == nil {
					t.Errorf("GetAPIKey() error = nil, wantErr %v", tt.wantErrString)
					return
				}
				if err.Error() != tt.wantErrString {
					t.Errorf("GetAPIKey() error = %v, wantErr %v", err.Error(), tt.wantErrString)
					return
				}
				return
			}

			// Check for unexpected error
			if err != nil {
				t.Errorf("GetAPIKey() unexpected error: %v", err)
				return
			}

			// Check returned key
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() = %v, want %v", gotKey, tt.wantKey)
			}
		})
	}
}
