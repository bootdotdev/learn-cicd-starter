package main

import (
	"reflect"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input map[string][]string
		want  string
	}{
		"auth_provided": {input: map[string][]string{"Authorization": {"ApiKey randomAccessKey"}}, want: "randomAccessKey"},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, _ := auth.GetAPIKey(tc.input)
			if !reflect.DeepEqual(tc.want, got) {
				t.Fatalf("Expected %#v, got %#v", tc.want, got)
			}
		})
	}
}
