package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetApiKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  struct {
			value string
			err   error
		}
	}{
		"no auth": {input: http.Header{}, want: struct {
			value string
			err   error
		}{"", auth.ErrNoAuthHeaderIncluded}},
		"valid auth": {input: http.Header{"Authorization": []string{"ApiKey my-api-key"}}, want: struct {
			value string
			err   error
		}{"my-api-key", nil}},
		"malformed auth": {input: http.Header{"Authorization": []string{"Bearer invalid-api-key"}}, want: struct {
			value string
			err   error
		}{"", auth.ErrNoAuthHeaderIncluded}},
	}

	for name, test := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := auth.GetAPIKey(test.input)
			if got != test.want.value {
				t.Fatalf("got value %s - wanted value %s", got, test.want.value)
			}
			if err != test.want.err {
				t.Fatalf("got err %v - wanted err %v", err, test.want.err)
			}
		})
	}
}
