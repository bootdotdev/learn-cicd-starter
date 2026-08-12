package auth_test

import (
	"errors"
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestApiKey(t *testing.T){
	tests := []struct{
		name string
		headers http.Header
		expectedKey string
		expectedError error
	}{
		{
			name: "successfull extraction with ApiKey scheme",
			headers: http.Header{
				"Authorization":[]string{"ApiKey secret-token-123"},
			},
			expectedKey: "secret-token-123",
			expectedError: nil,
		},
		{
			name: "malformed header - wrong scheme prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer secret-token-123"},
			},
			expectedKey: "",
			expectedError: errors.New("malformed authorization header"),
		},
	}
	for _,tc := range tests{
		t.Run(tc.name, func (t * testing.T)  {
			key, err := auth.GetAPIKey(tc.headers)

			if tc.expectedError != nil {
				if err == nil {
					t.Fatalf("expected error %v, got nil", tc.expectedError)
				}
				
				// Use errors.Is for sentinel errors, or string comparison for generic errors
				if errors.Is(tc.expectedError, auth.ErrNoAuthHeaderIncluded) {
					if !errors.Is(err, auth.ErrNoAuthHeaderIncluded) {
						t.Errorf("expected sentinel error %v, got %v", tc.expectedError, err)
					}
				} else if err.Error() != tc.expectedError.Error() {
					t.Errorf("expected error message %q, got %q", tc.expectedError.Error(), err.Error())
				}
			} else {
				if err != nil {
					t.Fatalf("unexpected error: %v", err)
				}
			}

			// 2. Handle key assertions
			if key != tc.expectedKey {
				t.Errorf("expected key %q, got %q", tc.expectedKey, key)
			}
		})
	}
}