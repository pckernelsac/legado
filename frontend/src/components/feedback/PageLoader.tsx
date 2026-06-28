import { Logo } from "@/components/brand/Logo";

export function PageLoader() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4">
        <div className="animate-flame">
          <Logo className="h-12 w-12" />
        </div>
        <div className="h-1 w-32 overflow-hidden rounded-full bg-muted">
          <div className="h-full w-1/2 animate-[shimmer_1.2s_infinite] rounded-full bg-brand" />
        </div>
      </div>
    </div>
  );
}
