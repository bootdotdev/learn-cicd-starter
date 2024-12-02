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
			name: "empty",
			args: args{
				headers: map[string][]string{},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "blah authorization",
			args: args{
				headers: map[string][]string{
					"Authorization": {
						"blah",
					},
				},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Blah ApiKey",
			args: args{
				headers: map[string][]string{
					"Authorization": {
						"ApiKey blah",
					},
				},
			},
			want:    "blah",
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
