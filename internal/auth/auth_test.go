package auth

import (
	"net/http"
	"testing"
)


func TestBadGetAPIKey(t *testing.T){
    testH := make(http.Header)
    testH.Add("Authorization", "")
    apikey, err := GetAPIKey(testH)
    if err == nil || apikey != ""{
        t.Logf("err: %v | apikey: %v", err, apikey)
        t.Fatalf("Error should be filled and/or apikey should be default val\n")

    }
}

func TestGoodGetAPIKey(t *testing.T){
    testH := make(http.Header)
    testH.Add("Authorization", "ApiKey test@123test")
    apikey, err := GetAPIKey(testH)
    if err != nil || apikey == ""{
        t.Logf("err: %v | apikey: %v", err, apikey)
        t.Fatalf("Error should not be filled and/or apikey should not be default val\n")
    }

}
