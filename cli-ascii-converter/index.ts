import readline from "readline";

// bunx prettier --check .
// echo $? will return you the un-formated files & status code either of 0 || 1
// bunx prettier --write .
// echo $? will formate you file & return status code 0

function stringToAscii(input: string) {
  return Array.from(input)
    .map((char) => char.charCodeAt(0))
    .join(",");
}

function evaluate(line: string) {const userPrompt = line.toLowerCase().trim();try {
    const toAscii = stringToAscii(userPrompt);
    return toAscii;
  } catch (err) {
    console.error(err);
  }
}

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: "> ",
});

console.log(
  "Welcome to CLI-Ascii Converter! Give me anything or type 'exit' to quit.",
);
rl.prompt();

rl.on("line", (line) => {
  const response = evaluate(line);

  if (line === "exit") {
    rl.close();
  } else {
    console.log(`ASCII: ${response}`);
    rl.prompt();
  }
});
