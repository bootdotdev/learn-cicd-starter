package main

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input   string
		wantErr bool
	}{
		"valid header":     {input: "Authorization", wantErr: false},
		"empty header":     {input: "", wantErr: true},
		"malformed header": {input: "auth", wantErr: true},
	}

	for name, test := range tests {
		header := http.Header{}
		header.Set(test.input, "ApiKey test")
		t.Run(name, func(t *testing.T) {
			_, err := auth.GetAPIKey(header)
			if (err != nil) != test.wantErr {
				t.Fatalf("test %v failed, wanted err - %v, got: %v", name, test.wantErr, err)
			}
		})
	}
}
