package auth

import (
	"fmt"
	"net/http"
	"strings"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := []struct {
		key       string
		value     string
		expect    string
		expectErr string
	}{
		{
			expectErr: "no authorization header",
		},
		{
			key:       "Authorization",
			expectErr: "no authorization header",
		},
		{
			key:       "Authorization",
			value:     "-",
			expectErr: "malformed authorization header",
		},
		{
			key:       "Authorization",
			value:     "Bearer xxxxxx",
			expectErr: "malformed authorization header",
		},
		{
			key:       "Authorization",
			value:     "ApiKey xxxxxx",
			expect:    "xxxxxx",
			expectErr: "not expecting an error",
		},
	}

	for i, test := range tests {
		t.Run(fmt.Sprintf("TestGetApiKey Case #%v: ", i), func(t *testing.T) {
			header := http.Header{}
			header.Add(test.key, test.value)

			out, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), test.expectErr) {
					return
				}

				t.Errorf("Unexpected err: %v\n", err)
				return
			}

			if out != test.expect {
				t.Errorf("Unexpected output: %s\n", out)
				return
			}

		})
	}

}
