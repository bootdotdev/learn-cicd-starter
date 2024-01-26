package auth_test

import (
	"errors"
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name  string
		input http.Header
		want  string
		err   error
	}{
		{
			name:  "no header",
			input: http.Header{},
			want:  "",
			err:   auth.ErrNoAuthHeaderIncluded,
		},
		{
			name: "empty auth header ",
			input: http.Header{
				"Authorization": []string{""},
			},
			want: "",
			err:  auth.ErrNoAuthHeaderIncluded,
		},
		{
			name: "unknown auth type",
			input: http.Header{
				"Authorization": []string{"Bearer token"},
			},
			want: "",
			err:  auth.ErrMalformedAuthHeader,
		},
		{
			name: "ok",
			input: http.Header{
				"Authorization": []string{"ApiKey token"},
			},
			want: "token1",
			err:  nil,
		},
	}
	for _, tc := range tests {
		got, err := auth.GetAPIKey(tc.input)
		if got != tc.want {
			t.Errorf("got %v, wanted: %v", got, tc.want)
		}
		if tc.err != nil && !errors.Is(err, tc.err) {
			t.Errorf("got error: %v, wanted error: %v", tc.err, err)
		}
	}
}
