package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name     string
		headers  http.Header
		expected string
		err      error
	}{
		{
			name:     "no auth header",
			headers:  http.Header{},
			expected: "",
			err:      ErrNoAuthHeaderIncluded,
		},
		{
			name:     "malformed auth header",
			headers:  http.Header{"Authorization": []string{"Bearer"}},
			expected: "",
			err:      errors.New("malformed authorization header"),
		},
		{
			name:     "correct auth header",
			headers:  http.Header{"Authorization": []string{"ApiKey 1234"}},
			expected: "1234",
			err:      nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			apiKey, err := GetAPIKey(tt.headers)
			if err != nil && err.Error() != tt.err.Error() {
				t.Errorf("expected error %v, got %v", tt.err, err)
			}
			if apiKey != tt.expected {
				t.Errorf("expected %s, got %s", tt.expected, apiKey)
			}
		})
	}
}
