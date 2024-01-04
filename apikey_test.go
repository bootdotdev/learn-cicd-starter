package apikey

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	expectedAPIKey := "your-api-key"
	actualAPIKey := GetAPIKey()
	if actualAPIKey != expectedAPIKey {
		t.Errorf("Expected API Key (%s) is not same as actual API key (%s)", expectedAPIKey, actualAPIKey)
	}
}
