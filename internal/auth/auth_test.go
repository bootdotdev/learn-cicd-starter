package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	test := []struct {
		input string
		want  string
	}{
		{
			input: "ApiKey 1234",
			want:  "1234",
		},
		{
			input: "ApiKey 26587-45459-232245-1234",
			want:  "26587-45459-232245-1234",
		},
		{
			input: "",
			want:  "",
		},
		{
			input: "GITKEY 26587-45459-232245-1234",
			want:  "",
		},
		{
			input: "ApiKey",
			want:  "",
		},
	}

	for _, tc := range test {
		header := http.Header{}
		header.Set("Authorization", tc.input)
		got, _ := GetAPIKey(header)
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("expected: %v, got: %v", tc.want, got)
		}
	}
}
