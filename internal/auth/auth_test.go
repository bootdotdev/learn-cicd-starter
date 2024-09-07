package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestApiKey(t *testing.T) {
	tests := map[string]struct {
		header        http.Header
		ExpectedToken string
		ExpectedError error
	}{
		"No Auth Header": {
			header:        http.Header{},
			ExpectedToken: "",
			ExpectedError: ErrNoAuthHeaderIncluded,
		},
		"Malformed Auth Header": {
			header:        http.Header{"Authorization": []string{"Bearer some-token"}},
			ExpectedToken: "",
			ExpectedError: errors.New("malformed authorization header"),
		},
		"Correct Auth Header": {
			header:        http.Header{"Authorization": []string{"ApiKey my-api-key"}},
			ExpectedToken: "my-api-key",
			ExpectedError: nil,
		},
		"Auth Header without Key": {
			header:        http.Header{"Authorization": []string{"ApiKey"}},
			ExpectedToken: "",
			ExpectedError: errors.New("malformed authorization header"),
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tc.header)

			if apiKey != tc.ExpectedToken {
				t.Errorf("expected %v got %v", tc.ExpectedToken, apiKey)
			}

			if err != nil && tc.ExpectedError != nil && err.Error() != tc.ExpectedError.Error() {
				t.Errorf("Expected error %v got %v", tc.ExpectedError, err)
			} else if err == nil && tc.ExpectedError != nil {
				t.Errorf("expected error %v got nil", tc.ExpectedError)
			}
		})
	}
}
