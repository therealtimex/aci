import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { ArrowRight } from "lucide-react";

interface ChatInputProps {
  input: string;
  handleInputChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  status: string;
  linkedAccountOwnerId: string | null;
}

export function ChatInput({
  input,
  handleInputChange,
  handleSubmit,
  status,
  linkedAccountOwnerId,
}: ChatInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (linkedAccountOwnerId) {
        const formEvent = new Event(
          "submit",
        ) as unknown as React.FormEvent<HTMLFormElement>;
        handleSubmit(formEvent);
      } else {
        toast.error("Please select a linked account");
      }
    }
  };

  return (
    <div className="pt-4 border-none relative -mt-6 z-10">
      <form
        onSubmit={(event) => {
          if (!linkedAccountOwnerId) {
            toast.error("Please select a linked account");
            return;
          }
          handleSubmit(event);
        }}
        className="flex flex-col w-full max-w-3xl mx-auto"
      >
        <div className="flex flex-col items-start bg-white rounded-2xl border shadow-sm">
          <Textarea
            value={input}
            placeholder="Ask me anything..."
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            className="flex-1 p-4 bg-transparent outline-none resize-none min-h-[4rem] border-none shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 focus-visible:outline-none"
            disabled={status !== "ready"}
            rows={2}
          />
          <div className="flex flex-row justify-end w-full p-2">
            <Button
              type="submit"
              variant="outline"
              disabled={status !== "ready" || !linkedAccountOwnerId}
              className="px-4 py-2 text-gray-500 hover:text-gray-900 disabled:opacity-50 flex items-center gap-2"
            >
              <span>Run</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
