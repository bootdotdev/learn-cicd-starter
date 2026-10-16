package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headers    http.Header
		wantKey    string
		wantErr    error
		wantErrMsg string // used when we only care about error text, not a sentinel
	}{
		{
			name:    "valid api key",
			headers: http.Header{"Authorization": []string{"ApiKey abc123"}},
			wantKey: "abc123",
			wantErr: nil,
		},
		{
			name:    "missing authorization header",
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:       "malformed header - no space",
			headers:    http.Header{"Authorization": []string{"ApiKeyabc123"}},
			wantKey:    "",
			wantErrMsg: "malformed authorization header",
		},
		{
			name:       "malformed header - wrong prefix",
			headers:    http.Header{"Authorization": []string{"Bearer abc123"}},
			wantKey:    "",
			wantErrMsg: "malformed authorization header",
		},
		{
			name:       "malformed header - only prefix, no key",
			headers:    http.Header{"Authorization": []string{"ApiKey"}},
			wantKey:    "",
			wantErrMsg: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tt.headers)

			if gotKey != tt.wantKey {
				t.Errorf("got key %q, want %q", gotKey, tt.wantKey)
			}

			switch {
			case tt.wantErr != nil:
				if !errors.Is(gotErr, tt.wantErr) {
					t.Errorf("got err %v, want %v", gotErr, tt.wantErr)
				}
			case tt.wantErrMsg != "":
				if gotErr == nil || gotErr.Error() != tt.wantErrMsg {
					t.Errorf("got err %v, want message %q", gotErr, tt.wantErrMsg)
				}
			default:
				if gotErr != nil {
					t.Errorf("got unexpected err %v", gotErr)
				}
			}
		})
	}
}
