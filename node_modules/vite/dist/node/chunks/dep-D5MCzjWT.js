import { __commonJS, __toESM } from "./dep-lCKrEJQm.js";
import readline from "node:readline";

//#region ../../node_modules/.pnpm/picocolors@1.1.1/node_modules/picocolors/picocolors.js
var require_picocolors = /* @__PURE__ */ __commonJS({ "../../node_modules/.pnpm/picocolors@1.1.1/node_modules/picocolors/picocolors.js": ((exports, module) => {
	let p = process || {}, argv = p.argv || [], env = p.env || {};
	let isColorSupported = !(!!env.NO_COLOR || argv.includes("--no-color")) && (!!env.FORCE_COLOR || argv.includes("--color") || p.platform === "win32" || (p.stdout || {}).isTTY && env.TERM !== "dumb" || !!env.CI);
	let formatter = (open, close, replace = open) => (input) => {
		let string = "" + input, index = string.indexOf(close, open.length);
		return ~index ? open + replaceClose(string, close, replace, index) + close : open + string + close;
	};
	let replaceClose = (string, close, replace, index) => {
		let result = "", cursor = 0;
		do {
			result += string.substring(cursor, index) + replace;
			cursor = index + close.length;
			index = string.indexOf(close, cursor);
		} while (~index);
		return result + string.substring(cursor);
	};
	let createColors = (enabled = isColorSupported) => {
		let f = enabled ? formatter : () => String;
		return {
			isColorSupported: enabled,
			reset: f("\x1B[0m", "\x1B[0m"),
			bold: f("\x1B[1m", "\x1B[22m", "\x1B[22m\x1B[1m"),
			dim: f("\x1B[2m", "\x1B[22m", "\x1B[22m\x1B[2m"),
			italic: f("\x1B[3m", "\x1B[23m"),
			underline: f("\x1B[4m", "\x1B[24m"),
			inverse: f("\x1B[7m", "\x1B[27m"),
			hidden: f("\x1B[8m", "\x1B[28m"),
			strikethrough: f("\x1B[9m", "\x1B[29m"),
			black: f("\x1B[30m", "\x1B[39m"),
			red: f("\x1B[31m", "\x1B[39m"),
			green: f("\x1B[32m", "\x1B[39m"),
			yellow: f("\x1B[33m", "\x1B[39m"),
			blue: f("\x1B[34m", "\x1B[39m"),
			magenta: f("\x1B[35m", "\x1B[39m"),
			cyan: f("\x1B[36m", "\x1B[39m"),
			white: f("\x1B[37m", "\x1B[39m"),
			gray: f("\x1B[90m", "\x1B[39m"),
			bgBlack: f("\x1B[40m", "\x1B[49m"),
			bgRed: f("\x1B[41m", "\x1B[49m"),
			bgGreen: f("\x1B[42m", "\x1B[49m"),
			bgYellow: f("\x1B[43m", "\x1B[49m"),
			bgBlue: f("\x1B[44m", "\x1B[49m"),
			bgMagenta: f("\x1B[45m", "\x1B[49m"),
			bgCyan: f("\x1B[46m", "\x1B[49m"),
			bgWhite: f("\x1B[47m", "\x1B[49m"),
			blackBright: f("\x1B[90m", "\x1B[39m"),
			redBright: f("\x1B[91m", "\x1B[39m"),
			greenBright: f("\x1B[92m", "\x1B[39m"),
			yellowBright: f("\x1B[93m", "\x1B[39m"),
			blueBright: f("\x1B[94m", "\x1B[39m"),
			magentaBright: f("\x1B[95m", "\x1B[39m"),
			cyanBright: f("\x1B[96m", "\x1B[39m"),
			whiteBright: f("\x1B[97m", "\x1B[39m"),
			bgBlackBright: f("\x1B[100m", "\x1B[49m"),
			bgRedBright: f("\x1B[101m", "\x1B[49m"),
			bgGreenBright: f("\x1B[102m", "\x1B[49m"),
			bgYellowBright: f("\x1B[103m", "\x1B[49m"),
			bgBlueBright: f("\x1B[104m", "\x1B[49m"),
			bgMagentaBright: f("\x1B[105m", "\x1B[49m"),
			bgCyanBright: f("\x1B[106m", "\x1B[49m"),
			bgWhiteBright: f("\x1B[107m", "\x1B[49m")
		};
	};
	module.exports = createColors();
	module.exports.createColors = createColors;
}) });

