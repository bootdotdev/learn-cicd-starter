package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantKey    string
		wantErr    error
		wantErrMsg string
	}{
		{
			name:    "valid API key",
			headers: http.Header{"Authorization": []string{"ApiKey my-secret-key"}},
			wantKey: "my-secret-key",
			wantErr: nil,
		},
		{
			name:    "no authorization header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:       "malformed header - wrong prefix",
			headers:    http.Header{"Authorization": []string{"Bearer my-token"}},
			wantKey:    "",
			wantErrMsg: "malformed authorization header",
		},
		{
			name:       "malformed header - no space",
			headers:    http.Header{"Authorization": []string{"ApiKey"}},
			wantKey:    "",
			wantErrMsg: "malformed authorization header",
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tt.headers)
			if gotKey != tt.wantKey {
				t.Errorf("GetAPIKey() key = %q, want %q", gotKey, tt.wantKey)
			}
			if tt.wantErr != nil {
				if gotErr != tt.wantErr {
					t.Errorf("GetAPIKey() error = %v, want %v", gotErr, tt.wantErr)
				}
			} else if tt.wantErrMsg != "" {
				if gotErr == nil || gotErr.Error() != tt.wantErrMsg {
					t.Errorf("GetAPIKey() error = %v, want error with message %q", gotErr, tt.wantErrMsg)
				}
			} else if gotErr != nil {
				t.Errorf("GetAPIKey() unexpected error = %v", gotErr)
			}
		})
	}
}
