package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKeySuccess(t *testing.T) {
	token := "3terfsfafsa3rregdrfg"
	tests := []struct {
		name    string
		header  http.Header
		wantRes string
		wantErr error
	}{
		{
			name: "Valid API Key",
			header: http.Header{
				"Authorization": []string{"ApiKey " + token},
			},
			wantRes: token,
			wantErr: nil,
		},
		{
			name: "No API Key",
			header: http.Header{
				"Authorization": []string{""},
			},
			wantRes: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			res, err := GetAPIKey(tt.header)
			if err != nil && err.Error() != tt.wantErr.Error() {
				t.Errorf("Expected error %v, got %v", tt.wantErr, err)
			}
			if res != tt.wantRes {
				t.Errorf("Expected %s, got %s", tt.wantRes, res)
			}
		})
	}
}
