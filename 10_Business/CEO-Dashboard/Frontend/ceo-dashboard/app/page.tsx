'use client';

import React, { useState, useRef } from 'react';
import { Mic, Send, Menu, Square } from 'lucide-react';
import { ChatBubble } from '@/components/chat/ChatBubble';

export default function CEODashboard() {
  const [messages, setMessages] = useState<{sender: 'user' | 'system', text: string, time: string}[]>([
    { sender: 'system', text: 'TRACE AI OS bereit. System online.', time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }
  ]);
  const [inputText, setInputText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isSending, setIsSending] = useState(false);
  
  // Referenzen für die Web Audio API
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  // 1. Audio-Recording-Logik (Web Audio API)
  const startRecording = async () => {
    try {
      // Mikrofon-Berechtigung anfragen und Audio-Stream holen
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = []; // Chunks zurücksetzen

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Blob aus den Audio-Chunks erstellen (z.B. als webm)
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Füge eine visuelle Platzhalter-Nachricht in den Chat ein
        addMessage('user', '🎤 Sprachnachricht gesendet...');
        
        // Nach dem Stoppen sofort an die API senden
        await sendMessageToAgent(undefined, audioBlob);
        
        // Kamera/Mikrofon-Tracks wieder beenden, um das rote Aufnahmesymbol im Browser zu entfernen
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Fehler beim Zugriff auf das Mikrofon:', error);
      addMessage('system', 'Fehler: Mikrofon-Zugriff verweigert.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Hilfsfunktion zum Hinzufügen von Chat-Nachrichten
  const addMessage = (sender: 'user' | 'system', text: string) => {
    setMessages(prev => [...prev, { 
      sender, 
      text, 
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) 
    }]);
  };

  // 2. API-Anbindung (Fetch) an FastAPI
  const sendMessageToAgent = async (text?: string, audioBlob?: Blob) => {
    setIsSending(true);
    try {
      // Beispiellogik für den Versand (Backend-URL anpassen, falls nötig)
      const apiUrl = '/api/v1/execute-agent';
      let response;

      if (audioBlob) {
        // Bei Audio: FormData verwenden
        const formData = new FormData();
        // Die Datei "audio.webm" an das Backend senden (FastAPI erwartet UploadFile)
        formData.append('file', audioBlob, 'voice-message.webm');
        
        // WICHTIG: Für den echten Versand auskommentieren:
        /*
        response = await fetch(apiUrl, {
          method: 'POST',
          body: formData,
        });
        */
        // Simuliere einen erfolgreichen Backend-Call:
        await new Promise(r => setTimeout(r, 1500));
        addMessage('system', 'Audio transkribiert & Agenten-Task ausgeführt. Log: "PR #13 erstellt."');
        
      } else if (text) {
        // Bei Text: JSON verwenden (FastAPI erwartet Pydantic BaseModel)
        const payload = { prompt: text };
        
        /*
        response = await fetch(apiUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
        */
        // Simuliere einen erfolgreichen Backend-Call:
        await new Promise(r => setTimeout(r, 1000));
        addMessage('system', `Befehl ausgeführt: "${text}". Keine Fehler im Terminal.`);
      }

      // Bei einer echten API-Anbindung würden wir hier das Ergebnis der Response verarbeiten:
      // const result = await response.json();
      // addMessage('system', result.message || 'Task erfolgreich.');
      
    } catch (error) {
      console.error('Fehler beim Senden an die API:', error);
      addMessage('system', 'Fehler: Server nicht erreichbar.');
    } finally {
      setIsSending(false);
    }
  };

  const handleTextSubmit = () => {
    if (!inputText.trim()) return;
    addMessage('user', inputText);
    sendMessageToAgent(inputText);
    setInputText('');
  };

  return (
    // Wir wrappen das Layout in eine schmale Spalte (max-w-md), damit es wie eine PWA/Mobile App aussieht
    <div className="flex flex-col h-screen max-w-md mx-auto relative border-x border-gray-800 bg-gray-950 shadow-2xl overflow-hidden">
      
      {/* --- HEADER --- */}
      <header className="flex items-center justify-between p-4 border-b border-gray-800 bg-gray-900/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg">
            <span className="font-bold text-xs tracking-wider text-white">AI</span>
          </div>
          <div>
            <h1 className="font-semibold text-sm tracking-wide text-gray-100">TRACE AI OS</h1>
            <p className="text-xs text-emerald-400 flex items-center gap-1.5 mt-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]"></span>
              System online
            </p>
          </div>
        </div>
        <button className="p-2 rounded-full hover:bg-gray-800 transition-colors">
          <Menu className="w-5 h-5 text-gray-400" />
        </button>
      </header>

      {/* --- CHAT VERLAUF --- */}
      <main className="flex-1 overflow-y-auto p-4 space-y-6 scroll-smooth pb-24">
        {messages.map((msg, index) => (
          <ChatBubble key={index} sender={msg.sender} time={msg.time} message={msg.text} />
        ))}
        {isSending && (
          <div className="flex items-center gap-2 text-gray-500 text-xs ml-2">
            <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce"></div>
            <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
            <span>System verarbeitet...</span>
          </div>
        )}
      </main>

      {/* --- EINGABEBEREICH (BOTTOM BAR) --- */}
      <footer className="absolute bottom-0 w-full p-4 border-t border-gray-800 bg-gray-900/90 backdrop-blur-xl">
        <div className="flex items-center gap-2">
          
          {/* Text-Eingabefeld */}
          <div className="flex-1 relative group">
            <input 
              type="text" 
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleTextSubmit()}
              placeholder="Nachricht tippen..." 
              className="w-full bg-gray-800/50 border border-gray-700 text-sm rounded-full py-3.5 pl-4 pr-10 focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition-all placeholder:text-gray-500 text-white"
            />
            <button 
              onClick={handleTextSubmit}
              className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full hover:bg-gray-700 transition-colors text-gray-400 hover:text-white"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>

          {/* Dynamischer Mikrofon-Button (onMouseDown / onMouseUp für Touch & Click) */}
          <button 
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onMouseLeave={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            className={`w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-all flex-shrink-0 cursor-pointer select-none ${
              isRecording 
                ? 'bg-red-500 shadow-red-500/50 animate-pulse scale-110' 
                : 'bg-gradient-to-tr from-indigo-500 to-purple-600 shadow-indigo-500/25 hover:shadow-indigo-500/40 hover:scale-105 active:scale-95'
            }`}
          >
            {isRecording ? <Square className="w-5 h-5 text-white" /> : <Mic className="w-5 h-5 text-white" />}
          </button>
          
        </div>
        <div className="text-center mt-3 h-4">
          <span className={`text-[10px] font-medium tracking-widest uppercase transition-colors ${isRecording ? 'text-red-400' : 'text-gray-500'}`}>
            {isRecording ? 'Aufnahme läuft...' : 'Halten für Sprachnachricht'}
          </span>
        </div>
      </footer>
    </div>
  );
}
