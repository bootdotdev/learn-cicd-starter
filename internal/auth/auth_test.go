package auth

import (
	"testing"
	"net/http"
)

func TestGetAPIKey (t *testing.T) {
	tests := []struct {
		name	string
		headers	http.Header
		expectedKey string
		expectError bool
	}{
		{
			name: "Valid API key in header",
			headers: http.Header{"Authorization": []string{"ApiKey valid-key-123"}},
			expectedKey: "valid-key-123",
			expectError: false,
		},
		{
			name: "Missing Authorization header",
			headers: http.Header{},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "Invalid header",
			headers: http.Header{"Authorization": []string{"Api Key valid-key-123"}},
                        expectedKey: "",
                        expectError: true,
		},
	}
		        
	for _, tc := range tests {
        	t.Run(tc.name, func(t *testing.T) {
            		key, err := GetAPIKey(tc.headers)
            
            // Check if error was expected
            		if tc.expectError && err == nil {
                		t.Errorf("Expected error but got none")
            		}
            		if !tc.expectError && err != nil {
                		t.Errorf("Did not expect error but got: %v", err)
            		}
            
            // If no error was expected, check the key
            		if !tc.expectError && key != tc.expectedKey {
                		t.Errorf("Expected key %q, got %q", tc.expectedKey, key)
            		}
       	 	})
    	}
}

