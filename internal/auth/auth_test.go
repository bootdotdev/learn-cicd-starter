package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	type test struct {
		input  http.Header
		outStr string
		outErr error
	}

	tests := []test{
		{
			input:  http.Header{"Authorization": []string{"ApiKey 12345"}},
			outStr: "12345",
			outErr: nil,
		},
		{
			input:  http.Header{"Authorization": []string{"poodle"}},
			outStr: "",
			outErr: errors.New("malformed authorization header"),
		},
		{
			input:  http.Header{},
			outStr: "",
			outErr: errors.New("no authorization header included"),
		},
	}

	for _, tc := range tests {
		res, err := GetAPIKey(tc.input)
		if res != tc.outStr {
			t.Errorf("Mismatch in Api Key Getter: Expected Api Key '%s', got '%s'", tc.outStr, res)
		}

		if tc.outErr == nil && err != nil {
			t.Errorf("Mismatch in Api Key Getter: Expected err == nil, got %v", err)
		}

		if tc.outErr != nil && err == nil {
			t.Errorf("Mismatch in Api Key Getter: Expected err == %v, got nil", tc.outErr)
		}

		if err != nil && tc.outErr != nil {
			if err.Error() != tc.outErr.Error() {
				t.Errorf("Mismatch in Api Key Getter: Expected err '%v', got '%v'", tc.outErr, err)
			}
		}
	}
}
