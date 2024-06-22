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
			name:    "No Authorization Header",
			headers: http.Header{},
			want:    "",
			err:     ErrNoAuthHeaderIncluded,
		},
		{
			name: "Authorization Header Without Space",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want: "",
			err:  errors.New("malformed authorization header"),
		},
		{
			name: "Incorrect Prefix in Authorization Header",
			headers: http.Header{
				"Authorization": []string{"Bearer 123456"},
			},
			want: "",
			err:  errors.New("malformed authorization header"),
		},
		{
			name: "Correct Authorization Header",
			headers: http.Header{
				"Authorization": []string{"ApiKey 123456"},
			},
			want: "123456",
			err:  nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if got != tt.want || (err != nil && err.Error() != tt.err.Error()) || (err == nil && tt.err != nil) {
				t.Errorf("GetAPIKey() = %v, err %v; want %v, err %v", got, err, tt.want, tt.err)
			}
		})
	}
}
