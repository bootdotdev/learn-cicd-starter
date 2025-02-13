package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input       http.Header
		expectedErr error
		expected    string
	}

	properHeader := http.Header{}
	properHeader.Add("Authorization", "ApiKey FakeToken")
	incorrectHeader := http.Header{}
	incorrectHeader.Set("Authorization", "Bearer Badddd")
	tests := []test{
		{input: http.Header{"Authorization": {""}}, expectedErr: ErrNoAuthHeaderIncluded, expected: ""},
		{input: properHeader, expectedErr: nil, expected: "FakeToken"},
		{input: incorrectHeader, expectedErr: MalformedAuthHeader, expected: ""},
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.input)
		if tc.expected != got {
			t.Fatalf("expected: %v, got: %v", tc.expected, got)
		}
		if !errors.Is(tc.expectedErr, err) {
			t.Fatalf("expected: %v, got: %v", tc.expectedErr, err)
		}
	}
}
