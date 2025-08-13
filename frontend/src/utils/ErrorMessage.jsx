export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="mt-10 flex flex-col items-center justify-center p-8 text-red-300 bg-red-600/20 rounded-2xl border border-red-500/30 w-full max-w-lg mx-auto shadow-lg">
      <svg
        className="h-12 w-12 text-red-400 mb-4"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p className="text-xl font-bold mb-2">Error</p>
      <p className="text-center mb-4">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-6 py-2 bg-blue-600/20 text-blue-300 rounded-lg border border-blue-500/30 hover:bg-blue-700/30 transition-colors"
        >
          Retry
        </button>
      )}
    </div>
  );
}
