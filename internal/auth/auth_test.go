package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		wantKey string
		wantErr error
	}{
		{
			name:    "no header included",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:    "valid header",
			headers: http.Header{"Authorization": []string{"ApiKey 123321"}},
			wantKey: "123321",
			wantErr: nil,
		},
		{
			name:    "wrong format",
			headers: http.Header{"Authorization": []string{"ApiKey123321"}},
			wantKey: "",
			wantErr: MalformedAuthHeader,
		},
	}
	//headers := make(http.Header)
	//headers.Add("Authorization", "")
	//key, err := GetAPIKey(headers)
	//wantErr := ErrNoAuthHeaderIncluded
	//if key != "" {
	//	t.Fatalf("wanting an empty key, got: %v", key)
	//}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tt.headers)
			if tt.wantKey != gotKey {
				t.Errorf("expected: %v, got: %v", tt.wantKey, gotKey)
			}

			if !errors.Is(gotErr, tt.wantErr) {
				t.Errorf("expected: %v, got: %v", tt.wantErr, gotErr)
			}
		})
	}
}
