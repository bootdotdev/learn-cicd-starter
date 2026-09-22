package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := []struct {
		name    string
		headers http.Header
		want    string
		wantErr bool
	}{
		{
			name: "Isječak s ispravnim ApiKey zaglavljem",
			headers: http.Header{
				"Authorization": []string{"ApiKey secret123"},
			},
			want:    "secret123",
			wantErr: false,
		},
		{
			name:    "Nedostaje Authorization zaglavlje",
			headers: http.Header{},
			want:    "",
			wantErr: true,
		},
		{
			name: "Neispravan format - pogrešan prefiks (Bearer)",
			headers: http.Header{
				"Authorization": []string{"Bearer secret123"},
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Neispravan format - nedostaje vrijednost ključa",
			headers: http.Header{
				"Authorization": []string{"ApiKey"},
			},
			want:    "",
			wantErr: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.headers)
			if (err != nil) != tt.wantErr {
				t.Errorf("GetAPIKey() error = %v, wantErr %v", err, tt.wantErr)
				return
			}
			if got != tt.want {
				t.Errorf("GetAPIKey() = %v, want %v", got, tt.want)
			}
		})
	}
}
