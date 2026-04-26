const SERVER_DEBUG_ENABLED =
  process.env.NODE_ENV === 'development' || process.env.ROUTER_DEBUG === 'true';

export function serverDebugLog(...args: unknown[]) {
  if (SERVER_DEBUG_ENABLED) {
    globalThis.console.log(...args);
  }
}

export function serverDebugWarn(...args: unknown[]) {
  if (SERVER_DEBUG_ENABLED) {
    globalThis.console.warn(...args);
  }
}
