import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  LangGraphHttpAgent,
  EmptyAdapter,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";

const serviceAdapter = new EmptyAdapter();
const runtime = new CopilotRuntime({
  agents: {
    bankbot: new LangGraphHttpAgent({
      url: `${process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/bankbot`,
    }),
  },
});

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });

  return handleRequest(req);
};
