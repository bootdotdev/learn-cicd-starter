package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	cases := []struct {
		input    http.Header
		expected string
	}{
		{
			input:    map[string][]string{"Authorization": {"ApiKey aljfalakjfaakffksfajafka"}},
			expected: "aljfalakjfaakffksfajafka",
		},
		{
			input:    map[string][]string{"Authorization": {"ApiKey aaljfalakjfaakffksfajafka"}},
			expected: "aaljfalakjfaakffksfajafka",
		},
	}
	for _, cs := range cases {
		actual, err := GetAPIKey(cs.input)
		if err != nil {
			t.Errorf("%v is malformed input", cs.input)
		}
		expectedString := cs.expected
		if actual != expectedString {
			t.Errorf("%v is not equal to %v", cs.input, cs.expected)
		}
	}

}
