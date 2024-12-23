package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		name    string
		headers http.Header
		wantKey string
		wantErr string
	}
	testCases := []test{
		{
			name:    "Missing authorization header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded.Error(),
		},
		{
			name: "Missing API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			wantKey: "",
			wantErr: "malformed authorization header",
		},
		{
			name: "Invalid authorization header",
			headers: http.Header{
				"Authorization": []string{"Random tlkwqekowqkeop"},
			},
			wantKey: "",
			wantErr: "malformed authorization header",
		},
		{
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey testtoseeifthisworks"},
			},
			wantKey: "testtoseeifthisworks",
			wantErr: "",
		},
	}

	for _, testCase := range testCases {
		t.Run(testCase.name, func(t *testing.T) {
			key, err := GetAPIKey(testCase.headers)
			if key != testCase.wantKey {
				t.Errorf("expected key: %q, got: %q\n", testCase.wantKey, key)
			}
			if (err != nil && err.Error() != testCase.wantErr) || (err == nil && testCase.wantErr != "") {
				t.Errorf("expected error: %q, got: %q\n", testCase.wantErr, err)
			}
		})
	}
}
