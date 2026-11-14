package auth

import "testing"

func TestGetAPIKey(t *testing.T) {
	_, err := GetAPIKey(nil)

	if err == nil {
		t.Fail()
	}
}
