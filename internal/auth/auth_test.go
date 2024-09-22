package auth

import (
	"errors"
	"net/http"
	"testing"
)

var (
	ErrMalformedHeader = errors.New("malformed authorization header")
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		input     http.Header
		wantKey   string
		wantErr   error
		wantError string
	}{
		{
			name:    "happy-flow",
			input:   http.Header{"Authorization": []string{"ApiKey valid_api_key"}},
			wantKey: "valid_api_key",
			wantErr: nil,
		},
		{
			name:      "missing-header",
			input:     http.Header{},
			wantErr:   ErrNoAuthHeaderIncluded,
			wantError: "no authorization header included",
		},
		{
			name:      "malformed-header-wrong-prefix",
			input:     http.Header{"Authorization": []string{"NotApiKey invalid_api_key"}},
			wantErr:   ErrMalformedHeader,
			wantError: "malformed authorization header",
		},
		{
			name:    "malformed-header-empty-key",
			input:   http.Header{"Authorization": []string{"ApiKey "}},
			wantErr: nil,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.input)

			if gotErr != nil {
				if gotErr.Error() != tc.wantError {
					t.Errorf("Expected errorL %v, got: %v", tc.wantError, gotErr.Error())
					return
				}
			} else if tc.wantErr != nil {
				t.Errorf("Expected error, got none")
				return
			}
			if gotKey != tc.wantKey {
				t.Errorf("Expected key: %s, got: %s", tc.wantKey, gotKey)
			}
		})
	}
}
