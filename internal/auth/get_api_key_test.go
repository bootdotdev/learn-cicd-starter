package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		wantKey     string
		wantErr     error
		wantErrText string
	}{
		{
			name:        "Valid ApiKey header",
			headers:     http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantKey:     "my-secret-key",
			wantErr:     nil,
			wantErrText: "",
		},
		{
			name:        "Missing Authorization header",
			headers:     http.Header{},
			wantKey:     "",
			wantErr:     ErrNoAuthHeaderIncluded,
			wantErrText: "",
		},
		{
			name:        "Empty Authorization header value",
			headers:     http.Header{"Authorization": []string{""}},
			wantKey:     "",
			wantErr:     ErrNoAuthHeaderIncluded,
			wantErrText: "",
		},
		{
			name:        "Malformed header - wrong prefix (Bearer instead of ApiKey)",
			headers:     http.Header{"Authorization": []string{"Bearer my-secret-key"}},
			wantKey:     "",
			wantErr:     nil,
			wantErrText: "malformed authorization header",
		},
		{
			name:        "Malformed header - missing key part",
			headers:     http.Header{"Authorization": []string{"ApiKey"}},
			wantKey:     "",
			wantErr:     nil,
			wantErrText: "malformed authorization header",
		},
		{
			name:        "Malformed header - no space separation",
			headers:     http.Header{"Authorization": []string{"ApiKeymy-secret-key"}},
			wantKey:     "",
			wantErr:     nil,
			wantErrText: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, err := GetAPIKey(tt.headers)

			// Check key output
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() gotKey = %v, want %v", gotKey, tt.wantKey)
			}

			// Check sentinel error matching
			if tt.wantErr != nil && !errors.Is(err, tt.wantErr) {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			// Check exact error text for custom error strings
			if tt.wantErrText != "" {
				if err == nil || err.Error() != tt.wantErrText {
					t.Errorf("GetAPIKey() error = %v, wantErrText %v", err, tt.wantErrText)
				}
			}
		})
	}
}
