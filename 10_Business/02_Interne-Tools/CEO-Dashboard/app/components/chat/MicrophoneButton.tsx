import React from 'react';
import { Mic } from 'lucide-react';

export function MicrophoneButton() {
  return (
    <button className="w-12 h-12 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-105 active:scale-95 transition-all flex-shrink-0 cursor-pointer">
      <Mic className="w-5 h-5 text-white" />
    </button>
  );
}
