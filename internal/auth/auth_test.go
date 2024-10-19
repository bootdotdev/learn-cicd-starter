package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {

	type testCase struct {
		name        string
		headerKey   string
		headerValue string
		wantMsg     string
		wantErr     string
	}

	testCases := []testCase{
		{
			name:        "Valid API Key",
			headerKey:   "Authorization",
			headerValue: "ApiKey test",
			wantMsg:     "test",
			wantErr:     "",
		},
		{
			name:        "Invalid Header",
			headerKey:   "Authorizatio",
			headerValue: "ApiKey test",
			wantMsg:     "",
			wantErr:     "no authorization header included",
		},
		{
			name:        "Invalid Header 2 - ApiKey missspel",
			headerKey:   "Authorization",
			headerValue: "ApiKe test",
			wantMsg:     "",
			wantErr:     "malformed authorization header",
		},
		{
			name:        "Invalid Header 3 - less than 2 args",
			headerKey:   "Authorization",
			headerValue: "test",
			wantMsg:     "",
			wantErr:     "malformed authorization header",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			req, _ := http.NewRequest("GET", "http://google.com", nil)
			req.Header.Set(tc.headerKey, tc.headerValue)

			resp, err := GetAPIKey(req.Header)
			if resp != tc.wantMsg {
				t.Errorf("GetAPIKey() got message = %v, want %v", resp, tc.wantMsg)
			}

			if tc.wantErr == "" && err != nil {
				t.Errorf("GetAPIKey() unexpected error: %v", err)
			} else if tc.wantErr != "" && (err == nil || err.Error() != tc.wantErr) {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tc.wantErr)
			}

		})
	}

}
