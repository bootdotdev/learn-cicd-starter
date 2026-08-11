package auth

import (
	"fmt"
	"net/http"
	"strings"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := map[string]struct {
		key         string
		value       string
		expect      string
		expectedErr string
	}{
		"no header":             {expectedErr: "no authorization header"},
		"bad header with value": {key: "Authorization", expectedErr: "no authorization header"},
		"bad value":             {key: "Authorization", value: "-", expectedErr: "malformed authorization header"},
		"bad value prefix":      {key: "Authorization", value: "Bearer xxxxxx", expectedErr: "malformed authorization header"},
		"success case":          {key: "Authorization", value: "ApiKey xxxxxx", expect: "xxxxxx", expectedErr: "not expecting an error"},
	}

	for name, tc := range tests {
		t.Run(fmt.Sprintf("TestGetAPIKey Case #%v:", name), func(t *testing.T) {
			header := http.Header{}
			header.Add(tc.key, tc.value)

			output, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), tc.expectedErr) {
					return
				}
				t.Errorf("Unexpected: TestGetApiKey:%v\n", err)
				return
			}

			if output != tc.expect {
				t.Errorf("unexpected: TestGetAPIKey:%s", output)
				return
			}
		})
	}
}
