package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type args struct {
		headers map[string][]string
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "no auth header",
			args: args{
				headers: map[string][]string{},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "valid auth header",
			args: args{
				headers: map[string][]string{
					"Authorization": {"ApiKey abc123"},
				},
			},
			want:    "abc123",
			wantErr: false,
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
