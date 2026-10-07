package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		wantKey string
		wantErr error
	}{
		"clave válida": {
			headers: http.Header{"Authorization": []string{"ApiKey mi-clave-secreta"}},
			wantKey: "mi-clave-secreta",
			wantErr: nil,
		},
		"sin header Authorization": {
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		"header malformado - prefijo incorrecto": {
			headers: http.Header{"Authorization": []string{"Bearer mi-clave-secreta"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		"header malformado - sin valor": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.headers)

			if gotKey != tc.wantKey {
				t.Errorf("clave: se obtuvo %q, se esperaba %q", gotKey, tc.wantKey)
			}

			if tc.wantErr == nil {
				if gotErr != nil {
					t.Errorf("error: se obtuvo %v, no se esperaba error", gotErr)
				}
				return
			}

			if gotErr == nil {
				t.Fatalf("error: no se obtuvo error, se esperaba %v", tc.wantErr)
			}

			if gotErr.Error() != tc.wantErr.Error() {
				t.Errorf("error: se obtuvo %q, se esperaba %q", gotErr, tc.wantErr)
			}
		})
	}
}
