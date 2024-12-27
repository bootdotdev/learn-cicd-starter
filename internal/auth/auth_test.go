package auth

import (
	"net/http"
	"testing"
)

func TestAPIKey(t *testing.T) {
	header1 := http.Header{}
	header2 := http.Header{}
	header3 := http.Header{}

	header1.Set("Authorization", "ApiKey 123456")
	header2.Set("Auth", "1234")
	header3.Set("Authorization", "abc123")

	type testCase struct {
		name        string
		header      http.Header
		expectedErr bool
		expectedKey string
	}

	tests := []testCase{
		{
			name:        "Valid token",
			header:      header1,
			expectedErr: false,
			expectedKey: "123456",
		},
		{
			name:        "Invalid Header Key",
			header:      header2,
			expectedErr: true,
			expectedKey: "",
		},
		{
			name:        "Invalid value",
			header:      header3,
			expectedErr: true,
			expectedKey: "",
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			token, err := GetAPIKey(tc.header)

			if (err != nil) != tc.expectedErr {
				t.Errorf("unexpected error, got %v, expected error: %v", err, tc.expectedErr)
			}

			if !tc.expectedErr && token != tc.expectedKey {
				t.Errorf("unexpected token, got %v, expected %v", token, tc.expectedKey)
			}
		})
	}

}
