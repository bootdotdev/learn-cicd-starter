package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct{
		name string
		header http.Header
		wantErr bool
	}{
		{
			name: "Exact API token",
			header: http.Header{
				"Authorization": []string{"ApiKey TOKEN_STRING"},
			},
			wantErr: false,
		},
		{
			name: "Has API token amidst other headers",
			header: http.Header{
				"Authorization": []string{"ApiKey TOKEN_STING", "Other SOME_OTHER_STRING"},
				"Non-Authorization": []string{"ApiKey NON_AUTH_TOKEN_STRING", "Another SOMETHING_ELSE"},
			},
			wantErr: false,
		},
		{
			name: "API token is missing amidst other headers",
			header: http.Header{
				"Authorization": []string{"Access-token TOKEN_STRING", "Other SOME_OTHER_STRING"},
				"Non-Authorization": []string{"ApiKey NON_AUTH_TOKEN_STRING", "Another SOMETHING_ELSE"},
			},
			wantErr: true,
		},
		{
			name: "Has no Authorization header",
			header: http.Header{
				"Non-Authorization": []string{"ApiKey NON_AUTH_TOKEN_STRING", "Another SOMETHING_ELSE"},
			},
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func (t *testing.T){
			token, err := GetAPIKey(tt.header)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr = %v", err, tt.wantErr)
			}
			if !tt.wantErr && token != "TOKEN_STRING" {
				t.Errorf("GetAPIKey() token = %v, Expected 'TOKEN_STRING'", token)
			}
		})
	}
}
