package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input   http.Header
		want    string
		wantErr error
	}{
		"simple": {
			http.Header{"Authorization": []string{"ApiKey hello"}},
			"hell",
			nil,
		},
		"no header": {
			http.Header{},
			"",
			errors.New("no authorization header included"),
		},
		"empty header value": {
			http.Header{"Authorization": []string{}},
			"",
			ErrNoAuthHeaderIncluded,
		},
		"wrong prefix": {
			http.Header{"Authorization": []string{"WrongKey goodbye"}},
			"",
			errors.New("malformed authorization header"),
		},
		"weird long word": {
			http.Header{"Authorization": []string{"ApiKey LKJ245j(/&)(&ghjk**::;\\/)"}},
			"LKJ245j(/&)(&ghjk**::;\\/)",
			nil,
		},
	}
	for name, tt := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tt.input)
			if got != tt.want {
				t.Errorf("Got: %s, wanted %s. Err got: %v, err wanted %v", got, tt.want, err, tt.wantErr)
			}

		})
	}
}

/*
// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}
	splitAuth := strings.Split(authHeader, " ")
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", errors.New("malformed authorization header")
	}

	return splitAuth[1], nil
}
*/
