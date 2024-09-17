package auth

import (
	"errors"
	"net/http"
	"testing"
)

type testValues struct {
	input http.Header
	want  string
	err   error
}

func TestAuth(t *testing.T) {
	tests := []testValues{
		{
			input: http.Header{},
			want:  "",
			err:   ErrNoAuthHeaderIncluded,
		},
		{
			input: http.Header{"Authorization": {}},
			want:  "",
			err:   errors.New("malformed authorization header"),
		},
		{
			input: http.Header{"Authorization": {"ApiKey key"}},
			want:  "key",
			err:   nil,
		},
	}

	for _, test := range tests {
		got, err := GetAPIKey(test.input)

		if got != test.want && err != test.err {
			t.Fatalf("wantVal: %v, wantErr: %v, got: %v", test.want, test.err, got)
		}
	}

}
