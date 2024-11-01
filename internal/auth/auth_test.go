package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func createHeaderWithAPIKey(apiKey string) http.Header {
	headers := make(http.Header)
	headers.Set("Authorization", apiKey)
	return headers
}

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input http.Header
		want  string
		err   error
	}{
		"simple test case":           {input: createHeaderWithAPIKey("ApiKey TestApiKey"), want: "TestApiKey", err: nil},
		"malformed header no ApiKey": {input: createHeaderWithAPIKey("TestApiKey"), want: "", err: errors.New("malformed authorization header")},
		"header with many sapces":    {input: createHeaderWithAPIKey("ApiKey TestApiKey TestApiKey TestApiKey"), want: "TestApiKey", err: nil},
		"empty header":               {input: make(http.Header), want: "", err: ErrNoAuthHeaderIncluded},
	}

	for name, testCase := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(testCase.input)
			if !reflect.DeepEqual(testCase.want, got) || (err != nil && err.Error() != testCase.err.Error()) {
				t.Fatalf("expected '%s', got '%v' // expected error '%v', got Error '%v'", testCase.want, got, testCase.err, err)
			}
		})
	}
}
