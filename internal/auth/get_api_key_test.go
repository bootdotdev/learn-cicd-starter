package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name  string
		input http.Header
		want  string
		err   error
	}{
		{
			name:  "no auth header",
			input: http.Header{},
			want:  "",
			err:   ErrNoAuthHeaderIncluded,
		},
	}

	for _, tt := range tests {
		got, err := GetAPIKey(tt.input)
		if got != tt.want {
			t.Error("diff results")
		}
		if err != tt.err {
			t.Errorf("GetAPIKey() error = %v, want %v", err, tt.err)
		}
	}
}
