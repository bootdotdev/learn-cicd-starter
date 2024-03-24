package auth

import (
	"net/http"
	"testing"

	cmp "github.com/google/go-cmp/cmp"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  string
	}{
		"correct": {
			input: http.Header{"Authorization": []string{"ApiKey testing"}},
			want:  "testing",
		},
		"wrong header": {
			input: http.Header{"Auth": []string{"ApiKey testing"}},
			want:  "",
		},
		"empty header": {
			input: http.Header{"Authorization": []string{""}},
			want:  "",
		},
		"too short header": {
			input: http.Header{"Authorization": []string{"ApiKey"}},
			want:  "",
		},
		"wrong prefix": {
			input: http.Header{"Authorization": []string{"Bearer testing"}},
			want:  "testing",
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, _ := GetAPIKey(tc.input)
			diff := cmp.Diff(tc.want, got)
			if diff != "" {
				t.Fatalf(diff)
			}
		})
	}
}
