package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type want struct {
		str string
		err string
	}

	type test struct {
		input http.Header
		want  want
	}

	tests := []test{
		{
			input: http.Header{"Authorization": []string{""}},
			want:  want{str: "", err: "no authorization header included"},
		},
		{
			input: http.Header{"Authorization": []string{"Bearer fakeapikey"}},
			want:  want{str: "", err: "malformed authorization header"},
		},
		{
			input: http.Header{"Authorization": []string{"ApiKey 1234123123"}},
			want:  want{str: "1234123123", err: ""},
		},
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.input)

		if got != tc.want.str {
			t.Errorf("got API key: %q, want: %q", got, tc.want.str)
		}

		// Check the error message
		if err != nil {
			if err.Error() != tc.want.err {
				t.Errorf("got error: %q, want: %q", err.Error(), tc.want.err)
			}
		} else if tc.want.err != "" {
			t.Errorf("expected error: %q, but got none", tc.want.err)
		}
	}

}
