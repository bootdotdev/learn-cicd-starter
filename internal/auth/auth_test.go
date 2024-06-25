package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name         string
		headers      http.Header
		want         string
		expectErr    bool
		expectErrMsg string
	}{
		{
			name:      "Valid API Key",
			headers:   http.Header{"Authorization": {"ApiKey abcdef12345"}},
			want:      "abcdef12345",
			expectErr: false,
		},
		{
			name:         "No Authorization Header",
			headers:      http.Header{},
			want:         "",
			expectErr:    true,
			expectErrMsg: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name:         "Malformed Authorization Header - Missing ApiKey",
			headers:      http.Header{"Authorization": {"Bearer abcdef12345"}},
			want:         "",
			expectErr:    true,
			expectErrMsg: "malformed authorization header",
		},
		{
			name:         "Malformed Authorization Header - Missing Token",
			headers:      http.Header{"Authorization": {"ApiKey"}},
			want:         "",
			expectErr:    true,
			expectErrMsg: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.expectErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.expectErr)
				return
			}
			if err != nil && err.Error() != tt.expectErrMsg {
				t.Errorf("GetAPIKey() error = %v, wantErrMsg %v", err, tt.expectErrMsg)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
