import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ULTRON Orb UI",
  description: "An Iron Man-inspired holographic orb built with Three.js and Next.js",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#000000",
};

import "./holographic.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <div className="main-layout">
          <nav className="sidebar">
            <div style={{ padding: '0 25px', marginBottom: '40px' }}>
              <h1 className="glowing-text" style={{ fontFamily: 'Inter', fontSize: '1.5rem', letterSpacing: '2px' }}>ULTRON</h1>
            </div>
            <a href="/" className="nav-link">Dashboard</a>
            <a href="/chat" className="nav-link">AI Chat</a>
            <a href="/email" className="nav-link">Smart Email</a>
            <a href="/calendar" className="nav-link">Calendar</a>
            <a href="/voice" className="nav-link">Voice Control</a>
            <a href="/automation" className="nav-link">Automations</a>
          </nav>
          <main className="content-area">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
