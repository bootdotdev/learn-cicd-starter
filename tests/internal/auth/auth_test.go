package test

import (
	"fmt"
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {

	type test struct {
		input    http.Header
		expected string
	}

	header := http.Header{}

	header.Add("Authorization", "ApiKey abcdefgh")

	var cases []test = []test{
		{input: header, expected: "abcdefg"},
	}

	for _, c := range cases {
		actual, err := auth.GetAPIKey(c.input)
		if err != nil {
			fmt.Println("err:", err)
			t.Errorf("expected %s but got %v", c.expected, actual)
		}
	}

}
