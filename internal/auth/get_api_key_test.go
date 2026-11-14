package auth

import (
	"net/http"
	"testing"
)
a
func TestGetAPIKey(t *testing.T) {
	type test struct {
		header string
		value  string
		want   string
	}

	tests := []test{
		{header: "Authorization", value: "ApiKey test123", want: "test123"},
		{header: "Authentication", value: "ApiKey test123", want: ""},
		{header: "Authorization", value: "test123", want: ""},
		{header: "Authorization", value: "test123 ApiKey", want: ""},
	}

	for _, tc := range tests {
		headers := http.Header{}
		headers.Set(tc.header, tc.value)

		val, _ := GetAPIKey(headers)
		if val != tc.want {
			t.Fatalf("Expected value failed got %s expected: %s", tc.value, tc.want)
		}

	}
}
