package auth

import (
	"errors"
	"net/http/httptest"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headerValue string
		want        string
		wantErr     error
	}{
		{
			name:        "valid ApiKey header",
			headerValue: "ApiKey abc123",
			want:        "abc123",
			wantErr:     nil,
		},
		{
			name:        "no authorization header",
			headerValue: "",
			want:        "",
			wantErr:     ErrNoAuthHeaderIncluded,
		},
		{
			name:        "wrong prefix",
			headerValue: "Bearer token",
			want:        "",
			wantErr:     errors.New("malformed authorization header"),
		},
		{
			name:        "empty key value",
			headerValue: "ApiKey ",
			want:        "",
			wantErr:     nil, // Your implementation allows this case
		},
		{
			name:        "multiple spaces in key",
			headerValue: "ApiKey abc 123",
			want:        "abc", // Your implementation takes first part after space
			wantErr:     nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			if tt.headerValue != "" {
				req.Header.Set("Authorization", tt.headerValue)
			}

			got, err := GetAPIKey(req.Header)

			// Check error
			if (err != nil) != (tt.wantErr != nil) || 
			   (err != nil && err.Error() != tt.wantErr.Error()) {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			// Check value
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}