import React from "react";
import { BiCopy } from "react-icons/bi";
import { toast } from "sonner";

interface AppIdDisplayProps {
  id: string;
}

export function IdDisplay({ id: appId }: AppIdDisplayProps) {
  const copyToClipboard = () => {
    if (!navigator.clipboard) {
      console.error("Clipboard API not supported");
      toast.error("Your browser doesn't support copying to clipboard");
      return;
    }
    navigator.clipboard
      .writeText(appId)
      .then(() => {
        toast.success("Copied to clipboard");
      })
      .catch((err) => {
        console.error("Failed to copy:", err);
        toast.error("Failed to copy App ID to clipboard");
      });
  };

  return (
    <div className="flex items-center  w-full">
      <span className="text-sm text-gray-500 truncate min-w-0">#{appId}</span>
      <button
        onClick={(e) => {
          e.preventDefault();
          copyToClipboard();
        }}
        className="text-gray-500 hover:text-gray-700"
        aria-label="Copy app ID"
        title="Copy app ID to clipboard"
      >
        <BiCopy/>
      </button>
    </div>
  );
}
