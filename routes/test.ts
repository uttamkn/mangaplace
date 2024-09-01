import { Hono } from "hono";

const test = new Hono();

test.get("/", (c) => {
  return c.json({ message: "hello world from test" });
});

export default test;
