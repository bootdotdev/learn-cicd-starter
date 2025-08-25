package auth

import (
	"errors"
	"net/http"
	"reflect"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := []struct {
		name    string
		input   http.Header
		want    string
		wantErr error
	}{
		{
			name:    "no authorization header",
			input:   http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "missing key",
			input:   http.Header{"Authorization": []string{"ApiKey"}},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name:    "valid header",
			input:   http.Header{"Authorization": []string{"ApiKey validapikey"}},
			want:    "validapikey",
			wantErr: nil,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.input)

			if gotKey != tc.want {
				t.Fatalf("expected key %q, got %v", tc.want, gotKey)
			}

			if (gotErr != nil && tc.wantErr == nil) ||
				(gotErr == nil && tc.wantErr != nil) {
				t.Fatalf("expected err %q, got %v", tc.wantErr.Error(), gotErr.Error())
			}

			if gotErr != nil && tc.wantErr != nil &&
				!reflect.DeepEqual(gotErr.Error(), tc.wantErr.Error()) {
				t.Fatalf("expected err %q, got %q", tc.wantErr.Error(), gotErr.Error())
			}
		})
	}
}
