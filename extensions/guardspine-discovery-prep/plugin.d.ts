// Type shim for the CJS plugin entry (plugin.js). OpenClaw's Jiti loader
// calls register(api) at runtime; index.ts re-exports this default.
declare const plugin: {
  register: (api: unknown) => void;
};
export default plugin;
