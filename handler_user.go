package main

import (
	"encoding/json"
	"net/http"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
)

func (cfg *apiConfig) handlerUsersCreate(w http.ResponseWriter, r *http.Request) {
	type parameters struct {
		Email    string `json:"email"`
		Password string `json:"password"`
	}

	decoder := json.NewDecoder(r.Body)
	params := parameters{}
	if err := decoder.Decode(&params); err != nil {
		respondWithError(w, http.StatusBadRequest, "invalid JSON body")
		return
	}

	user := cfg.DB.CreateUser(r.Context(), database.CreateUserParams{
		Email:          params.Email,
		HashedPassword: params.Password,
	})

	respondWithJSON(w, http.StatusCreated, user)
}

func (cfg *apiConfig) handlerUsersGet(
	w http.ResponseWriter,
	r *http.Request,
	user database.User,
) {
	respondWithJSON(w, http.StatusOK, user)
}
