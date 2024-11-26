package auth

import (
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	headers1 := http.Header{
		"Content-Type": []string{"application/json"},
	}

	headers2 := http.Header{
		"Authorization": []string{"Bearer B10ijfjlkj393jslsjf2"},
	}

	headers3 := http.Header{
		"Authorization": []string{"ApiKey"},
	}

	headers4 := http.Header{
		"Authorization": []string{"ApiKey B10ijfjlkj393jslsjf2"},
	}

	type args struct {
		headers http.Header
	}
	tests := []struct {
		name    string
		args    args
		want    string
		wantErr bool
	}{
		{
			name: "Test 1 - No auth header included",
			args: args{
				headers: headers1,
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Test 2 - Authorization header missing keyword 'ApiKey'",
			args: args{
				headers: headers2,
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Test 3 - Authorization header too short - malformed",
			args: args{
				headers: headers3,
			},
			want:    "",
			wantErr: true,
		},
		{
			name: "Test 4 - No errors - everything works",
			args: args{
				headers: headers4,
			},
			want:    "B10ijfjlkj393jslsjf2",
			wantErr: false,
		},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := GetAPIKey(tt.args.headers)
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
