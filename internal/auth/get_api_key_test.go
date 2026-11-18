package auth

import (
	"net/http"
	"testing"
)

func TestGetApiKey(t *testing.T) {

	tests := []struct {
		name         string
		inputHeaders http.Header
		expectedKey  string
		shouldError  bool
	}{
		{
			name:         "Правильный заголовок",
			inputHeaders: http.Header{"Authorization": []string{"ApiKey 123456"}},
			expectedKey:  "123456",
			shouldError:  false,
		},
		{
			name:         "Нет заголовка",
			inputHeaders: http.Header{},
			shouldError:  true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			key, err := GetAPIKey(tt.inputHeaders)

			if (err != nil) != tt.shouldError {
				t.Errorf("Ошибка %v,ожидали что ошибка будет %v", err, tt.shouldError)
				return
			}

			if key != tt.expectedKey {
				t.Errorf("Ожидали %v, получили %v", tt.expectedKey, key)
			}

		})
	}

}
