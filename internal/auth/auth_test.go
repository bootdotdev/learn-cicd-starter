package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// A table of test cases, each with a name, input, and expected output.
	cases := []struct {
		name           string
		inputHeader    http.Header
		expectedAPIKey string
		expectedErr    error
	}{
		{
			name: "Valid Auth Header",
			inputHeader: http.Header{
				"Authorization": []string{"ApiKey my-secret-api-key"},
			},
			expectedAPIKey: "my-secret-api-key",
			expectedErr:    nil,
		},
		{
			name:           "No Auth Header",
			inputHeader:    http.Header{},
			expectedAPIKey: "",
			expectedErr:    ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - Wrong Prefix",
			inputHeader: http.Header{
				"Authorization": []string{"Bearer my-secret-api-key"},
			},
			expectedAPIKey: "",
			expectedErr:    errors.New("malformed authorization header"),
		},
		{
			name: "Malformed Header - No Value",
			inputHeader: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedAPIKey: "",
			expectedErr:    errors.New("malformed authorization header"),
		},
	}

	// Loop through all the test cases.
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			// Call the function we are testing.
			apiKey, err := GetAPIKey(tc.inputHeader)

			// Check if the returned API key is what we expected.
			if apiKey != tc.expectedAPIKey {
				t.Errorf("expected api key '%s', got '%s'", tc.expectedAPIKey, apiKey)
			}

			// Check if the returned error is what we expected.
			if tc.expectedErr != nil {
				if err == nil || err.Error() != tc.expectedErr.Error() {
					t.Errorf("expected error '%v', got '%v'", tc.expectedErr, err)
				}
			} else if err != nil {
				t.Errorf("expected no error, got '%v'", err)
			}
		})
	}
}
