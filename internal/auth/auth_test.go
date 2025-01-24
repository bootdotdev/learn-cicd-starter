package auth

import (
	"errors"
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		authToken string
		want      string
		wantErr   error
	}{
		"simple":                     {"ApiKey test", "test", nil},
		"no Auth header":             {"nothing", "", ErrNoAuthHeaderIncluded},
		"empty auth header":          {"", "", ErrNoAuthHeaderIncluded},
		"does not start with ApiKey": {"nokey test", "", errors.New("malformed authorization header")},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			headers := make(http.Header)

			if tc.authToken != "nothing" {
				headers.Set("Authorization", tc.authToken)
			}
			got, gotErr := GetAPIKey(headers)

			diff := cmp.Diff(tc.want, got)
			if diff != "" {
				t.Fatal(diff)
			}

			if gotErr != nil && gotErr.Error() != tc.wantErr.Error() {
				t.Errorf("GetAPIKey() error = %v, want %v", gotErr, tc.wantErr)
			}
		})
	}
}
