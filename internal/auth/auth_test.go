package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		name    string
		input   http.Header
		want    string
		wantErr string
	}{
		"Correct input": {
			input:   http.Header{"Authorization": []string{"ApiKey 123"}},
			want:    "123",
			wantErr: "",
		},
		"Missing header completely": {
			input:   http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded.Error(),
		},
		"Missing 'ApiKey' at string beginning": {
			input:   http.Header{"Authorization": []string{"Wrong 123"}},
			want:    "",
			wantErr: "malformed authorization header",
		},
		"Missing bearer indicator at string beginning": {
			input:   http.Header{"Authorization": []string{"123"}},
			want:    "",
			wantErr: "malformed authorization header",
		},
	}

	for name, tc := range tests {
		res, err := GetAPIKey(tc.input)

		if !ErrorContains(err, tc.wantErr) {
			t.Fatalf("%s: expected: %v, got: %v", name, tc.want, res)
		}

		if res != tc.want {
			t.Fatalf("%s: expected: %v, got: %v", name, tc.want, res)
		}
	}
}

func ErrorContains(out error, want string) bool {
	if out == nil {
		return want == ""
	}

	if want == "" {
		return false
	}

	return strings.Contains(out.Error(), want)
}
