package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headerValue string
		wantKey     string
		wantErr     bool
	}{
		"valid key":     {headerValue: "ApiKey abc123", wantKey: "abc123", wantErr: false},
		"no header":     {headerValue: "", wantKey: "", wantErr: true},
		"wrong scheme":  {headerValue: "Bearer abc123", wantKey: "", wantErr: true},
		"missing value": {headerValue: "ApiKey", wantKey: "", wantErr: true},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			headers := http.Header{}
			if tc.headerValue != "" {
				headers.Set("Authorization", tc.headerValue)
			}

			gotKey, err := GetAPIKey(headers)

			if (err != nil) != tc.wantErr {
				t.Errorf("wantErr %v, got err %v", tc.wantErr, err)
			}
			if gotKey != tc.wantKey {
				t.Errorf("want key %q, got %q", tc.wantKey, gotKey)
			}
		})
	}
}
