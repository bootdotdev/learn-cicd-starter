package auth_test

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
	"github.com/google/go-cmp/cmp"
	"github.com/google/go-cmp/cmp/cmpopts"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  func() (string, error)
	}{
		"simple":       {input: createHeader("Authorization", "ApiKey ABC"), want: createWant("ABC", auth.ErrNoAuthHeaderIncluded)},
		"no header":    {input: createHeader("", ""), want: createWant("", auth.ErrNoAuthHeaderIncluded)},
		"wrong header": {input: createHeader("Authorization", "Bearer ABC"), want: createWant("", auth.ErrMalformedAuthHeader)},
		"empty header": {input: createHeader("Authorization", ""), want: createWant("", auth.ErrNoAuthHeaderIncluded)},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotResult, gotError := auth.GetAPIKey(tc.input)
			wantResult, wantError := tc.want()
			diff := cmp.Diff(wantResult, gotResult) + cmp.Diff(wantError, gotError, cmpopts.EquateErrors())
			if diff != "" {
				t.Fatal(diff)
			}
		})
	}
}

func createHeader(key string, value string) http.Header {
	header := http.Header{}
	if key != "" {
		header.Add(key, value)
	}
	return header
}

func createWant(result string, err error) func() (string, error) {
	return func() (string, error) {
		return result, err
	}
}
