package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		inputKey   string
		inputValue string
		wantedStr  string
		wantedErr  error
	}{
		"no header key":       {wantedErr: ErrNoAuthHeaderIncluded},
		"no header value":     {inputKey: "Authorization", wantedErr: ErrNoAuthHeaderIncluded},
		"extra data front":    {inputKey: "Authorization", inputValue: "Key: ApiKey 0123", wantedErr: errors.New("malformed authorization header")},
		"extra data back":     {inputKey: "Authorization", inputValue: "ApiKey 0123 User ;DROP TABLE(users);", wantedStr: "0123"},
		"incorrect signifier": {inputKey: "Authorization", inputValue: "Key: 4321", wantedErr: errors.New("malformed authorization header")},
		"sunshine":            {inputKey: "Authorization", inputValue: "ApiKey abcd", wantedStr: "abcd"},
	}

	for name, test := range tests {
		t.Run(name, func(t *testing.T) {
			h := make(http.Header)
			h.Add(test.inputKey, test.inputValue)

			gotStr, gotErr := GetAPIKey(h)
			if gotErr == nil && gotErr.Error() != test.wantedErr.Error() {
				t.Errorf("eERROR\tTestGetAPIKey: %v\n", gotErr)
				return
			}
			if gotStr != test.wantedStr {
				t.Errorf("vERROR\tTestGetAPIKey: %s\n", gotStr)
				return
			}
		})
	}
}
