package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headerValue    string
		expectedKey    string
		expectedResult bool
	}{
		{
			name:           "equal APIkey",
			headerValue:    "ApiKey GoodAPIKey",
			expectedKey:    "GoodAPIKey",
			expectedResult: true,
		},
		{
			name:           "not equal APIKey",
			headerValue:    "ApiKey BadAPIKey",
			expectedKey:    "GoodAPIKey",
			expectedResult: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			header := make(http.Header)
			if tt.headerValue != "" {
				header.Add("Authorization", tt.headerValue)
			}

			testGetAPIKey, err := GetAPIKey(header)
			if err != nil {
				t.Fatalf("Got an error getting the API key: %v", err)
			}

			testResult := tt.expectedKey == testGetAPIKey

			if testResult != tt.expectedResult {
				t.Fail()
			}
		})
	}

}
