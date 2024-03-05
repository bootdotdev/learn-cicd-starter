package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		headers       http.Header
		expectedKey   string
		expectedError error
	}{
		{
			name: "Valid Authorization Header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-api-key"},
			},
			expectedKey:   "my-api-key",
			expectedError: nil,
		},
		{
			name: "No Authorization Header",
			headers: http.Header{
				"X-Some-Other-Header": []string{"some-value"},
			},
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Authorization Header",
			headers: http.Header{
				"Authorization": []string{"SomeOtherScheme my-api-key"},
			},
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.headers)

			if key != test.expectedKey {
				t.Errorf("got %s, want %s", key, test.expectedKey)
			}

			if (err == nil && test.expectedError != nil) || (err != nil && test.expectedError == nil) || (err != nil && err.Error() != test.expectedError.Error()) {
				t.Errorf("got error %v, want error %v", err, test.expectedError)
			}
		})
	}
}
