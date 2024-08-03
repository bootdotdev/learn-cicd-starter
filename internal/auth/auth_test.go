package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		got  http.Header
		want string
		err  error
	}{
		"Ideal case":                    {http.Header{"Authorization": []string{"ApiKey 1234"}}, "1234", nil},
		"Auth header not APIKey":        {http.Header{"Authorization": []string{"somethingelse 1234"}}, "", errors.New("malformed authorization header")},
		"Auth header missing APIKey":    {http.Header{"Authorization": []string{"1234"}}, "", errors.New("malformed authorization header")},
		"Wrong auth header":             {http.Header{"NotAuthorization": []string{""}}, "", ErrNoAuthHeaderIncluded},
		"Empty header":                  {http.Header{}, "", ErrNoAuthHeaderIncluded},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.got)
			if err != nil && err.Error() != tc.err.Error() {
				t.Fatalf("%v: expected error: %v, got: %v", name, tc.err, err)
			}
			if err == nil && tc.err != nil {
				t.Fatalf("%v: expected error: %v, got: nil", name, tc.err)
			}
			if !reflect.DeepEqual(tc.want, got) {
				t.Errorf("%v: want: %v, got: %v", name, tc.want, got)
			}
		})
	}
}