package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Define a slice of test structures with various input scenarios
	tests := []struct {
		name           string      // Name of the test case
		headers        http.Header // Input HTTP headers
		expectedAPIKey string      // Expected API Key on success
		expectedError  error       // Expected error on failure
	}{
		{
			name: "Success - Correct ApiKey header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-api-key"},
			},
			expectedAPIKey: "my-secret-api-key",
			expectedError:  nil,
		},
		{
			name:           "Failure - No Authorization header",
			headers:        http.Header{}, // Empty headers
			expectedAPIKey: "",
			expectedError:  ErrNoAuthHeaderIncluded, // Matches the specific error var
		},
		{
			name: "Failure - Header present but empty value",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedAPIKey: "",
			// This case triggers the malformed error due to the Split logic
			expectedError: errors.New("malformed authorization header"),
		},
		{
			name: "Failure - Malformed header - missing space/key part",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name: "Failure - Malformed header - only value present",
			headers: http.Header{
				"Authorization": []string{"only-a-key-no-prefix"},
			},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name: "Failure - Wrong authorization scheme (e.g., Bearer)",
			headers: http.Header{
				"Authorization": []string{"Bearer some-jwt-token"},
			},
			expectedAPIKey: "",
			expectedError:  errors.New("malformed authorization header"),
		},
		{
			name: "Failure - Extra spaces in header value (library handles trim implicitly)",
			headers: http.Header{
				"Authorization": []string{"  ApiKey  my-key-with-spaces  "},
			},
			// Note: http.Header.Get() trims leading/trailing whitespace automatically.
			// The Split function then handles internal spacing appropriately for this structure.
			expectedAPIKey: "my-key-with-spaces",
			expectedError:  nil,
		},
	}

	// Iterate through all defined test cases
	for _, tt := range tests {
		// Run each case as a subtest
		t.Run(tt.name, func(t *testing.T) {
			gotAPIKey, gotError := GetAPIKey(tt.headers)

			// Check for API Key match
			if gotAPIKey != tt.expectedAPIKey {
				t.Errorf("GetAPIKey() gotAPIKey = %v, want %v", gotAPIKey, tt.expectedAPIKey)
			}

			// Check for error match
			// Using Error() string comparison is generally acceptable for expected static errors in simple functions,
			// but for specific known errors like ErrNoAuthHeaderIncluded, an `errors.Is` check is better practice.
			if (gotError != nil && tt.expectedError != nil) && gotError.Error() != tt.expectedError.Error() {
				t.Errorf("GetAPIKey() gotError = %v, want %v", gotError, tt.expectedError)
			} else if (gotError != nil) != (tt.expectedError != nil) {
				// Checks if one is nil and the other is not
				t.Errorf("GetAPIKey() gotError presence mismatch: got %v, want %v", gotError, tt.expectedError)
			}
		})
	}
}
