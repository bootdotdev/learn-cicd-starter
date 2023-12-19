package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	cases := []struct {
		input           http.Header
		expected_string string
		expected_error  error
	}{
		{
			input:           http.Header{"Authentication": {"Bearer Token"}},
			expected_string: "",
			expected_error:  ErrNoAuthHeaderIncluded,
		},
		{
			input:           http.Header{"Authorization": {"Bearer Token"}},
			expected_string: "",
			expected_error:  errors.New("malformed authorization header"),
		},
		{
			input:           http.Header{"Authorization": {"ApiKey"}},
			expected_string: "",
			expected_error:  errors.New("malformed authorization header"),
		},
		{
			input:           http.Header{"Authorization": {"ApiKey Key"}},
			expected_string: "Key",
			expected_error:  nil,
		},
	}

	for _, cs := range cases {
		actual_string, actual_error := GetAPIKey(cs.input)
		if actual_string != cs.expected_string {
			t.Errorf("The key don't coincide: %v vs %v", actual_string, cs.expected_string)
			continue
		}
		if actual_error == nil {
			if cs.expected_error != nil {
				t.Errorf("The errors don't coincide")
				continue
			}
			continue
		}
		if actual_error.Error() != cs.expected_error.Error() {
			t.Errorf("The errors don't coincide: %v vs %v", actual_error, cs.expected_error)
			continue
		}
	}

}
