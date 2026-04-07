package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		want    string
		wantErr string
	}{
		"valid api key": {
			headers: http.Header{"Authorization": []string{"ApiKey secret-123"}},
			want:    "secret-123",
		},
		"missing auth header": {
			headers: http.Header{},
			wantErr: ErrNoAuthHeaderIncluded.Error(),
		},
		"wrong prefix": {
			headers: http.Header{"Authorization": []string{"Bearer secret-123"}},
			wantErr: "malformed authorization header",
		},
		"missing token value": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantErr: "malformed authorization header",
		},
		"multiple spaces": {
			headers: http.Header{"Authorization": []string{"ApiKey  too-many-spaces"}},
			// strings.Split will result in splitAuth[1] being an empty string ""
			want: "",
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)

			// Check error case
			if tc.wantErr != "" {
				if err == nil {
					t.Fatal("expected error but got nil")
				}
				if err.Error() != tc.wantErr {
					t.Fatalf("expected error %q, got %q", tc.wantErr, err.Error())
				}
				return
			}

			// Check success case
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tc.want {
				t.Errorf("expected %q, got %q", tc.want, got)
			}
		})
	}
}
