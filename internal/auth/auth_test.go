package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	var (
		DummyApiKey = "DummyApiKey"
	)

	type expected struct {
		apiKey string
		err    error
	}

	type test struct {
		name     string
		header   http.Header
		expected expected
	}

	malformedAuthHeader := http.Header{}
	malformedAuthHeader.Set("Authorization", "thisisthekey")

	validAutHeader := http.Header{}
	validAutHeader.Set("Authorization", "ApiKey "+DummyApiKey)

	tests := []test{
		{name: "authorization header is not provided", header: http.Header{}, expected: expected{apiKey: "", err: ErrNoAuthHeaderIncluded}},
		{name: "malformed authorization header", header: malformedAuthHeader, expected: expected{apiKey: "", err: errors.New("malformed authorization header")}},
		{name: "valid authorization header", header: validAutHeader, expected: expected{apiKey: DummyApiKey, err: nil}},
	}

	for _, tc := range tests {
		apiKey, err := GetAPIKey(tc.header)

		if apiKey != tc.expected.apiKey {
			t.Fatalf("expected: %v, got: %v", tc.expected.apiKey, apiKey)
		}

		if err == nil && tc.expected.err != nil {
			t.Fatalf("expected: %v, got: %v", err, tc.expected.err)
		}

		if err != nil && err.Error() != tc.expected.err.Error() {
			t.Fatalf("expected: %v, got: %v", err, tc.expected.err)
		}
	}
}
