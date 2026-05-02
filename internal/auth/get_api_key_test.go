package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name        string
		headers     http.Header
		expectedKey string
		expectedErr error
	}{
		{
			name:        "No authorization header",
			headers:     http.Header{}, // пустой заголовок
			expectedKey: "",
			expectedErr: ErrNoAuthHeaderIncluded,
		},
		{
			name: "Malformed authorization header",
			headers: http.Header{
				"Authorization": []string{"Bearer token"},
			},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
		{
			name: "Valid authorization header",
			headers: http.Header{
				"Authorization": []string{"ApiKey 12345"},
			},
			expectedKey: "12345",
			expectedErr: nil,
		},
		{
			name: "Invalid authorization scheme",
			headers: http.Header{
				"Authorization": []string{"Bearer 12345"},
			},
			expectedKey: "",
			expectedErr: errors.New("malformed authorization header"),
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tt.headers)
			// Проверяем, что ключ и ошибка совпадают с ожидаемыми значениями
			if gotKey != tt.expectedKey || (gotErr != nil && gotErr.Error() != tt.expectedErr.Error()) {
				t.Errorf("GetAPIKey() = (%v, %v), want (%v, %v)", gotKey, gotErr, tt.expectedKey, tt.expectedErr)
			}
		})
	}
}
