package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input   http.Header
		wantKey string
		wantErr error
	}{
		"valid header":     {input: http.Header{"Authorization": []string{"ApiKey ChumaAchike"}}, wantKey: "ChumaAchike", wantErr: nil},
		"no header":        {input: nil, wantErr: ErrNoAuthHeaderIncluded, wantKey: ""},
		"malformed header": {input: http.Header{"Authorization": []string{"NoAPIkey hapum"}}, wantErr: ErrMalformedAuthHeader, wantKey: ""},
	}
	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			key, err := GetAPIKey(tc.input)
			if key != tc.wantKey {
				t.Errorf("expected key %q, got %q", tc.wantKey, key)
			}
			if !errors.Is(err, tc.wantErr) {
				t.Errorf("expected error %v, got %v in %s", tc.wantErr, err, name)
			}
		})
	}
}