//#endregion
//#region src/node/logger.ts
var import_picocolors = /* @__PURE__ */ __toESM(require_picocolors(), 1);
const LogLevels = {
	silent: 0,
	error: 1,
	warn: 2,
	info: 3
};
let lastType;
let lastMsg;
let sameCount = 0;
function clearScreen() {
	const repeatCount = process.stdout.rows - 2;
	const blank = repeatCount > 0 ? "\n".repeat(repeatCount) : "";
	console.log(blank);
	readline.cursorTo(process.stdout, 0, 0);
	readline.clearScreenDown(process.stdout);
}
let timeFormatter;
function getTimeFormatter() {
	timeFormatter ??= new Intl.DateTimeFormat(void 0, {
		hour: "numeric",
		minute: "numeric",
		second: "numeric"
	});
	return timeFormatter;
}
function createLogger(level = "info", options = {}) {
	if (options.customLogger) return options.customLogger;
	const loggedErrors = /* @__PURE__ */ new WeakSet();
	const { prefix = "[vite]", allowClearScreen = true, console: console$1 = globalThis.console } = options;
	const thresh = LogLevels[level];
	const canClearScreen = allowClearScreen && process.stdout.isTTY && !process.env.CI;
	const clear = canClearScreen ? clearScreen : () => {};
	function format(type, msg, options$1 = {}) {
		if (options$1.timestamp) {
			let tag = "";
			if (type === "info") tag = import_picocolors.default.cyan(import_picocolors.default.bold(prefix));
			else if (type === "warn") tag = import_picocolors.default.yellow(import_picocolors.default.bold(prefix));
			else tag = import_picocolors.default.red(import_picocolors.default.bold(prefix));
			const environment = options$1.environment ? options$1.environment + " " : "";
			return `${import_picocolors.default.dim(getTimeFormatter().format(/* @__PURE__ */ new Date()))} ${tag} ${environment}${msg}`;
		} else return msg;
	}
	function output(type, msg, options$1 = {}) {
		if (thresh >= LogLevels[type]) {
			const method = type === "info" ? "log" : type;
			if (options$1.error) loggedErrors.add(options$1.error);
			if (canClearScreen) if (type === lastType && msg === lastMsg) {
				sameCount++;
				clear();
				console$1[method](format(type, msg, options$1), import_picocolors.default.yellow(`(x${sameCount + 1})`));
			} else {
				sameCount = 0;
				lastMsg = msg;
				lastType = type;
				if (options$1.clear) clear();
				console$1[method](format(type, msg, options$1));
			}
			else console$1[method](format(type, msg, options$1));
		}
	}
	const warnedMessages = /* @__PURE__ */ new Set();
	const logger = {
		hasWarned: false,
		info(msg, opts) {
			output("info", msg, opts);
		},
		warn(msg, opts) {
			logger.hasWarned = true;
			output("warn", msg, opts);
		},
		warnOnce(msg, opts) {
			if (warnedMessages.has(msg)) return;
			logger.hasWarned = true;
			output("warn", msg, opts);
			warnedMessages.add(msg);
		},
		error(msg, opts) {
			logger.hasWarned = true;
			output("error", msg, opts);
		},
		clearScreen(type) {
			if (thresh >= LogLevels[type]) clear();
		},
		hasErrorLogged(error) {
			return loggedErrors.has(error);
		}
	};
	return logger;
}
function printServerUrls(urls, optionsHost, info) {
	const colorUrl = (url) => import_picocolors.default.cyan(url.replace(/:(\d+)\//, (_, port) => `:${import_picocolors.default.bold(port)}/`));
	for (const url of urls.local) info(`  ${import_picocolors.default.green("➜")}  ${import_picocolors.default.bold("Local")}:   ${colorUrl(url)}`);
	for (const url of urls.network) info(`  ${import_picocolors.default.green("➜")}  ${import_picocolors.default.bold("Network")}: ${colorUrl(url)}`);
	if (urls.network.length === 0 && optionsHost === void 0) info(import_picocolors.default.dim(`  ${import_picocolors.default.green("➜")}  ${import_picocolors.default.bold("Network")}: use `) + import_picocolors.default.bold("--host") + import_picocolors.default.dim(" to expose"));
}

//#endregion
export { LogLevels, createLogger, printServerUrls, require_picocolors };