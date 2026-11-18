package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		header    string
		want      string
		shouldErr bool
	}{
		{
			name:      "valid api key",
			header:    "ApiKey abc123",
			want:      "abc123",
			shouldErr: false,
		},
		{
			name:      "missing authorization header",
			header:    "",
			want:      "",
			shouldErr: true,
		},
		{
			name:      "wrong auth type",
			header:    "Bearer abc123",
			want:      "",
			shouldErr: true,
		},
		{
			name:      "malformed header missing key",
			header:    "ApiKey",
			want:      "",
			shouldErr: true,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			headers := http.Header{}

			if tc.header != "" {
				headers.Set("Authorization", tc.header)
			}

			got, err := GetAPIKey(headers)

			if (err != nil) != tc.shouldErr {
				t.Fatalf(
					"expected error=%v, got error=%v",
					tc.shouldErr,
					err != nil,
				)
			}

			if got != tc.want {
				t.Fatalf(
					"expected key=%q, got=%q",
					tc.want,
					got,
				)
			}
		})
	}
}
