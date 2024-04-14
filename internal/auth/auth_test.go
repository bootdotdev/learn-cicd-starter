package auth

import (
	"testing"
)

func TestAuth_Fail_Empty(t *testing.T) {
	head := map[string][]string{
		"Authorization": {""},
	}
	_, err := GetAPIKey(head)
	if err == nil {
		t.Fail()
	}
}

func TestAuth_Fail_InvalidKey(t *testing.T) {
	head := map[string][]string{
		"Authorization": {"{API-KEY}"},
	}
	_, err := GetAPIKey(head)
	if err == nil {
		t.Fail()
	}
}

func TestAuth_Fail_Pass(t *testing.T) {
	head := map[string][]string{
		"Authorization": {"ApiKey XXXXX"},
	}
	apiKey, err := GetAPIKey(head)
	if err != nil {
		t.Fail()
	}
	if apiKey != "XXXXX" {
		t.Fail()
	}
}
