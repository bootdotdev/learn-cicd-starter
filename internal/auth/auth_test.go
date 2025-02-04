package auth

import (
	"reflect"
    "testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		header map[string][]string
		want   struct {
			apikey string
			err    error
		}
	}{
		"no authorization header included": {
			header: map[string][]string{
				"Content-Type": {"application/json"},
			},
			want: struct {
				apikey string
				err    error
			}{
				apikey: "",
				err:    ErrNoAuthHeaderIncluded,
			},
		},

		"malformed authorization header 1": {
			header: map[string][]string{
				"Authorization": {"ApiKey"},
			},
			want: struct {
				apikey string
				err error
			}{
				apikey: "",
				err: ErrMalformedAuthorizationHeader,
			},
		},

		"malformed authorization header 2": {
			header: map[string][]string{
				"Authorization": {"123456789"},
			},
			want: struct {
				apikey string
				err error
			}{
				apikey: "",
				err: ErrMalformedAuthorizationHeader,
			},
		},

		"correct header": {
			header: map[string][]string{
				"Authorization": {"ApiKey 12345678"},
			},
			want: struct {
				apikey string
				err error
			}{
				apikey: "123456789",
				err: nil,
			},
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotApiKey, gotErr := GetAPIKey(tc.header)
			if !reflect.DeepEqual(tc.want.apikey, gotApiKey) {
				t.Fatalf("expected: %v, got: %v", tc.want.apikey, gotApiKey)
			}
			if gotErr != tc.want.err {
				t.Fatalf("expected: %v, got: %v", tc.want.err.Error(), gotErr.Error())
			}
		})
	}
}