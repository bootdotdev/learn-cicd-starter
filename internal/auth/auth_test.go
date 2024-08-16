package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	cases := []struct {
		headers        http.Header
		expectedString string
		shouldError    bool
	}{
		{http.Header{"Authorization": {"ApiKey dGVzdA=="}}, "dGVzdA==", false},
		{http.Header{"Authorization": {"ApiKey eyJ"}}, "eyJ", false},
		{http.Header{"Authorization": {""}}, "", true},
		{http.Header{"Authorizatio": {"ApiKey dGVzdA=="}}, "", true},
		{http.Header{"": {"ApiKey dGVzdA=="}}, "", true},
	}

	for i, c := range cases {
		t.Run(fmt.Sprintf("Get API Key Test Case %d", i), func(t *testing.T) {
			auth, err := GetAPIKey(c.headers)

			if auth != c.expectedString {
				t.Errorf("Incorrect return string, got %s want %s", auth, c.expectedString)
			}

			if c.shouldError && err == nil {
				t.Errorf("Expected error for input headers %+v but no error was returned", c.headers)
			}
		})
	}
}
