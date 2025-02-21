package auth

import (
	"errors"
	"net/http"
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name          string
		authorization string
		expectedKey   string
		expectedError error
	}{
		{
			name:          "No Authorization header",
			authorization: "",
			expectedKey:   "",
			expectedError: ErrNoAuthHeaderIncluded,
		},
		{
			name:          "Malformed Header - No Token",
			authorization: "ApiKey",
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Malformed Header - Wrong Prefix",
			authorization: "Bearer",
			expectedKey:   "",
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name:          "Valid Authorization Header",
			authorization: "ApiKey some_valid_token",
			expectedKey:   "some_valid_token",
			expectedError: nil,
		},
		{
			name:          "Authorization Header With Extra Spaces",
			authorization: "ApiKey  some_invalid_token",
			expectedKey:   "",
			expectedError: nil,
		},
	}

	for _, tableTest := range tests {
		t.Run(tableTest.name, func(t *testing.T) {
			headers := http.Header{}
			if tableTest.authorization != "" {
				headers.Set("Authorization", tableTest.authorization)
			}

			key, err := GetAPIKey(headers)
			assert.Equal(t, tableTest.expectedKey, key)
			if tableTest.expectedError != nil {
				assert.EqualError(t, err, tableTest.expectedError.Error())
			} else {
				assert.NoError(t, err)
			}
		})
	}
}
