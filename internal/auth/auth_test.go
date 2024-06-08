package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	t.Run("no authheader", func(t *testing.T) {
		empty := http.Header{}
		_, err := GetAPIKey(empty)
		if err != ErrNoAuthHeaderIncluded {
			t.Errorf("expected error '%v' but got '%v'", ErrNoAuthHeaderIncluded, err)
		}
	})

	t.Run("valid authheader", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "ApiKey myActualAPIKey")

		got, err := GetAPIKey(headers)
		want := "myActualAPIKey"

		if err != nil {
			t.Fatalf("unexpected error: %v", err)
		}

		if got != want {
			t.Errorf("expected '%s' but got '%s'", want, got)
		}
	})

	t.Run("malformed authheader", func(t *testing.T) {
		headers := http.Header{}
		headers.Set("Authorization", "BREAK myActualAPIKey")

		_, err := GetAPIKey(headers)
		expectedErr := "dummy fail"

		// expectedErr := "malformed authorization header"

		if err == nil || err.Error() != expectedErr {
			t.Errorf("expected error '%v' but got '%v'", expectedErr, err)
		}
	})

}
