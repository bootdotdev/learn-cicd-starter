package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers map[string]string
		want    string
		wantErr error
	}{
		{
			name:    "no auth header",
			headers: make(map[string]string),
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "auth header missing token",
			headers: map[string]string{
				"Authorization": "ApiKey",
			},
			want:    "",
			wantErr: ErrMalformedAuthHeader,
		},
		{
			name: "auth header is bearer token",
			headers: map[string]string{
				"Authorization": "Bearer 12345",
			},
			want:    "",
			wantErr: ErrMalformedAuthHeader,
		},
		{
			name: "valid auth header",
			headers: map[string]string{
				"Authorization": "ApiKey 12345",
			},
			want:    "12345",
			wantErr: nil,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			headers := make(map[string][]string)
			for k, v := range test.headers {
				headers[k] = []string{v}
			}

			got, gotErr := GetAPIKey(headers)
			if got != test.want {
				t.Errorf("got %s, want %s", got, test.want)
			}
			if gotErr != test.wantErr {
				t.Errorf("got error %v, want error %v", gotErr, test.wantErr)
			}
		})
	}
}
