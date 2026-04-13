package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		want    string
		wantErr bool
	}{
		"valid_api_key": {
			headers: http.Header{"Authorization": []string{"ApiKey some-secret-key-123"}},
			want:    "some-secret-key-123",
			wantErr: false,
		},
		"missing_auth_header": {
			headers: http.Header{},
			want:    "",
			wantErr: true,
		},
		"malformed_header_missing_apikey_prefix": {
			headers: http.Header{"Authorization": []string{"Bearer some-token"}},
			want:    "",
			wantErr: true,
		},
		"malformed_header_too_short": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			want:    "",
			wantErr: true,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)

			// Check if we expected an error
			if (err != nil) != tc.wantErr {
				t.Fatalf("GetAPIKey() error = %v, wantErr %v", err, tc.wantErr)
			}

			// Check if the result matches our expectation
			if !reflect.DeepEqual(got, tc.want) {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tc.want)
			}
		})
	}
}
