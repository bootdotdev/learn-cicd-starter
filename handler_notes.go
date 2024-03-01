package main

import (
	"encoding/json"
	"net/http"
	"time"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"
	"github.com/google/uuid"
)

func (cfg *apiConfig) handlerNotesGet(w http.ResponseWriter, r *http.Request, user database.User) {
	posts, err := cfg.DB.GetNotesForUser(r.Context(), user.ID)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't get posts for user")
		return
	}

	respondWithJSON(w, http.StatusOK, databasePostsToPosts(posts))
}

func (cfg *apiConfig) handlerNotesCreate(w http.ResponseWriter, r *http.Request, user database.User) {
	type parameters struct {
		Note string `json:"note"`
	}
	decoder := json.NewDecoder(r.Body)
	params := parameters{}
	err := decoder.Decode(&params)
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't decode parameters")
		return
	}

	id := uuid.New().String()
	err = cfg.DB.CreateNote(r.Context(), database.CreateNoteParams{
		ID:        id,
		CreatedAt: time.Now().UTC(),
		UpdatedAt: time.Now().UTC(),
		Note:      params.Note,
		UserID:    user.ID,
	})
	if err != nil {
		respondWithError(w, http.StatusInternalServerError, "Couldn't create note")
		return
	}

	note, err := cfg.DB.GetNote(r.Context(), id)
	if err != nil {
		respondWithError(w, http.StatusNotFound, "Couldn't get note")
		return
	}
	respondWithJSON(w, http.StatusCreated, databaseNoteToNote(note))
}
