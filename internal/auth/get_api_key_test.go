package auth

import (
	"fmt"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		key       string
		value     string
		except    string
		exceptErr string
	}{
		{
			exceptErr: "no authorization header",
		},
		{
			key:       "Authorization",
			exceptErr: "no authorization header",
		},
		{
			key:       "Authorization",
			value:     "ApiKey my-secret-key-97",
			except:    "my-secret-key-97",
			exceptErr: "",
		},
		{
			key:       "Authorization",
			value:     "ApiKey",
			exceptErr: "malformed authorization header",
		},
	}

	for i, test := range tests {
		t.Run(fmt.Sprintf("TestGetAPIKey Case #%v:", i), func(t *testing.T) {
			header := http.Header{}
			header.Add(test.key, test.value)

			output, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), test.exceptErr) {
					return
				}
				t.Errorf("Unexpected: TestGetAPIKey:%v\n", err)
				return
			}
			if output != test.except {
				t.Errorf("Unexpected: TestGetAPIKey:%s", output)
				return
			}
		})
	}
}
