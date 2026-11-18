package auth

import (
	"os"
	"testing"
)

func TestGetAPIKey_FromEnv(t *testing.T) {
	// t.Setenv está disponível em Go 1.17+ e restaura automaticamente ao fim do teste
	t.Setenv("NOTELY_API_KEY", "env-key-123")

	got := GetAPIKey()
	want := "env-key-123"

	if got != want {
		t.Fatalf("GetAPIKey() = %q; want %q", got, want)
	}
}

func TestGetAPIKey_EmptyWhenUnset(t *testing.T) {
	// Assegura que a env está limpa
	os.Unsetenv("NOTELY_API_KEY")

	got := GetAPIKey()
	if got != "" {
		t.Fatalf("expected empty string when env unset, got %q", got)
	}
}
