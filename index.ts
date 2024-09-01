import app from "./app";
/*
 * bun has a default server but still we will still use hono
 */

Bun.serve({
  fetch: app.fetch,
});
