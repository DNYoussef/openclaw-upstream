// Confirms the LIVE governance verifier is what plugin.js's own hook
// registration says it is, and that the dormant/unwired paths stay dormant.
// This is a structural check over source text, not a runtime trace -- it
// cannot detect a call built dynamically from string concatenation, but it
// covers every direct-invocation mechanism (subprocess spawning of any kind,
// worker threads, common subprocess-wrapper libraries) an actual wiring
// would realistically use.
//
// KNOWN LIMIT (audited, not fixed): this scans plugin.js's own source text
// only. plugin.js currently has zero local file requires (`require('./...')`,
// confirmed by grep) -- it only requires Node built-ins (fs, path, crypto,
// http, https) -- so there is nowhere for an indirect wrapper to hide today.
// If plugin.js is ever split into multiple local files, this check would
// need to resolve and scan that whole local module graph, not just this one
// file, to keep the same guarantee.

const fs = require("fs");

// Comments are stripped before matching so an old TODO or dead-code comment
// mentioning the bridge doesn't get treated as a live reference to it (and,
// symmetrically, so a real reference can't be defused by wrapping it in a
// comment) -- a real usage exists as executable code either way.
//
// The line-comment strip uses a negative lookbehind for `:` so it does NOT
// treat the `//` in `http://` or `https://` as a comment start -- plugin.js
// builds URLs for LiteLLM/Discord/Slack throughout, and a naive `//.*$`
// would blindly truncate the rest of any line containing one.
//
// HONEST, ACCEPTED RESIDUAL LIMIT (audited, not fixed, on purpose): this is
// regex, not a tokenizer -- it cannot tell a `//` inside a STRING LITERAL
// (e.g. `const x = " //"; realCode();`) from an actual comment start, and
// will incorrectly strip `realCode()` in that specific shape. A fully
// correct fix needs a real JS parser, which is disproportionate
// infrastructure for a single-file drift tripwire on a file confirmed to
// have zero local imports and one human-reviewed change surface -- adding
// that dependency to close a narrow, contrived edge case would cost more
// (R12: complexity is debt) than the risk it removes. Flagging this
// honestly rather than claiming a robustness this approach doesn't have.
function stripComments(sourceText) {
  return sourceText.replace(/\/\*[\s\S]*?\*\//g, "").replace(/(?<!:)\/\/.*$/gm, "");
}

// Patterns that would indicate plugin.js actually invokes the Python
// connector.py bridge (directly requiring it makes no sense cross-runtime,
// but a subprocess spawn referencing it, or referencing openclaw-hardening,
// would). Deliberately broad on subprocess/worker mechanisms -- plugin.js's
// real council is pure JS/HTTP (LiteLLM), it should need none of these.
const BRIDGE_INVOCATION_PATTERNS = [
  /connector\.py/i,
  /OpenClawConnector/,
  /openclaw-hardening/i,
  /child_process/,
  /worker_threads/,
  /\bexeca\b/,
  /cross-spawn/,
  /\bpython3?\b/i,
];

function findBridgeReferences(sourceText) {
  const stripped = stripComments(sourceText);
  const hits = [];
  for (const pattern of BRIDGE_INVOCATION_PATTERNS) {
    if (pattern.test(stripped)) {
      hits.push(pattern.source);
    }
  }
  return hits;
}

// Confirms plugin.js's own council implementation is present and is what
// the before_tool_call hook actually calls (via the `_runCouncilReview`
// indirection plugin.js itself uses). Comments stripped first so a call
// appearing only in a comment near the hook can't produce a false pass.
function checkOwnCouncilIsWired(sourceText) {
  const stripped = stripComments(sourceText);
  const hasRunCouncilReview = /function runCouncilReview\s*\(/.test(stripped);
  // \b after the target name so a renamed/disabled variant (e.g. assigning
  // from `runCouncilReviewMock` or `runCouncilReview_disabled`) is not
  // mistaken for the real function being aliased.
  const hasIndirection = /(?:let|const|var)\s+_runCouncilReview\s*=\s*runCouncilReview\b/.test(
    stripped,
  );
  // Bounded to the text between the ACTUAL before_tool_call registration
  // call and the NEXT api.on(...) registration (or end of file) -- not an
  // arbitrary fixed-size window, and not just the bare word "before_tool_call"
  // (which could appear earlier in a log message, string, or -- in this
  // exact file -- the header doc comment listing hook names). Anchoring to
  // the specific `api.on(..."before_tool_call"...)` code shape means the
  // boundary is correct regardless of what text happens to appear earlier,
  // and regardless of whether comments were stripped. Quote class includes
  // backticks so a template-literal-style registration is still matched.
  //
  // HONEST, ACCEPTED RESIDUAL LIMIT: if before_tool_call were ever made the
  // LAST api.on(...) registration in the file (today it is the first of
  // four -- confirmed by grep, three more follow it), there would be no
  // "next hook" to bound against, and the search window would extend to
  // end-of-file, where a stray _runCouncilReview( call in unrelated later
  // code could falsely satisfy this check. Not fixed here for the same
  // reason as the string-literal limit above: a fully robust fix needs a
  // real parser, which is disproportionate for this file's actual shape.
  const hookRegistrationMatch = /api\.on\s*\(\s*["'`]before_tool_call["'`]/.exec(stripped);
  let hookCallsIt = false;
  if (hookRegistrationMatch) {
    const hookIndex = hookRegistrationMatch.index;
    const nextHookMatch = /api\.on\s*\(/.exec(
      stripped.slice(hookIndex + hookRegistrationMatch[0].length),
    );
    const hookBlock = nextHookMatch
      ? stripped.slice(hookIndex, hookIndex + hookRegistrationMatch[0].length + nextHookMatch.index)
      : stripped.slice(hookIndex);
    // Optional whitespace before "(" -- a formatter adding a space must not
    // flip this to a false failure.
    hookCallsIt = /_runCouncilReview\s*\(/.test(hookBlock);
  }
  return {
    hasRunCouncilReview,
    hasIndirection,
    hookCallsIt,
    wired: hasRunCouncilReview && hasIndirection && hookCallsIt,
  };
}

function checkGovernanceRouting(pluginJsSource) {
  const bridgeReferences = findBridgeReferences(pluginJsSource);
  const ownCouncil = checkOwnCouncilIsWired(pluginJsSource);
  return {
    ok: bridgeReferences.length === 0 && ownCouncil.wired,
    bridgeReferences,
    ownCouncil,
  };
}

module.exports = { findBridgeReferences, checkOwnCouncilIsWired, checkGovernanceRouting };

if (require.main === module) {
  const path = require("path");
  const pluginPath = path.join(__dirname, "..", "extensions", "guardspine", "plugin.js");
  const source = fs.readFileSync(pluginPath, "utf8");
  const result = checkGovernanceRouting(source);
  if (!result.ok) {
    if (result.bridgeReferences.length) {
      console.error(
        `FAIL: plugin.js now references the dormant bridge: ${result.bridgeReferences.join(", ")}`,
      );
    }
    if (!result.ownCouncil.wired) {
      console.error(
        `FAIL: plugin.js's own council is no longer wired as expected: ${JSON.stringify(result.ownCouncil)}`,
      );
    }
    process.exit(1);
  }
  console.log(
    "Governance routing OK: plugin.js's own 3-model council is wired to before_tool_call; no reference to the dormant connector.py/openclaw-hardening bridge.",
  );
}
