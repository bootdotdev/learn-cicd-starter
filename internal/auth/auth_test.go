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
		expectedErrMsg string
	}{
		{
			name:           "No Authorization header",
			headers:        http.Header{},
			expectedKey:    "",
			expectedErrMsg: "no authorization header included",
		},
		{
			name: "Malformed Authorization header - no space",
			headers: http.Header{
				"Authorization": []string{"ApiKey123456"},
			},
			expectedKey:    "",
			expectedErrMsg: "malformed authorization header",
		},
		{
			name: "Wrong Authorization scheme",
			headers: http.Header{
				"Authorization": []string{"Bearer 123456"},
			},
			expectedKey:    "",
			expectedErrMsg: "malformed authorization header",
		},
		{
			name: "Valid Authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey 123456"},
			},
			expectedKey:    "123456",
			expectedErrMsg: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actualKey, err := GetAPIKey(tt.headers)
	
			if actualKey != tt.expectedKey {
				t.Errorf("expected key %v, got %v", tt.expectedKey, actualKey)
			}
	
			if err != nil && err.Error() != tt.expectedErrMsg {
				t.Errorf("expected error message %v, got %v", tt.expectedErrMsg, err.Error())
			}
	
			if err == nil && tt.expectedErrMsg != "" {
				t.Errorf("expected error message %v, but got no error", tt.expectedErrMsg)
			}
		})
	}
}
