package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestAPIHeaders(t *testing.T) {
	tests := map[string]struct {
		inputHeader       string
		want              string
		expectError       bool
		expectedError     error
		expectedErrorText string // Name muss mit Zugriff übereinstimmen
	}{
		"simple":         {inputHeader: "ApiKey xyz", want: "xyz", expectError: false},
		"wrong sep":      {inputHeader: "ApiKey/xyz", want: "", expectError: true, expectedErrorText: "malformed authorization header"},
		"no sep":         {inputHeader: "ApiKeyxyz", want: "", expectError: true, expectedErrorText: "malformed authorization header"},
		"no input":       {inputHeader: "", want: "", expectError: true, expectedError: ErrNoAuthHeaderIncluded},
		"no ApiKey":      {inputHeader: "IpaKey xyz", want: "", expectError: true, expectedErrorText: "malformed authorization header"},
		"more input":     {inputHeader: "ApiKey xyz xyz", want: "xyz", expectError: false},
		"only API Key":   {inputHeader: "ApiKey", want: "", expectError: true, expectedErrorText: "malformed authorization header"},
	}

	for name, tc := range tests {
		// Best Practice: Variable shadowing.
		// Sichert ab, dass 'tc' in diesem Scope isoliert ist (wichtig bei Pointern oder t.Parallel())
		tc := tc 
		
		t.Run(name, func(t *testing.T) {
			headers := http.Header{}
			headers.Set("Authorization", tc.inputHeader)

			got, err := GetAPIKey(headers)

			// 1. Prüfen ob generell ein Error kam (Ja/Nein)
			if (err != nil) != tc.expectError {
				t.Fatalf("error expectations mismatch: got error: %v, expectError: %v", err, tc.expectError)
			}

			// 2. Fehlerprüfung im Detail
			if err != nil {
				// Fall A: Wir erwarten einen spezifischen Sentinel Error (Variable)
				if tc.expectedError != nil {
					if !errors.Is(err, tc.expectedError) {
						t.Errorf("expected error variable %v, got %v", tc.expectedError, err)
					}
				}

				// Fall B: Wir erwarten einen spezifischen Fehlertext
				// Hier habe ich den Tippfehler korrigiert: tc.expectedErrorText statt tc.expectedErrText
				if tc.expectedErrorText != "" {
					if err.Error() != tc.expectedErrorText {
						t.Errorf("expected error text %q, got %q", tc.expectedErrorText, err.Error())
					}
				}
			}

			// 3. Ergebnisprüfung
			if got != tc.want {
				t.Errorf("got result %q, want %q", got, tc.want)
			}
		})
	}
}
