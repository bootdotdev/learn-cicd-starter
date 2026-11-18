package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type test struct {
		name    string
		input   http.Header
		want    string
		wantErr error
	}

	tests := []test{
		{
			name: "valid header", input: http.Header{
				"Authorization": []string{"ApiKey 1234567890abcdef"},
			},
			want:    "1234567890abcdef",
			wantErr: nil,
		},
		{
			name: "invalid header", input: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "no header", input: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.input)
			if key != tc.want {
				t.Errorf("expected: %s, got: %s", tc.want, key)
			}
			if (err == nil) != (tc.wantErr == nil) {
				t.Errorf("expected: %v, got: %v", tc.wantErr, err)
			} else if err != nil && tc.wantErr != nil && err.Error() != tc.wantErr.Error() {
				t.Errorf("expected error message: %v, got: %v", tc.wantErr.Error(), err.Error())
			}
		})
	}
}
