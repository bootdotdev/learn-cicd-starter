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
			name: "Get the api key successfully",
			args: args{
				headers: http.Header{
					"Authorization": []string{"ApiKey mytoken"},
				},
			},
			want: "mytoken",
		},
		{
			name: "Fail for no auth header",
			args: args{
				headers: http.Header{},
			},
			wantErr: true,
		},
		{
			name: "Fail for invalid auth header length",
			args: args{
				headers: http.Header{
					"Authorization": []string{"ApiKeymytokeniswrong"},
				},
			},
			wantErr: true,
		},
		{
			name: "Fail for invalid auth header prefix",
			args: args{
				headers: http.Header{
					"Authorization": []string{"Token mytokeniswrong"},
				},
			},
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
