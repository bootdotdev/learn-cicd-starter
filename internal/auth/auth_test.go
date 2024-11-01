package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		name      string
		headers   http.Header
		wantToken string
		wantErr   bool
	}{
		"Valid ApiKey": {
			headers: http.Header{
				"Authorization": []string{"ApiKey valid_token"},
			},
			wantToken: "valid_token",
			wantErr:   false,
		},
		"Missing Authorization header": {
			headers:   http.Header{},
			wantToken: "",
			wantErr:   true,
		},
		"Malformed Authorization header": {
			headers: http.Header{
				"Authorization": []string{"InvalidBearer token"},
			},
			wantToken: "",
			wantErr:   true,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)
			if (err != nil) != tc.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tc.wantErr)
				return
			}
			if got != tc.wantToken {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tc.wantToken)
			}
		})
	}
}
