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
		want    string
		wantErr error
	}{
		{
			name:    "no authorization header",
			headers: http.Header{},
			want:    "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "valid api key",
			headers: http.Header{
				"Authorization": []string{"ApiKey test-api-key"},
			},
			want:    "test-api-key",
			wantErr: nil,
		},
		{
			name: "malformed authorization header",
			headers: http.Header{
				"Authorization": []string{"Bearer test-token"},
			},
			want:    "",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)

			if got != tt.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tt.want)
			}

			if tt.wantErr != nil {
				if err == nil || err.Error() != tt.wantErr.Error() {
					t.Errorf("GetAPIKey() error = %v, want %v", err, tt.wantErr)
				}
			} else if err != nil {
				t.Errorf("GetAPIKey() unexpected error = %v", err)
			}
		})
	}
}
