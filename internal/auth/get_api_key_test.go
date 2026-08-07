package auth

import (
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
			name:    "valid api key",
			headers: http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantKey: "my-secret-key",
		},
		{
			name:    "extra whitespace separated parts are ignored",
			headers: http.Header{"Authorization": []string{"ApiKey my-secret-key trailing"}},
			wantKey: "my-secret-key",
		},
		{
			name:    "no headers at all",
			headers: http.Header{},
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "empty authorization header",
			headers: http.Header{"Authorization": []string{""}},
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:        "missing key after prefix",
			headers:     http.Header{"Authorization": []string{"ApiKey"}},
			wantErrText: "malformed authorization header",
		},
		{
			name:        "wrong scheme",
			headers:     http.Header{"Authorization": []string{"Bearer my-secret-key"}},
			wantErrText: "malformed authorization header",
		},
		{
			name:        "scheme is case sensitive",
			headers:     http.Header{"Authorization": []string{"apikey my-secret-key"}},
			wantErrText: "malformed authorization header",
		},
		{
			name:    "empty key is returned as-is",
			headers: http.Header{"Authorization": []string{"ApiKey "}},
			wantKey: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			switch {
			case tt.wantErr != nil:
				if err != tt.wantErr {
					t.Fatalf("GetAPIKey() error = %v, want %v", err, tt.wantErr)
				}
			case tt.wantErrText != "":
				if err == nil {
					t.Fatalf("GetAPIKey() error = nil, want %q", tt.wantErrText)
				}
				if err.Error() != tt.wantErrText {
					t.Fatalf("GetAPIKey() error = %q, want %q", err.Error(), tt.wantErrText)
				}
			default:
				if err != nil {
					t.Fatalf("GetAPIKey() unexpected error = %v", err)
				}
			}

			if key != tt.wantKey {
				t.Errorf("GetAPIKey() key = %q, want %q", key, tt.wantKey)
			}
		})
	}
}
