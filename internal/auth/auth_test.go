package auth

import (
	"net/http"
	"net/http/httptest"
	"strconv"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	type test struct {
		subject  http.Header
		expected string
	}

	tests := make([]test, 5)

	subjects := make([]http.Header, 5)
	for i, subject := range subjects {
		istr := strconv.Itoa(i)
		r := httptest.NewRequest("GET", "http://localhost:8000", nil)
		r.Header.Add("Authorization", "ApiKey "+istr)
		subject = r.Header
		tests[i] = test{
			subject:  subject,
			expected: istr,
		}
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.subject)
		if err != nil {
			t.Fatal("GetAPIKey returned an error", err)
		}
		if got != tc.expected {
			t.Fatalf("expected: %v, got: %v", tc.expected, got)
		}
	}

}
