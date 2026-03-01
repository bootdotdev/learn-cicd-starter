package auth // Ensure this matches the package name in your auth.go file

import (
	"net/http"
	"testing"
)

func TestGetAPIKey_Failure(t *testing.T) {
	headers := http.Header{}
	headers.Set("Authorization", "ApiKey red-panda-99")

	got, _ := GetAPIKey(headers)

	// CHANGE THIS: Expect a different value than what is actually sent
	want := "wrong-key-to-force-ci-failure"

	if got != want {
		t.Errorf("FAILING FOR CI TEST: got %q, want %q", got, want)
	}
}
