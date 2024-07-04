package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	testcases := []struct {
		name      string
		headers   http.Header
		want      string
		wantError bool
	}{
		{
			name: "Happy path",
			headers: buildHeaders(t, map[string]string{
				"Authorization": "ApiKey foobar",
			}),
			want:      "foobar",
			wantError: false,
		},
		{
			name:      "Missing auth header",
			headers:   buildHeaders(t, map[string]string{}),
			wantError: true,
		},
		{
			name: "Malformed auth header - missing value",
			headers: buildHeaders(t, map[string]string{
				"Authorization": "ApiKey",
			}),
			wantError: true,
		},
		{
			name: "Malformed auth header - not ApiKey",
			headers: buildHeaders(t, map[string]string{
				"Authorization": "Key foobar",
			}),
			wantError: true,
		},
	}

	for _, tc := range testcases {
		t.Run(tc.name, func(t *testing.T) {
			apiKey, err := auth.GetAPIKey(tc.headers)
			if err != nil {
				if !tc.wantError {
					t.Fatalf("expected no error, got %v", err)
				}
			}

			if apiKey != tc.want {
				t.Errorf("apikey: got %s, want %s", apiKey, tc.want)
			}
		})
	}
}

func buildHeaders(t *testing.T, m map[string]string) http.Header {
	t.Helper()

	headers := http.Header{}

	for header, value := range m {
		headers.Set(header, value)
	}

	return headers
}
