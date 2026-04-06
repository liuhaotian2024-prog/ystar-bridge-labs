import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Y* Bridge Labs — Who Governs the Agents?",
  description: "The world's first AI-governed company. Every agent action audited. Every decision public.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-full flex flex-col" style={{ fontFamily: "'Libre Baskerville', 'Georgia', serif", background: '#f4efe4', color: '#1a1a1a' }}>
        {children}
      </body>
    </html>
  );
}
