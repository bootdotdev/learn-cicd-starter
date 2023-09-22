package main

import (
	"net/http"
	"testing"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

func Test_apiConfig_handlerNotesGet(t *testing.T) {
	type args struct {
		w    http.ResponseWriter
		r    *http.Request
		user database.User
	}
	tests := []struct {
		name string
		cfg  *apiConfig
		args args
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			tt.cfg.handlerNotesGet(tt.args.w, tt.args.r, tt.args.user)
		})
	}
}
