package auth

import (
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		key       string
		value     string
		expect    string
		expectErr string
	}{
		"no auth header": {
			expectErr: "no authorization header",
		},
		"no auth header value": {
			key:       "Authorization",
			expectErr: "no authorization header",
		},
		"malformed auth header value v1": {
			key:       "Authorization",
			value:     "-",
			expectErr: "malformed authorization header",
		},
		"malformed auth header value v2": {
			key:       "Authorization",
			value:     "Bearer xxxxxx",
			expectErr: "malformed authorization header",
		},
		"correctly formed auth header": {
			key:       "Authorization",
			value:     "ApiKey xxxxxx",
			expect:    "xxxxxx",
			expectErr: "not expecting an error",
		},
	}

	for name, test := range tests {
		t.Run(name, func(t *testing.T) {
			header := http.Header{}
			header.Add(test.key, test.value)

			output, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), test.expectErr) {
					return
				}
				t.Errorf("Unexpected: TestGetAPIKey:%v\n", err)
				return
			}

			if output != test.expect {
				t.Errorf("Unexpected: TestGetAPIKey:%s", output)
				return
			}
		})
	}
}
