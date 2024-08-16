package main

import (
	"reflect"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input map[string][]string
		want  string
	}
	var header = make(map[string][]string)
	header["Authorization"] = []string{"ApiKey randomAccessKey"}
	header["Content-Type"] = []string{"application/json"}

	tests := []test{
		{input: header, want: "randomAccessKey"},
	}

	for _, test := range tests {
		got, _ := auth.GetAPIKey(test.input)
		if !reflect.DeepEqual(test.want, got) {
			t.Fatalf("Expected %#v, got %#v", test.want, got)
		}

	}
}
