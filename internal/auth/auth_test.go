package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {
	tests := map[string]struct {
		header http.Header
		expect string
	}{
		"validApiKey": {
			header: http.Header{"Authorization": []string{"ApiKey 12345"}},
			expect: "12345",
		},
		"missingApiKey": {
			header: http.Header{},
			expect: "",
		},
		"malformedApiKey": {
			header: http.Header{"Authorization": []string{"Api Key 12345"}},
			expect: "",
		},
	}

	for name, test := range tests {
		result, _ := GetAPIKey(test.header)
		if result != test.expect {
			t.Fatalf("%s: expected %s, got %s", name, test.expect, result)
		}
	}
}
