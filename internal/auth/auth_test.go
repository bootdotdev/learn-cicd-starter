package auth

import (
	"net/http"
	"testing"

	"github.com/google/go-cmp/cmp"
)

func TestGetApiKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  string
	}{
		"No Authorization Header": {
			input: http.Header{},
			want:  "",
		},
		"No token": {
			input: http.Header{
				"Authorization": []string{"ApiKey "},
			},
			want: "",
		},
		"Invalid Grant": {
			input: http.Header{
				"Authorization": []string{"Api something something"},
			},
			want: "",
		},
		"Success": {
			input: http.Header{
				"Authorization": []string{"ApiKey somethingsomething"},
			},
			want: "somethingsomething",
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			ApiKey, _ := GetAPIKey(tc.input)
			diff := cmp.Diff(tc.want, ApiKey)
			if diff != "" {
				t.Error(diff)
			}
		})
	}
}
