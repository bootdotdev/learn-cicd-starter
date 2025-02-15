package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type output struct {
		key string
		err error
	}

	type test struct {
		header          http.Header
		expected_result output
	}

	tests := []test{
		{header: http.Header{"Authorization": []string{"ApiKey 12345678-abcd-90ef-gh12-ijklmnopqrst"}}, expected_result: output{key: "12345678-abcd-90ef-gh12-ijklmnopqrst", err: nil}},
		{header: http.Header{"Authorization": []string{"Key 12345678-abcd-90ef-gh12-ijklmnopqrst"}}, expected_result: output{key: "", err: errors.New("malformed authorization header")}},
		{header: http.Header{}, expected_result: output{key: "", err: ErrNoAuthHeaderIncluded}},
	}

	for i, tc := range tests {
		key, err := GetAPIKey(tc.header)
		if !reflect.DeepEqual(tc.expected_result.key, key) {
			t.Fatalf("test %d failed: expected key: %s, actual key: %s", i+1, tc.expected_result.key, key)
		} else if err != nil && tc.expected_result.err.Error() != err.Error() {
			t.Fatalf("test %d failed: expected err: %v, actual err: %v", i+1, tc.expected_result.err, err)
		}
	}
}
