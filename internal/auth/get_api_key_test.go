package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		input   http.Header
		want    string
		wantErr bool
	}{
		"valid api key": {
			input:   http.Header{"Authorization": []string{"ApiKey abc123"}},
			want:    "abc123",
			wantErr: false,
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			got, err := GetAPIKey(tc.input)

			if (err != nil) != tc.wantErr {
				t.Fatalf("unexpected status: err=%v, wantErr=%v", err, tc.wantErr)
			}
			if got != tc.want {
				t.Errorf("expected %q, got %q", tc.want, got)
			}
		})
	}
}
