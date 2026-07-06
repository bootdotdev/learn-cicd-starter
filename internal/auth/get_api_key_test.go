// unit test for getAPIKey function
package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers map[string][]string
		want    string
		wantErr bool
	}{
		{
			name: "valid API key",
			headers: map[string][]string{
				"Authorization": {"ApiKey my-api-key"},
			},
			want:    "my-api-key",
			wantErr: false,
		},
		{
			name:    "missing Authorization header",
			headers: map[string][]string{},
			want:    "",
			wantErr: true,
		},
		{
			name: "malformed Authorization header",
			headers: map[string][]string{
				"Authorization": {"Bearer my-api-key"},
			},
			want:    "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
