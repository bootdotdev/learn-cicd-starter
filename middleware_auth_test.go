package main

import (
	"net/http"
	"reflect"
	"testing"
)

func Test_apiConfig_middlewareAuth(t *testing.T) {
	type args struct {
		handler authedHandler
	}
	tests := []struct {
		name string
		cfg  *apiConfig
		args args
		want http.HandlerFunc
	}{
		// TODO: Add test cases.
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := tt.cfg.middlewareAuth(tt.args.handler); !reflect.DeepEqual(got, tt.want) {
				t.Errorf("apiConfig.middlewareAuth() = %v, want %v", got, tt.want)
			}
		})
	}
}
