package auth

import (
	"net/http"
	"testing"
)

func TestApiKey(t *testing.T) {
	tests := []struct {
		name      string
		header    http.Header
		want      string
		wantedErr bool
	}{
		{
			name: "valid token",
			header: http.Header{
				"Authorization": []string{"ApiKey validtoken123"},
			},
			want:      "validtoken123",
			wantedErr: false,
		},
		{
			name:      "missing authorization header",
			header:    http.Header{},
			want:      "",
			wantedErr: true,
		},
		{
			name: "missing ApiKey prefix",
			header: http.Header{
				"Authorization": []string{"invalidprefix token123"},
			},
			want:      "",
			wantedErr: true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {

			got, err := GetAPIKey(test.header)

			// Check error behavior
			if (err != nil) != test.wantedErr {
				t.Fatalf("Expected error: %v, got: %v", test.wantedErr, err)
			}

			// Check token value
			if got != test.want {
				t.Fatalf("Expected token: %s, got: %s", test.want, got)
			}
		})
	}
}
