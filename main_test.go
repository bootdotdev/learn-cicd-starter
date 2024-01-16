package main

import (
	"testing"
)

func TestGenerateHash(t *testing.T) {
	var err error
	if _, err = generateRandomSHA256Hash(); err != nil {
		t.Fatal(err)
	}
}
