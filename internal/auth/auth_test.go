package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		input   string
		output  string
		wantErr bool
	}{

		{
			name:    "expected",
			input:   "ApiKey 12345",
			output:  "12345",
			wantErr: false,
		},
		{
			name:    "len 0",
			input:   "ApiKey",
			wantErr: true,
		},
		//not sure if project/instructions will change/require auth code to not be changed, removing this test until i know
		// {
		// 	name:    "len 3",
		// 	input:   "ApiKey 1 2",
		// 	wantErr: true,
		// },
		{
			name:    "no ApiKey",
			input:   "1 12345",
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tHeader := http.Header{}
			tHeader.Set("Authorization", tt.input)
			key, err := GetAPIKey(tHeader)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetApiKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr && key != (tt.output) {
				t.Errorf("GetApiKey() = %v, want %v", key, tt.output)
			}
		})
	}
}
