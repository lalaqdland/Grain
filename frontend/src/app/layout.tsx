import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Grain - 字斟句酌',
  description: 'The AI Humanizer & Academic Shield',
  icons: {
    icon: '/favicon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  )
}

