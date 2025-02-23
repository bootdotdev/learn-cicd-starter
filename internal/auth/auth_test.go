package auth

import (
	"fmt"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		key       string
		value     string
		want      string
		expectErr string
	}{
		{
			name: "Valid Header",
			key:  "Authorization",
			// value:     "ApiKey valid_token",
			value:     "Bearer valid_token", // temp break code
			want:      "valid_token",
			expectErr: "not expecting an error",
		},
		{
			name:      "Invalid Header 1",
			key:       "Authorization",
			value:     "invalid_token",
			expectErr: "malformed authorization header",
		},
		{
			name:      "Invalid Header 2",
			key:       "Authorization",
			value:     "Bearer valid_token",
			expectErr: "malformed authorization header",
		},
		{
			name:      "Invalid Key",
			key:       "Invalid",
			value:     "ApiKey valid_token",
			expectErr: "no authorization header included",
		},
		{
			name:      "No Header",
			expectErr: "no authorization header included",
		},
	}

	for i, tt := range tests {
		t.Run(fmt.Sprintf("TestGetAPIKey Case #%v:, Name: %v", i, tt.name), func(t *testing.T) {
			header := http.Header{}
			header.Add(tt.key, tt.value)

			gotAPIKey, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), tt.expectErr) {
					return
				}
				t.Errorf("Unexpected: TestGetAPIKey:%v\n", err)
			}

			if gotAPIKey != tt.want {
				t.Errorf("Unexpected: TestGetAPIKey:%v\n", gotAPIKey)
				return
			}
		})
	}
}
