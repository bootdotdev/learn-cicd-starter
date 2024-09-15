package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name      string
		headers   http.Header
		want      string
		wantError error
	}{{
		name:      "No Authorization Header",
		headers:   http.Header{},
		want:      "",
		wantError: ErrNoAuthHeaderIncluded,
	},
		{
			name: "Malformed Authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			want:      "abc123",
			wantError: nil,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if got != tt.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tt.want)
			}

			if (err != nil && tt.wantError == nil) || (err == nil && tt.wantError != nil) || (err != nil && err.Error() != tt.wantError.Error()) {
				t.Errorf("GetAPIKey() error = %v, wantError %v", err, tt.wantError)
			}
		})
	}

}
