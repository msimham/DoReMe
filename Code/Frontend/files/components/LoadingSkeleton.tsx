export default function LoadingSkeleton() {
  return (
    <div className="card p-6 animate-pulse">
      <div className="flex items-start gap-3 mb-4">
        <div className="w-10 h-10 bg-black/5 rounded-full" />
        <div className="flex-1">
          <div className="h-4 bg-black/5 rounded w-32 mb-2" />
          <div className="h-3 bg-black/5 rounded w-24" />
        </div>
      </div>
      <div className="space-y-2 mb-4">
        <div className="h-4 bg-black/5 rounded w-full" />
        <div className="h-4 bg-black/5 rounded w-3/4" />
      </div>
      <div className="w-full aspect-video bg-black/5 rounded-lg mb-4" />
      <div className="flex gap-4">
        <div className="h-8 bg-black/5 rounded w-20" />
        <div className="h-8 bg-black/5 rounded w-20" />
        <div className="h-8 bg-black/5 rounded w-20" />
      </div>
    </div>
  );
}
