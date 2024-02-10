package your_package

import (
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	expected := "expected_api_key"
	apiKey := GetAPIKey()

	if apiKey != expected {
		t.Errorf("GetAPIKey() = %v; want %v", apiKey, expected)
	}
}