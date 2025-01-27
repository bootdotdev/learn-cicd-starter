package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		Input          http.Header
		ExpectedOutput string
		ExpectedError  error
	}{
		"successful": {
			Input:          http.Header{"Authorization": []string{"ApiKey 123456789"}},
			ExpectedOutput: "123456789",
			ExpectedError:  nil,
		},
		"no auth header": {
			Input:          http.Header{"Authorization": []string{""}},
			ExpectedOutput: "",
			ExpectedError:  ErrNoAuthHeaderIncluded,
		},
		"malformed header": {
			Input:          http.Header{"Authorization": []string{"wrongValue 123456"}},
			ExpectedOutput: "",
			ExpectedError:  ErrMalformedHeader,
		},
		"len(parts) < 2": {
			Input:          http.Header{"Authorization": []string{"ApiKey"}},
			ExpectedOutput: "",
			ExpectedError:  ErrMalformedHeader,
		},
	}

	for name, testCase := range tests {
		t.Run(name, func(t *testing.T) {
			out, err := GetAPIKey(testCase.Input)
			if testCase.ExpectedOutput != out {
				t.Fatalf("%s: expected: %#v, got: %#v", name, testCase.ExpectedOutput, out)
			}
			if !errors.Is(testCase.ExpectedError, err) {
				t.Fatalf("%s: expected: %#v, got: %#v", name, testCase.ExpectedError, err)
			}
		})
	}
}
