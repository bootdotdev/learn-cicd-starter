package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		header       http.Header
		wantKey      string
		wantErr      bool
		wantSentinel error
	}{
		"no auth header": {
			header:       http.Header{},
			wantErr:      true,
			wantSentinel: ErrNoAuthHeaderIncluded,
		},
		"missing key after ApiKey": {
			header:  http.Header{"Authorization": []string{"ApiKey"}},
			wantErr: true,
		},
		"wrong auth keyword": {
			header:  http.Header{"Authorization": []string{"Bearer abcdh"}},
			wantErr: true,
		},
		"case-sensitive keyword": {
			header:  http.Header{"Authorization": []string{"apikey abcdh"}},
			wantErr: true,
		},
		"good apikey": {
			header:  http.Header{"Authorization": []string{"ApiKey abcdh"}},
			wantKey: "abcdh",
		},
	}
	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.header)

			if gotKey != tc.wantKey {
				t.Errorf("key = %q, want %q", gotKey, tc.wantKey)
			}

			if (gotErr != nil) != tc.wantErr {
				t.Errorf("error = %v, wantErr %v", gotErr, tc.wantErr)
			}

			if tc.wantSentinel != nil && !errors.Is(gotErr, tc.wantSentinel) {
				t.Errorf("error = %v, want %v", gotErr, tc.wantSentinel)
			}
		})
	}
}
