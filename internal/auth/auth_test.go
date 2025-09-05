package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type args struct {
		headers http.Header
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "Valid ApiKey header",
			args: args{
				headers: http.Header{
					"Authorization": []string{"ApiKey secretKey"},
				},
			},
			want:    "secretKey",
			wantErr: false,
		},
		{
			name: "missing AUthorization header",
			args: args{
				headers: http.Header{},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "malformed authorization header",
			args: args{
				headers: http.Header{
					"Authorization": []string{"Bearer token"},
				},
			},
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
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
