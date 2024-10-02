package auth

import (
	"errors"
	"net/http"
	"testing"
)

type testout struct {
	apiKey string
	err    error
}

type test struct {
	input http.Header
	want  testout
}

func TestGetAPIKey(t *testing.T) {
	tests := []test{
		{
			input: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want: testout{
				apiKey: "",
				err:    errors.New("malformed authorization header"),
			},
		},
		{
			input: http.Header{
				"notauth": []string{"ApiKey"},
			},
			want: testout{
				apiKey: "",
				err:    errors.New("no authorization header included"),
			},
		},
		{
			input: http.Header{
				"Authorization": []string{"NotApiKey 123456"},
			},
			want: testout{
				apiKey: "",
				err:    errors.New("no authorization header included"),
			},
		},
		{
			input: http.Header{
				"Authorization": []string{"ApiKey 123456"},
			},
			want: testout{
				apiKey: "123456",
				err:    nil,
			},
		},
	}

	for _, tc := range tests {
		got, err := GetAPIKey(tc.input)
		if got != tc.want.apiKey {
			t.Errorf("GetAPIKey(%v) = %v, want %v", tc.input, got, tc.want.apiKey)
		}
		if err != nil && tc.want.err == nil {
			t.Errorf("GetAPIKey(%v) = %v, want %v", tc.input, err, tc.want.err)
		}
		if err == nil && tc.want.err != nil {
			t.Errorf("GetAPIKey(%v) = %v, want %v", tc.input, err, tc.want.err)
		}
	}
}
