import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "NutriCore",
  description: "Plataforma para consulta nutricional con FastAPI, Next.js y Docker Compose",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
