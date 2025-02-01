package auth

import(

 	"net/http"
    "testing"

)


func TestGetAPIKey(t *testing.T){

	t.Run( "mytest1", func(t *testing.T){

		headers := http.Header{}
		
		key, err := GetAPIKey(headers);

		if err.Error() != "no authorization header included" {
			t.Errorf("got %v",err)
		}
		if key != "" {t.Errorf("not empty got %v",key)};


	} )



	t.Run( "mytest2", func(t *testing.T){

		headers := http.Header{}
		headers.Add("Authorization", "ApiKey abc123")

		key, err := GetAPIKey(headers);

		if err != nil {
			t.Errorf("got %v",err)
		}
		if key != "abc123" {t.Errorf("not empty got %v",key)};


	} )






}
