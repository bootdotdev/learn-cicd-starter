package auth

import "testing"

func TestGetApiKey(t *testing.T) {
	header := make(map[string][]string)

	header["Authorization"] = append(header["Authorization"], "ApiKey 2432")
	apiKey, _ := GetAPIKey(header)

	if apiKey != "2432" {
		t.Errorf("Api Key does not match")
	}
}
