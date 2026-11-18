//go:build staticcheck
// +build staticcheck

package main

import "net/http"

// These are empty stubs so staticcheck can “see” the symbols when run
// with the `staticcheck` build tag. They are EXCLUDED from normal builds/tests.

type apiConfig struct{} // only to satisfy method receivers in this file

func (a *apiConfig) handlerUserCreate(w http.ResponseWriter, r *http.Request) {}
func (a *apiConfig) handlerUserGet(w http.ResponseWriter, r *http.Request)    {}
func (a *apiConfig) handlerUsersCreate(w http.ResponseWriter, r *http.Request) {}
func (a *apiConfig) handlerUsersGet(w http.ResponseWriter, r *http.Request)    {}
func (a *apiConfig) handlerNotesGet(w http.ResponseWriter, r *http.Request)    {}
func (a *apiConfig) handlerNotesCreate(w http.ResponseWriter, r *http.Request) {}
func handlerHeadLoss(w http.ResponseWriter, r *http.Request)                   {}
func (a *apiConfig) handlerUserSelect(w http.ResponseWriter, r *http.Request)  {}

func handleReadiness(w http.ResponseWriter, r *http.Request)                   {}
func authMiddleware(next http.Handler) http.Handler { return next }
