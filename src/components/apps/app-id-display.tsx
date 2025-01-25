import React from "react";
import { BiCopy } from "react-icons/bi";

interface AppIdDisplayProps {
  appId: string;
}

export function AppIdDisplay({ appId }: AppIdDisplayProps) {
  const copyToClipboard = () => {
    if (!navigator.clipboard) {
      console.error("Clipboard API not supported");
      return;
    }
    navigator.clipboard
      .writeText(appId)
      .then(() => {
        // TODO: add a Sonner notification when copied
      })
      .catch((err) => {
        console.error("Failed to copy:", err);
        // TODO: Show error notification
      });
  };

  return (
    <div
      className="flex items-center gap-2"
      onClick={(e) => e.preventDefault()}
    >
      <span className="text-sm text-gray-500">#{appId}</span>
      <button
        onClick={copyToClipboard}
        className="text-gray-500 hover:text-gray-700"
        aria-label="Copy app ID"
        title="Copy app ID to clipboard"
      >
        <BiCopy className="w-5 h-5" />
      </button>
    </div>
  );
}
