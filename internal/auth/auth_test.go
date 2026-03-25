package auth

import (
	"fmt"
	"net/http"
	"strings"
	"testing"
)

func TestAPIKey(t *testing.T) {
	tests := []struct {
		key    string
		value  string
		expect string
		err    string
	}{
		{
			err: "no authorization header",
		},
		{
			key: "Authorization",
			err: "no authorization header",
		},
		{
			key:   "Authorization",
			value: "h293hr928h3",
			err:   "malformed authorization header",
		},
		{
			key:    "Authorization",
			value:  "ApiKey hf29hd923",
			expect: "hf29hd923",
			err:    "none",
		},
	}
	for i, test := range tests {
		t.Run(fmt.Sprintf("TestGetAPIKey Case #%v:", i), func(t *testing.T) {
			header := http.Header{}
			header.Add(test.key, test.value)

			output, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), test.err) {
					return
				}
				t.Error(err)
				return
			}
			if output != test.expect {
				t.Error(err)
				return
			}
		})
	}
}
