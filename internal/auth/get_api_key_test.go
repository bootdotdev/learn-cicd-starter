package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		header    string
		want      string
		wantError error
	}{
		{
			name:   "valid API key",
			header: "ApiKey abc123",
			want:   "abc123",
		},
		{
			name:      "missing authorization header",
			header:    "",
			wantError: ErrNoAuthHeaderIncluded,
		},
		{
			name:      "malformed authorization header",
			header:    "Bearer abc123",
			wantError: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.header != "" {
				headers.Set("Authorization", tt.header)
			}

			got, err := GetAPIKey(headers)

			if got != tt.want {
				t.Errorf("GetAPIKey() got = %q, want %q", got, tt.want)
			}

			if tt.wantError != nil {
				if err == nil || err.Error() != tt.wantError.Error() {
					t.Errorf("GetAPIKey() error = %v, want %v", err, tt.wantError)
				}
			} else if err != nil {
				t.Errorf("GetAPIKey() unexpected error = %v", err)
			}
		})
	}
}
