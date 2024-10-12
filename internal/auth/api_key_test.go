package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input         http.Header
		want          string
		errorContains string
	}{
		"no auth header": {
			input:         nil,
			want:          "",
			errorContains: "no authorization header",
		},
		"malformed auth header": {
			input: http.Header{
				"Content-Type":  []string{"text/html"},
				"Authorization": []string{"xpKey jodfiasdjfoijweaoifjajfjall"},
			},
			want:          "",
			errorContains: "malformed authorization header",
		},
		"correct api keys": {
			input: http.Header{
				"Content-Type":  []string{"text/html"},
				"Authorization": []string{"ApiKey making the test fail in purpose to check if the CI is running the tests correctly"},
			},
			want:          "kfpqhj3weofjefioisiogjsdugjfqopugjwoiejgqwoegjqoj",
			errorContains: "",
		},
	}

	for tcName, tc := range tests {
		t.Run(tcName, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)
			if err != nil && !strings.Contains(err.Error(), tc.errorContains) {
				t.Errorf("Test Failed -- expected error to contain \"%s\", actual error contains \"%s\"", tc.errorContains, err.Error())
				return
			}
			if err != nil && tc.errorContains == "" {
				t.Errorf("Test Failed -- unexpected error \"%s\"", err.Error())
				return
			}
			if err == nil && tc.errorContains != "" {
				t.Errorf("Test Failed -- expected error \"%s\" got none", tc.errorContains)
				return
			}

			if got != tc.want {
				t.Errorf("Test Failed -- expected \"%s\", got \"%s\"", tc.want, got)
				return
			}

		})
	}
}
