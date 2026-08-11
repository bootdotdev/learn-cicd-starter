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
			name:    "missing auth header",
			headers: http.Header{},
			wantErr: true,
		},
		{
			name: "valid api key",
			headers: http.Header{
				"Authorization": []string{"ApiKey abc123"},
			},
			want: "abc123",
		},
		{
			name: "malformed auth header",
			headers: http.Header{
				"Authorization": []string{"Bearer abc123"},
			},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			if (err != nil) != tt.wantErr {
				t.Fatalf("error = %v, wantErr %v", err, tt.wantErr)
			}

			if got != tt.want {
				t.Errorf("got %q, want %q", got, tt.want)
			}
		})
	}
}
