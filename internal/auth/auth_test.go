package auth

import (
	"errors"
	"net/http"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr error
	}{
		{
			name: "success case",
			headers: http.Header{
				"Authorization": []string{"ApiKey secret123"},
			},
			want:    "secret123",
			wantErr: nil,
		},
		{
			name:    "missing authorization header",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "malformed header - wrong prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer secret123"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
		{
			name: "malformed header - no key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			// Check error cases
			if tt.wantErr != nil {
				if err == nil {
					t.Errorf("GetAPIKey() error = nil, wantErr %v", tt.wantErr)
					return
				}
				if err.Error() != tt.wantErr.Error() {
					t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
					return
				}
				return
			}

			// Check success cases
			if err != nil {
				t.Errorf("GetAPIKey() unexpected error = %v", err)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
