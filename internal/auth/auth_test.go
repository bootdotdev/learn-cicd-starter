package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		want    string
		err     error
	}{
		"valid header": {
			headers: http.Header{"Authorization": {"ApiKey abc123"}},
			want:    "abc123",
			err:     nil,
		},
		"missing header": {
			headers: http.Header{},
			want:    "",
			err:     ErrNoAuthHeaderIncluded,
		},
		"malformed header - missing ApiKey": {
			headers: http.Header{"Authorization": {"Bearer abc123"}}, 
			want:    "",
			err:     ErrMalformedAuthHeader,
		},
		"malformed header - missing token": {
			headers: http.Header{"Authorization": {"ApiKey"}},
			want:    "",
			err:     ErrMalformedAuthHeader,
		},
		"malformed header - empty": {
			headers: http.Header{"Authorization": {""}},
			want:    "",
			err:     ErrNoAuthHeaderIncluded,
		},
		"malformed header - extra spaces": {
			headers: http.Header{"Authorization": {"ApiKey  abc123"}},
			want:    "",
			err:     ErrMalformedAuthHeader,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.headers)
			if !reflect.DeepEqual(tc.want, got) || !errors.Is(err, tc.err) {
				t.Fatalf("%s: expected: %v, got: %v, expected err: %v, got err: %v", name, tc.want, got, tc.err, err)
			}
		})
	}
}
