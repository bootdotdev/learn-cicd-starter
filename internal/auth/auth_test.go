package auth

import (
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestAuth(t *testing.T) {

	headers := make(map[string]http.Header)
	headers["simple"] = http.Header{"Authorization": []string{"ApiKey 123"}}
	headers["missing"] = http.Header{"NotAuth": []string{"ApiKey 123"}}
	headers["malformed"] = http.Header{"Authorization": []string{"Something"}}

	tests := map[string]struct {
		input http.Header
		want  string
	}{
		"simple":    {input: headers["simple"], want: "123"},
		"missing":   {input: headers["missing"], want: ""},
		"malformed": {input: headers["malformed"], want: ""},
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
