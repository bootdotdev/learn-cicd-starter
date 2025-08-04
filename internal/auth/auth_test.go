package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr bool
	}{
		{
			name: "Valid API key",
			headers: http.Header{
				"Authorization": []string{"ApiKey 1234"},
			},
			want:    "1234",
			wantErr: false,
		},
		{
			name:    "Missing authorization header",
			headers: http.Header{},
			want:    "",
			wantErr: true,
		},
		{
			name: "Empty authorization header",
			headers: http.Header{
				"Authorization": []string{""},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Wrong auth type",
			headers: http.Header{
				"Authorization": []string{"Bearer token123"},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Malformed header - no space",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Malformed header - missing key",
			headers: http.Header{
				"Authorization": []string{"ApiKey "},
			},
			want:    "",
			wantErr: false,
		},
		{
			name: "Case sensitive header key",
			headers: http.Header{
				"authorization": []string{"ApiKey 5678"},
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
