import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <h1 className="text-6xl font-bold text-zinc-300">404</h1>
      <p className="mt-4 text-lg text-zinc-500">页面未找到</p>
      <Link
        href="/"
        className="mt-6 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500"
      >
        返回首页
      </Link>
    </div>
  )
}
