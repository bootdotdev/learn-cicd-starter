package tests

import (
	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
	"reflect"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	got, _ := auth.GetAPIKey(nil)
	want := ""
	if !reflect.DeepEqual(got, want) {
		t.Errorf("GetAPIKey() = %v, want %v", got, want)
	}
}
