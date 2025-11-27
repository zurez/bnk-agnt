import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  LangGraphAgent,
  EmptyAdapter,
} from "@copilotkit/runtime";
import { NextRequest } from "next/server";

const serviceAdapter = new EmptyAdapter();
const runtime = new CopilotRuntime({
  agents: {
    my_agent: new LangGraphAgent({
      deploymentUrl: "http://localhost:8000",
      graphId: "agent",
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
