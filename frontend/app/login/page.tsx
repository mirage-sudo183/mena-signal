"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await login(email, password);
      router.push("/");
    } catch (error) {
      toast({
        title: "Login failed",
        description: "Invalid email or password",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-6">
      {/* Background */}
      <div className="pointer-events-none fixed inset-0 bg-gradient-to-b from-muted/30 via-background to-background" />
      
      <div className="relative z-10 w-full max-w-sm animate-fade-in-up">
        {/* Logo */}
        <div className="mb-10 flex flex-col items-center">
          <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-foreground shadow-soft-lg">
            <Zap className="h-7 w-7 text-background" />
          </div>
          <h1 className="text-[22px] font-semibold tracking-tight">Welcome back</h1>
          <p className="mt-1.5 text-[15px] text-muted-foreground">
            Sign in to MENA Signal
          </p>
        </div>

        {/* Form */}
        <div className="rounded-2xl border border-border/60 bg-card p-8 shadow-soft">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-[13px] font-medium">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
                className="h-11 rounded-xl border-border/60 text-[14px]"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-[13px] font-medium">
                Password
              </Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="h-11 rounded-xl border-border/60 text-[14px]"
              />
            </div>

            <Button 
              type="submit" 
              className="h-11 w-full rounded-xl text-[14px] font-medium" 
              disabled={loading}
            >
              {loading ? "Signing in..." : "Sign in"}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-[14px] text-muted-foreground">
          <Link href="/" className="hover:text-foreground transition-colors">
            Back to dashboard
          </Link>
        </p>
      </div>
    </div>
  );
}
