import type {Metadata, Viewport} from 'next';
import { Inter } from 'next/font/google';
import './globals.css'; // Globale Styles (Tailwind CSS)

// Wir nutzen die Schriftart Inter, da sie sehr clean, lesbar und modern für Dashboards wirkt.
const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'CEO Dashboard - TRACE AI OS',
  description: 'Zentrales Interface für die Steuerung der Backend-Agenten.',
};

export const viewport: Viewport = {
  themeColor: '#030712', // Entspricht bg-gray-950 für einen nahtlosen Übergang
};

export default function RootLayout({children}: {children: React.ReactNode}) {
  return (
    // "dark" Klasse erzwingt den Dark Mode für Tailwind, falls konfiguriert.
    // Wir setzen standardmäßig sehr dunkle Grau/Schwarz-Töne (bg-gray-950) für einen eleganten Look.
    <html lang="de" className="dark">
      <body className={`${inter.className} bg-gray-950 text-gray-50 min-h-screen antialiased`} suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
