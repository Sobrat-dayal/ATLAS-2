import React from "react";
import { ShieldAlert, ArrowLeft, Home } from "lucide-react";
import { useRouter } from "next/navigation";

export function AccessDenied() {
  const router = useRouter();

  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] text-center p-6 space-y-6 animate-in fade-in duration-300">
      <div className="flex items-center justify-center w-16 h-16 rounded-full bg-destructive/10 text-destructive">
        <ShieldAlert size={32} />
      </div>
      
      <div className="space-y-2">
        <h2 className="text-2xl font-semibold tracking-tight text-foreground">Access Denied</h2>
        <p className="text-muted-foreground max-w-md">
          You do not have permission to access this area. If you believe this is an error, 
          please contact an administrator.
        </p>
      </div>

      <div className="flex items-center gap-4 pt-4">
        <button
          onClick={() => router.back()}
          className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back
        </button>
        <button
          onClick={() => router.push("/home")}
          className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground shadow hover:bg-primary/90 h-9 px-4 py-2"
        >
          <Home className="mr-2 h-4 w-4" />
          Go Home
        </button>
      </div>
    </div>
  );
}
