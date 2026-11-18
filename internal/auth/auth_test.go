package auth

import (
	"net/http/httptest"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	casos := []struct {
		nombre        string
		headerValue   string
		esperaError   bool
		claveEsperada string
	}{
		{
			nombre:        "Header válido",
			headerValue:   "ApiKey secreto123",
			esperaError:   false,
			claveEsperada: "secreto123",
		},
		{
			nombre:      "Header ausente",
			headerValue: "",
			esperaError: true,
		},
		{
			nombre:      "Prefijo incorrecto",
			headerValue: "Bearer secreto123",
			esperaError: true,
		},
		{
			nombre:      "Sin espacio entre prefijo y clave",
			headerValue: "ApiKeysecreto123",
			esperaError: true,
		},
		{
			nombre:      "Demasiados tokens",
			headerValue: "ApiKey uno dos",
			esperaError: true,
		},
	}

	for _, c := range casos {
		t.Run(c.nombre, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			if c.headerValue != "" {
				req.Header.Set("Authorization", c.headerValue)
			}

			apiKey, err := GetAPIKey(req.Header)
			if c.esperaError && err == nil {
				t.Fatalf("se esperaba un error pero no se recibió ninguno")
			}
			if !c.esperaError && err != nil {
				t.Fatalf("no se esperaba error, pero se obtuvo: %v", err)
			}
			if !c.esperaError && apiKey != c.claveEsperada {
				t.Errorf("se esperaba clave '%s', pero se obtuvo '%s'", c.claveEsperada, apiKey)
			}
		})
	}
}
