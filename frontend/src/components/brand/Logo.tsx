/** Marca de Legado Eterno: una hoja/llama que simboliza vida y permanencia. */
export function Logo({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Legado Eterno"
    >
      <defs>
        <linearGradient id="le-grad" x1="0" y1="0" x2="48" y2="48">
          <stop stopColor="#00B34A" />
          <stop offset="0.6" stopColor="#008931" />
          <stop offset="1" stopColor="#C8A97E" />
        </linearGradient>
      </defs>
      <path
        d="M24 4C24 4 8 14 8 28a16 16 0 0 0 32 0C40 14 24 4 24 4Z"
        fill="url(#le-grad)"
      />
      <path
        d="M24 14c0 8-6 10-6 16a6 6 0 0 0 12 0c0-6-6-8-6-16Z"
        fill="#FFFFFF"
        fillOpacity="0.92"
      />
    </svg>
  );
}
