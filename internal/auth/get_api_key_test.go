package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectError bool
	}{
		{
			name:        "Pas de header Authorization",
			headers:     http.Header{},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "Format incorrect - Bearer",
			headers: http.Header{
				"Authorization": []string{"Bearer token123"},
			},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "Header valide avec ApiKey",
			headers: http.Header{
				"Authorization": []string{"ApiKey ma_cle_secrete"},
			},
			expectedKey: "ma_cle_secrete",
			expectError: false,
		},
	}

	for _, tc := range tests {
		t.Run(tc.name, func(t *testing.T) {
			key, err := GetAPIKey(tc.headers)
			if tc.expectError && err == nil {
				t.Errorf("Erreur attendue mais aucune erreur retournée")
			}
			if !tc.expectError && err != nil {
				t.Errorf("Aucune erreur attendue mais got: %v", err)
			}
			if key != tc.expectedKey {
				t.Errorf("Attendu '%s', obtenu '%s'", tc.expectedKey, key)
			}
		})
	}
}
