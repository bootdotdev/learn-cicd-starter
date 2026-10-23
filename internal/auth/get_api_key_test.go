package auth

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	cases := []struct {
		name      string
		in        map[string][]string
		want      string
		wantError string
	}{
		{
			name:      "properly formed authorization header",
			in:        map[string][]string{"Authorization": []string{"ApiKey ABCDEF0123456789"}},
			want:      "ABCDEF0123456789",
			wantError: "",
		},
		{
			name:      "no authorization header included",
			in:        map[string][]string{"Accept": []string{"application/json"}},
			want:      "",
			wantError: "no authorization header included",
		},
		{
			name:      "malformed authorization header",
			in:        map[string][]string{"Authorization": []string{"Api Key ABCDEF0123456789"}},
			want:      "",
			wantError: "malformed authorization header",
		},
	}
	for _, c := range cases {
		got, err := GetAPIKey(c.in)
		if err != nil && err.Error() != c.wantError {
			t.Errorf("GetAPIKey() got error %s, want %s", err, c.wantError)
		}
		if got != c.want {
			t.Errorf("GetAPIKey() got %q, want %q", got, c.want)
		}
	}
}
