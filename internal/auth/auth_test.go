package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		want    string
		wantErr string // Use string to check error message content
	}{
		"valid api key": {
			headers: http.Header{"Authorization": []string{"ApiKey my-secret-token"}},
			want:    "my-secret-token",
			wantErr: "",
		},
		"no auth header included": {
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded.Error(),
		},
		"malformed authorization header - wrong prefix": {
			headers: http.Header{"Authorization": []string{"Bearer my-token"}},
			want:    "",
			wantErr: "malformed authorization header",
		},
		"malformed authorization header - missing key": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			want:    "",
			wantErr: "malformed authorization header",
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)

			// Check the returned string value
			if got != tc.want {
				t.Errorf("expected: %v, got: %v", tc.want, got)
			}

			// Check the error behavior
			if err != nil {
				if err.Error() != tc.wantErr {
					t.Errorf("expected error: %v, got: %v", tc.wantErr, err.Error())
				}
			} else if tc.wantErr != "" {
				t.Errorf("expected error: %v, got: nil", tc.wantErr)
			}
		})
	}
}
