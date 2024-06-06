package auth_test

import (
	"errors"
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	const authorizationH = "Authorization"
	type test struct {
		name        string
		input       http.Header
		expected    string
		expectedErr error
	}

	tests := []test{
		{
			name: "ValidAPIKey1",
			input: http.Header{
				authorizationH: []string{"ApiKey ValidAPIKey"},
			},
			expected:    "ValidAPIKey",
			expectedErr: nil,
		},
		{
			name: "ValidAPIKey2",
			input: http.Header{
				authorizationH: []string{"ApiKey ThisIAnotherValidKey"},
			},
			expected:    "ThisIAnotherValidKey",
			expectedErr: nil,
		},
		{
			name:        "NoAuthHeaderErr",
			input:       http.Header{},
			expected:    "",
			expectedErr: auth.ErrNoAuthHeaderIncluded,
		},
		{
			name: "WrongAPIKeyErr",
			input: http.Header{
				authorizationH: []string{"api Not a valid key"},
			},
			expected:    "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "WrongAPIKeyLenghtErr",
			input: http.Header{
				authorizationH: []string{"apiKey"},
			},
			expected:    "",
			expectedErr: errors.New("malformed authorization header"),
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			actual, acErr := auth.GetAPIKey(tc.input)
			if tc.expected != actual {
				t.Errorf("Expected differs from the result; \ntest name: %v\nexpected: %v \ninput: %v", tc.name, tc.expected, tc.input)
			}
			if (tc.expectedErr == nil && acErr != nil) || (tc.expectedErr != nil && acErr == nil) {
				t.Errorf("Expected error differs from actual error; \ntest name: %v\nexpected error: %v\nactual error: %v", tc.name, tc.expectedErr, acErr)
			}
			if acErr != nil && acErr.Error() != tc.expectedErr.Error() {
				t.Errorf("Expected error differs from actual error; \ntest name: %v\nexpected error: %v\nactual error: %v", tc.name, tc.expectedErr, acErr)
			}
		})
	}
}
