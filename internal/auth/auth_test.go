package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type args struct {
		headers http.Header
	}

	validHeader := http.Header{}
	validHeader.Set("Authorization", "ApiKey 12345")

	missingApiKeyHeader := http.Header{}
	missingApiKeyHeader.Set("Authorization", "Bearer 12345")

	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		// TODO: Add test cases.
		{
			name:    "Test valid ApiKey Authorization header",
			args:    args{headers: validHeader},
			want:    "12345",
			wantErr: false,
		}, {
			name:    "Test missing ApiKey type in Authorization header",
			args:    args{headers: missingApiKeyHeader},
			want:    "",
			wantErr: true,
		}, {
			name:    "Test missing authorization header",
			args:    args{headers: http.Header{}},
			want:    "",
			wantErr: true,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.args.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() got = %v, want %v", got, tt.want)
			}
		})
	}
}
