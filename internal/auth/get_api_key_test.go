package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestAPIKey(t *testing.T) {
	// 1. Define the 'table' of test cases
	tests := []struct {
		name          string
		inputHeader   http.Header
		expectedKey   string
		expectedError string
	}{
		{name: "valid api key",
			inputHeader: http.Header{
				"Authorization": []string{"ApiKey secret-sauce"},
			},
			expectedKey:   "secret-sauce",
			expectedError: "",
		},
	}

	// 2. Iterate over the table
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.inputHeader)
			if err != nil {
				if !strings.Contains(err.Error(), tt.expectedError) {
					t.Errorf("expected error containing %s, got %v", tt.expectedError, err)
				}
				return
			}
			if apiKey != tt.expectedKey {
				t.Errorf("expected %s, got %s", tt.expectedKey, apiKey)
			}
		})
	}
}
