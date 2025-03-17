package auth

import (
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	want := []string{"a"}
	got := []string{"a"}
	if !reflect.DeepEqual(want, got) {
		t.Fatalf("fatal")
	}
}
