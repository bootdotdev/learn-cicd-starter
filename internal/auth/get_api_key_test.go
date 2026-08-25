package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name       string
		headerVal  string // value to set for "Authorization" header; empty means don't set it
		setHeader  bool
		wantKey    string
		wantErr    error // if non-nil, we expect errors.Is to match this
		wantErrMsg string // if wantErr is nil but we still expect an error, check message text
	}{
		{
			name:      "no auth header",
			setHeader: false,
			wantKey:   "",
			wantErr:   ErrNoAuthHeaderIncluded,
		},
		{
			name:       "malformed header - no space",
			setHeader:  true,
			headerVal:  "ApiKey",
			wantKey:    "",
			wantErrMsg: "malformed authorization header",
		},
		{
			name:       "malformed header - wrong prefix",
			setHeader:  true,
			headerVal:  "Bearer abc123",
			wantKey:    "",
			wantErrMsg: "malformed authorization header",
		},
		{
			name:      "valid header",
			setHeader: true,
			headerVal: "ApiKey abc123",
			wantKey:   "abc123",
			wantErr:   nil,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			headers := http.Header{}
			if tt.setHeader {
				headers.Set("Authorization", tt.headerVal)
			}

			gotKey, err := GetAPIKey(headers)

			if gotKey != tt.wantKey {
				t.Errorf("got key %q, want %q", gotKey, tt.wantKey)
			}

			switch {
			case tt.wantErr != nil:
				if !errors.Is(err, tt.wantErr) {
					t.Errorf("got err %v, want %v", err, tt.wantErr)
				}
			case tt.wantErrMsg != "":
				if err == nil || err.Error() != tt.wantErrMsg {
					t.Errorf("got err %v, want message %q", err, tt.wantErrMsg)
				}
			default:
				if err != nil {
					t.Errorf("got unexpected err %v", err)
				}
			}
		})
	}
}
