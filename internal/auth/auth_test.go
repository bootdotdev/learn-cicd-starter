package auth

import (
	"errors"
	"net/http"
	"strings"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input       string
		expectedErr error
	}

	testCases := []test{
		{input: "ApiKey supersecretkey", expectedErr: nil},
		{input: "NotApiKey supersecretkey", expectedErr: errors.New("malformed authorization header")},
		{input: "supersecretkey", expectedErr: errors.New("malformed authorization header")},
	}

	for _, testCase := range testCases {

		h := make(http.Header)
		h.Set("Authorization", testCase.input)
		gotKey, err := GetAPIKey(h)
		if err != nil {
			if err.Error() != testCase.expectedErr.Error() {
				t.Fatalf("Expected error: %s, got: %s", testCase.expectedErr.Error(), err.Error())
			}
			continue
		}
		inputWords := strings.Split(testCase.input, " ")
		if gotKey != inputWords[len(inputWords)-1] {
			t.Fatalf("Expected key: %s, got key: %s", inputWords[len(inputWords)-1], gotKey)
		}
	}

}
