package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	type test struct {
		name           string
		header         http.Header
		expected       string
		isExpectErr    bool
		expectedErrMsg string
	}
	tests := []test{
		{
			"happy flow should pass",
			http.Header{"Authorization": {"ApiKey 123"}},
			"123",
			false,
			"",
		},
		{
			"empty header, should fail",
			http.Header{},
			"",
			true,
			"malformed authorization header",
		},
		{
			"only ApiKey, should fail",
			http.Header{"Authorization": {"ApiKey"}},
			"",
			true,
			"",
		},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got, err := GetAPIKey(test.header)
			switch test.isExpectErr {
			case false:
				if err != nil {
					t.Errorf("didn't expect error, got %v", err)
					return
				}
				if test.expected != got {
					t.Errorf("expected %s, got %s", test.expected, got)
					return
				}
			default:
				if err == nil {
					t.Errorf("expected error, didn't get one")
					return

				}

			}
		})
	}

}
