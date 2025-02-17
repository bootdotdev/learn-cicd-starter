package auth

import (
	"net/http"
	"testing"
)

func TestAuth(t *testing.T) {
	cases := []struct {
		name          string
		headers       http.Header
		wantError bool
	}{
		{
			name:          "No Headers",
			headers:       make(http.Header),
			wantError: true,
		},
	}
	
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			_, err := GetAPIKey(c.headers)
			if (err != nil) == c.wantError {
				t.Errorf("%v expecting error %v but received %v", c.name, c.wantError, err)
			}
		})
	}
}