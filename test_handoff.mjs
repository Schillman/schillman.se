#!/usr/bin/env node
/* Tests the two ways progress gets into /d4/ledger.html: the fragment handoff
 * from d4.schillman.se, and the Import button.
 *
 *     node test_handoff.mjs
 *
 * No browser, no server, no framework, no dependencies. The rest of that page
 * needs a DOM and is not covered here; this covers the functions that take input
 * from a stranger's link or from the clipboard and whose failure mode is
 * destroying a season of someone's progress.
 *
 * It does not carry a copy of the code under test. It slices the pure block out
 * of d4/ledger.html between the sentinels in that file and evaluates it, so what
 * is asserted on is the shipped source. Break the page and this goes red.
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const START = "/* --- pure handoff logic, extracted verbatim by test_handoff.mjs --- */";
const END = "/* --- end pure handoff logic --- */";

const page = readFileSync(new URL("./d4/ledger.html", import.meta.url), "utf8");
const from = page.indexOf(START);
const to = page.indexOf(END);
assert.ok(from !== -1 && to > from,
  "handoff sentinels not found in d4/ledger.html, so nothing was tested");

const { decodeHandoff, parseBackup, mergeProgress } = new Function(
  page.slice(from + START.length, to) +
  "\nreturn { decodeHandoff: decodeHandoff, parseBackup: parseBackup," +
  " mergeProgress: mergeProgress };")();

const b64url = value => Buffer.from(JSON.stringify(value)).toString("base64url");
const KNOWN = new Set(["esc-1", "esc-2", "esc-3", "esc-4"]);
const isKnownId = id => KNOWN.has(id);

let failures = 0;
function test(name, fn) {
  try {
    fn();
    console.log("  PASS  " + name);
  } catch (err) {
    failures++;
    console.log("  FAIL  " + name + "\n        " + String(err.message).split("\n")[0]);
  }
}
/* Every rejection is one assertion: it threw, so importFromFragment takes its
   catch branch, shows the failure toast and never reaches storage. */
const rejects = (name, payload) =>
  test(name, () => assert.throws(() => decodeHandoff(payload)));

console.log("\ndecodeHandoff, payloads that should be accepted");

test("a plain map decodes", () =>
  assert.deepEqual(decodeHandoff(b64url({ "esc-1": true, "esc-2": false })),
    { "esc-1": true, "esc-2": false }));

test("base64url alphabet and stripped padding are both reversed", () => {
  /* Real item ids are ASCII and never produce + or / in base64, so the
     substitution the format specifies has to be exercised deliberately or it is
     never covered at all. This payload produces both, and padding. */
  const payload = { "k~~~": true, "a~~?": false };
  const standard = Buffer.from(JSON.stringify(payload)).toString("base64");
  assert.ok(standard.includes("+") && standard.includes("/") && standard.endsWith("="),
    "this payload no longer exercises + and / and padding");
  const urlSafe = standard.replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  assert.ok(!urlSafe.includes("+") && !urlSafe.includes("/") && !urlSafe.includes("="));
  assert.deepEqual(decodeHandoff(urlSafe), payload);
});

test("an empty map is valid, it just carries nothing", () =>
  assert.deepEqual(decodeHandoff(b64url({})), {}));

console.log("\ndecodeHandoff, payloads that must be rejected without touching anything");

rejects("not base64 at all", "!!!!not-base64!!!!");
rejects("truncated halfway", b64url({ "esc-1": true, "esc-2": false }).slice(0, 12));
rejects("one character short, so the padding cannot be rebuilt",
  b64url({ "esc-1": true }).slice(0, -1) + "x=");
rejects("valid base64 that is not JSON", Buffer.from("not json").toString("base64url"));
rejects("a value that is not a boolean", b64url({ "esc-1": "yes" }));
rejects("a value that is only truthy", b64url({ "esc-1": 1 }));
rejects("one bad value among good ones", b64url({ "esc-1": true, "esc-2": null }));
rejects("an array", b64url(["esc-1", "esc-2"]));
/* An array of strings is already caught by the value check, so it does not
   isolate the Array.isArray guard. An array of booleans does: without that
   guard it decodes cleanly and merges as the keys "0" and "1". */
rejects("an array of booleans, which nothing else would catch", b64url([true, false]));
rejects("a bare number", b64url(42));
rejects("a bare string", b64url("esc-1"));
rejects("null", b64url(null));
rejects("an empty payload", "");

console.log("\nmergeProgress, last write wins per item key");

test("an incoming key overwrites the local value", () => {
  const local = { "esc-1": true, "esc-2": true };
  const carried = mergeProgress(local, { "esc-2": false }, isKnownId);
  assert.deepEqual(local, { "esc-1": true, "esc-2": false });
  assert.equal(carried, 1);
});

test("a local key the payload does not mention survives", () => {
  /* This is the Send my progress again case: the old page can send a second,
     overlapping map, and it must not look like a reset of everything else. */
  const local = { "esc-1": true, "esc-4": true };
  const carried = mergeProgress(local, { "esc-2": false, "esc-3": true }, isKnownId);
  assert.deepEqual(local, { "esc-1": true, "esc-4": true, "esc-2": false, "esc-3": true });
  assert.equal(carried, 2);
});

