import React from 'react';

interface ChatBubbleProps {
  sender: 'system' | 'user';
  time: string;
  message: string;
}

export function ChatBubble({ sender, time, message }: ChatBubbleProps) {
  const isUser = sender === 'user';

  return (
    <div className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}>
      <span className={`text-[10px] uppercase tracking-wider text-gray-500 font-medium ${isUser ? 'mr-1' : 'ml-1'}`}>
        {isUser ? 'Du' : 'System'} • {time}
      </span>
      <div 
        className={`p-3.5 text-sm leading-relaxed max-w-[85%] ${
          isUser 
            ? 'bg-indigo-600 rounded-2xl rounded-tr-sm shadow-md shadow-indigo-900/20 text-white' 
            : 'bg-gray-800/80 rounded-2xl rounded-tl-sm border border-gray-700/50 text-gray-200'
        }`}
      >
        {message}
      </div>
    </div>
  );
}
