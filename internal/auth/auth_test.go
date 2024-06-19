package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		key    string
		value  string
		resVal string
		resErr error
	}

	tests := []test{
		{key: "Authorization", value: "ApiKey 123", resVal: "123", resErr: nil},
		{key: "Authorization", value: "Foo", resVal: "", resErr: errors.New("malformed authorization header")},
		{key: "Authorization", value: "Foo 123", resVal: "", resErr: errors.New("malformed authorization header")},
		{key: "Bad", value: "ApiKey 123", resVal: "", resErr: ErrNoAuthHeaderIncluded},
	}

	for _, tc := range tests {
		h := http.Header{}
		h.Add(tc.key, tc.value)

		apikey, err := GetAPIKey(h)

		if !reflect.DeepEqual(tc.resVal, apikey) {
			t.Fatalf("expected: %v, got: %v", tc.resVal, apikey)
		}
		if tc.resErr == nil && err != nil {
			t.Fatalf("expected nil err, got %v", err)
		}
		if tc.resErr != nil && tc.resErr.Error() != err.Error() {
			t.Fatalf("expected: %v, got: %v", tc.resErr.Error(), err.Error())
		}
	}
}