test("false is carried across as a value, not skipped as falsy", () => {
  const local = { "esc-1": true };
  assert.equal(mergeProgress(local, { "esc-1": false }, isKnownId), 1);
  assert.equal(local["esc-1"], false);
});

test("an id that is not on this list is ignored and not counted", () => {
  const local = { "esc-1": true };
  const carried = mergeProgress(local, { "not-an-item": true, "esc-2": true }, isKnownId);
  assert.deepEqual(local, { "esc-1": true, "esc-2": true });
  assert.equal(carried, 1);
});

test("a payload of nothing but unknown ids carries nothing", () => {
  const local = { "esc-1": true };
  assert.equal(mergeProgress(local, { "nope": true }, isKnownId), 0);
  assert.deepEqual(local, { "esc-1": true });
});

test("an empty map carries nothing and changes nothing", () => {
  const local = { "esc-1": true };
  assert.equal(mergeProgress(local, {}, isKnownId), 0);
  assert.deepEqual(local, { "esc-1": true });
});

console.log("\nparseBackup, blobs pasted into the Import prompt");

/* Import is parseBackup and then mergeProgress, and the bug being pinned here is
   that it used to be neither: it wrote every key it was handed straight into
   storage. So the assertions run the pair, the way the click handler does, and
   check both what landed in storage and the two numbers the toast reports. */
function importBlob(local, raw) {
  const incoming = parseBackup(raw);
  const offered = Object.keys(incoming).length;
  const restored = mergeProgress(local, incoming, isKnownId);
  return { restored, skipped: offered - restored };
}

test("a blob of nothing but known ids restores all of them", () => {
  const local = {};
  const counts = importBlob(local, JSON.stringify({ "esc-1": true, "esc-2": false, "esc-3": true }));
  assert.deepEqual(local, { "esc-1": true, "esc-2": false, "esc-3": true });
  assert.deepEqual(counts, { restored: 3, skipped: 0 });
});

test("a blob mixing known and unknown ids stores only the known ones", () => {
  /* The reported bug exactly: an id from an old season, a typo and a hand
     edited key all used to be written to storage and then never render. */
  const local = {};
  const counts = importBlob(local, JSON.stringify({
    "esc-1": true, "s13-legacy": true, "esc-2": true, "esc-1 ": true, "": true
  }));
  assert.deepEqual(local, { "esc-1": true, "esc-2": true },
    "an id that is not on this list reached storage");
  assert.deepEqual(counts, { restored: 2, skipped: 3 });
});

test("a blob of entirely unknown ids writes nothing at all", () => {
  const local = { "esc-1": true };
  const counts = importBlob(local, JSON.stringify({ "nope": true, "old-1": false }));
  assert.deepEqual(local, { "esc-1": true }, "storage was touched by a blob with nothing on this list");
  assert.deepEqual(counts, { restored: 0, skipped: 2 });
});

test("values are coerced, so a hand edited 1/0 backup still restores", () => {
  const local = {};
  assert.deepEqual(importBlob(local, '{"esc-1":1,"esc-2":0}'), { restored: 2, skipped: 0 });
  assert.deepEqual(local, { "esc-1": true, "esc-2": false });
});

test("prototype keys are ignored like any other unknown id", () => {
  const local = {};
  importBlob(local, '{"__proto__":true,"constructor":true}');
  assert.deepEqual(local, {});
  assert.equal(({}).__proto__, Object.prototype, "Object.prototype was reachable through a backup");
});

console.log("\nparseBackup, malformed input that must throw before anything is written");

/* Each of these throws, so the click handler takes its catch branch, shows the
   failure toast and never reaches mergeProgress, saveState or storage. */
const rejectsBlob = (name, raw) =>
  test(name, () => assert.throws(() => parseBackup(raw)));

rejectsBlob("not JSON at all", "not json");
rejectsBlob("truncated JSON", '{"esc-1":true,"esc-2":fal');
rejectsBlob("a trailing comma", '{"esc-1":true,}');
rejectsBlob("an array", '["esc-1","esc-2"]');
rejectsBlob("an array of booleans", "[true,false]");
rejectsBlob("a bare number", "42");
rejectsBlob("a bare string", '"esc-1"');
rejectsBlob("null", "null");
rejectsBlob("an empty blob", "");

test("a blob that goes bad partway through writes nothing, not a prefix of itself", () => {
  /* parseBackup builds a whole object before returning, so there is no state to
     roll back: the merge is never reached. This is the half apply case. */
  const local = { "esc-1": false };
  assert.throws(() => importBlob(local, '{"esc-1":true,"esc-2":true'));
  assert.deepEqual(local, { "esc-1": false });
});

console.log(failures ? `\n${failures} FAILURE(S)` : "\nall handoff and import tests passed");
process.exit(failures ? 1 : 0);
