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
	tests := []test{
		{input: nil, want: ""},
		{input: map[string][]string{"Authorization": {"ApiKey 123"}}, want: "123"},
	}

	for _, tc := range tests {
		got, _ := auth.GetAPIKey(tc.input)
		if !reflect.DeepEqual(got, tc.want) {
			t.Errorf("got %v; want %v", got, tc.want)
		}

	}

}
