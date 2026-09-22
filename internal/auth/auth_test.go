package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    map[string][]string
		wantAPIKey string
		wantErr    bool
	}{
		{
			name:       "valid header",
			headers:    map[string][]string{"Authorization": {"ApiKey my-secret-key"}},
			wantAPIKey: "my-secret-key",
			wantErr:    false,
		},
		{
			name:    "no header",
			headers: map[string][]string{},
			wantErr: true,
		},
		{
			name:    "malformed header - no space",
			headers: map[string][]string{"Authorization": {"ApiKeymy-secret-key"}},
			wantErr: true,
		},
		{
			name:    "malformed header - wrong prefix",
			headers: map[string][]string{"Authorization": {"Bearer my-secret-key"}},
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotAPIKey, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if gotAPIKey != tt.wantAPIKey {
				t.Errorf("GetAPIKey() gotAPIKey = %v, want %v", gotAPIKey, tt.wantAPIKey)
			}
		})
	}
}
