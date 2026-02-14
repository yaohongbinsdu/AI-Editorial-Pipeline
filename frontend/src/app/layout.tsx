import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'AI Editorial Pipeline — 智能投资新闻编辑部',
  description: '全自动AI新闻聚合与智能分析平台，面向投资者',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN" className="dark">
      <body className="min-h-screen bg-zinc-950 text-zinc-100 antialiased">
        <div className="flex min-h-screen">
          <aside className="hidden w-64 shrink-0 border-r border-zinc-800 bg-zinc-900/50 lg:block">
            <div className="flex h-14 items-center border-b border-zinc-800 px-4">
              <h1 className="text-lg font-bold tracking-tight">
                <span className="text-red-500">AI</span> Editorial
              </h1>
            </div>
            <nav className="p-3">
              {/* CategoryNav component will be placed here */}
            </nav>
          </aside>
          <main className="flex-1 overflow-auto">
            <div className="mx-auto max-w-7xl p-4 lg:p-6">{children}</div>
          </main>
        </div>
      </body>
    </html>
  )
}
