package auth

import "testing"

func TestGetAPIKey(t *testing.T) {
	headers := map[string][]string{
		"Authorization": {"ApiKey 123"},
	}

	got, _ := GetAPIKey(headers)
	want := "123"

	if got != want {
		t.Errorf("got %q want %q", got, want)
	}

	_, err := GetAPIKey(map[string][]string{})
	if err != ErrNoAuthHeaderIncluded {
		t.Errorf("got %q want %q", err, ErrNoAuthHeaderIncluded)
	}

	_, err = GetAPIKey(map[string][]string{"Authorization": {"123"}})
	if err == nil {
		t.Errorf("got %q want %q", err, "malformed authorization header")
	}
}
