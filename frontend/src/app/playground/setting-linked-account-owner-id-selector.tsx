"use client";

import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from "@/components/ui/select";
import { useAgentStore } from "@/lib/store/agent";
import { Message } from "ai";

interface LinkAccountOwnerIdSelectorProps {
  linkedAccounts: { linked_account_owner_id: string }[];
  status: string;
  setMessages: (messages: Message[]) => void;
}

export function LinkAccountOwnerIdSelector({
  linkedAccounts,
  status,
  setMessages,
}: LinkAccountOwnerIdSelectorProps) {
  const { linkedAccountOwnerId, setLinkedAccountOwnerId } = useAgentStore();

  const resetLinkedAccountOwnerId = (value: string) => {
    setLinkedAccountOwnerId(value);
    setMessages([]);
  };

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-medium">Linked Account Owner ID</h3>
      <Select
        value={linkedAccountOwnerId}
        onValueChange={resetLinkedAccountOwnerId}
        disabled={status !== "ready"}
      >
        <SelectTrigger className="w-full">
          <SelectValue placeholder="Select a Linked Account Owner" />
        </SelectTrigger>
        <SelectContent>
          {linkedAccounts.map((account) => (
            <SelectItem
              key={account.linked_account_owner_id}
              value={account.linked_account_owner_id}
            >
              {account.linked_account_owner_id}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
