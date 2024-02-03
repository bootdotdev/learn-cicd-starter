package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input string
		want  string
	}

	tests := []test{
		{"ApiKey 11223", "11223"},
		{"ApiKey 45768", "45768"},
	}

	for _, tc := range tests {
		header := http.Header{}
		header.Add("Authorization", tc.input)
		got, _ := GetAPIKey(header)
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("GetAPIKey(%v): expected: %v, got: %v", tc.input, got, tc.want)
		}
	}
}
