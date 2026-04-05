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
      <body className="min-h-full flex flex-col" style={{ fontFamily: "'Georgia', 'Times New Roman', serif", background: '#faf8f5', color: '#2a2520' }}>
        {children}
      </body>
    </html>
  );
}
