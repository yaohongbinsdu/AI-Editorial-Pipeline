'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
      <h1 className="text-4xl font-bold text-zinc-300">出错了</h1>
      <p className="mt-4 max-w-md text-sm text-zinc-500">
        {error.message || '发生未知错误，请稍后重试'}
      </p>
      <button
        onClick={reset}
        className="mt-6 rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-500"
      >
        重试
      </button>
    </div>
  )
}
