# Curso: CI/CD with GitHub Actions — Boot.dev

**Estudiante:** Auda (Cecibel Espinoza)
**Repositorio:** https://github.com/cecibelauda/learn-cicd-starter
**Ramas:** `addtests` (PR #1), `formatting` (PR #2), `linting` (PR #3/#4), `security` (PR #5), `build` (PR #7), `auto-build` (PR #8) — todas mergeadas a `main`
**Directorio local:** `~/learn-cicd-starter`

---

# SECCIÓN 1 — Fundamentos de CI/CD y GitHub Actions

## 1.1 Conceptos base

### ¿Qué es CI/CD?

| Sigla | Significado | Qué hace |
|---|---|---|
| **CI** | Continuous Integration | Los devs suben cambios a un repo central y se disparan builds y pruebas automáticas |
| **CD** | Continuous Delivery / Deployment | Si CI pasa, el código se publica automáticamente |

**Tipos de pruebas que puede incluir el CI:**
- Pruebas unitarias
- Pruebas de integración
- Verificaciones de estilo (formatting)
- Linting
- Verificaciones de seguridad

Si alguna falla, el build se considera **"roto"** y se notifica al desarrollador.

> **Idea central:** CI se trata de automatizar la mayor parte posible del proceso de pruebas y revisión, para que el revisor humano no tenga que verificar formato ni correr tests localmente.

### Códigos de salida (exit codes)

Convención universal de las herramientas CLI:

| Exit code | Significado |
|---|---|
| `0` | Éxito — el step pasa |
| Cualquier otro | Falla — el step falla |

Ejemplo: `go test` sale con código `1` si un caso de prueba falla.

---

## 1.2 Flujo de trabajo con Git en equipo

### El problema del flujo lineal

```bash
# trabajando directo sobre "main"
git add .
git commit -m "mensaje"
git push origin main
```

Funciona para proyectos personales, pero en equipo genera problemas:
- Dos personas modifican la misma función y ambas pushean a `main`
- No hay punto de revisión de código antes del merge
- No se puede trabajar en varias funcionalidades en paralelo

### Ramas (branches)

Una **rama** es (básicamente) una copia de la base de código, de un tipo especial que hace simple fusionar cambios de una rama a otra.

**Convención en equipos:** `main` refleja el estado de producción → siempre debe estar estable y lista para desplegar.

Crear una rama nueva para:
- Agregar una funcionalidad
- Corregir un bug
- Refactorizar código

### Comandos de ramas

```bash
git branch                    # ver ramas; el asterisco marca la actual
git switch -c addtests        # crear rama nueva y cambiarse a ella
git switch addtests           # cambiarse a una rama existente
git push -u origin addtests   # subir la rama al remoto (solo existe local al crearla)
```

El flag `-u` establece el upstream: después basta con `git push`.

### Pull Requests

Un **PR** propone fusionar los cambios de una rama en otra. Permite revisión de código y ejecución de CI antes del merge.

**Crear un PR desde un fork — el error más común:**

GitHub pone por defecto el repositorio **original** como base repository. Hay que cambiarlo al fork propio.

URL directa para comparar dentro del propio fork:

```
https://github.com/cecibelauda/learn-cicd-starter/compare/main...addtests
```

Verificar que ambos lados digan `cecibelauda/learn-cicd-starter` (no `bootdotdev`).

Con GitHub CLI:

```bash
gh pr create --repo cecibelauda/learn-cicd-starter \
  --base main --head addtests \
  --title "Add tests" --body "Descripción"

gh pr list --repo cecibelauda/learn-cicd-starter   # verificar
gh pr close NUMERO --repo OWNER/REPO               # cerrar uno equivocado
```

---

## 1.3 Estructura de directorios `.github`

### Por qué el punto

El `.` inicial es una **convención de Unix**: marca archivos/directorios ocultos. No es de GitHub.

```bash
ls        # no muestra ocultos
ls -a     # muestra todo (-a = all)
```

Ejemplos que ya se usan a diario: `~/.zshrc`, `~/.gitconfig`, `~/.ssh/`, `.git/`

**En Finder (Mac):** `Cmd + Shift + .` alterna la vista de ocultos.

### El nombre `.github` sí es específico de GitHub

```
tu-repo/
├── .git/                     ← interno de Git (no se toca)
├── .github/                  ← convención de GitHub (sí se edita)
│   ├── workflows/
│   │   └── ci.yml            ← Actions busca AQUÍ y solo aquí
│   ├── PULL_REQUEST_TEMPLATE.md
│   ├── ISSUE_TEMPLATE/
│   ├── CODEOWNERS
│   └── dependabot.yml
├── .gitignore
├── README.md
└── main.go                   ← código
```

⚠️ Si el archivo está en `workflows/ci.yml` o en `.github/workflow/` (singular), **no se ejecuta nada**.

⚠️ Boot.dev valida la extensión `.yml` (no `.yaml`, aunque YAML acepte ambas).

### Regla general del punto

| Con punto | Sin punto |
|---|---|
| `.github/`, `.gitignore`, `.env`, `.dockerignore` | `README.md`, `LICENSE`, `Dockerfile`, `pom.xml` |
| Configuración de herramientas | Código, documentación, manifiestos |

Los directorios propios (`src/`, `internal/`, `docs/`) van **sin punto**.

---

## 1.4 Anatomía de un workflow de GitHub Actions

### Archivo completo de referencia

```yaml
name: ci

on:
  pull_request:
    branches: [main]

jobs:
  tests:
    name: Tests
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Echo Go version
        run: go version
```

### Jerarquía conceptual

```
Workflow  (el archivo ci.yml completo)
   │
   ├── se dispara por un EVENTO (on:)
   │
   └── Job(s)  (corren en un RUNNER = máquina virtual de GitHub)
          │
          └── Step(s)  (tareas individuales)
                 │
                 ├── uses: → ejecuta una ACTION reutilizable
                 └── run:  → ejecuta un comando de shell
```

### Desglose línea por línea

| Clave | Función |
|---|---|
| `name:` (nivel raíz) | Nombre legible del workflow |
| `on:` | Evento que dispara el workflow |
| `pull_request.branches: [main]` | Se dispara al abrir un PR hacia `main` |
| `jobs:` | Lista de jobs que componen el workflow |
| `runs-on:` | Tipo de runner (VM). `ubuntu-latest` = última versión de Ubuntu |
| `steps:` | Lista de tareas del job |
| `uses:` | Action reutilizable a ejecutar |
| `with:` | Inputs (parámetros) de la action |
| `run:` | Comando de línea de comandos arbitrario en el runner |

### Conceptos clave

- **Workflow:** se dispara cuando ocurre un evento en el repositorio.
- **Job:** conjunto de steps que corren en el mismo runner. Se usan varios jobs para correr pruebas en paralelo o sobre múltiples sistemas operativos.
- **Runner:** máquina virtual en los servidores de GitHub que ejecuta el job.
- **Step:** tarea única — un comando, un script o una action.
- **Action:** aplicación personalizada reutilizable que reduce la complejidad de crear workflows.

### Actions usadas

| Action | Para qué |
|---|---|
| `actions/checkout@v6` | Clona el repo dentro del runner. **Casi siempre necesaria** |
| `actions/setup-go@v6` | Configura el entorno de Go |

### Comportamiento del re-disparo

Un workflow que se dispara con `pull_request` **se vuelve a ejecutar automáticamente** cuando se actualiza la rama a fusionar. No hace falta cerrar y reabrir el PR.

---

## 1.5 Comandos de terminal aprendidos

### Crear directorios y archivos

```bash
mkdir docs                 # un directorio
mkdir docs scripts         # varios
mkdir -p .github/workflows # anidados, crea los padres faltantes

touch notas.md             # archivo vacío
```

### Ver vs. editar archivos

`cat` solo **muestra**, no edita.

```bash
cat README.md              # mostrar contenido
nano README.md             # editar (Ctrl+O guardar, Ctrl+X salir)
vim README.md              # editar (:wq guardar y salir)
code README.md             # abrir en VS Code
```

### Redirecciones

```bash
echo "texto" >> README.md  # AGREGA al final
echo "texto" >  README.md  # SOBRESCRIBE todo (¡cuidado!)
```

Heredoc para escribir varias líneas:

```bash
cat > .github/workflows/ci.yml << 'EOF'
name: ci
...
EOF
```

Las comillas simples en `'EOF'` evitan que el shell interprete `$` o backticks.

### Verificación

```bash
tail -5 README.md          # últimas 5 líneas
ls -la                     # listado detallado con ocultos
git diff                   # qué cambió desde el último commit
git status                 # estado del working tree
```

En `ls -la`: los directorios empiezan con `d`, los archivos con `-`.

```
drwxr-xr-x  2 auda  staff   64 Sep 15 10:22 docs
-rw-r--r--  1 auda  staff    0 Sep 15 10:22 notas.md
```

### Verificar workflows con GitHub CLI

```bash
gh run list --branch addtests --limit 5   # últimas ejecuciones
gh run view --log-failed                  # logs de los steps fallidos
```

---

## 1.6 Notas y errores encontrados

| Situación | Causa | Solución |
|---|---|---|
| PR abierto contra `bootdotdev` en vez del fork | GitHub pone el repo original como base por defecto | Cerrar el PR y usar la URL `compare` del propio fork |
| `cat` no permite editar | `cat` es solo de lectura | Usar `nano`, `vim`, `code` o redirección `>>` |
| Git no versiona directorios vacíos | Comportamiento de diseño de Git | Agregar un archivo dentro, o `touch docs/.gitkeep` |
| Workflow no aparece en el PR | Ruta incorrecta o PR contra el repo equivocado | Verificar `.github/workflows/` exacto |
| Error "workflow file issue" | Indentación YAML con tabs | YAML solo acepta **espacios**, nunca tabs |
| `setup-go` no encuentra la versión | Versión no disponible en el runner | Alinear con `go.mod` o usar `go-version-file: go.mod` |

---

## 1.7 Flujo completo ejecutado en la Sección 1

```bash
# 1. Fork del repo en GitHub (botón Fork)

# 2. Clonar el fork
git clone https://github.com/cecibelauda/learn-cicd-starter.git
cd learn-cicd-starter

# 3. Crear rama de trabajo
git branch
git switch -c addtests
git push -u origin addtests

# 4. Editar README y commitear
echo "Cecibel's version of Boot.dev's Notely app." >> README.md
git add README.md
git commit -m "update README"
git push origin addtests

# 5. Abrir PR (sin fusionar) — base: main, compare: addtests, ambos en el fork

# 6. Crear el workflow de CI
mkdir -p .github/workflows
nano .github/workflows/ci.yml      # contenido en la sección 1.4

# 7. Commit y push → el CI se dispara en el PR
git add .github/workflows/ci.yml
git commit -m "add ci workflow"
git push origin addtests

# 8. Verificar
gh run list --branch addtests --limit 3
```

---

## 1.8 Referencias oficiales

**GitHub Actions**
- Documentación principal: https://docs.github.com/en/actions
- Entender GitHub Actions: https://docs.github.com/en/actions/learn-github-actions/understanding-github-actions
- Sintaxis de workflows: https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions
- Eventos que disparan workflows: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows
- Exit codes en actions: https://docs.github.com/en/actions/creating-actions/setting-exit-codes-for-actions

**Actions usadas**
- `actions/checkout`: https://github.com/actions/checkout
- `actions/setup-go`: https://github.com/actions/setup-go

**Git / GitHub**
- Fork a repo: https://docs.github.com/en/get-started/quickstart/fork-a-repo
- Sobre las ramas: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-branches
- PR desde un fork: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork
- Archivos de comunidad en `.github`: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file

**Otros**
- YAML: https://en.wikipedia.org/wiki/YAML
- `nano`: https://www.nano-editor.org/dist/latest/nano.html
- Git FAQ (directorios vacíos): https://git-scm.com/docs/gitfaq#empty-directories

---

# SECCIÓN 2 — Running Tests

## 2.1 Pruebas unitarias en Go

### Por qué importan en CI

Un pipeline de CI sin pruebas no verifica nada. El repo de Notely venía con **cero pruebas unitarias**, así que el primer paso fue escribirlas.

### El código bajo prueba: `internal/auth/auth.go`

```go
package auth

import (
	"errors"
	"net/http"
	"strings"
)

var ErrNoAuthHeaderIncluded = errors.New("no authorization header included")

// GetAPIKey -
func GetAPIKey(headers http.Header) (string, error) {
	authHeader := headers.Get("Authorization")
	if authHeader == "" {
		return "", ErrNoAuthHeaderIncluded
	}
	splitAuth := strings.Split(authHeader, " ")
	if len(splitAuth) < 2 || splitAuth[0] != "ApiKey" {
		return "", errors.New("malformed authorization header")
	}

	return splitAuth[1], nil
}
```

**Análisis:** recibe los headers HTTP, busca `Authorization`, espera el formato `ApiKey <valor>` y devuelve `<valor>`.

Tiene **tres caminos posibles** → mínimo tres casos de prueba:

| Camino | Entrada | Salida esperada |
|---|---|---|
| Éxito | `ApiKey mi-clave` | `"mi-clave"`, `nil` |
| Sin header | (vacío) | `""`, `ErrNoAuthHeaderIncluded` |
| Malformado | `Bearer mi-clave` | `""`, `errors.New("malformed authorization header")` |

### Reglas del lenguaje que condicionan el archivo de prueba

**1. El paquete lo define el directorio, no el archivo.**

Todos los archivos `.go` de un mismo directorio deben declarar el mismo `package X`.

```
internal/auth/                 ← este directorio = un paquete
├── auth.go                    → package auth
└── get_api_key_test.go        → package auth   (obligado)
```

Si no coinciden, el compilador falla:

```
found packages auth (auth.go) and split (get_api_key_test.go)
```

**2. El sufijo `_test.go` es aparte del `package`.**

Son dos cosas distintas que se confunden fácil:

| Elemento | Qué determina |
|---|---|
| `package auth` (dentro del archivo) | A qué paquete pertenece el archivo |
| `_test.go` (en el nombre del archivo) | Que es código de prueba → **se excluye del binario final** |

Equivale a tener `src/test/java` separado de `src/main/java` en Maven, pero resuelto por el nombre del archivo en lugar de por la carpeta.

**3. Única excepción — el paquete `_test`.**

Go permite un paquete extra por directorio: el que termina en `_test`. Es *black-box testing*, solo ve lo **exportado** (mayúscula inicial) y requiere import explícito:

```go
package auth_test

import (
	"testing"
	"github.com/bootdotdev/learn-cicd-starter/internal/auth"
)

func TestGetAPIKey(t *testing.T) {
	gotKey, gotErr := auth.GetAPIKey(...)   // requiere el prefijo
}
```

Para el curso conviene `package auth` a secas: menos ruido y permite probar funciones privadas.

### Equivalencias JUnit 5 ↔ Go

| Java / JUnit 5 | Go |
|---|---|
| `GetAPIKeyTest.java` | `get_api_key_test.go` — sufijo `_test.go` **obligatorio** |
| `@Test void shouldX()` | `func TestX(t *testing.T)` — prefijo `Test` **obligatorio** |
| `assertEquals(a, b)` | No existe: escribes un `if` y llamas `t.Errorf(...)` |
| `fail()` | `t.Fatalf(...)` |
| `@ParameterizedTest` / `@CsvSource` | *Table-driven tests*: `map` de casos + `for` |
| `mvn test` | `go test ./...` |
| `src/test/java` separado | Sufijo `_test.go` en el nombre |

**No hay librería de asserts en la stdlib.** Si nadie llama a `t.Errorf`, el test pasa.

### `t.Errorf` vs `t.Fatalf`

| | Comportamiento | Cuándo usarlo |
|---|---|---|
| `t.Errorf` | Registra el fallo y **continúa** | Comparaciones normales — muestra todos los problemas de una vez |
| `t.Fatalf` | Detiene el test **inmediatamente** | Cuando seguir causaría un *panic* (ej: desreferenciar un error `nil`) |

### Solución: `internal/auth/get_api_key_test.go`

```go
package auth

import (
	"errors"
	"net/http"
	"testing"
)

func TestGetAPIKey(t *testing.T) {
	tests := map[string]struct {
		headers http.Header
		wantKey string
		wantErr error
	}{
		"clave válida": {
			headers: http.Header{"Authorization": []string{"ApiKey mi-clave-secreta"}},
			wantKey: "mi-clave-secreta",
			wantErr: nil,
		},
		"sin header Authorization": {
			headers: http.Header{},
			wantKey: "",
			wantErr: ErrNoAuthHeaderIncluded,
		},
		"header malformado - prefijo incorrecto": {
			headers: http.Header{"Authorization": []string{"Bearer mi-clave-secreta"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
		"header malformado - sin valor": {
			headers: http.Header{"Authorization": []string{"ApiKey"}},
			wantKey: "",
			wantErr: errors.New("malformed authorization header"),
		},
	}

	for name, tc := range tests {
		t.Run(name, func(t *testing.T) {
			gotKey, gotErr := GetAPIKey(tc.headers)

			if gotKey != tc.wantKey {
				t.Errorf("clave: se obtuvo %q, se esperaba %q", gotKey, tc.wantKey)
			}

			if tc.wantErr == nil {
				if gotErr != nil {
					t.Errorf("error: se obtuvo %v, no se esperaba error", gotErr)
				}
				return
			}

			if gotErr == nil {
				t.Fatalf("error: no se obtuvo error, se esperaba %v", tc.wantErr)
			}

			if gotErr.Error() != tc.wantErr.Error() {
				t.Errorf("error: se obtuvo %q, se esperaba %q", gotErr, tc.wantErr)
			}
		})
	}
}
```

**Claves del código:**

- `struct{...}` anónimo dentro del `map` → la "fila" de la tabla de casos, equivalente a `@CsvSource`
- `http.Header` es un `map[string][]string`; por eso el valor va entre corchetes: `[]string{"ApiKey ..."}`
- `t.Run(name, func...)` crea un **subtest** con nombre propio: si falla, Go indica exactamente qué caso
- Los errores se comparan con `.Error()` (el texto) porque el error "malformed" se crea nuevo en cada llamada y no puede compararse por identidad con `==`

### Sobre `reflect.DeepEqual`

El [blog de Dave Cheney](https://dave.cheney.net/2019/05/07/prefer-table-driven-tests) que recomienda la lección usa `reflect.DeepEqual` porque compara un **slice** (`[]string`), y en Go los slices no se comparan con `==`.

Como `GetAPIKey` devuelve un `string`, basta con `!=` y no hace falta importar `reflect`.

⚠️ El código del blog **no funciona copiado literal**: declara `package split` y llama a una función `Split` que no existe en Notely. Del blog se toma el **patrón**, no el código.

### Verificación local

```bash
go test ./...                  # todos los tests
go test ./internal/auth -v     # detalle por subtest
go build ./...                 # compila (silencio = éxito)
go vet ./...                   # análisis estático
```

Salida esperada de `-v`:

```
=== RUN   TestGetAPIKey
=== RUN   TestGetAPIKey/clave_válida
=== RUN   TestGetAPIKey/sin_header_Authorization
=== RUN   TestGetAPIKey/header_malformado_-_prefijo_incorrecto
--- PASS: TestGetAPIKey (0.00s)
PASS
```

---

## 2.2 Tests on CI — ejecutar las pruebas en el pipeline

**Tarea:** eliminar el step `go version` del workflow y reemplazarlo por uno que ejecute las pruebas.

### Workflow actualizado: `.github/workflows/ci.yml`

```yaml
name: ci

on:
  pull_request:
    branches: [main]

jobs:
  tests:
    name: Tests
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Run unit tests
        run: go test ./...
```

El único cambio respecto a la Sección 1.4 es el último step: `run: go version` → `run: go test ./...`

### Por qué esto hace fallar el CI

Cada `run:` ejecuta un shell. Si el comando devuelve un **exit code distinto de 0**, el step falla y el job entero se marca en rojo.

`go test` devuelve `1` cuando algún test falla. Ahí está todo el mecanismo — no hay integración especial entre GitHub Actions y Go.

Esto conecta directamente con la convención de exit codes vista en la Sección 1.1.

### Validación del fallo (paso crítico de la lección)

La lección insiste en **romper el código a propósito** para confirmar que el CI realmente detecta fallos.

> *"Te sorprendería cuántas veces las empresas en las que he trabajado creían tener un CI que verificaba fallos, pero el código roto en realidad no hacía fallar el CI."*

Se modificó `internal/auth/auth.go` temporalmente:

```go
if len(splitAuth) < 2 || splitAuth[0] != "Bearer" {   // roto a propósito
```

Verificación del exit code — **esto es lo que lee GitHub Actions**:

```bash
go test ./... ; echo "exit code: $?"
```

```
--- FAIL: TestGetAPIKey/clave_válida (0.00s)
    get_api_key_test.go:39: clave: se obtuvo "", se esperaba "mi-clave-secreta"
FAIL
exit code: 1
```

Se hizo commit y push del código roto, se confirmó el ❌ en el PR, y luego se revirtió a `"ApiKey"` → ✅ verde.

### Diagrama del mecanismo completo

```
git push  →  evento pull_request  →  GitHub levanta un runner Ubuntu
                                      ├── actions/checkout  (clona el código)
                                      ├── actions/setup-go  (instala Go)
                                      └── go test ./...
                                             ├── exit 0 → ✅ step pasa → job verde
                                             └── exit 1 → ❌ step falla → job rojo
```

Un job se detiene en el **primer step que falle**; los siguientes no se ejecutan.

### Inspeccionar fallos desde la terminal

```bash
gh pr checks --watch        # seguir los checks en vivo
gh run list --limit 3
gh run view --log-failed    # logs de los steps que fallaron
```

---

## 2.3 Code Coverage

```
code_coverage = (lineas_cubiertas / lineas_totales) * 100
```

Si hay `1000` líneas de código y las pruebas cubren `500`, la cobertura es `50%`.

**Tarea:** agregar el flag `-cover` para imprimir la cobertura en los logs (sin hacer fallar el CI).

### El cambio

```yaml
      - name: Run unit tests
        run: go test -cover ./...
```

⚠️ **El orden importa.** En Go los flags van **entre el subcomando y los paquetes**. `go test ./... -cover` no funciona como se espera.

### Salida

```
ok      github.com/bootdotdev/learn-cicd-starter/internal/auth  0.003s  coverage: 100.0% of statements
?       github.com/bootdotdev/learn-cicd-starter               [no test files]
```

La línea con `?` significa que ese paquete **no tiene pruebas**. No cuenta como 0% — queda fuera del cálculo. Por eso aparece `100.0%`: es la cobertura del paquete `auth` solamente.

Para obtener el número global del proyecto:

```bash
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | tail -1
go tool cover -html=coverage.out          # reporte visual en el navegador
```

### Reportar vs. Exigir

| | Qué hace | Efecto |
|---|---|---|
| **Reportar** (`-cover`) | Imprime el % en los logs | Informativo. El CI pasa igual |
| **Exigir** (*quality gate*) | Compara el % contra un umbral | Si no llega, el build **falla** y el PR se bloquea |

Esta lección solo implementa el primero.

### Equivalencia con el stack de La Tinka (Java + SonarQube + JaCoCo)

```
mvn test  →  JaCoCo instrumenta y genera target/site/jacoco/jacoco.xml
                              ↓
          sonar-scanner lee ese XML
                              ↓
          SonarQube calcula % y lo compara con el Quality Gate
                              ↓
                  ✅ Passed  /  ❌ Failed
```

Equivalente local de `go test -cover`:

```bash
mvn clean verify
open target/site/jacoco/index.html
```

**Condiciones por defecto del *Sonar way*** — aplican sobre **código nuevo**, no sobre todo el proyecto (concepto *Clean as You Code*):

| Condición | Umbral |
|---|---|
| Cobertura en código nuevo | ≥ 80% |
| Líneas duplicadas en código nuevo | ≤ 3% |
| Bugs / vulnerabilidades nuevas | 0 |
| Security hotspots revisados | 100% |

**Cómo saber si el gate bloquea o solo reporta:**

1. Dashboard de SonarQube → *Project Settings → Quality Gate* (cuál está asignado) y *Quality Gates* global (sus condiciones)
2. En el pipeline, buscar el paso que espera el resultado. En Jenkins es:
   ```groovy
   waitForQualityGate abortPipeline: true
   ```
   Si ese paso **no está**, Sonar reporta pero no bloquea nada — el escenario más común en equipos que adoptaron Sonar sin cerrar el ciclo
3. `cat sonar-project.properties` → verificar que `sonar.coverage.jacoco.xmlReportPaths` apunte a un archivo que realmente se genera. Si no, Sonar reporta **0%** aunque existan pruebas

### Por qué la métrica es controversial

Es posible tener 100% de cobertura y aun así tener bugs, y 0% de cobertura con una app libre de errores. Las pruebas unitarias codifican el comportamiento esperado de unidades de código, pero no garantizan ausencia de bugs.

El autor del curso argumenta que no todas las funciones merecen la misma atención, y que **mockear sistemas externos (como bases de datos) en pruebas unitarias no es buena idea** — ese es mejor caso de uso para pruebas de integración.

Postura recomendada para un desarrollador que entra a un equipo nuevo: conocer la métrica, respetar el umbral de la organización, y plantear opiniones propias cuando ya se tenga confianza ganada.

---

## 2.4 README Badge

**Tarea:** agregar un badge dinámico al `README.md` que muestre el estado de las pruebas.

### Estructura de la URL

```
https://github.com/<OWNER>/<REPOSITORY>/actions/workflows/<WORKFLOW_FILE>/badge.svg
```

### Sintaxis de imagen en Markdown

```markdown
![texto alternativo](URL_DE_LA_IMAGEN)
```

### Línea agregada al inicio del README

```markdown
![Tests](https://github.com/cecibelauda/learn-cicd-starter/actions/workflows/ci.yml/badge.svg)
```

### Detalles importantes

| Aspecto | Detalle |
|---|---|
| Qué va en `<WORKFLOW_FILE>` | El **nombre del archivo** (`ci.yml`), no el `name:` interno |
| Qué texto muestra el badge | El `name:` interno del workflow → por eso dice `ci passing` |
| Es dinámico | GitHub regenera el SVG en cada request, consultando el último run |
| Qué rama consulta | La **rama por defecto** (`main`), salvo que se especifique otra |
| Cuándo aparece | Solo tras mergear a `main` — en una rama no se ve en la portada |

### Variantes útiles

```markdown
<!-- Badge de una rama específica -->
![Tests](https://github.com/cecibelauda/learn-cicd-starter/actions/workflows/ci.yml/badge.svg?branch=develop)

<!-- Badge clickeable → sintaxis [![alt](imagen)](destino) -->
[![Tests](https://github.com/cecibelauda/learn-cicd-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/cecibelauda/learn-cicd-starter/actions/workflows/ci.yml)
```

### Si el badge sale gris con "no status"

Significa que el workflow nunca corrió sobre la rama por defecto. Con un `on:` que solo tiene `pull_request`, normalmente se resuelve tras el merge del PR.

Para forzar que también corra en `main`:

```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
```

**Resultado obtenido:** ✅ badge en verde mostrando `ci passing`.

---

## 2.5 Comandos nuevos de la Sección 2

### Go

```bash
go test ./...                    # todas las pruebas, recursivo
go test ./internal/auth -v       # detalle por subtest
go test -cover ./...             # con reporte de cobertura
go test ./... ; echo $?          # ver el exit code (0 = ok, 1 = falla)
go build ./...                   # compila (silencio = éxito)
go vet ./...                     # análisis estático
gofmt -w <archivo>               # formatea e indenta automáticamente

go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | tail -1
go tool cover -html=coverage.out
```

`./...` significa: el directorio actual **y todos sus subdirectorios**.

### GitHub CLI

```bash
gh repo set-default cecibelauda/learn-cicd-starter   # obligatorio en forks
gh repo set-default --view

gh pr status
gh pr checks --watch
gh pr merge --merge
gh pr view --web

gh run list --limit 3
gh run view --log-failed
gh run watch
gh repo view --web
```

Alternativa sin configurar el default:

```bash
gh pr checks --repo cecibelauda/learn-cicd-starter
gh pr merge --repo cecibelauda/learn-cicd-starter --merge
```

### Ciclo de ramas por sección

```bash
git checkout main
git pull origin main             # ⚠️ el paso que más se olvida
git checkout -b <nombre-rama>
# ... trabajo ...
git add .
git commit -m "tipo: descripción"
git push origin <nombre-rama>
```

Limpieza tras el merge:

```bash
git branch -d <rama>                   # borra local
git push origin --delete <rama>        # borra remota
git fetch --prune                      # limpia referencias muertas
```

---

## 2.6 Notas y errores encontrados

| Situación | Causa | Solución |
|---|---|---|
| `zsh: command not found: code` | VS Code no instaló el comando en el PATH | En VS Code: `Cmd+Shift+P` → *Shell Command: Install 'code' command in PATH*. Alternativa: usar `nano` |
| `No default remote repository has been set` | `gh` detecta que el repo es un fork y no sabe si apuntar al fork o al upstream | `gh repo set-default cecibelauda/learn-cicd-starter` ⚠️ nunca `bootdotdev` |
| `found packages auth and split` | Se copió literal el código del blog de Dave Cheney | Usar `package auth` y llamar a `GetAPIKey`, no a `Split` |
| Código pegado en `nano` se escalona | Auto-indent del editor | Abrir con `nano -i`, o correr `gofmt -w <archivo>` después |
| `go test ./... -cover` no reporta cobertura | Los flags de Go van antes de los paquetes | `go test -cover ./...` |
| Badge en gris con "no status" | El workflow nunca corrió sobre `main` | Se resuelve tras el merge. Opcional: agregar `push: branches: [main]` |

### Reglas de trabajo consolidadas

1. **Una rama = una unidad de cambio = un PR.** Rama mergeada = ciclo cerrado, no reutilizar
2. **Siempre `git pull` en `main` antes de ramificar**, o habrá conflictos al mergear
3. **Validar el CI rompiéndolo a propósito** al menos una vez, para confirmar que sí detecta fallos
4. **Los flags de Go van antes de los paquetes:** `go test -cover ./...`
5. Tras pegar código Go en un editor de terminal, siempre `gofmt -w`

---

## 2.7 Flujo completo ejecutado en la Sección 2

```bash
# 1. Crear el archivo de pruebas
nano internal/auth/get_api_key_test.go     # contenido en la sección 2.1
gofmt -w internal/auth/get_api_key_test.go
go test ./...

# 2. Agregar las pruebas al workflow
nano .github/workflows/ci.yml              # go version → go test ./...

# 3. Romper el código a propósito y validar que el CI falla
nano internal/auth/auth.go                 # "ApiKey" → "Bearer"
go test ./... ; echo $?                    # debe imprimir 1
git add .
git commit -m "ci: run unit tests in CI (intentionally broken code)"
git push origin addtests
gh repo set-default cecibelauda/learn-cicd-starter
gh pr checks --watch                       # ❌ rojo

# 4. Arreglar el código
nano internal/auth/auth.go                 # "Bearer" → "ApiKey"
go test ./...
git add internal/auth/auth.go
git commit -m "fix: restore ApiKey prefix check"
git push origin addtests                   # re-dispara el workflow ✅

# 5. Agregar el flag de cobertura
nano .github/workflows/ci.yml              # go test -cover ./...
git add .github/workflows/ci.yml
git commit -m "ci: report test coverage"
git push origin addtests

# 6. Agregar el badge al README
nano README.md                             # línea del badge al inicio
git add README.md
git commit -m "docs: add tests status badge to README"
git push origin addtests

# 7. Mergear y sincronizar
gh pr checks --watch
gh pr merge --merge
git checkout main
git pull origin main
gh repo view --web                         # verificar badge "ci passing" ✅
```

---

## 2.8 Referencias oficiales de la Sección 2

**Go — testing**
- Paquete `testing`: https://pkg.go.dev/testing
- Tutorial oficial "Add a test": https://go.dev/doc/tutorial/add-a-test
- Flags de testing (incluye `-cover`): https://pkg.go.dev/cmd/go#hdr-Testing_flags
- Test packages: https://pkg.go.dev/cmd/go#hdr-Test_packages
- Package clause (spec): https://go.dev/ref/spec#Package_clause
- `reflect.DeepEqual`: https://pkg.go.dev/reflect#DeepEqual
- Dave Cheney — Prefer table driven tests: https://dave.cheney.net/2019/05/07/prefer-table-driven-tests

**GitHub Actions**
- `jobs.<job_id>.steps[*].run`: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idstepsrun
- Adding a workflow status badge: https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/monitoring-workflows/adding-a-workflow-status-badge

**GitHub CLI**
- `gh repo set-default`: https://cli.github.com/manual/gh_repo_set-default
- `gh pr merge`: https://cli.github.com/manual/gh_pr_merge

**Cobertura y calidad (contexto Java / La Tinka)**
- SonarQube — Quality Gates: https://docs.sonarsource.com/sonarqube-server/latest/instance-administration/analysis-functions/quality-gates/
- SonarQube — Test coverage: https://docs.sonarsource.com/sonarqube-server/latest/analyzing-source-code/test-coverage/overview/
- Boot.dev — Don't mock database connections: https://www.boot.dev/blog/backend/writing-good-unit-tests-dont-mock-database-connections/
- CircleCI — Unit vs integration testing: https://circleci.com/blog/unit-testing-vs-integration-testing/

**Markdown**
- Cheat sheet: https://www.markdownguide.org/cheat-sheet/
- Imágenes: https://www.markdownguide.org/basic-syntax/#images-1

---

# SECCIÓN 3 — Formatting

## 3.1 Formateo automático con `go fmt`

### Por qué formatear automáticamente

El formateo automático mantiene el código **consistente y legible**, y evita discusiones sobre estilo (*bikeshedding*: debatir detalles triviales en lugar de lo importante).

```go
// Técnicamente válido, pero fuera de convención
func main(){
	fmt.Println("hello world!") }

// Formato estándar
func main() {
	fmt.Println("hello world!")
}
```

> **Idea central:** en Go no hay debate de estilo. `gofmt` define **un único formato oficial**, integrado en el toolchain, sin instalar nada adicional.

### `go fmt` vs. `gofmt`

| Herramienta | Qué es | Opera sobre |
|---|---|---|
| `gofmt` | El formateador en sí | Archivos y directorios |
| `go fmt` | Atajo que ejecuta `gofmt -l -w` | Paquetes (`./...`) |

### Flags de `gofmt`

| Comando | Qué hace | ¿Modifica archivos? |
|---|---|---|
| `gofmt -l .` | **Lista** los archivos mal formateados | No |
| `gofmt -d <archivo>` | Muestra el **diff** de lo que corregiría | No |
| `gofmt -w <archivo>` | **Escribe** la corrección en el archivo | Sí |
| `go fmt ./...` | Formatea todos los paquetes e imprime los archivos que corrigió | Sí |

Equivalencia Java: es como tener Spotless o `google-java-format` integrado en el JDK, sin configurar plugins en el `pom.xml`.

### El directorio `vendor/`: no se toca

Al ejecutar `gofmt -l .` en Notely aparecieron muchos archivos bajo `vendor/`:

```
internal/auth/get_api_key_test.go
vendor/github.com/go-chi/chi/chi.go
vendor/github.com/google/uuid/dce.go
...
```

`vendor/` contiene **copias del código de librerías de terceros** generadas con `go mod vendor`. Es como tener los `.jar` de las dependencias dentro del repo en lugar de en `~/.m2`.

Aparecen porque el `gofmt` local es más nuevo que el que usaron sus autores. Algunas versiones de Go cambiaron reglas de formato, como los comentarios de documentación (Go 1.19) o las directivas `//go:build` (Go 1.17).

| | `gofmt -l .` | `go fmt ./...` |
|---|---|---|
| ¿Revisa `vendor/`? | **Sí**: recorre carpetas sin distinguir | **No**: el patrón `./...` excluye `vendor` |

⚠️ **Nunca modificar `vendor/`**: no es código propio y se sobrescribe con el próximo `go mod vendor`.

Revisar solo el código propio:

```bash
gofmt -l $(find . -name '*.go' -not -path './vendor/*')
```

### Cómo leer un diff de `gofmt -d`

Caso real encontrado en `get_api_key_test.go`:

```diff
@@ -8,9 +8,9 @@
 func TestGetAPIKey(t *testing.T) {
 	tests := map[string]struct {
-		headers   http.Header
-		wantKey   string
-		wantErr   error
+		headers http.Header
+		wantKey string
+		wantErr error
 	}{
```

| Símbolo | Significado |
|---|---|
| `@@ -8,9 +8,9 @@` | Bloque de 9 líneas desde la línea 8, antes y después |
| `-` | Línea actual, que se eliminará |
| `+` | Línea corregida que la reemplaza |
| (espacio) | Línea de contexto sin cambios |

### Regla de alineación de campos de un struct

`gofmt` alinea los tipos en columna tomando como referencia el **nombre de campo más largo**:

```go
// Los tres nombres tienen 7 caracteres → basta un espacio
headers http.Header
wantKey string
wantErr error

// Con un campo más largo, los cortos reciben espacios extra
id        int
headers   http.Header
createdAt time.Time
```

El archivo tenía espacios de más, probablemente por el auto-indent de `nano` al pegar el código (ver Sección 2.6).

---

## 3.2 Check Formatting — convertir la salida en exit code

### El problema

`go fmt` **siempre termina con exit code `0`**, aunque haya corregido archivos. Para GitHub Actions eso significa "éxito" siempre (Sección 1.1).

Lo que sí hace es **imprimir los nombres de los archivos que corrigió**. Si no imprime nada, el repo ya estaba formateado.

### La solución: `test -z`

```bash
test -z $(go fmt ./...)
```

| Parte | Qué hace |
|---|---|
| `go fmt ./...` | Formatea e imprime los archivos corregidos; si no hay ninguno, salida vacía |
| `$( ... )` | **Sustitución de comandos**: ejecuta el comando y reemplaza la expresión por su salida |
| `test -z <string>` | Devuelve `0` si el string está **vacío** y `1` si no lo está |

### Diagrama del mecanismo

```
1ª vez:  go fmt ./...  ──► imprime "internal/auth/auth.go" (y lo corrige)
              │
         $( ... ) = "internal/auth/auth.go"
              │
         test -z "internal/auth/auth.go"  ──► no está vacío ──► exit 1 ❌

2ª vez:  go fmt ./...  ──► no imprime nada
              │
         $( ... ) = ""
              │
         test -z  ──► vacío ──► exit 0 ✅
```

> **Idea central:** se transforma *"¿se imprimió algo en stdout?"* en un **exit code**, que es lo único que entiende GitHub Actions.

### Verificación del exit code

```bash
test -z $(go fmt ./...)
echo $?          # 1 → había archivos sin formato (y ya los corrigió)

test -z $(go fmt ./...)
echo $?          # 0 → repo formateado
```

⚠️ `echo $?` debe ir **inmediatamente después** del comando. Cualquier comando intermedio cambia el valor de `$?`.

### Versión más robusta: con comillas

Si hay **varios archivos** desformateados, la salida tiene varias palabras y `test` recibe demasiados argumentos:

```
test: too many arguments   → exit 2
```

Igual falla, pero por la razón equivocada. Con comillas la salida se trata como un único string:

```bash
test -z "$(go fmt ./...)"
```

El curso usa la versión sin comillas; la versión con comillas es la recomendable en pipelines reales.

---

## 3.3 Formatting CI — job "Style" en paralelo

**Tarea:** agregar la verificación de formato como un **job separado** llamado `Style`, en paralelo al job `Tests`.

### Workflow actualizado: `.github/workflows/ci.yml`

```yaml
name: ci

on:
  pull_request:
    branches: [main]

jobs:
  tests:
    name: Tests
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Run unit tests
        run: go test -cover ./...

  style:
    name: Style
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Check formatting
        run: test -z $(go fmt ./...)
```

⚠️ `style:` debe quedar en la **misma columna** que `tests:` (2 espacios). Si queda más indentado, GitHub no lo reconoce como job.

Verificar la estructura de jobs:

```bash
grep -n "^  [a-z]*:$" .github/workflows/ci.yml
# 8:  tests:
# 25:  style:
```

### Jobs en paralelo

```
PR hacia main
      │
      ├──► Runner 1: job "Tests"          ├──► Runner 2: job "Style"
      │     ├─ checkout                   │     ├─ checkout
      │     ├─ setup-go                   │     ├─ setup-go
      │     └─ go test -cover ./...       │     └─ test -z $(go fmt ./...)
      │                                   │
      └──────────── ambos corren al mismo tiempo ───────────┘
```

| Concepto | Detalle |
|---|---|
| Paralelismo | Los jobs corren **en paralelo por defecto** |
| Secuencia | Solo corren en orden si se declara `needs: <job>` |
| Aislamiento | Cada job corre en **su propia VM**, sin compartir archivos |
| Consecuencia | `checkout` y `setup-go` **se duplican** en cada job |
| Independencia | Un fallo en `Style` no detiene `Tests`, y viceversa |

Analogía: son dos revisores trabajando al mismo tiempo en escritorios distintos. Cada uno necesita su propia copia del código (`checkout`) y sus propias herramientas (`setup-go`).

⚠️ En el runner, `go fmt` sí corrige el archivo, pero **solo dentro de esa VM temporal**. El repo sigue desformateado hasta corregirlo localmente y hacer push.

### Por qué se necesita un PR nuevo

El workflow se dispara con `pull_request` hacia `main`. El PR #1 ya se mergeó y cerró, así que un push a una rama nueva **no dispara nada** hasta abrir otro PR.

```
PR #1 (addtests → main)   ── mergeado ── cerrado ✅ → ya no escucha pushes

git push origin formatting  ──► ❌ sin PR abierto, el CI no corre

gh pr create (formatting → main) ──► PR #2 abierto
                                          │
                                          ▼
                              evento pull_request ──► Tests + Style
```

Con el PR abierto, **cada push a la rama vuelve a ejecutar el CI** automáticamente.

```bash
gh pr create --repo cecibelauda/learn-cicd-starter \
  --base main --head formatting \
  --title "Add formatting check" \
  --body "Adds a Style job that fails if code is not formatted with go fmt"
```

### Validación del fallo en GitHub

Se rompió el formato de `auth.go` a propósito, se hizo push y se confirmó:

```bash
gh pr checks --watch
```

```
X  ci/Style (pull_request)    Fail
✓  ci/Tests (pull_request)    Pass
```

```bash
gh run view --log-failed
```

```
Style  Check formatting  ##[group]Run test -z $(go fmt ./...)
Style  Check formatting  shell: /usr/bin/bash -e {0}
Style  Check formatting  ##[error]Process completed with exit code 1.
```

**`Process completed with exit code 1`** es la prueba de que el check funciona.

En la web: página del PR → pestaña **Conversation** → al final aparece *"Some checks were not successful"* → **Details** junto a Style.

| Resultado con el código roto | Significado |
|---|---|
| Style ❌, Tests ✅ | Correcto: detecta formato roto y los jobs son independientes |
| Style ✅ | El check no funciona, o el cambio no llegó a GitHub |
| Solo aparece Tests | El `ci.yml` con el job Style no está en la rama remota |

Luego se restauró con `go fmt ./...` y push → ✅ ambos en verde.

### Pestañas de un PR en GitHub

```
┌─────────────────────────────────────────────────────────┐
│ Add formatting check  #2                                │
│ [Conversation] [Commits] [Checks] [Files changed]       │
│                                                         │
│  ❌ Some checks were not successful                     │
│     ✕ ci / Style (pull_request)   Details               │
│     ✓ ci / Tests (pull_request)   Details               │
└─────────────────────────────────────────────────────────┘
```

| Pestaña | Uso para diagnosticar |
|---|---|
| Conversation | Resumen de checks al final de la página |
| Commits | Cuántos commits llegaron realmente al PR |
| Checks | Cuántos jobs se ejecutaron y sus logs |
| Files changed | Qué archivos incluye el PR |

---

## 3.4 Git: los tres estados de un cambio

El error principal de esta sección: `ci.yml` estaba modificado pero **nunca se hizo commit**, así que GitHub seguía usando la versión anterior.

```
Working directory ──git add──► Staging ──git commit──► Repo local ──git push──► GitHub
   (archivo editado)            (preparado)            (commit)                 (remoto)
```

`git push` **solo sube commits**. Un archivo sin `git add` + `git commit` se queda en la Mac.

### La trampa del mensaje "up to date"

```
On branch formatting
Your branch is up to date with 'origin/formatting'.

Changes not staged for commit:
	modified:   .github/workflows/ci.yml
```

*"Up to date"* se refiere a los **commits**, no a los archivos. Los commits estaban sincronizados, pero el cambio nunca se convirtió en commit.

### Diagnóstico local vs. remoto

```bash
git status                              # ¿hay cambios sin commit?
git log --oneline -3                    # commits en la Mac
git log --oneline -3 origin/formatting  # commits en GitHub
gh run list --branch formatting --limit 3   # ¿el último push disparó una ejecución?
cat -e .github/workflows/ci.yml         # fin de línea = $, tabs = ^I
```

Si `HEAD` y `origin/formatting` apuntan al mismo commit y el archivo sigue en *not staged*, falta `git add` + `git commit` + `git push`.

---

## 3.5 Comandos nuevos de la Sección 3

### Formato en Go

```bash
go fmt ./...                          # formatea paquetes (excluye vendor)
gofmt -l .                            # lista archivos sin formato (incluye vendor)
gofmt -l $(find . -name '*.go' -not -path './vendor/*')   # solo código propio
gofmt -d <archivo>                    # diff sin modificar
gofmt -w <archivo>                    # corrige el archivo
test -z $(go fmt ./...) ; echo $?     # 0 = formateado, 1 = había cambios
test -z "$(go fmt ./...)"             # versión robusta con comillas
```

### Shell

```bash
$(comando)                            # sustitución de comandos
test -z "$var"                        # ¿string vacío?
echo $?                               # exit code del último comando
sed -i '' 's/viejo/nuevo/' archivo    # reemplazo en sitio (Mac)
sed -i 's/viejo/nuevo/' archivo       # reemplazo en sitio (Linux)
grep -n "texto" archivo               # buscar con número de línea
grep -n $'\t' archivo                 # detectar tabs (Mac)
cat -e archivo                        # ver fin de línea ($) y tabs (^I)
```

### Git y GitHub CLI

```bash
git branch --show-current             # rama actual
git diff <archivo>                    # cambios sin commit
git log --oneline -3 origin/<rama>    # commits en el remoto
git show HEAD --stat                  # archivos del último commit

gh pr create --repo OWNER/REPO --base main --head <rama> --title "..." --body "..."
gh pr checks                          # estado de los checks (exit ≠ 0 si alguno falla)
gh pr checks --watch                  # seguir en vivo
gh run view --log-failed              # logs de los steps fallidos
gh pr view --web                      # abrir el PR en el navegador
```

---

## 3.6 Notas y errores encontrados

| Situación | Causa | Solución |
|---|---|---|
| El curso dice "sigue en `addtests`", pero ya estaba mergeada | El curso asume que no se mergeó el PR #1 | Crear rama nueva desde `main` actualizado: `formatting` |
| `gofmt -l .` lista decenas de archivos en `vendor/` | Dependencias de terceros formateadas con un `gofmt` más antiguo | Ignorarlas; `go fmt ./...` ya las excluye |
| `get_api_key_test.go` aparecía sin formato | Espacios de más al alinear campos del struct (auto-indent de `nano`) | `go fmt ./...` y commit `style: ...` |
| `sed -i` falla en Mac | El `sed` de macOS (BSD) exige un argumento de extensión | `sed -i ''` en Mac; `sed -i` en Linux |
| El editor deshace el cambio al guardar | Auto-format on save (VS Code) | Usar `nano` o `sed` para romper el formato |
| `echo $?` no muestra el valor esperado | Se ejecutó otro comando entre `test` y `echo` | Ejecutar `echo $?` inmediatamente después |
| `test: too many arguments` | Varios archivos en la salida sin comillas | `test -z "$(go fmt ./...)"` |
| Push a la rama nueva sin ejecución de CI | No había PR abierto hacia `main` | Crear PR #2 (`formatting → main`) |
| El PR solo mostraba el check **Tests** | `ci.yml` modificado pero nunca commiteado | `git add` + `git commit` + `git push` |
| `git status` decía "up to date" con cambios pendientes | "Up to date" compara commits, no archivos | Revisar la sección *Changes not staged* |
| Duda sobre si hacer push a `main` para ver el CI | Confusión sobre qué dispara el workflow | Nunca push a `main`: push a la rama del PR |

### Reglas de trabajo consolidadas

1. **Rama mergeada = ciclo cerrado.** Si el curso nombra una rama ya mergeada, usar la rama activa.
2. **Nunca modificar `vendor/`.** Revisar formato solo sobre el código propio.
3. **Un archivo editado no está en GitHub** hasta pasar por `add` → `commit` → `push`.
4. **Antes de dudar del CI, comparar local vs. remoto:** `git log origin/<rama>`.
5. **Validar cada check nuevo rompiéndolo a propósito**, igual que con los tests.
6. **Jobs independientes van en paralelo**; solo usar `needs:` cuando hay dependencia real.

---

## 3.7 Flujo completo ejecutado en la Sección 3

```bash
# 1. Rama nueva desde main actualizado
cd ~/cicd_course/learn-cicd-starter
git checkout main
git pull origin main
git checkout -b formatting

# 2. Detectar y corregir el archivo propio sin formato
gofmt -l $(find . -name '*.go' -not -path './vendor/*')
gofmt -d internal/auth/get_api_key_test.go
go fmt ./...
go test ./...
git add internal/auth/get_api_key_test.go
git commit -m "style: format get_api_key_test.go with gofmt"

# 3. Lección Formatting: romper y restaurar con go fmt
sed -i '' 's/func GetAPIKey(headers http.Header) (string, error) {/func GetAPIKey(headers http.Header) (string, error){/' internal/auth/auth.go
gofmt -d internal/auth/auth.go
go fmt ./...
git status                                   # working tree clean

# 4. Lección Check Formatting: exit code con test -z
sed -i '' 's/func GetAPIKey(headers http.Header) (string, error) {/func GetAPIKey(headers http.Header) (string, error){/' internal/auth/auth.go
test -z $(go fmt ./...) ; echo $?            # 1
test -z $(go fmt ./...) ; echo $?            # 0

# 5. Lección Formatting CI: job Style
nano .github/workflows/ci.yml                # contenido en la sección 3.3
grep -n "^  [a-z]*:$" .github/workflows/ci.yml
git add .github/workflows/ci.yml
git commit -m "ci: add style job to check formatting"
git push -u origin formatting

# 6. PR #2 contra el fork
gh pr create --repo cecibelauda/learn-cicd-starter \
  --base main --head formatting \
  --title "Add formatting check" \
  --body "Adds a Style job that fails if code is not formatted with go fmt"
gh pr checks --watch                         # Tests ✅  Style ✅

# 7. Validar el fallo en GitHub
sed -i '' 's/func GetAPIKey(headers http.Header) (string, error) {/func GetAPIKey(headers http.Header) (string, error){/' internal/auth/auth.go
git add internal/auth/auth.go
git commit -m "test: break formatting on purpose"
git push
gh pr checks --watch                         # Tests ✅  Style ❌
gh run view --log-failed                     # exit code 1

# 8. Restaurar
go fmt ./...
git add internal/auth/auth.go
git commit -m "style: restore formatting"
git push
gh pr checks --watch                         # Tests ✅  Style ✅
```

---

## 3.8 Referencias oficiales de la Sección 3

**Go — formato**
- `go fmt`: https://pkg.go.dev/cmd/go#hdr-Gofmt__reformat__package_sources
- `gofmt` y sus flags: https://pkg.go.dev/cmd/gofmt
- Effective Go, Formatting: https://go.dev/doc/effective_go#formatting
- Patrones de paquetes (`./...` y `vendor`): https://pkg.go.dev/cmd/go#hdr-Package_lists_and_patterns
- Vendoring de módulos: https://go.dev/ref/mod#vendoring
- Go 1.19, doc comments: https://go.dev/doc/go1.19#go-doc

**Shell**
- `test` (POSIX): https://pubs.opengroup.org/onlinepubs/9699919799/utilities/test.html
- Command Substitution (Bash): https://www.gnu.org/software/bash/manual/html_node/Command-Substitution.html
- Exit Status (Bash): https://www.gnu.org/software/bash/manual/html_node/Exit-Status.html
- Bikeshedding: https://en.wiktionary.org/wiki/bikeshedding

**GitHub Actions**
- Jobs en un workflow (paralelos y `needs`): https://docs.github.com/en/actions/using-jobs/using-jobs-in-a-workflow
- `jobs.<job_id>.name`: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idname
- Shell por defecto en `run`: https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions#jobsjob_idstepsshell
- Evento `pull_request`: https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#pull_request
- Logs de ejecución: https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/monitoring-workflows/using-workflow-run-logs
- Status checks en PRs: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks

**GitHub CLI**
- `gh pr create`: https://cli.github.com/manual/gh_pr_create
- `gh pr checks`: https://cli.github.com/manual/gh_pr_checks
- `gh run view`: https://cli.github.com/manual/gh_run_view

**Git**
- Recording changes (estados de un archivo): https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository
- GitHub Flow: https://docs.github.com/en/get-started/using-github/github-flow

---

# SECCIÓN 4 — Linting

## 4.1 Formatting vs. Linting

| | Formatting (Sección 3) | Linting (Sección 4) |
|---|---|---|
| Se ocupa de | La **apariencia** del código: espacios, indentación, longitud de línea | El **análisis** del código para detectar problemas funcionales |
| Resultado | Código reescrito con el formato estándar | Advertencias o errores sobre código potencialmente problemático |
| Herramienta en Go | `go fmt` / `gofmt` | `staticcheck` |
| ¿Modifica archivos? | Sí | No, solo reporta |

> **Idea central:** el formato dice *cómo se ve* el código; el linter dice *si algo huele mal* aunque compile.

### Staticcheck

[Staticcheck](https://staticcheck.dev/docs/) es el linter recomendado por el curso: tiene muchas verificaciones útiles, valores por defecto sensatos y es fácil de configurar. En la práctica reemplazó a `golint` (deprecado) como el linter más popular de Go.

### Equivalencia con el stack de La Tinka

| Go | Java |
|---|---|
| `go fmt` | Spotless / google-java-format |
| `staticcheck` | SpotBugs, PMD, reglas de SonarQube |
| `go vet` | Advertencias de `javac -Xlint` |

---

## 4.2 Instalar y ejecutar staticcheck localmente

### Instalación

```bash
go install honnef.co/go/tools/cmd/staticcheck@latest
```

O con Homebrew en Mac:

```bash
brew install staticcheck
```

### Si aparece `command not found`

`go install` deja el binario en `$(go env GOPATH)/bin` (por defecto `~/go/bin`), que puede no estar en el `PATH`.

La lección usa `~/.bashrc`, pero en Mac el shell por defecto es **Zsh** → el archivo es `~/.zshrc`:

```bash
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.zshrc
source ~/.zshrc
which staticcheck
staticcheck -version
```

Se usa `$(go env GOPATH)` en lugar de `$GOPATH` porque en Mac esa variable suele estar vacía en el shell.

### Ejecutar — siempre desde la raíz del repo

```bash
cd ~/cicd_course/learn-cicd-starter
staticcheck ./... ; echo "exit code: $?"
```

Con el proyecto limpio: **sin salida** y `exit code: 0` (en las herramientas de Go, silencio = éxito).

### El patrón `./...`

Es un **patrón de paquetes de Go**, no del shell: el directorio actual **y todos sus subdirectorios**, recursivamente.

```
learn-cicd-starter/         ← ejecutas aquí: ./...
├── main.go                 ✅ incluido
├── internal/
│   ├── auth/               ✅ incluido
│   └── database/           ✅ incluido
└── vendor/                 ❌ excluido automáticamente
```

⚠️ Ejecutado desde `~`, `./...` intenta recorrer todo el home y choca con carpetas protegidas por macOS:

```
-: pattern ./...: open Library/Accounts: operation not permitted (compile)
```

---

## 4.3 Validar localmente con una función sin usar (U1000)

### Agregar la función con un heredoc

```bash
cat >> main.go << 'EOF'

func unused() {
	// this function does nothing
	// and is called nowhere
}
EOF
```

### Anatomía del heredoc

| Parte | Qué hace |
|---|---|
| `cat` | Lee texto de entrada y lo imprime |
| `>> main.go` | En lugar de imprimirlo, lo **agrega al final** de `main.go` |
| `<< 'EOF'` | "Lo que escriba a continuación es la entrada, hasta encontrar `EOF`" |
| `EOF` (línea final) | Marca de cierre (*End Of File*). Puede ser cualquier palabra; va **sola en su línea** |

```
cat >> main.go << 'EOF'     ← "empieza a capturar texto"
func unused() {             ┐
    // ...                  │  texto capturado
}                           ┘
EOF                         ← "deja de capturar" → se escribe en main.go
```

| Forma | Comportamiento |
|---|---|
| `<< EOF` | El shell **interpreta** `$variables` y `$(comandos)` dentro del texto |
| `<< 'EOF'` | El texto se copia **literal** (recomendado para código) |

El prompt `heredoc>` indica que Zsh está esperando la palabra de cierre.

### `>>` vs `>`

```bash
echo "hola" >> archivo.txt   # AGREGA al final
echo "hola" >  archivo.txt   # BORRA todo y escribe solo "hola" ⚠️
```

⚠️ Ambos **crean el archivo si no existe**. Un error de tipeo (`mian.go`) crea un archivo nuevo sin dar error. Usar **Tab** para autocompletar nombres.

### Verificar

```bash
tail -6 main.go
go fmt ./...
go build ./...                   # compila sin errores
staticcheck ./... ; echo "exit code: $?"
```

```
main.go:XX:6: func unused is unused (U1000)
exit code: 1
```

| Parte | Significado |
|---|---|
| `main.go:XX:6` | Archivo, línea y columna |
| `func unused is unused` | Descripción del problema |
| `U1000` | Código del check (familia `U` = *unused*) |
| `exit code: 1` | Lo que leerá GitHub Actions para hacer fallar el step |

### Compilador vs. linter

**El código compila.** Go solo prohíbe *imports* y *variables locales* sin usar; una función sin usar es válida para el compilador. Para eso existe el linter.

| Detecta | Compilador de Go | staticcheck |
|---|---|---|
| Imports y variables locales sin usar | ✅ (no compila) | ✅ |
| Funciones y tipos sin usar | ❌ | ✅ U1000 |
| `Printf` con formato incorrecto | ❌ | ✅ SA5009 |
| Código simplificable | ❌ | ✅ S1001 |

### Exit code: `go fmt` vs. `staticcheck`

| | `go fmt` | `staticcheck` |
|---|---|---|
| Exit code si hay problemas | Siempre `0` → requiere `test -z` | `1` directamente |
| Uso en CI | `run: test -z $(go fmt ./...)` | `run: staticcheck ./...` |

---

## 4.4 CI Linting — staticcheck en el job Style

**Tarea:** agregar staticcheck al **mismo job `style`**, después de `go fmt`. Como el runner no trae staticcheck instalado, hay que instalarlo antes de usarlo.

### Workflow actualizado: `.github/workflows/ci.yml`

```yaml
name: ci

on:
  pull_request:
    branches: [main]

jobs:
  tests:
    name: Tests
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Run unit tests
        run: go test -cover ./...

  style:
    name: Style
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Check formatting
        run: test -z $(go fmt ./...)

      - name: Install staticcheck
        run: go install honnef.co/go/tools/cmd/staticcheck@latest

      - name: Run staticcheck
        run: staticcheck ./...
```

Solo cambian las **dos últimas steps** del job `style`.

### Orden de los steps en el job Style

```
Runner "Style"
 ├── checkout                  (clona el código)
 ├── setup-go                  (instala Go y agrega GOPATH/bin al PATH)
 ├── test -z $(go fmt ./...)   ✅ formato correcto
 ├── go install staticcheck    (el runner no lo trae instalado)
 └── staticcheck ./...         ❌ exit 1 → U1000
```

`staticcheck` se instala **después** de `setup-go`, porque `go install` necesita Go. `setup-go` además agrega `GOPATH/bin` al `PATH` del runner, por eso el comando se encuentra sin configurar nada.

### Validación del fallo en GitHub

| Commit | Contenido | Resultado |
|---|---|---|
| `ci: add staticcheck linting (unused function on purpose)` | Workflow nuevo + función `unused` | Style ❌ / Tests ✅ |
| `fix: remove unused function` | `main.go` restaurado desde `main` | Style ✅ / Tests ✅ |

```bash
gh run view --repo cecibelauda/learn-cicd-starter --log-failed
```

```
Style  Run staticcheck  main.go:XX:6: func unused is unused (U1000)
Style  Run staticcheck  ##[error]Process completed with exit code 1.
```

| Resultado con la función `unused` | Significado |
|---|---|
| Style ❌ en *Run staticcheck* | ✅ Correcto |
| Style ❌ en *Check formatting* | `main.go` quedó sin formato: `go fmt ./...`, commit y push |
| Style ✅ | El `ci.yml` o el `main.go` no llegaron al commit: `git show HEAD --stat` |

### Eliminar la función de forma segura

Restaurar `main.go` desde `main`, donde la función nunca existió:

```bash
git restore --source=main main.go
git diff main -- main.go         # sin salida = idéntico a main ✅
```

### Dónde ver el CI en la web

| Camino | Pasos |
|---|---|
| Desde el PR | **Pull requests** → PR #3 → sección de checks al final (o pestaña **Checks**) |
| Desde Actions | **Actions** → ejecución más reciente (rama `linting`) → job **Style** |

La portada del repo muestra la rama `main`, que no refleja el CI del PR.

### Buena práctica: fijar la versión

`@latest` puede traer checks nuevos y romper el CI sin que cambie el código. En pipelines reales se fija la versión:

```yaml
run: go install honnef.co/go/tools/cmd/staticcheck@2025.1.1
```

Alternativa: la action oficial [`dominikh/staticcheck-action`](https://github.com/dominikh/staticcheck-action).

---

## 4.5 Git: sincronizar una rama con `main`

### El problema

La rama `linting` se creó desde un `main` local **desactualizado**, sin el job Style del PR #2.

```
GitHub main:   A ── B ── C (merge PR #2: job Style ✅)
                    │
local main:    A ── B          ← sin git pull
                    │
linting:            └── (copia de B: ci.yml sin Style ❌)
```

### La solución

```bash
git restore .github/workflows/ci.yml internal/auth/get_api_key_test.go
git stash
git checkout main
git pull origin main
grep -n "style:" .github/workflows/ci.yml
git checkout linting
git merge main
git stash pop
```

| Archivo | Acción | Motivo |
|---|---|---|
| `ci.yml` | Descartar (`git restore`) | Se editó sobre la versión vieja; se reescribe completo |
| `get_api_key_test.go` | Descartar | La corrección de formato ya venía desde `main` |
| `main.go` | Guardar (`git stash`) | Contenía la función `unused` necesaria para la lección |

### `pull` vs. `merge`

```
git pull origin main  =  git fetch origin main  +  git merge origin/main
                         (descargar)               (fusionar)
```

| Comando | Origen de los cambios | Cuándo usarlo |
|---|---|---|
| `git pull origin main` | GitHub (remoto) | Actualizar una rama con su versión en GitHub |
| `git merge main` | Tu Mac (local) | Traer cambios de otra rama local ya actualizada |

```
GitHub main ──pull──► local main ──merge──► linting
```

### Fast-forward

```
Updating 64a0745..e0af0a7
Fast-forward
```

Git solo movió el puntero de `main` hacia adelante, porque no había commits locales que fusionar → sin conflictos.

### `git stash`

| Comando | Qué hace |
|---|---|
| `git stash` | Guarda los cambios sin commit y deja la carpeta limpia |
| `git stash list` | Muestra lo guardado |
| `git stash show` | Archivos del último stash |
| `git stash pop` | Aplica los cambios **y los borra** del stash |
| `git stash apply` | Aplica los cambios **pero los conserva** |
| `git stash drop` | Borra el stash manualmente |

Analogía: guardar papeles en un cajón para despejar el escritorio (`stash`) y luego sacarlos (`pop`).

El stash no guarda una copia del archivo, sino **las diferencias**. Al hacer `pop`:

| Situación | Resultado |
|---|---|
| El archivo no cambió en la otra rama | Aplica tus cambios directamente |
| Cambios en líneas distintas | Fusiona ambos automáticamente |
| Cambios en las mismas líneas | Conflicto (`<<<<<<<` / `=======` / `>>>>>>>`); el stash **se conserva** |

Resolver un conflicto de stash:

```bash
nano text.go          # dejar el código correcto y borrar las marcas
git add text.go
git stash drop
```

### Cómo leer `git diff`

```diff
diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
index 7748090..0e4f957 100644
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -35,3 +36,9 @@ jobs:
       - name: Check formatting
         run: test -z $(go fmt ./...)
+
+      - name: Install staticcheck
+        run: go install honnef.co/go/tools/cmd/staticcheck@latest
```

| Elemento | Significado |
|---|---|
| `--- a/...` | **a** = versión anterior (último commit) |
| `+++ b/...` | **b** = versión nueva (archivo actual) |
| `index 7748090..0e4f957` | Identificadores de la versión antes y después |
| `100644` | Permisos: archivo normal, no ejecutable |
| `@@ -35,3 +36,9 @@` | Antes: desde la línea 35, 3 líneas. Después: desde la 36, 9 líneas |
| `+` / `-` / (espacio) | Agregada / eliminada / contexto |

---

## 4.6 Repaso de checks de staticcheck

Lista completa: https://staticcheck.dev/docs/checks/

| Código | Nombre | Qué detecta |
|---|---|---|
| **U1000** | Unused | Variables, funciones y tipos sin usar |
| **SA5009** | Invalid Printf call | Llamadas a `Printf` inválidas, ej. un string con `%d` |
| **SA9001** | Defer in range loops | `defer` dentro de bucles `range`, que puede no ejecutarse cuando se espera |
| **S1001** | Replace for loop with copy | Bucles que copian un slice elemento por elemento |

Ejemplo de S1001:

```go
// Antes
for i, x := range src {
    dst[i] = x
}

// Después
copy(dst, src)
```

### Familias de checks

| Prefijo | Familia |
|---|---|
| `SA` | *staticcheck*: bugs y usos incorrectos |
| `S` | *simple*: código que se puede simplificar |
| `ST` | *stylecheck*: convenciones de estilo |
| `QF` | *quickfix*: refactorizaciones sugeridas |
| `U` | *unused*: código sin usar |

---

## 4.7 Comandos nuevos de la Sección 4

### Staticcheck

```bash
go install honnef.co/go/tools/cmd/staticcheck@latest
brew install staticcheck
which staticcheck
staticcheck -version
staticcheck ./...
staticcheck ./... ; echo $?           # 0 = limpio, 1 = hallazgos
go env GOPATH                         # dónde instala go install (~/go)
```

### Zsh / shell

```bash
echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.zshrc
echo 'setopt interactivecomments' >> ~/.zshrc   # permite # como comentario al pegar comandos
source ~/.zshrc
cat >> archivo << 'EOF'               # heredoc: agregar varias líneas
...
EOF
cd ../..                              # subir dos niveles
pwd                                   # directorio actual
```

### Git

```bash
git stash
git stash list
git stash show
git stash pop
git stash drop
git merge main
git restore <archivo>                 # descartar cambios sin commit
git restore --source=main <archivo>   # restaurar desde otra rama
git diff main -- <archivo>            # comparar con otra rama
```

### GitHub CLI

```bash
gh pr list --repo bootdotdev/learn-cicd-starter --author cecibelauda   # detectar PRs equivocados
gh pr close <N> --repo bootdotdev/learn-cicd-starter
gh pr view <N> --repo cecibelauda/learn-cicd-starter --json state
gh pr merge <N> --repo cecibelauda/learn-cicd-starter --merge
```

---

## 4.8 Notas y errores encontrados

| Situación | Causa | Solución |
|---|---|---|
| `open Library/Accounts: operation not permitted` | `staticcheck ./...` ejecutado desde `~` | Ejecutar desde la raíz del repo |
| La lección indica `~/.bashrc` | El shell de la Mac es Zsh | Usar `~/.zshrc` |
| Se creó `mian.go` en lugar de editar `main.go` | Error de tipeo; `>>` crea el archivo si no existe | `rm mian.go` y repetir; usar Tab para autocompletar |
| `git diff .github/workflows/ci.yml` → *ambiguous argument* | Ejecutado dentro de `.github/workflows/` | Volver a la raíz: `cd ~/cicd_course/learn-cicd-starter` |
| `ci.yml` de `linting` sin el job Style | Rama creada desde un `main` local desactualizado | `git pull` en `main` y `git merge main` en `linting` |
| `get_api_key_test.go` modificado sin motivo | `go fmt` corrigió de nuevo el archivo viejo | `git restore`: la corrección ya venía de `main` |
| `error: pathspec '#' did not match` / `invalid mode specification` | Zsh no trata `#` como comentario al pegar comandos | `setopt interactivecomments` en `~/.zshrc` |
| `git status` con comentario dijo "clean" sin serlo | Las palabras del comentario se tomaron como rutas | Ejecutar `git status` sin comentarios |
| Commit del documento no aparecía en la portada | Se hizo en `formatting`; la portada muestra `main` | Ver la rama en GitHub o mergear el PR |
| PR creado desde la web fue a `bootdotdev` (#2988) | GitHub propone el repo original como base | `gh pr close` y crear desde `.../compare/main...linting` del fork |
| GitHub muestra *Merge pull request* tras los checks | Es normal cuando todo pasa | Enviar primero en Boot.dev; mergear después |

### Reglas de trabajo consolidadas

1. **Todos los comandos con `./...` y de Git se ejecutan desde la raíz del repo.** Revisar que el prompt diga `learn-cicd-starter %`.
2. **`git pull origin main` antes de `git checkout -b`**, siempre.
3. **Al crear un PR desde la web, verificar que la base sea el fork**, no `bootdotdev`.
4. **Un linter no modifica código**: reporta y devuelve exit code ≠ 0.
5. **Instalar en el runner toda herramienta que no venga por defecto**, después de `setup-go`.
6. **Fijar versiones de herramientas en CI** para builds reproducibles.

---

## 4.9 Flujo completo ejecutado en la Sección 4

```bash
# 1. Cerrar el ciclo del PR #2
cd ~/cicd_course/learn-cicd-starter
gh pr merge 2 --repo cecibelauda/learn-cicd-starter --merge
git checkout main
git pull origin main
git checkout -b linting

# 2. Lección Linting: validar staticcheck localmente
staticcheck ./... ; echo "exit code: $?"          # 0
cat >> main.go << 'EOF'

func unused() {
	// this function does nothing
	// and is called nowhere
}
EOF
go fmt ./...
go build ./...
staticcheck ./... ; echo "exit code: $?"          # U1000, 1

# 3. Lección CI Linting: agregar staticcheck al job Style
cat > .github/workflows/ci.yml << 'EOF'
# contenido completo en la sección 4.4
EOF
git diff .github/workflows/ci.yml
grep -n $'\t' .github/workflows/ci.yml            # sin salida

# 4. Commit con la función unused (debe fallar)
git add .github/workflows/ci.yml main.go
git commit -m "ci: add staticcheck linting (unused function on purpose)"
git push -u origin linting

# 5. PR #3 contra el fork
gh pr create --repo cecibelauda/learn-cicd-starter \
  --base main --head linting \
  --title "Add linting check" \
  --body "Adds staticcheck to the Style job"
gh pr checks --repo cecibelauda/learn-cicd-starter --watch   # Style ❌  Tests ✅

# 6. Eliminar la función unused
git restore --source=main main.go
staticcheck ./... ; echo "lint: $?"               # 0
git add main.go
git commit -m "fix: remove unused function"
git push origin linting
gh pr checks --repo cecibelauda/learn-cicd-starter --watch   # Style ✅  Tests ✅

# 7. Enviar en Boot.dev la URL del repo
# https://github.com/cecibelauda/learn-cicd-starter
```

---

## 4.10 Referencias oficiales de la Sección 4

**Staticcheck**
- Documentación: https://staticcheck.dev/docs/
- Getting started: https://staticcheck.dev/docs/getting-started/
- Lista de checks: https://staticcheck.dev/docs/checks/
- U1000: https://staticcheck.dev/docs/checks/#U1000
- Running in CI (GitHub Actions): https://staticcheck.dev/docs/running-staticcheck/ci/github-actions/
- `dominikh/staticcheck-action`: https://github.com/dominikh/staticcheck-action
- `golint` (deprecado): https://github.com/golang/lint

**Go**
- Package lists and patterns (`./...`): https://pkg.go.dev/cmd/go#hdr-Package_lists_and_patterns
- GOPATH: https://pkg.go.dev/cmd/go#hdr-GOPATH_environment_variable
- `go vet`: https://pkg.go.dev/cmd/vet

**Shell**
- Here Documents: https://www.gnu.org/software/bash/manual/html_node/Redirections.html#Here-Documents
- Redirections: https://www.gnu.org/software/bash/manual/html_node/Redirections.html
- Zsh INTERACTIVE_COMMENTS: https://zsh.sourceforge.io/Doc/Release/Options.html#index-INTERACTIVE_005fCOMMENTS
- Lint (software): https://en.wikipedia.org/wiki/Lint_%28software%29

**Git**
- `git stash`: https://git-scm.com/docs/git-stash
- `git merge` (fast-forward): https://git-scm.com/docs/git-merge#_fast_forward_merge
- `git pull`: https://git-scm.com/docs/git-pull
- `git fetch`: https://git-scm.com/docs/git-fetch
- `git restore`: https://git-scm.com/docs/git-restore
- `git diff`: https://git-scm.com/docs/git-diff
- Formato unificado de diff: https://www.gnu.org/software/diffutils/manual/html_node/Detailed-Unified.html
- Resolver conflictos: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/addressing-merge-conflicts/resolving-a-merge-conflict-using-the-command-line

**GitHub**
- Viewing workflow run history: https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/monitoring-workflows/viewing-workflow-run-history
- Viewing branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/viewing-branches-in-your-repository
- `gh pr close`: https://cli.github.com/manual/gh_pr_close

---

# SECCIÓN 5 — Security

## 5.1 Verificaciones de seguridad estáticas

Otro uso habitual de la CI son las **verificaciones de seguridad estáticas**: análisis que se ejecutan sobre el código (sin correrlo) para encontrar posibles vulnerabilidades.

La herramienta open source más popular para Go es **[Gosec](https://github.com/securego/gosec)**.

> **Idea central:** `go fmt` cuida la apariencia, `staticcheck` cuida la calidad y `gosec` cuida la **seguridad**. Las tres convierten sus hallazgos en un exit code ≠ 0 que GitHub Actions entiende.

### Instalación y ejecución local

```bash
go install github.com/securego/gosec/v2/cmd/gosec@latest
gosec ./...                 # siempre desde la raíz del repo
```

Si aparece `command not found`, aplica la misma solución de la Sección 4.2 (`$(go env GOPATH)/bin` en el `PATH` de `~/.zshrc`).

### Cómo leer un hallazgo de gosec

```
[/Users/Cecibel/learn-cicd-starter/main.go:92-95] - G112 (CWE-400): Potential Slowloris Attack because ReadHeaderTimeout is not configured in the http.Server (Confidence: LOW, Severity: MEDIUM)
    91: router.Mount("/v1", v1Router)
  > 92: srv := &http.Server{
  > 93: Addr:    ":" + port,
  > 94: Handler: router,
  > 95: }

Summary:
  Files  : 12
  Lines  : 618
  Nosec  : 0
  Issues : 1
```

| Parte | Significado |
|---|---|
| `main.go:92-95` | Archivo y líneas afectadas |
| `G112` | Código de la regla de gosec |
| `CWE-400` | Clasificación estándar de la debilidad ([MITRE CWE](https://cwe.mitre.org/)) |
| `Confidence` | Qué tan seguro está gosec de que es un problema real |
| `Severity` | Qué tan grave sería si lo es |
| `>` | Líneas exactas del hallazgo |
| `Nosec` | Cuántas líneas fueron excluidas con `#nosec` |
| `Issues` | Total de hallazgos → si es > 0, exit code 1 |

### Equivalencia con el stack de La Tinka

| Go | Java |
|---|---|
| `gosec` | SpotBugs + Find Security Bugs, reglas de seguridad de SonarQube (*Vulnerabilities* y *Security Hotspots*) |
| Códigos `G1xx` | Reglas `java:S...` de Sonar / categorías OWASP |
| `// #nosec G706 -- motivo` | `@SuppressWarnings` / `// NOSONAR` |

---

## 5.2 CI Security — gosec en el job Tests

**Tarea:** igual que `staticcheck`, `gosec` no viene con Go, así que hay que instalarlo en el runner. Como la seguridad **no es un tema de estilo**, va en el job **Tests**, después de `go test`.

### Workflow actualizado: `.github/workflows/ci.yml`

```yaml
name: ci

on:
  pull_request:
    branches: [main]

jobs:
  tests:
    name: Tests
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Run unit tests
        run: go test -cover ./...

      - name: Install gosec
        run: go install github.com/securego/gosec/v2/cmd/gosec@latest

      - name: Run gosec
        run: gosec ./...

  style:
    name: Style
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Check formatting
        run: test -z $(go fmt ./...)

      - name: Install staticcheck
        run: go install honnef.co/go/tools/cmd/staticcheck@latest

      - name: Run staticcheck
        run: staticcheck ./...
```

Solo cambian las **dos últimas steps del job `tests`**.

### Qué va en cada job

| Job | Pregunta que responde | Steps |
|---|---|---|
| **Tests** | ¿El código funciona y es seguro? | `go test`, `gosec` |
| **Style** | ¿El código se ve y está escrito bien? | `go fmt`, `staticcheck` |

> 💡 No hace falta configurar el `PATH` en el runner: `actions/setup-go` ya agrega `$(go env GOPATH)/bin`.

### Validación del fallo (intencional)

La primera vez que se hace push del nuevo `ci.yml`, el check **debe fallar**, porque el código de Notely todavía tiene hallazgos.

```
           ┌──────────── Job: Tests ────────────┐
 push ──►  checkout → setup-go → go test ✅ → install gosec ✅ → gosec ❌
           └────────────────────────────────────┘
           ┌──────────── Job: Style ────────────┐
           checkout → setup-go → go fmt ✅ → staticcheck ✅
           └────────────────────────────────────┘
```

| Commit | Resultado |
|---|---|
| `ci: add gosec security check to tests job` | Tests ❌ (en *Run gosec*) / Style ✅ |

---

## 5.3 Fix Security Issues — corregir los hallazgos

**Tarea:** corregir los problemas de seguridad **sin romper funcionalidad**. Si el archivo `.env` no existe, el servidor solo debe imprimir una advertencia y continuar (eso ya estaba resuelto en `main.go`).

### Hallazgos encontrados

| Regla | CWE | Archivo | Problema | Riesgo |
|---|---|---|---|---|
| **G104** | CWE-703 | `json.go` | `w.Write(dat)` ignora el error que devuelve | Fallos silenciosos al escribir la respuesta |
| **G112** | CWE-400 | `main.go` | `http.Server` sin `ReadHeaderTimeout` | Ataque **Slowloris** (agotar conexiones) |
| **G706** | CWE-117 | `main.go` | Se loguea `port` (variable de entorno) sin validar | **Log injection** (líneas falsas en el log) |

> ⚠️ **G706 no lo menciona el curso**: es una regla nueva de gosec que salió en el análisis local (versión `dev`). Como el CI usa `@latest`, también la habría detectado.

### G104 — errores no manejados

En Go, ignorar un error es un bug silencioso. Si `Write` falla (por ejemplo, porque el cliente cerró la conexión), nadie se entera.

**Antes:**

```go
	w.WriteHeader(code)
	w.Write(dat)
}
```

**Después:**

```go
	w.WriteHeader(code)
	if _, err := w.Write(dat); err != nil {
		log.Printf("Error writing response: %s", err)
	}
}
```

Solo se registra en el log: como `WriteHeader` ya envió los headers, no se puede cambiar el status code.

### G112 — Slowloris

🧠 **Analogía:** un cliente llega a la ventanilla y dicta su pedido letra por letra, una cada 10 minutos. Si nadie le pone un límite, unos pocos clientes así bloquean todas las ventanillas. `ReadHeaderTimeout` es ese límite.

```
Cliente lento ──H──(espera)──e──(espera)──a──...  ⏱ 10 s → ❌ conexión cerrada
```

```go
	srv := &http.Server{
		Addr:              ":" + strconv.Itoa(portNum),
		Handler:           router,
		ReadHeaderTimeout: 10 * time.Second,
	}
```

Requiere `import "time"`.

Otros timeouts de `http.Server` que se usan en producción:

| Campo | Limita |
|---|---|
| `ReadHeaderTimeout` | Tiempo para leer **los headers** |
| `ReadTimeout` | Tiempo para leer **toda la request** (headers + body) |
| `WriteTimeout` | Tiempo para escribir la respuesta |
| `IdleTimeout` | Tiempo que una conexión keep-alive puede quedar inactiva |

### G706 — Log injection (taint analysis)

`port` viene de `os.Getenv("PORT")`, es decir, de **fuera del programa**. gosec lo marca como dato **contaminado** (*tainted*) y sigue su recorrido hasta el log.

🧠 **Analogía:** un libro de visitas donde alguien escribe `"Juan\n10:40 ADMIN: acceso concedido"` e inventa una línea falsa en el registro.

```
os.Getenv("PORT") ──(sin validar)──────────────────► log.Printf(...)  ❌ G706
os.Getenv("PORT") ──► strconv.Atoi ──► int validado ──► log.Printf(...)  ✅
```

**Solución:** validar que el puerto sea un número en el rango válido y usar **solo el valor validado**:

```go
	port := os.Getenv("PORT")
	if port == "" {
		log.Fatal("PORT environment variable is not set")
	}
	portNum, err := strconv.Atoi(port)
	if err != nil || portNum < 1 || portNum > 65535 {
		log.Fatal("PORT environment variable must be a number between 1 and 65535")
	}
	...
	log.Printf("Serving on port: %d\n", portNum)   // %d y portNum, no %s y port
```

Requiere `import "strconv"`.

⚠️ **Detalle clave:** si se valida pero se sigue logueando `port` (el string original), G706 **persiste**. Hay que usar `portNum` en todos los lugares donde antes se usaba `port`.

### `#nosec`: excepciones justificadas

Si una regla marca un falso positivo, se puede silenciar **con justificación**:

```go
log.Printf("Serving on port: %d\n", portNum) // #nosec G706 -- portNum validated as int in range 1-65535
```

| ✅ Correcto | ❌ Incorrecto |
|---|---|
| `#nosec G706 -- motivo` (regla específica + justificación) | `#nosec` a secas (silencia todas las reglas de la línea) |
| Después de validar el dato | Para que el CI pase sin corregir nada |

No fue necesario en este caso: con `portNum` validado, gosec reportó `Issues : 0`.

### Código final de `main.go` (partes modificadas)

```go
import (
	"database/sql"
	"embed"
	"io"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/go-chi/chi"
	"github.com/go-chi/cors"
	"github.com/joho/godotenv"

	"github.com/bootdotdev/learn-cicd-starter/internal/database"

	_ "github.com/tursodatabase/libsql-client-go/libsql"
)

func main() {
	err := godotenv.Load(".env")
	if err != nil {
		log.Printf("warning: assuming default configuration. .env unreadable: %v", err)
	}

	port := os.Getenv("PORT")
	if port == "" {
		log.Fatal("PORT environment variable is not set")
	}
	portNum, err := strconv.Atoi(port)
	if err != nil || portNum < 1 || portNum > 65535 {
		log.Fatal("PORT environment variable must be a number between 1 and 65535")
	}

	// ... (sin cambios) ...

	router.Mount("/v1", v1Router)
	srv := &http.Server{
		Addr:              ":" + strconv.Itoa(portNum),
		Handler:           router,
		ReadHeaderTimeout: 10 * time.Second,
	}

	log.Printf("Serving on port: %d\n", portNum)
	log.Fatal(srv.ListenAndServe())
}
```

### Verificación local completa (replica el CI)

```bash
cd ~/learn-cicd-starter
go fmt ./...
go build -o notely && echo "build OK"
go test -cover ./...
test -z "$(go fmt ./...)" && echo "fmt OK"
staticcheck ./...
gosec ./...                                   # Issues : 0
```

### Prueba funcional

```bash
PORT=8080 ./notely
# en otra terminal:
curl -i http://localhost:8080/v1/healthz     # HTTP/1.1 200 OK
```

---

## 5.4 Security Review — la CI no reemplaza el criterio

Pasar todos los tests, linters y checks de seguridad **no significa que el código sea perfecto**, ni siquiera que sea "bueno".

Las pruebas automatizadas eliminan aproximadamente el **~80 %** de los bugs obvios, antipatrones de estilo y vulnerabilidades, pero no todo. **Igual hay que usar la cabeza.**

🧠 **Analogía:** la CI es el detector de metales del aeropuerto. Atrapa lo obvio, pero no reemplaza al agente que observa comportamientos sospechosos.

```
┌────────── Calidad del código ──────────┐
│  ~80 % → CI automática                 │
│          (tests, fmt, staticcheck,     │
│           gosec)                       │
│  ~20 % → criterio humano               │
│          (code review, diseño,         │
│           lógica de negocio, authz)    │
└────────────────────────────────────────┘
```

Ejemplos de lo que `gosec` **no** detecta:

| Riesgo | Por qué se le escapa |
|---|---|
| Un usuario puede ver notas de otro (falla de autorización) | Es lógica de negocio, no un patrón de código |
| CORS demasiado abierto (`AllowedOrigins: "https://*"`) | Es una decisión de configuración válida en sintaxis |
| API keys sin expiración ni rotación | Es diseño del sistema |
| Datos sensibles en logs por diseño | Solo detecta flujos que reconoce como *tainted* |

---

## 5.5 Comandos nuevos de la Sección 5

### Gosec

```bash
go install github.com/securego/gosec/v2/cmd/gosec@latest
gosec ./...                          # analizar todo el código propio
gosec ./... ; echo $?                # 0 = limpio, 1 = hallazgos
gosec -include=G104,G112 ./...       # solo ciertas reglas
gosec -exclude=G104 ./...            # excluir reglas
gosec -fmt=json -out=report.json ./...   # reporte en JSON
```

### nano (edición sin mouse)

Seleccionar con el mouse lo hace la **Terminal de Mac**, no nano; por eso `Delete` no borra la selección.

| Atajo | Acción |
|---|---|
| `nano +99 archivo` | Abrir el archivo directamente en la línea 99 |
| `Ctrl + K` | Cortar (borrar) la línea completa |
| `Ctrl + 6` | Iniciar una selección (*mark*); luego flechas + `Ctrl + K` |
| `Ctrl + U` | Pegar lo último cortado |
| `Ctrl + _` | Ir a un número de línea |
| `Ctrl + E` / `Ctrl + A` | Ir al final / inicio de la línea |
| `Ctrl + O` → `Enter` | Guardar |
| `Ctrl + X` | Salir |

### Shell y Git

```bash
sed -n '103p' main.go                 # imprimir solo la línea 103
cat -n main.go | sed -n '90,110p'     # ver un rango con números de línea
tail -12 main.go                      # últimas 12 líneas
git rev-parse --show-toplevel         # ruta de la raíz del repo
cd $(git rev-parse --show-toplevel)   # ir a la raíz desde cualquier subcarpeta
git branch -d security                # borrar la rama local ya mergeada
```

---

## 5.6 Notas y errores encontrados

| Situación | Causa | Solución |
|---|---|---|
| `fatal: pathspec '.github/workflows/ci.yml' did not match any files` | `git add` ejecutado **dentro** de `.github/workflows/` → Git buscó `.github/workflows/.github/workflows/ci.yml` | Volver a la raíz (`cd ~/learn-cicd-starter`) y repetir `add` + `commit` + `push` |
| `git push` creó la rama `security` en GitHub, pero vacía | El commit anterior falló; `push` subió la rama sin cambios nuevos | Hacer el commit desde la raíz y `git push` de nuevo |
| `no new variables on left side of :=` | El bloque `srv := &http.Server{...}` se **pegó debajo** del original en vez de reemplazarlo | Borrar el bloque viejo; dejar un solo `srv :=` antes de `ListenAndServe()` |
| Código después de `log.Fatal(srv.ListenAndServe())` | Ese código nunca se ejecuta: el servidor bloquea ahí | El `srv` siempre se define **antes** |
| En nano, seleccionar con el mouse + `Delete` no borra | La selección es de la Terminal, no de nano | `Ctrl + K` por línea, o `Ctrl + 6` + flechas + `Ctrl + K` |
| G706 persistía después de validar con `strconv.Atoi` | El `log.Printf` seguía usando `port` (string original) | Usar `portNum` con `%d` |
| `gosec` reporta G706, que el curso no menciona | Regla nueva de gosec (taint analysis) | Validar el dato de entrada; `#nosec` solo con justificación |
| `Error building the SSA representation... type errors` | `gosec` no puede analizar código que no compila | Primero `go build`; después `gosec` |

### Reglas de trabajo consolidadas

1. **Todos los comandos de Git y Go se ejecutan desde la raíz del repo.** Revisar que el prompt diga `learn-cicd-starter %`, no `workflows %`.
2. **Reemplazar no es agregar:** al corregir un bloque de código, borrar el original.
3. **Orden de verificación:** `go build` → `go test` → `go fmt` → `staticcheck` → `gosec`. Si no compila, los demás no sirven.
4. **Todo dato externo (env vars, headers, body) se valida antes de usarlo**, y después se usa **solo el valor validado**.
5. **Nunca ignorar un error en Go:** manejarlo o, como mínimo, loguearlo.
6. **`#nosec` solo con regla específica y justificación.**
7. **La CI cubre ~80 %; el code review cubre el resto.**

---

## 5.7 Flujo completo ejecutado en la Sección 5

```bash
# 1. Rama nueva desde main actualizado
cd ~/learn-cicd-starter
git checkout main
git pull origin main
git checkout -b security

# 2. Lección Security Checks: gosec local
go install github.com/securego/gosec/v2/cmd/gosec@latest
gosec ./...                                    # hallazgos (no corregir aún)

# 3. Lección CI Security: agregar gosec al job Tests
nano .github/workflows/ci.yml                  # contenido en la sección 5.2
git add .github/workflows/ci.yml               # ⚠️ desde la raíz
git commit -m "ci: add gosec security check to tests job"
git push -u origin security

# 4. PR #5 (security → main) en el fork → Tests ❌ en "Run gosec" (intencional)

# 5. Lección Fix Security Issues
nano json.go                                   # G104: manejar error de w.Write
nano main.go                                   # G112: ReadHeaderTimeout
                                               # G706: validar PORT con strconv.Atoi, loguear portNum
go fmt ./...
go build -o notely && echo "build OK"
go test -cover ./...
staticcheck ./...
gosec ./...                                    # Issues : 0
PORT=8080 ./notely                             # + curl /v1/healthz → 200 OK

git add json.go main.go
git commit -m "fix: handle write error and add ReadHeaderTimeout (gosec G104, G112)"
git push                                       # Tests ✅  Style ✅

# 6. Enviar en Boot.dev la URL del repo y mergear
# https://github.com/cecibelauda/learn-cicd-starter
git checkout main
git pull origin main                           # Fast-forward → 11e3175 Merge PR #5
```

Commits de la rama `security`:

```
6b9c404 fix: handle write error and add ReadHeaderTimeout (gosec G104, G112)
922191a ci: add gosec security check to tests job
```

> El commit `6b9c404` también incluye la corrección de G706 (validación de `PORT`), aunque el mensaje solo menciona G104 y G112.

---

## 5.8 Referencias oficiales de la Sección 5

**Gosec**
- Repositorio y documentación: https://github.com/securego/gosec
- Reglas disponibles: https://github.com/securego/gosec#available-rules
- Anotar código con `#nosec`: https://github.com/securego/gosec#annotating-code
- Uso como GitHub Action: https://github.com/securego/gosec#github-action

**Go**
- `http.Server` (timeouts): https://pkg.go.dev/net/http#Server
- `http.ResponseWriter.Write`: https://pkg.go.dev/net/http#ResponseWriter
- `strconv.Atoi` / `strconv.Itoa`: https://pkg.go.dev/strconv
- `fmt` (verbos `%d`, `%s`): https://pkg.go.dev/fmt#hdr-Printing
- Short variable declarations (`:=`): https://go.dev/ref/spec#Short_variable_declarations
- Error handling and Go: https://go.dev/blog/error-handling-and-go
- Buenas prácticas de seguridad en Go: https://go.dev/doc/security/best-practices
- The complete guide to Go net/http timeouts (Cloudflare): https://blog.cloudflare.com/the-complete-guide-to-golang-net-http-timeouts/

**Seguridad (CWE / OWASP)**
- CWE-117 Log injection: https://cwe.mitre.org/data/definitions/117.html
- CWE-400 Uncontrolled resource consumption: https://cwe.mitre.org/data/definitions/400.html
- CWE-703 Improper handling of exceptional conditions: https://cwe.mitre.org/data/definitions/703.html
- OWASP Log Injection: https://owasp.org/www-community/attacks/Log_Injection
- Slowloris: https://en.wikipedia.org/wiki/Slowloris_(computer_security)
- OWASP Code Review Guide: https://owasp.org/www-project-code-review-guide/

**Herramientas**
- nano cheatsheet: https://www.nano-editor.org/dist/latest/cheatsheet.html
- `git rev-parse --show-toplevel`: https://git-scm.com/docs/git-rev-parse#Documentation/git-rev-parse.txt---show-toplevel
- GitHub — revisiones de PR: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews

---

# SECCIÓN 6 — Continuous Deployment (Build)

## 6.1 CI vs. CD

| | **CI** | **CD** |
|---|---|---|
| Pregunta que responde | ¿El código integra bien y es correcto? | ¿Cómo llega ese código a un ambiente real? |
| Qué produce | Un ✅ / ❌ sobre el cambio | Un artefacto publicado (imagen Docker) y, luego, una app corriendo |
| Cuándo corre | En cada PR (`pull_request`) | Al mergear (`push` a `main`) |
| Efecto | No toca ningún ambiente | Cambia lo que existe en la nube |

> **Idea central:** la CI **verifica**; la CD **entrega**. La CI también compila (`go test` y `gosec` compilan internamente), pero el resultado se descarta con el runner.

### Las dos "D"

| Variante | Qué hace |
|---|---|
| **Continuous Delivery** | El artefacto queda **listo** para desplegar; una persona aprueba el pase |
| **Continuous Deployment** | Se despliega a producción **automáticamente** |

🧠 **Analogía — una imprenta:** CI = revisar la prueba de impresión · Delivery = libro empacado en el almacén · Deployment = el camión sale solo a las librerías.

**Equivalencia La Tinka:** CI = `mvn verify` + JaCoCo + SonarQube en el PR · CD = imagen Docker → ECR → EKS. Si el pase a producción requiere aprobación, es **Delivery**.

### CI y CD son workflows independientes

```
PR abierto   ──► evento pull_request ──► ci.yml  (Tests + Style)
Merge a main ──► evento push a main  ──► cd.yml  (Deploy)
```

Por eso en un PR **solo aparecen los checks de CI**: el CD se dispara recién tras el merge.

---

## 6.2 Git: `pull`, `push` y Pull Request

| Comando | Dirección | Qué hace |
|---|---|---|
| `git pull origin <rama>` | GitHub → Mac | Baja commits de esa rama remota y los fusiona en la rama **donde estás** |
| `git push origin <rama>` | Mac → GitHub | Sube los commits de tu rama local a su gemela remota |
| **Pull Request** | (GitHub) | Propone fusionar una rama en `main`. No tiene relación con el comando `pull` |

```
        GitHub (origin)                         Tu Mac
   ┌──────────────────────┐            ┌──────────────────────┐
   │ main                 │ ──pull──►  │ main                 │
   │ build                │ ◄──push──  │ build  (estás aquí)  │
   └──────────────────────┘            └──────────────────────┘
```

- `push` sube a la rama donde estás, **no** a `main`.
- `main` en GitHub solo cambia por **PR + Merge**. Nunca `git push origin main`.
- `-u` se usa una vez para fijar el *upstream*.
- `-m` cambia de significado: `commit -m` = mensaje; `branch -m` = renombrar (*move*).

---

## 6.3 Docker: construir la imagen localmente

### Archivos del repo

`scripts/buildprod.sh`:

```bash
#!/bin/bash

CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o notely
```

`Dockerfile`:

```dockerfile
FROM --platform=linux/amd64 debian:stable-slim

RUN apt-get update && apt-get install -y ca-certificates

ADD notely /usr/bin/notely

CMD ["notely"]
```

| Variable | Efecto |
|---|---|
| `GOOS=linux` | Compila para Linux (binario ELF, no Mach-O) |
| `GOARCH=amd64` | Arquitectura Intel/AMD, la de Cloud Run |
| `CGO_ENABLED=0` | Binario estático, sin depender de librerías del sistema |

⚠️ **No cambiar a `arm64`** aunque la Mac sea Apple Silicon: Cloud Run corre en amd64. Docker Desktop lo emula con Rosetta.

### Flujo

```
1. buildprod.sh              2. docker build                   3. docker run
┌─────────────┐             ┌──────────────────────────┐      ┌──────────────────┐
│ Código Go   │──go build─► │ debian:stable-slim       │─run─►│ Contenedor       │
│ (tu Mac)    │ linux/amd64 │ + ca-certificates        │      │ PORT=8080        │
└─────────────┘     ↓       │ + /usr/bin/notely        │      │ :8080 ◄── tu Mac │
               binario      │ CMD ["notely"]           │      └──────────────────┘
               notely (ELF) └──────────────────────────┘
```

🧠 **Analogía:** binario = comida cocinada · imagen = lonchera con comida y cubiertos · contenedor = lonchera abierta sirviéndose.

```bash
docker --version                                  # ≥ 20.10.21
./scripts/buildprod.sh
file notely                                       # ELF 64-bit ... x86-64 ... statically linked
docker build -t DOCKERHUB_NAMESPACE/notely:latest .
docker run -e PORT=8080 -p 8080:8080 DOCKERHUB_NAMESPACE/notely:latest
# navegador: http://localhost:8080  (http, no https)
```

| Flag | Significado |
|---|---|
| `-t usuario/notely:latest` | Nombre (*tag*) de la imagen |
| `.` | *Build context*: carpeta con `Dockerfile` y `notely` |
| `-e PORT=8080` | Variable de entorno dentro del contenedor |
| `-p 8080:8080` | Puerto de la Mac → puerto del contenedor |

⚠️ **Docker Desktop debe estar abierto:** en Mac, el *daemon* de Docker corre dentro de una VM Linux que levanta Docker Desktop. Sin él: `Cannot connect to the Docker daemon`.

💡 El binario `notely` no corre en la Mac (`exec format error`) y está en `.gitignore`.

---

## 6.4 Workflow de CD inicial (`cd.yml`)

```yaml
name: cd

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Build the app
        run: ./scripts/buildprod.sh
```

Diferencia clave con `ci.yml`: el evento es **`push` a `main`**, no `pull_request`.

---

## 6.5 Google Cloud Platform: cuenta, facturación y proyecto

### Jerarquía creada

```
cecibel-espinoza02-org                (organización, creada automáticamente)
   ├── notely-billing                 (cuenta de facturación — "Cuenta pagada", sin créditos de prueba)
   └── Proyecto "notely"              (ID: inner-cinema-511617-v1 · número: 728416536675)
          ├── Artifact Registry  → notely-ar-repo (us-central1)
          ├── Cloud Build
          ├── Service Account    → cloud-run-deployer
          └── Workload Identity Pool "github" → Provider "my-repo"
```

| Concepto | Detalle |
|---|---|
| **Project** | Agrupa todos los recursos. Al terminar el curso, **borrar el proyecto** limpia todo |
| **Billing Account** | Donde se registra la tarjeta; debe estar **vinculada** al proyecto |
| **Project ID vs. número** | `inner-cinema-511617-v1` (nombre) ≠ `728416536675` (número; aparece en IDs de WIF) |
| **Budget alert** | Recomendado (ej. S/. 10): la cuenta cobra todo lo que exceda el nivel gratuito |

⚠️ La prueba gratuita (USD 300) se da **una sola vez por persona**. La cuenta anterior estaba cerrada y no se podía reabrir, por eso se creó `notely-billing`.

### Google Cloud SDK (`gcloud`)

```bash
gcloud init                              # login por navegador (OAuth); no requiere SSH
gcloud config get-value project          # inner-cinema-511617-v1
gcloud components update                 # opcional
```

`--console-only` solo hace falta en entornos sin navegador (por ejemplo WSL).

### Equivalencias con AWS

| GCP | AWS |
|---|---|
| Project | Cuenta de AWS |
| Billing Account | Facturación / AWS Organizations |
| Artifact Registry | ECR |
| Cloud Build | CodeBuild |
| Cloud Run | ECS Fargate / App Runner |
| Service Account | IAM Role |

---

## 6.6 Artifact Registry

Registro **privado** de imágenes Docker en GCP (como Docker Hub, pero privado).

### Configuración realizada

1. Habilitar **Cloud Build API**.
2. En *Cloud Build → Settings*, habilitar el rol **Cloud Build Service Account** para la cuenta por defecto.
3. Habilitar **Artifact Registry API**.
4. Crear repositorio:

| Campo | Valor |
|---|---|
| Nombre | `notely-ar-repo` |
| Formato | Docker |
| Modo | Standard |
| Ubicación | Region → `us-central1` |
| Cifrado | Google-managed encryption key |
| Análisis de vulnerabilidades | **Desactivado** (cuesta USD 0.26 por imagen) |

5. Construir y subir desde la Mac:

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/inner-cinema-511617-v1/notely-ar-repo/notely:latest .
```

### Anatomía de la URL de imagen

```
us-central1-docker.pkg.dev / inner-cinema-511617-v1 / notely-ar-repo / notely : latest
└──── región + host ─────┘  └────── proyecto ─────┘  └ repositorio ─┘ └imagen┘ └ tag ┘
```

### Dónde ver cada cosa

| Lugar | Qué muestra |
|---|---|
| **Cloud Build → Historial** | El *proceso*: logs, éxito/falla, duración |
| **Artifact Registry → notely-ar-repo → notely** | El *resultado*: versiones de la imagen |

🧠 **Analogía:** Cloud Build es la cocina; Artifact Registry es la vitrina.

### Digest vs. tag

| | Digest (`sha256:92febe9ee084...`) | Tag (`latest`) |
|---|---|---|
| ¿Cambia? | **Inmutable**: identifica el contenido exacto | **Móvil**: se mueve a la imagen más nueva |
| Analogía | El DNI | El "empleado del mes" |

```
Build 1:  92febe9ee084  ← latest
Build 2:  92febe9ee084  (sin tag)
          <digest nuevo> ← latest
```

La región de las imágenes y la de despliegue no tienen por qué coincidir ([regiones y zonas](https://cloud.google.com/compute/docs/regions-zones)).

---

## 6.7 Workload Identity Federation (WIF)

### El problema

`gcloud builds submit` funciona en la Mac con **tu** cuenta de Google. Desde GitHub Actions se necesita otra identidad, **sin** guardar llaves JSON de larga duración (que hay que esconder y rotar).

**Federación** = un sistema (GCP) confía en una identidad emitida por otro (GitHub), usando **OpenID Connect (OIDC)**.

### Cómo funciona

```
GitHub Actions (workflow)
   │ 1. GitHub emite un token OIDC firmado
   │    { repository: "cecibelauda/learn-cicd-starter", ref: "refs/heads/main", ... }
   ▼
google-github-actions/auth ──2. token + "quiero ser Cloud Run Deployer"──► GCP
                                                                            │
                     Pool "github" → Provider "my-repo"                     │
                       ├─ ¿firma de GitHub? (issuer-uri)              ✅    │
                       ├─ ¿es mi repo? (attribute-condition)          ✅    │
                       └─ ¿puede suplantar a la service account?      ✅    │
   ◄────────────── 3. credenciales temporales (~1 hora) ────────────────────┘
   ▼
4. gcloud builds submit con los permisos de "Cloud Run Deployer"
```

| Pieza | Función |
|---|---|
| **Workload identity pool** | Agrupa identidades externas |
| **Workload identity provider** | Define cómo verificar tokens de un emisor (GitHub) y qué condiciones aceptar |
| **Attribute mapping** | Convierte *claims* del token (`assertion.repository`) en atributos de IAM |
| **Attribute condition** | Solo acepta tokens de **tu** repo, no de cualquier workflow de GitHub |
| **`roles/iam.workloadIdentityUser`** | Permite a esas identidades **suplantar** a la service account |

🧠 **Analogía — pase de visitante:** token OIDC = DNI de tu empresa · provider = guardia que verifica el DNI y la empresa · pool = lista de empresas con convenio · service account = rol "técnico de mantenimiento" · credencial temporal = pase que vence al final del día · llave JSON = copia permanente de la llave del edificio (lo que se evita).

### Equivalencia AWS

| GCP | AWS |
|---|---|
| Workload Identity Federation | IAM OIDC Identity Provider + `AssumeRoleWithWebIdentity` |
| Service Account | IAM Role |
| `roles/iam.workloadIdentityUser` | *Trust policy* del rol |
| `google-github-actions/auth` | `aws-actions/configure-aws-credentials` |
| `attribute-condition` | Condición `token.actions.githubusercontent.com:sub` |

### Service account "Cloud Run Deployer"

Email: `cloud-run-deployer@inner-cinema-511617-v1.iam.gserviceaccount.com`

| Rol (lección) | Nombre en consola (español) | ID |
|---|---|---|
| Cloud Build Editor | Editor de Cloud Build | `roles/cloudbuild.builds.editor` |
| Cloud Build Service Account | Cuenta de servicio de Cloud Build | `roles/cloudbuild.builds.builder` |
| Cloud Run Admin | Administrador de Cloud Run | `roles/run.admin` |
| Service Account User | Usuario de cuenta de servicio | `roles/iam.serviceAccountUser` |
| Viewer | Visualizador (categoría **Básico**) | `roles/viewer` |

⚠️ "Visualizador de Vertex AI" u otros "Visualizador de X" **no** son `roles/viewer`.

En la consola es un rol por fila (**+ Agregar otro rol**). Alternativa con `gcloud`:

```bash
GCP_PROJECT_ID="$(gcloud config get-value project)"
SA="cloud-run-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com"

for ROLE in roles/cloudbuild.builds.editor roles/cloudbuild.builds.builder \
            roles/run.admin roles/iam.serviceAccountUser roles/viewer; do
  gcloud projects add-iam-policy-binding "$GCP_PROJECT_ID" \
    --member="serviceAccount:${SA}" --role="$ROLE" --condition=None
done
```

### APIs habilitadas para WIF

- Identity and Access Management (IAM) API
- Cloud Resource Manager API
- IAM Service Account Credentials API
- Security Token Service API

### Comandos de configuración (desde la raíz del repo)

```bash
GCP_PROJECT_ID="$(gcloud config get-value project)"
GCP_SERVICE_ACCOUNT_EMAIL="cloud-run-deployer@${GCP_PROJECT_ID}.iam.gserviceaccount.com"
GITHUB_REPO="$(git remote get-url origin | sed -E 's#.*github.com[:/]##; s#\.git$##')"

gcloud iam workload-identity-pools create "github" \
  --location="global" \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc "my-repo" \
  --location="global" \
  --workload-identity-pool="github" \
  --display-name="My GitHub repo Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == '${GITHUB_REPO}'" \
  --issuer-uri="https://token.actions.githubusercontent.com"

export WORKLOAD_IDENTITY_POOL="$(
  gcloud iam workload-identity-pools describe "github" \
    --location="global" \
    --format="value(name)"
)"

gcloud iam service-accounts add-iam-policy-binding \
  ${GCP_SERVICE_ACCOUNT_EMAIL} \
  --role=roles/iam.workloadIdentityUser \
  --member="principalSet://iam.googleapis.com/${WORKLOAD_IDENTITY_POOL}/attribute.repository/${GITHUB_REPO}"
```

"Raíz del repo" = `/Users/Cecibel/learn-cicd-starter` (con guiones). Es necesario porque `git remote get-url origin` solo funciona dentro del repo.

---

## 6.8 Automate Builds — CD completo hacia Artifact Registry

### ID del provider

```bash
gcloud iam workload-identity-pools providers describe "my-repo" \
  --location="global" \
  --workload-identity-pool="github" \
  --format="value(name)"
# projects/728416536675/locations/global/workloadIdentityPools/github/providers/my-repo
```

Empieza con el **número** del proyecto, no con el ID.

### Workflow final: `.github/workflows/cd.yml`

```yaml
name: cd

on:
  push:
    branches: [main]

jobs:
  deploy:
    name: Deploy
    runs-on: ubuntu-latest

    permissions:
      contents: "read"
      id-token: "write"

    steps:
      - name: Check out code
        uses: actions/checkout@v6

      - name: Set up Go
        uses: actions/setup-go@v6
        with:
          go-version: "1.27.1"

      - name: Build the app
        run: ./scripts/buildprod.sh

      - id: auth
        name: Authenticate to Google Cloud
        uses: google-github-actions/auth@v3
        with:
          workload_identity_provider: "projects/728416536675/locations/global/workloadIdentityPools/github/providers/my-repo"
          service_account: "cloud-run-deployer@inner-cinema-511617-v1.iam.gserviceaccount.com"

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v3

      - name: Build and push Docker image
        run: gcloud builds submit --tag us-central1-docker.pkg.dev/inner-cinema-511617-v1/notely-ar-repo/notely:latest .
```

| Bloque | Para qué |
|---|---|
| `permissions.id-token: write` | Permite que el job **pida el token OIDC**; sin esto, `auth` falla |
| `permissions.contents: read` | Al declarar `permissions` se pierden los permisos por defecto; `checkout` necesita leer el repo |
| `auth@v3` | Intercambia el token OIDC por credenciales temporales (WIF) |
| `setup-gcloud@v3` | Instala la CLI `gcloud` en el runner, ya autenticada |
| `gcloud builds submit` | Construye en Cloud Build y sube a Artifact Registry |

### Flujo resultante

```
merge PR #8 ──► push a main ──► cd.yml (Deploy, ~1m 15s)
                                  ├─ checkout
                                  ├─ setup-go
                                  ├─ buildprod.sh
                                  ├─ auth (WIF: token OIDC → credenciales temporales)
                                  ├─ setup-gcloud
                                  └─ gcloud builds submit ──► Artifact Registry (notely:latest)
```

### Antes vs. ahora

| | Lección Artifact Registry | Automate Builds |
|---|---|---|
| ¿Quién construye? | Tú, desde la Mac | GitHub Actions |
| ¿Con qué identidad? | Tu cuenta de Google | Service account Cloud Run Deployer |
| ¿Cuándo? | Manualmente | En cada merge a `main` |
| ¿Llaves guardadas en GitHub? | — | **Ninguna** |

### Verificación

```bash
gh run list --repo cecibelauda/learn-cicd-starter --workflow cd.yml --limit 3
gh run watch --repo cecibelauda/learn-cicd-starter
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/inner-cinema-511617-v1/notely-ar-repo/notely \
  --include-tags --sort-by=~CREATE_TIME --limit=2
```

El "1 notice" en *Annotations* del run es informativo, no un error.

---

## 6.9 Comandos nuevos de la Sección 6

### Docker

```bash
docker --version
docker info --format '{{.OSType}}/{{.Architecture}}'
docker build -t usuario/notely:latest .
docker images | grep notely
docker image inspect usuario/notely:latest --format '{{.Os}}/{{.Architecture}}'
docker run -e PORT=8080 -p 8080:8080 usuario/notely:latest
file notely                                  # ELF (Linux) vs Mach-O (Mac)
```

### gcloud

```bash
gcloud init
gcloud config get-value project
gcloud components update
gcloud builds submit --tag <URL_IMAGEN> .
gcloud artifacts docker images list <REPO_O_IMAGEN> --include-tags
gcloud iam service-accounts list --format="value(email)"
gcloud projects add-iam-policy-binding <PROYECTO> --member=... --role=...
gcloud projects get-iam-policy <PROYECTO> --flatten="bindings[].members" \
  --filter="bindings.members:<SA>" --format="value(bindings.role)"
gcloud iam workload-identity-pools create ...
gcloud iam workload-identity-pools providers create-oidc ...
gcloud iam workload-identity-pools providers describe ... --format="value(name)"
gcloud iam service-accounts add-iam-policy-binding ...
```

### Git y GitHub CLI

```bash
git branch -m cd build                        # renombrar rama (conserva cambios)
git rev-parse --show-toplevel                 # raíz del repo
gh pr list --repo OWNER/REPO --state all --json number,title,state,mergedAt
gh pr checks <N> --repo OWNER/REPO --watch    # con --repo, el número es obligatorio
gh pr merge <N> --repo OWNER/REPO --merge
gh run list --repo OWNER/REPO --workflow cd.yml --limit 3
gh run watch --repo OWNER/REPO
gh run view --repo OWNER/REPO --log-failed
```

---

## 6.10 Notas y errores encontrados

| Situación | Causa | Solución |
|---|---|---|
| En el PR solo aparecen checks de CI, no de CD | `cd.yml` escucha `push` a `main` | Normal: el CD corre tras el merge |
| `Cannot connect to the Docker daemon` | Docker Desktop cerrado | Abrir Docker Desktop (hospeda la VM Linux del daemon) |
| `./notely` → `exec format error` en la Mac | Binario compilado para linux/amd64 | Es solo para el contenedor; no cambiar a arm64 |
| La cuenta de facturación anterior no se podía reabrir | Prueba gratuita ya usada / cuenta cerrada | Crear `notely-billing` (cuenta pagada) + alerta de presupuesto |
| Banner "Activa el análisis de vulnerabilidades" | Oferta paga (USD 0.26/imagen) | Cerrar con X; no activar |
| "Visualizador de IA" en lugar de Viewer | Rol predefinido de otro servicio | Categoría **Básico** → **Visualizador** (`roles/viewer`) |
| No se pueden elegir varios roles en un desplegable | La consola asigna un rol por fila | **+ Agregar otro rol**, o loop con `gcloud` |
| `gh pr list` sin columna de estado | La vista por defecto no muestra MERGED/CLOSED | `--json number,title,state,mergedAt` |
| `argument required when using the --repo flag` | `gh pr checks --repo` sin número de PR | `gh pr checks 8 --repo ...` |
| `gh run list` no mostraba el run nuevo tras el merge | GitHub tarda segundos en disparar el workflow | `sleep 10` y volver a listar |
| Rama `build` ya mergeada al retomar | PR #7 mergeado el 14/10 | Rama nueva `auto-build` desde `main` actualizado |

### Reglas de trabajo consolidadas

1. **CI verifica, CD entrega.** Son workflows separados con eventos distintos.
2. **Nunca `git push origin main`.** `main` solo cambia por PR + Merge.
3. **Compilar para la arquitectura de destino** (Cloud Run = linux/amd64), no la de la Mac.
4. **Sin llaves de larga duración en CI:** usar WIF/OIDC con credenciales temporales.
5. **Restringir el provider a tu repo** (`attribute-condition`); nunca confiar en todo GitHub.
6. **Mínimo privilegio:** la service account solo tiene los roles que necesita.
7. **Controlar costos:** alerta de presupuesto, sin escaneos pagos, y borrar el proyecto `notely` al terminar.

---

## 6.11 Flujo completo ejecutado en la Sección 6

```bash
# 1. Preparar rama (se renombró cd → build)
cd ~/learn-cicd-starter
git branch -m cd build

# 2. Lección Docker
./scripts/buildprod.sh
docker build -t DOCKERHUB_NAMESPACE/notely:latest .
docker run -e PORT=8080 -p 8080:8080 DOCKERHUB_NAMESPACE/notely:latest

# 3. Lección CD: crear .github/workflows/cd.yml (sección 6.4)
git add .github/workflows/cd.yml
git commit -m "..."
git push -u origin build
# PR #7 (build → main) → solo CI ✅ → merge (14/10)

# 4. GCP: cuenta de facturación notely-billing, proyecto notely,
#    gcloud init (sección 6.5)

# 5. Artifact Registry (sección 6.6)
gcloud config get-value project              # inner-cinema-511617-v1
gcloud builds submit --tag us-central1-docker.pkg.dev/inner-cinema-511617-v1/notely-ar-repo/notely:latest .

# 6. WIF: service account + APIs + pool + provider + binding (sección 6.7)

# 7. Automate Builds
gh pr list --repo cecibelauda/learn-cicd-starter --state all --limit 3 --json number,title,state,mergedAt
git checkout main
git pull origin main
git checkout -b auto-build
cat > .github/workflows/cd.yml << 'EOF2'
# contenido completo en la sección 6.8
EOF2
git diff .github/workflows/cd.yml
grep -n $'\t' .github/workflows/cd.yml
git add .github/workflows/cd.yml
git commit -m "cd: build and push Docker image to Artifact Registry"
git push -u origin auto-build
gh pr create --repo cecibelauda/learn-cicd-starter \
  --base main --head auto-build \
  --title "Automate Docker builds" \
  --body "Authenticates to GCP via WIF and pushes the image to Artifact Registry"
# PR #8 → Tests ✅ Style ✅
gh pr merge 8 --repo cecibelauda/learn-cicd-starter --merge
sleep 10
gh run list --repo cecibelauda/learn-cicd-starter --workflow cd.yml --limit 3
# cd: Merge pull request #8 → Deploy ✅ (d1889af)

# 8. Sincronizar y limpiar
git checkout main
git pull origin main
git branch -d auto-build
```

---

## 6.12 Referencias oficiales de la Sección 6

**CI/CD**
- About continuous integration: https://docs.github.com/en/actions/about-github-actions/about-continuous-integration-with-github-actions
- About continuous deployment: https://docs.github.com/en/actions/about-github-actions/about-continuous-deployment-with-github-actions
- CI vs. Delivery vs. Deployment (Atlassian): https://www.atlassian.com/continuous-delivery/principles/continuous-integration-vs-delivery-vs-deployment
- Eventos que disparan workflows: https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows

**Docker y Go**
- `docker build`: https://docs.docker.com/reference/cli/docker/buildx/build/
- `docker run`: https://docs.docker.com/reference/cli/docker/container/run/
- `GOOS` / `GOARCH`: https://go.dev/doc/install/source#environment
- Digests de imágenes: https://docs.docker.com/reference/cli/docker/image/pull/#pull-an-image-by-digest-immutable-identifier

**Google Cloud**
- Programa gratuito: https://cloud.google.com/free/docs/free-cloud-features
- Crear y administrar proyectos: https://cloud.google.com/resource-manager/docs/creating-managing-projects
- Crear cuenta de facturación: https://cloud.google.com/billing/docs/how-to/create-billing-account
- Alertas de presupuesto: https://cloud.google.com/billing/docs/how-to/budgets
- Instalar gcloud CLI: https://cloud.google.com/sdk/docs/install
- Artifact Registry: https://cloud.google.com/artifact-registry/docs/overview
- Crear repositorios Docker: https://cloud.google.com/artifact-registry/docs/repositories/create-repos
- Administrar imágenes: https://cloud.google.com/artifact-registry/docs/docker/manage-images
- `gcloud builds submit`: https://cloud.google.com/sdk/gcloud/reference/builds/submit
- Ver resultados de Cloud Build: https://cloud.google.com/build/docs/view-build-results
- Regiones y zonas: https://cloud.google.com/compute/docs/regions-zones
- Roles básicos: https://cloud.google.com/iam/docs/roles-overview#basic
- Roles de Cloud Build: https://cloud.google.com/build/docs/iam-roles-permissions
- Roles de Cloud Run: https://cloud.google.com/run/docs/reference/iam/roles

**Workload Identity Federation / OIDC**
- WIF (visión general): https://cloud.google.com/iam/docs/workload-identity-federation
- WIF con pipelines de despliegue: https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines
- OIDC en GitHub Actions: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/about-security-hardening-with-openid-connect
- Configurar OIDC en Google Cloud: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-google-cloud-platform
- `google-github-actions/auth`: https://github.com/google-github-actions/auth
- `google-github-actions/setup-gcloud`: https://github.com/google-github-actions/setup-gcloud
- Sintaxis de `permissions`: https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions#permissions

**Git / GitHub CLI**
- `git pull`: https://git-scm.com/docs/git-pull
- `git push`: https://git-scm.com/docs/git-push
- GitHub Flow: https://docs.github.com/en/get-started/using-github/github-flow
- `gh pr list`: https://cli.github.com/manual/gh_pr_list
- `gh pr checks`: https://cli.github.com/manual/gh_pr_checks
- `gh run watch`: https://cli.github.com/manual/gh_run_watch

---

# ESTADO DEL CURSO

| Sección | Estado |
|---|---|
| 1 — Fundamentos de CI/CD y GitHub Actions | ✅ Completada |
| 2 — Running Tests | ✅ Completada |
| 3 — Formatting | ✅ Completada |
| 4 — Linting | ✅ Completada |
| 5 — Security | ✅ Completada |
| 6 — Continuous Deployment (Build) | ✅ Completada |
| 7 — Por confirmar al iniciar | ⏳ Pendiente |

### Pipeline actual

```
PR hacia main (ci.yml)
      │
      ├──► Job "Tests"                    ├──► Job "Style"
      │     ├─ checkout                   │     ├─ checkout
      │     ├─ setup-go                   │     ├─ setup-go
      │     ├─ go test -cover ./...       │     ├─ test -z $(go fmt ./...)
      │     ├─ go install gosec           │     ├─ go install staticcheck
      │     └─ gosec ./...                │     └─ staticcheck ./...

Push a main (cd.yml)
      │
      └──► Job "Deploy"
            ├─ checkout
            ├─ setup-go
            ├─ ./scripts/buildprod.sh
            ├─ google-github-actions/auth  (WIF)
            ├─ google-github-actions/setup-gcloud
            └─ gcloud builds submit ──► Artifact Registry (notely:latest)
```

### Ramas y PRs

| Rama | PR | Estado |
|---|---|---|
| `addtests` | #1 | ✅ Mergeada a `main` — ciclo cerrado |
| `formatting` | #2 | ✅ Mergeada a `main` — ciclo cerrado |
| `linting` | #3, #4 | ✅ Mergeada a `main` — ciclo cerrado |
| `security` | #5 | ✅ Mergeada a `main` (`11e3175`) — ciclo cerrado |
| `build` | #6 | ❌ Cerrado sin merge (reemplazado por #7) |
| `build` | #7 | ✅ Mergeada a `main` (`a2d18d0`) — ciclo cerrado |
| `auto-build` | #8 | ✅ Mergeada a `main` (`d1889af`) — ciclo cerrado |
| — | bootdotdev#2988 | ❌ Creado por error contra el repo original — cerrado |

### Recursos en GCP (eliminar al terminar el curso)

| Recurso | Valor |
|---|---|
| Proyecto | `notely` (`inner-cinema-511617-v1`) |
| Facturación | `notely-billing` (cuenta pagada) |
| Artifact Registry | `notely-ar-repo` (us-central1) |
| Service account | `cloud-run-deployer@inner-cinema-511617-v1.iam.gserviceaccount.com` |
| WIF | Pool `github` / Provider `my-repo` |

**Próximo paso:** al iniciar la siguiente sección, crear una rama nueva desde `main` actualizado:

```bash
cd ~/learn-cicd-starter
git checkout main
git pull origin main
git checkout -b <nombre-rama-seccion-7>
```
