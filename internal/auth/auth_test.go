package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		input      http.Header
		wantResult string
		wantErr    error
	}

	h1 := http.Header{}
	h1.Set("Authorization", "ApiKey success")

	h2 := http.Header{}
	h2.Set("Authorization", "Bearer something")

	h3 := http.Header{}

	tests := []test{
		{input: h1, wantResult: "success", wantErr: nil},
		{input: h2, wantResult: "", wantErr: errors.New("malformed authorization header")},
		{input: h3, wantResult: "", wantErr: ErrNoAuthHeaderIncluded},
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.input)
		if !reflect.DeepEqual(tc.wantResult, got) {
			t.Fatalf("expected: %v, got: %v", tc.wantResult, got)
		}
		if err != nil && !reflect.DeepEqual(tc.wantErr.Error(), err.Error()) {
			t.Fatalf("expected error: %v, got %v", tc.wantErr, err)
		}
	}
}
