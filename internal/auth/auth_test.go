package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := []struct {
		name       string
		authHeader string
		want       string
		wantErr    bool
	}{
		{
			name:       "no auth header",
			authHeader: "",
			want:       "",
			wantErr:    true,
		},
		{
			name:       "wrong scheme (Bearer)",
			authHeader: "Bearer abc123",
			want:       "",
			wantErr:    true,
		},
		{
			name:       "missing token after ApiKey",
			authHeader: "ApiKey",
			want:       "",
			wantErr:    true,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			h := http.Header{}
			if test.authHeader != "" {
				h.Set("Authorization", test.authHeader)
			}
			got, err := GetAPIKey(h)

			if test.wantErr && err == nil {
				t.Fatalf("expected error, got nil (key=%q)", got)
				return
			}
			if test.wantErr && err != nil {
				t.Fatalf("expected no error, got %v", err)
				return
			}
			if got != test.want {
				t.Fatalf("expected key=%q, got %q", test.want, got)
				return
			}
		})
	}
}
