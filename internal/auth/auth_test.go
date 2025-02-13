package auth

import (
	"fmt"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		input   http.Header
		want    string
		wantErr error
	}{
		{
			name: "simple API",
			input: http.Header{
				"Content-Type":  {"application/json"},
				"User-Agent":    {"Golang"},
				"Authorization": {"ApiKey thisIsAnApiKey"},
			},
			want:    "thisIsAnApiKey",
			wantErr: nil,
		},
		{
			name: "Test invalid Authorization",
			input: http.Header{
				"Content-Type":  {"application/json"},
				"User-Agent":    {"Golang"},
				"Authorization": {"Bearer clearlyNotAPI"},
			},
			want:    "",
			wantErr: fmt.Errorf("malformed authorization header"),
		},
		{
			name: "Test missing header",
			input: http.Header{
				"Content-Type": {"application/json"},
				"User-Agent":   {"Golang"},
			},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.input)
		if !reflect.DeepEqual(tc.want, got) {
			t.Fatalf("%s: expected: %v, got: %v, err: %v", tc.name, tc.want, got, err)
		}
		if err != nil && err.Error() != tc.wantErr.Error() {
			t.Fatalf("%s: expected Error: %v, got: %v", tc.name, tc.wantErr, err)
		}
	}

}
