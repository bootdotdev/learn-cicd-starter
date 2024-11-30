package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := map[string]struct {
		args           string
		expectedKey    string
		expectedErrStr string
	}{
		"Proper API Key":   {args: "ApiKey 1234", expectedKey: "1234", expectedErrStr: ""},
		"No Header":        {args: "", expectedKey: "", expectedErrStr: "no authorization header included"},
		"Incorrect Header": {args: "test 23", expectedKey: "", expectedErrStr: "malformed authorization header"},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			headers := http.Header{}
			headers.Add("Authorization", tc.args)
			key, err := GetAPIKey(headers)
			if key != tc.expectedKey && err.Error() != tc.expectedErrStr {
				t.Fatalf("Expected Key: %v, Recieved Key: %v\nExpected Err: %v, Received Err: %v", key, tc.expectedKey, err, tc.expectedErrStr)
			}
		})
	}
}
