package auth

import (
	"fmt"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		apiKey         string
		expectedResult string
	}

	tests := []test{
		{
			apiKey:         "key",
			expectedResult: "key",
		},
		{
			apiKey:         "123",
			expectedResult: "123",
		},
		{
			apiKey:         "nlkwaejlkawe",
			expectedResult: "nlkwaejlkawe",
		},
	}

	for _, tc := range tests {
		headers := make(http.Header)
		headers.Set("Authorization", "ApiKey "+tc.apiKey)

		got, err := GetAPIKey(headers)
		if err != nil {
			fmt.Println(err)
			t.Fatal("test error")
		}

		if tc.expectedResult != got {
			t.Fatalf("got %s but expected %s", got, tc.expectedResult)
		}
	}
}
