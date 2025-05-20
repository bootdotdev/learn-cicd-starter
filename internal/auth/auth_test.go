package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type testCase struct {
		name         string
		header       http.Header
		expectedKey  string
		expectError  error
		errorMessage string
	}

	runCases := []testCase{
		{
			name:         "No Authorization Header",
			header:       http.Header{},
			expectedKey:  "",
			expectError:  ErrNoAuthHeaderIncluded,
			errorMessage: "no authorization header included",
		},
		{
			name: "Malformed Header - Wrong Prefix",
			header: http.Header{
				"Authorization": []string{"Bearer somekey"},
			},
			expectedKey:  "",
			expectError:  errors.New("malformed authorization header"),
			errorMessage: "malformed authorization header",
		},
		{
			name: "Valid API Key Header",
			header: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			expectedKey:  "abc123",
			expectError:  nil,
			errorMessage: "",
		},
	}

	for _, test := range runCases {
		t.Run(test.name, func(t *testing.T) {
			key, err := GetAPIKey(test.header)

			if key != test.expectedKey {
				t.Errorf("expected key %q, got %q", test.expectedKey, key)
			}

			if err != nil {
				if test.expectError == nil {
					t.Errorf("expected no error, got %v", err)
				} else if err.Error() != test.errorMessage {
					t.Errorf("expected error message %q, got %q", test.errorMessage, err.Error())
				}
			} else if test.expectError != nil {
				t.Errorf("expected error %v, got nil", test.expectError)
			}
		})
	}
}
