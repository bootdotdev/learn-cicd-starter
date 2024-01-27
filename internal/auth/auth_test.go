package auth

import (
  "net/http"
  "testing"
)

func TestGetAPIKey(t *testing.T) {
  tests := map[string]struct{
    authHeader string
    errorIsExpected bool
    expectedOutput string
  }{
    "No auth header": {
      authHeader: "",
      errorIsExpected: true,
      expectedOutput: "",
    },
    "Too long auth header": {
      authHeader: "I am way too long for this",
      errorIsExpected: true,
      expectedOutput: "",
    },
    "Malformed auth header": {
      authHeader: "TheApiKey 12345",
      errorIsExpected: true,
      expectedOutput: "",
    },
    "Correct auth header": {
      authHeader: "ApiKey 12345",
      errorIsExpected: false,
      expectedOutput: "12345",
    },
  }

  for name, test := range tests {
    t.Run(name, func(t *testing.T) {
      header := http.Header{}
      header.Set("Authorization", test.authHeader)
      output, err := GetAPIKey(header)
      if err != nil && test.errorIsExpected {
        t.Errorf("%s yielded an unexpected error %v\n", test.authHeader, err)
      }
      if output != test.expectedOutput {
        t.Errorf("%s yielded an unexpected output: %v\n", test.authHeader, output)
      }
    })
  }
}
