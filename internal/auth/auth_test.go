package auth

import (
	"errors"
	"net/http/httptest"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     map[string]string
		want        string
		expectedErr error
	}{
		{
			name:        "no authorization header",
			headers:     nil,
			want:        "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed authorization header",
			headers: map[string]string{
				"Authorization": "Bearer token",
			},
			want:        "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "invalid authorization format",
			headers: map[string]string{
				"Authorization": "ApiKey",
			},
			want:        "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "valid authorization header",
			headers: map[string]string{
				"Authorization": "ApiKey valid-key-123",
			},
			want:        "valid-key-123",
			expectedErr: nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			for k, v := range tt.headers {
				req.Header.Set(k, v)
			}

			got, err := GetAPIKey(req.Header)
			if err != nil && err.Error() != tt.expectedErr.Error() {
				t.Fatalf("expected error %v, got %v", tt.expectedErr, err)
			}
			if err == nil && got != tt.want {
				t.Fatalf("expected %s, got %s", tt.want, got)
			}
		})
	}
}
