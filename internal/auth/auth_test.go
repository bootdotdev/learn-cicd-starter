package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	tests := map[string]struct {
		input string
		want  string
	}{
		"simple": {
			input: "ApiKey 12345",
			want:  "12345",
		},
		"no auth header": {
			input: "",
			want:  "",
		},
		"wrong auth header format prefix": {
			input: "apikey 12345",
			want:  "",
		},
		"wrong auth header format postfix": {
			input: "ApiKey ",
			want:  "1",
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			header := http.Header{}
			header.Set("Authorization", tc.input)
			got, _ := GetAPIKey(header)
			if !reflect.DeepEqual(tc.want, got) {
				t.Fatalf("expected: %v, got: %v", tc.want, got)
			}
		})
	}
}
