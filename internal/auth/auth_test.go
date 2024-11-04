package auth

import (
	"testing"
)

func TestAuth(t *testing.T) {
	tests := []struct {
		name     string
		input    interface{}
		wantErr  bool
		wantValue interface{}
	}{
		{
			name: "No input",
			input:    nil,
			wantErr:  false,
			wantValue: nil,
		},
		{
			name: "Valid input returns expected value",
			input: map[string]string{"username": "testuser", "password": "testpass"},
			wantErr:  false,
			wantValue: "testuser",
		},
		{
			name: "Invalid input returns error",
			input: map[string]string{"username": "", "password": ""},
			wantErr: true,
			wantValue: "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := auth(tt.input)
			if (err != nil) != tt.wantErr {
				t.Errorf("auth() error = %v wantErr %v", err, tt.wantErr)
				return
			}
			if !tt.wantErr && got == "" {
				t.Errorf("auth() returned empty string want value %v", tt.wantValue)
			} else if tt.wantErr && got != "" {
				t.Errorf("auth() returned %v wantErr %v", got, tt.wantErr)
			}
		})
	}
}
