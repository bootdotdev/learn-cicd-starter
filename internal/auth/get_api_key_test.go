package auth

import (
	"net/http"
	"testing"
)

func TestBasicGetAPIKey(t *testing.T) {
	headers := http.Header{
		"Authorization": []string{"ApiKey valid_api_key"},
	}

	resp, err := GetAPIKey(headers)
	if err != nil {
		t.Errorf("TestBasicGetAPIKey error = %v", err)
	}

	if resp != "valid_api_key" {
		t.Errorf("TestBasicGetAPIKey, resp != expected")
	}
} // End TestBasicGetAPIKey() test
