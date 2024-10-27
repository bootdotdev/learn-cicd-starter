package auth

import(
  "reflect"
  "testing"
)

func TestGetAPIKey(t *testing.T){
  got:= GetAPIKey("")
  want:=[]string{"a"}
  if !reflect.DeepEqual(want, got){
    t.Fatalf("fatal")
  }
}
