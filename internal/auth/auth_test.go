package auth

import (
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestGetAPIKey(t *testing.T) {
	correctHeader := http.Header{}
	emptyHeader := http.Header{}
	malformedHeader := http.Header{}

	correctHeader.Set("Authorization", "ApiKey som-random-bullshit")
	emptyHeader.Set("Authorization", "")
	malformedHeader.Set("Authorization", "ApiKay som-random-bullshit")

	tests := map[string]struct {
		input http.Header
		want  string
	}{
		"correctly formed header": {input: correctHeader, want: "som-random-bullshi"},
		"empty header":            {input: emptyHeader, want: ""},
		"malformed header":        {input: malformedHeader, want: ""},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, _ := GetAPIKey(tc.input)
			diff := cmp.Diff(tc.want, got)
			if diff != "" {
				t.Fatal(diff)
			}
		})
	}
}
