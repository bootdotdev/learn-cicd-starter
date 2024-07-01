package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	headerGood := http.Header{}
	headerGood.Add("Authorization", "ApiKey 123")
	headerBadFormat := http.Header{}
	headerBadFormat.Add("Authorization", "AppKey 123")
	headerNoSplit := http.Header{}
	headerNoSplit.Add("Authorization", "ApiKey123")
	tests := map[string]struct {
		input    http.Header
		output   string
		errorMsg string
	}{
		"happyPath":    {input: headerGood, output: "123", errorMsg: ""},
		"emptyHeaders": {input: http.Header{}, output: "", errorMsg: ErrNoAuthHeaderIncluded.Error()},
		"badFormat":    {input: headerBadFormat, output: "", errorMsg: "malformed authorization header"},
		"noSplit":      {input: headerNoSplit, output: "", errorMsg: "malformed authorization header"},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, errGot := GetAPIKey(tc.input)
			if errGot != nil {
				if errGot.Error() != tc.errorMsg {
					t.Fatalf("expected: %s, got %s", tc.errorMsg, errGot.Error())
				}
			}
			if got != tc.output {
				t.Fatalf("expected: %s, got %s", tc.output, got)
			}
		})
	}
}
