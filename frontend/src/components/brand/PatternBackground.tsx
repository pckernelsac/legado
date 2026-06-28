import { useId } from "react";

import { cn } from "@/lib/utils";

/**
 * Fondo decorativo sutil con motivos del memorial (rama, llama, destello)
 * en los colores de la marca. Pensado para colocarse como primer hijo de un
 * contenedor `relative`; el contenido real debe ir con `relative z-10`.
 *
 * `intensity` escala la opacidad de los motivos (1 = sutil por defecto).
 */
export function PatternBackground({
  className,
  intensity = 1,
}: {
  className?: string;
  intensity?: number;
}) {
  const id = useId().replace(/:/g, "");
  const motif = `motif-${id}`;
  const o = (base: number) => Math.min(1, base * intensity);

  return (
    <div
      aria-hidden
      className={cn("pointer-events-none absolute inset-0 overflow-hidden", className)}
    >
      <svg className="h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern
            id={motif}
            width="220"
            height="220"
            patternUnits="userSpaceOnUse"
            patternTransform="rotate(-8)"
          >
            {/* Rama / hoja — verde marca */}
            <g
              transform="translate(34 46) scale(1.1)"
              fill="none"
              stroke="#008931"
              strokeWidth="1.4"
              strokeLinecap="round"
              opacity={o(0.1)}
            >
              <path d="M0 14 C 9 7 9 -7 0 -14 C -9 -7 -9 7 0 14 Z" />
              <path d="M0 -11 L0 11" />
            </g>

            {/* Llama de vela — dorado */}
            <g
              transform="translate(168 168)"
              fill="none"
              stroke="#C8A97E"
              strokeWidth="1.5"
              strokeLinejoin="round"
              opacity={o(0.14)}
            >
              <path d="M0 -13 C 7 -5 10 -1 6 6 A6 6 0 1 1 -6 6 C -8 0 -3 -4 0 -13 Z" />
            </g>

            {/* Destello — dorado relleno */}
            <path
              transform="translate(176 44)"
              d="M0 -9 L2.4 -2.4 L9 0 L2.4 2.4 L0 9 L-2.4 2.4 L-9 0 L-2.4 -2.4 Z"
              fill="#C8A97E"
              opacity={o(0.12)}
            />

            {/* Hoja pequeña — verde */}
            <g
              transform="translate(96 132) scale(0.7) rotate(20)"
              fill="none"
              stroke="#008931"
              strokeWidth="1.6"
              strokeLinecap="round"
              opacity={o(0.09)}
            >
              <path d="M0 14 C 9 7 9 -7 0 -14 C -9 -7 -9 7 0 14 Z" />
            </g>

            {/* Puntos sutiles */}
            <circle cx="120" cy="20" r="1.6" fill="#008931" opacity={o(0.1)} />
            <circle cx="20" cy="150" r="1.6" fill="#C8A97E" opacity={o(0.12)} />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={`url(#${motif})`} />
      </svg>
    </div>
  );
}
