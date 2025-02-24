// internal/auth/auth_test.go
package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	// Definimos los casos de prueba
	tests := []struct {
		name        string
		headers     http.Header
		want        string
		expectedErr error
	}{
		{
			name:        "No Authorization Header",
			headers:     http.Header{},
			want:        "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed Header - Missing ApiKey Prefix",
			headers: http.Header{
				"Authorization": []string{"Bearer 12345"},
			},
			want:        "",
			expectedErr: ErrMalformedAuthorizationHeader,
		},
		{
			name: "Malformed Header - Empty Key",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want:        "",
			expectedErr: ErrMalformedAuthorizationHeader,
		},
		{
			name: "Valid ApiKey Header",
			headers: http.Header{
				"Authorization": []string{"ApiKey my-secret-key"},
			},
			want:        "wrong-key", // Valor incorrecto
			expectedErr: nil,
		},
	}

	// Ejecutamos cada caso de prueba
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Llamamos a la función bajo prueba
			got, err := GetAPIKey(tt.headers)

			// Verificamos el valor retornado
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}

			// Verificamos el error retornado
			if (err != nil) != (tt.expectedErr != nil) {
				t.Fatalf("GetAPIKey() error = %v, wantErr %v", err, tt.expectedErr)
			}

			if err != nil && err.Error() != tt.expectedErr.Error() {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.expectedErr)
			}
		})
	}
}
