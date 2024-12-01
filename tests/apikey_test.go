package tests

import (
	"net/http"
	"reflect"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestSplit(t *testing.T) {
	tests := []struct {
		name  string
		input []string
		want  string
	}{
		{name: "simple", input: []string{"Authorization", "ApiKey 123456"}, want: "123456"},
	}

	for _, tc := range tests {
		header := http.Header{}
		header.Set(tc.input[0], tc.input[1])
		got, err := auth.GetAPIKey(header)
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("%s: expected: %v, got: %v", tc.name, tc.want, got)
		} else if err != nil {
			t.Fatalf("%s: expected: %v, got: %v", tc.name, tc.want, got)
		}
	}
}
