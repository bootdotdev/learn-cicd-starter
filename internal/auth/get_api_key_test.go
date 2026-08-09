package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name   string
		header http.Header
		result string
		error  error
	}{
		{
			name: "missing authorization",
			header: http.Header{
				"Authorization": []string{},
			},
			result: "",
			error:  ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed authorization header",
			header: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			result: "",
			error:  ErrMalformedAuthorizationHeader,
		},
		{
			name: "valid headers",
			header: http.Header{
				"Authorization": []string{
					"ApiKey test-key",
				},
			},
			result: "test-key",
			error:  nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			result, err := GetAPIKey(tt.header)
			if result != tt.result || err != tt.error {
				t.Errorf("got %v, %v. want %v, %v", result, err, tt.result, tt.error)
			}
		})
	}
}
