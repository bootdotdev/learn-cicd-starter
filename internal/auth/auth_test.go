package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		err     error
	}{
		{
			name:    "Valid Authorization Header",
			headers: http.Header{"Authorization": []string{"ApiKey abc123"}},
			want:    "abc123",
			err:     nil,
		},
		{
			name:    "Missing Authorization Header",
			headers: http.Header{},
			want:    "",
			err:     ErrNoAuthHeaderIncluded,
		},
		{
			name:    "Malformed Authorization Header",
			headers: http.Header{"Authorization": []string{"InvalidHeaderFormat"}},
			want:    "",
			err:     errors.New("malformed authorization header"),
		},
		{
			name:    "Incomplete Authorization Header",
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			want:    "",
			err:     errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			if got != tt.want {
				t.Errorf("Got %v, want %v", got, tt.want)
			}

			if (err == nil && tt.err != nil) || (err != nil && tt.err == nil) || (err != nil && err.Error() != tt.err.Error()) {
				t.Errorf("Got error %v, want %v", err, tt.err)
			}
		})
	}
}
