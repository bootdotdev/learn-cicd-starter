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
			"no auth header",
			args{map[string][]string{}},
			"",
			true,
		},
		{
			"malformed auth header",
			args{map[string][]string{"Authorization": {"Bearer"}}},
			"",
			true,
		},
		{
			"valid auth header",
			args{map[string][]string{"Authorization": {"ApiKey 123"}}},
			"123",
			false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := make(map[string][]string)
			for k, v := range tt.args.headers {
				headers[k] = v
			}
			got, err := GetAPIKey(headers)
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
