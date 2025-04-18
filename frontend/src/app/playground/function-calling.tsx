import type { ToolInvocation } from "ai";

type FunctionCallingProps = {
  toolInvocation: ToolInvocation;
};

export function FunctionCalling({ toolInvocation }: FunctionCallingProps) {
  const { toolName } = toolInvocation;

  return (
    <div>
      {/* TODO: Add tool call */}
      Function Calling: {toolName}
    </div>
  );
}
