package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		header    http.Header
		want      string
		wantError bool
	}{
		{
			name: "valid API key",
			header: http.Header{
				"Authorization": []string{"ApiKey test-api-key"},
			},
			want:      "test-api-key",
			wantError: false,
		},
		{
			name:      "missing authorization header",
			header:    http.Header{},
			want:      "",
			wantError: true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got, err := GetAPIKey(test.header)

			if test.wantError {
				if err == nil {
					t.Fatal("expected an error but got none")
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if got != test.want {
				t.Errorf("expected %q, got %q", test.want, got)
			}
		})
	}
}
