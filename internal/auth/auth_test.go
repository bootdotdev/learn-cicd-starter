package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name           string
		headers        http.Header
		expectedKey    string
		expectedError  string
		shouldError    bool
	}{
		{
			name: "valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-api-key"},
			},
			expectedKey: "my-secret-api-key",
			shouldError: false,
		},
		{
			name:          "missing authorization header",
			headers:       http.Header{},
			expectedError: "no authorization header included",
			shouldError:   true,
		},
		{
			name: "empty authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			expectedError: "no authorization header included",
			shouldError:   true,
		},
		{
			name: "malformed header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer my-token"},
			},
			expectedError: "malformed authorization header",
			shouldError:   true,
		},
		{
			name: "malformed header - missing key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			expectedError: "malformed authorization header",
			shouldError:   true,
		},
		{
			name: "malformed header - empty key",
			headers: http.Header{
				"Authorization": []string{"ApiKey "},
			},
			expectedKey: "",
			shouldError: false,
		},
		{
			name: "malformed header - no space",
			headers: http.Header{
				"Authorization": []string{"ApiKeymy-key"},
			},
			expectedError: "malformed authorization header",
			shouldError:   true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if tt.shouldError {
				if err == nil {
					t.Errorf("expected error but got none")
					return
				}
				if err.Error() != tt.expectedError {
					t.Errorf("expected error %q, got %q", tt.expectedError, err.Error())
				}
			} else {
				if err != nil {
					t.Errorf("expected no error but got: %v", err)
					return
				}
				if key != tt.expectedKey {
					t.Errorf("expected key %q, got %q", tt.expectedKey, key)
				}
			}
		})
	}
}

func TestGetAPIKey_ErrNoAuthHeaderIncluded(t *testing.T) {
	headers := http.Header{}
	_, err := GetAPIKey(headers)
	
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("expected ErrNoAuthHeaderIncluded, got %v", err)
	}
}
