package auth

import (
	"net/http"
	"testing"
)

func Test_APIKEY(t *testing.T) {
	tests := []struct {
		name    string
		input   http.Header
		want    string
		wantErr bool
	}{
		{
			name:    "Valid header",
			input:   http.Header{"Authorization": []string{"ApiKey abc123"}},
			want:    "abc123",
			wantErr: false,
		},
		{
			name:    "Empty Header",
			input:   http.Header{},
			wantErr: true,
		},
		{
			name:    "Malformed header",
			input:   http.Header{"Authorization": []string{"Bearer abc123"}},
			want:    "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.input)

			if (err != nil) != tt.wantErr {
				t.Fatalf("unexpected error state: %v", err)
			}

			if got != tt.want {
				t.Fatalf("got %q, want %q", got, tt.want)
			}
		})
	}
}
