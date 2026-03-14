package auth

import (
	"os"
	"testing"
)

// Test when API_KEY is set
func TestGetAPIKey_Set(t *testing.T) {
	expected := "12345"
	os.Setenv("API_KEY", expected)
	defer os.Unsetenv("API_KEY")

	got := GetAPIKey()
	if got != expected {
		t.Errorf("expected %s, got %s", expected, got)
	}
}

// Test when API_KEY is not set
func TestGetAPIKey_NotSet(t *testing.T) {
	os.Unsetenv("API_KEY")

	got := GetAPIKey()
	if got != "" {
		t.Errorf("expected empty string, got %s", got)
	}
}


package auth

import (
	"os"
	"testing"
)

// Test when API_KEY is set
func TestGetAPIKey_Set(t *testing.T) {
	expected := "12345"
	os.Setenv("API_KEY", expected) // set a fake API key
	defer os.Unsetenv("API_KEY")

	got := GetAPIKey()
	if got != expected {
		t.Errorf("expected %s, got %s", expected, got)
	}
}

// Test when API_KEY is NOT set
func TestGetAPIKey_NotSet(t *testing.T) {
	os.Unsetenv("API_KEY") // clear env variable

	got := GetAPIKey()
	if got != "" {
		t.Errorf("expected empty string, got %s", got)
	}
}
package auth

import "testing"

func TestGetAPIKey(t *testing.T) {
    key := GetAPIKey("Authorization: ApiKey 12345")
    expected := "12345"

    if key != expected {
        t.Errorf("Expected %s but got %s", expected, key)
    }
}

