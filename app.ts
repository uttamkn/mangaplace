import { Hono } from "hono";
import test from "./routes/test";

const app = new Hono();

/*
 * example code
 */
app.get("/", (c) => {
  return c.json({ message: "hello world" });
});

app.route("/test", test);

export default app;
