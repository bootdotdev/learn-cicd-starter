package main

import (
	"encoding/json"
	"log"
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

	postsResp, err := databasePostsToPosts(posts)
	if err != nil {
		log.Println(err)
		respondWithError(w, http.StatusInternalServerError, "Couldn't convert posts")
		return
	}

	respondWithJSON(w, http.StatusOK, postsResp)
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
		CreatedAt: time.Now().UTC().Format(time.RFC3339),
		UpdatedAt: time.Now().UTC().Format(time.RFC3339),
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

	noteResp, err := databaseNoteToNote(note)
	if err != nil {
		log.Println(err)
		respondWithError(w, http.StatusInternalServerError, "Couldn't convert note")
		return
	}

	respondWithJSON(w, http.StatusCreated, noteResp)
}
