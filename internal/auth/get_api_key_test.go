package auth

import (
	"net/http"
	"reflect"
	"testing"
)

func TestSplit(t *testing.T) {

    newHead := make(map[string][]string)
    newHead["Authorization"] = make([]string, 1)
    newHead["Authorization"] =[]string{"ApiKey blabla", "something"}

    tests := []struct {
        input http.Header
        want  string
    }{
        {input: newHead, want: "blabla"},
        {input: http.Header{
            "Authorization": []string{"ApiKeyblabla", "something"},
        }, want: "" },
    }

    for i, tc := range tests {
        got, got2 := GetAPIKey(tc.input)
        if !reflect.DeepEqual(tc.want, got) {
            t.Fatalf("test %d: expected: %v, got: %v and the error %v", i+1, tc.want, got, got2)
        }
    }
}