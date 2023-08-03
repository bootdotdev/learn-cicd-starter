package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input  http.Header
		expKey string
		expErr error
	}{
		"no header": {input: http.Header{}, expKey: "", expErr: ErrNoAuthHeaderIncluded},
		"valid key": {input: http.Header{"Authorization": []string{"ApiKey 123"}}, expKey: "123", expErr: nil},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)
			if !reflect.DeepEqual(tc.expKey, got) {
				t.Fatalf("%s: expected key: %v, got %v", name, tc.expKey, got)
			}
			if !errors.Is(err, tc.expErr) {
				t.Fatalf("%s: expected error: %v, got %v", name, tc.expErr, err)
			}
		})
	}
}
