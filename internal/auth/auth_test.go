package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	emptyHeader := http.Header{}

	authHeader := http.Header{}
	authHeader.Set("Authorization", "ApiKey apikeyhere")

	invalidAuthHeader := http.Header{}
	invalidAuthHeader.Set("Authorization", "Bearer tokenhere")

	noSpaceAuthHeader := http.Header{}
	noSpaceAuthHeader.Set("Authorization", "ApiKeyapikeyhere")

	testCases := map[string]struct {
		Input http.Header
		Want  string
	}{
		"No Auth Header": {
			Input: emptyHeader,
			Want:  "",
		},
		"Valid ApiKey Auth Header": {
			Input: authHeader,
			Want:  "apikeyhere",
		},
		"Invalid Auth Header": {
			Input: invalidAuthHeader,
			Want:  "",
		}, "No Space Header": {
			Input: noSpaceAuthHeader,
			Want:  "",
		},
	}

	for name, tc := range testCases {
		t.Run(name, func(t *testing.T) {
			apiKey, _ := GetAPIKey(tc.Input)
			if apiKey != tc.Want {
				t.Fatalf("expected: %v, got %v", tc.Want, apiKey)
			}
		})
	}

}
