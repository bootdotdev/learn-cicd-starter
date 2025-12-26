package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	type tc struct {
		name       string
		header     http.Header
		wantKey    string
		wantErr    error
		errMessage string // düz string karşılaştırması gereken durumlarda
	}

	makeHeader := func(v string) http.Header {
		h := http.Header{}
		if v != "" {
			h.Set("Authorization", v)
		}
		return h
	}

	tests := []tc{
		{
			name:    "no Authorization header",
			header:  makeHeader(""),
			wantErr: ErrNoAuthHeaderIncluded,
		},
		{
			name:       "wrong scheme (Bearer)",
			header:     makeHeader("Bearer abc123"),
			wantErr:    errors.New("malformed authorization header"),
			errMessage: "malformed authorization header",
		},
		{
			name:       "missing API key after scheme",
			header:     makeHeader("ApiKey"),
			wantErr:    errors.New("malformed authorization header"),
			errMessage: "malformed authorization header",
		},
		{
			name:    "valid ApiKey <token>",
			header:  makeHeader("ApiKey secret-123"),
			wantKey: "secret-123",
		},
		{
			name:   "extra parts -> halen ikinci parça alınır",
			header: makeHeader("ApiKey part1 part2"),
			// mevcut implementasyon strings.Split kullanıyor, bu yüzden ikinci parça döner
			// (beklenen davranış buysa anahtar "part1" olur; daha katı istenirse fonksiyon güncellenmeli)
			wantKey: "part1",
		},
		{
			name:       "scheme case-sensitive (apikey yerine ApiKey bekleniyor)",
			header:     makeHeader("apikey abc"),
			wantErr:    errors.New("malformed authorization header"),
			errMessage: "malformed authorization header",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.header)

			if tt.wantErr != nil {
				if err == nil {
					t.Fatalf("expected error, got nil")
				}
				// ErrNoAuthHeaderIncluded sabitini errors.Is ile kontrol edelim
				if errors.Is(tt.wantErr, ErrNoAuthHeaderIncluded) {
					if !errors.Is(err, ErrNoAuthHeaderIncluded) {
						t.Fatalf("expected ErrNoAuthHeaderIncluded, got %v", err)
					}
					return
				}
				// strings.New ile üretilen generic hata için mesajı kıyaslıyoruz
				if err.Error() != tt.errMessage {
					t.Fatalf("expected error %q, got %q", tt.errMessage, err.Error())
				}
				return
			}

			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if got != tt.wantKey {
				t.Fatalf("expected key %q, got %q", tt.wantKey, got)
			}
		})
	}
}
