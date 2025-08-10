func TestGetAPIKey_FromFile(t *testing.T) {
    // criar ficheiro temporário com a chave
    f, err := os.CreateTemp("", "apikey-")
    if err != nil { t.Fatalf("CreateTemp: %v", err) }
    defer os.Remove(f.Name())
    if _, err := f.WriteString("minha-chavedearquivo"); err != nil { t.Fatalf("write: %v", err) }
    f.Close()

    prev := os.Getenv("NOTELY_API_KEY_FILE")
    defer os.Setenv("NOTELY_API_KEY_FILE", prev)
    os.Setenv("NOTELY_API_KEY_FILE", f.Name())

    got, err := auth.GetAPIKey()
    if err != nil { t.Fatalf("esperava nil, obteve: %v", err) }
    if got != "minha-chavedearquivo" {
        t.Fatalf("esperava 'minha-chavedearquivo', obteve: %q", got)
    }
}