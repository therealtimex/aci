import React from "react";
import { BiCopy } from "react-icons/bi";
import { toast } from "sonner";

interface AppIdDisplayProps {
  appId: string;
}

export function AppIdDisplay({ appId }: AppIdDisplayProps) {
  const copyToClipboard = () => {
    if (!navigator.clipboard) {
      console.error("Clipboard API not supported");
      toast.error("Your browser doesn't support copying to clipboard");
      return;
    }
    navigator.clipboard
      .writeText(appId)
      .then(() => {
        toast.success("App ID copied to clipboard");
      })
      .catch((err) => {
        console.error("Failed to copy:", err);
        toast.error("Failed to copy App ID to clipboard");
      });
  };

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-500">#{appId}</span>
      <button
        onClick={(e) => {
          e.preventDefault();
          copyToClipboard();
        }}
        className="text-gray-500 hover:text-gray-700"
        aria-label="Copy app ID"
        title="Copy app ID to clipboard"
      >
        <BiCopy className="w-5 h-5" />
      </button>
    </div>
  );
}
