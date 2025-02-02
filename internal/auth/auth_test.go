package auth

import (
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
	"github.com/google/go-cmp/cmp/cmpopts"
)

func TestGetAPIKey(t *testing.T) {
	type Want struct {
		ApiKey string
		Err    error
	}

	tests := map[string]struct {
		input  http.Header
		output Want
	}{
		"simple": {input: http.Header{
			"Authorization": []string{"ApiKey a/b/c"},
		}, output: Want{
			ApiKey: "a/b/c",
			Err:    nil,
		}},
		"wrong format": {input: http.Header{
			"Authorization": []string{"ApiKeya/b/c"},
		}, output: Want{
			ApiKey: "",
			Err:    ErrMalformedAuthHeader,
		}},
		"no auth header": {input: http.Header{}, output: Want{
			ApiKey: "",
			Err:    ErrNoAuthHeaderIncluded,
		}},
	}
	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			output, err := GetAPIKey(tc.input)
			want := Want{
				ApiKey: output,
				Err:    err,
			}
			diff := cmp.Diff(tc.output, want, cmpopts.EquateErrors())
			if diff != "" {
				t.Fatal(diff)
			}
		})
	}
}
