package auth

import (
	"log"
	"net/http"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {

	tests := map[string]struct {
		headerType    string
		headerCommand string
		want          string
		wantErr       bool
	}{
		"simple":           {headerType: "Authorization", headerCommand: "ApiKey Superduperkey", want: "Superduperkey"},
		"many commands":    {headerType: "Authorization", headerCommand: "ApiKey Superduperkey this is a long key", want: "Superduperkey"},
		"long key":         {headerType: "Authorization", headerCommand: "ApiKey supercalifragilisticexpialidocious", want: "supercalifragilisticexpialidocious"},
		"key with symbols": {headerType: "Authorization", headerCommand: "ApiKey Sup3r.duper7-ey", want: "Sup3r.duper7-ey"},
		"missing header":   {headerType: "", headerCommand: "", want: "", wantErr: true},
		"invalid format":   {headerType: "Authorization", headerCommand: "Bearer token", want: "", wantErr: true},
		"empty key":        {headerType: "Authorization", headerCommand: "ApiKey ", want: "", wantErr: true},
	}

	for name, h := range tests {
		headers := http.Header{}
		headers.Set(h.headerType, h.headerCommand)
		log.Printf("%s, %s", h.headerType, h.headerCommand)
		got, err := GetAPIKey(headers)
		if h.wantErr {
			if err == nil {
				t.Errorf("%s: expected error, got none", name)
			}
			// Success - we expected an error and got one
			return
		}
		if err != nil {
			t.Errorf("unexpected error: %v", err)
			return
		}
		if !reflect.DeepEqual(h.want, got) {
			t.Fatalf("%s: expected: %v, got: %v", name, h.want, got)
		}

	}
}

//test error messages
/*
if err.Error() != "expected error message" {
    t.Errorf("got error %q, want %q", err.Error(), "expected error message")
}
*/
