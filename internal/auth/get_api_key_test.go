package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		wantAPI   string
		wantErr   bool
		errMsg    string
	}{
		{
			name:    "valid api key",
			headers: http.Header{"Authorization": []string{"ApiKey abc123"}},
			wantAPI: "abc123",
			wantErr: false,
		},
		{
			name:    "empty authorization header",
			headers: http.Header{},
			wantErr: true,
			errMsg:  ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name:    "malformed header missing value",
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantErr: true,
			errMsg:    "malformed authorization header",
		},
		{
			name:    "malformed header wrong prefix",
			headers: http.Header{"Authorization": []string{"Bearer abc123"}},
			wantErr: true,
			errMsg:    "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			api, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if tt.wantErr && err.Error() != tt.errMsg {
				t.Errorf("GetAPIKey() error = %v, wantErrMsg %v", err, tt.errMsg)
				return
			}
			if !tt.wantErr && api != tt.wantAPI {
				t.Errorf("GetAPIKey() = %v, want %v", api, tt.wantAPI)
			}
		})
	}
}
