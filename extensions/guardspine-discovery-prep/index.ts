// Thin re-export. The actual plugin is in plugin.js (CJS).
// OpenClaw's Jiti loader resolves module.exports -> { register }.
export { default } from "./plugin.js";
