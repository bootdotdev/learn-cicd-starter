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
			name: "Validni API ključ",
			headers: http.Header{
				"Authorization": []string{"ApiKey moj_tajni_kljuc_123"},
			},
			expectedKey: "moj_tajni_kljuc_123",
			expectError: false,
		},
		{
			name:        "Nedostaje Authorization zaglavlje",
			headers:     http.Header{},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "Pogrešan format - nedostaje ApiKey prefiks",
			headers: http.Header{
				"Authorization": []string{"samo_kljuc"},
			},
			expectedKey: "",
			expectError: true,
		},
		{
			name: "Pogrešna šema - koristi Bearer umesto ApiKey",
			headers: http.Header{
				"Authorization": []string{"Bearer neki_token"},
			},
			expectedKey: "",
			expectError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.headers)

			if (err != nil) != tt.expectError {
				t.Errorf("GetAPIKey() greška = %v, očekivana greška %v", err, tt.expectError)
				return
			}

			if key != tt.expectedKey {
				t.Errorf("GetAPIKey() = %v, očekivano %v", key, tt.expectedKey)
			}
		})
	}
}
