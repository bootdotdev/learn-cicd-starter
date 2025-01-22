package auth

import (
	"fmt"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		key     string
		value   string
		want    string
		wantErr string
	}{
		{
			wantErr: "no authorization header included",
		},
		{
			key:     "Authorization",
			wantErr: "no authorization header included",
		},
		{
			key:     "Authorization",
			value:   "-",
			wantErr: "malformed authorization header",
		},
		{
			key:     "Authorization",
			value:   "Bearer xxxxxx",
			wantErr: "malformed authorization header",
		},
		{
			key:     "Authorization",
			value:   "ApiKey xxxxxx",
			want:    "xxxxxx",
			wantErr: "not expecting an error",
		},
	}

	for i, test := range tests {
		t.Run(fmt.Sprintf("GetAPIKey Test #%v", i), func(t *testing.T) {
			header := http.Header{}
			header.Set(test.key, test.value)

			output, err := GetAPIKey(header)
			if err != nil {
				if strings.Contains(err.Error(), test.wantErr) {
					return
				}
				t.Errorf("Unexpected error: TestGetAPIKEY:%s", err.Error())
				return
			}

			if output != test.want {
				t.Errorf("Unexpected: TestGetAPIKEY:%s", output)
				return
			}
		})
	}
}
