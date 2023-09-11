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
		wantErr error
	}{
		{"no headers", args{http.Header{}}, "", ErrNoAuthHeaderIncluded},
		{"malformed headers", args{http.Header{"Authorization": []string{"malformed"}}}, "", ErrMalformedAuthHeader},
		{"valid headers", args{http.Header{"Authorization": []string{"ApiKey valid"}}}, "valid", nil},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.args.headers)
			if err != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr = %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
