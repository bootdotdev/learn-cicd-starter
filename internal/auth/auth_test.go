package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers map[string][]string
		want    string
		wantErr error
	}{
		{
			name:    "no auth header",
			headers: map[string][]string{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "valid auth header",
			headers: map[string][]string{"Authorization": {"ApiKey 123"}},
			want:    "123",
			wantErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, gotErr := GetAPIKey(tt.headers)
			if got != tt.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tt.want)
			}
			if gotErr != tt.wantErr {
				t.Errorf("GetAPIKey() gotErr = %v, want %v", gotErr, tt.wantErr)
			}
		})
	}
}