import { useState, useEffect } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalInputField } from "@/components/ui/brutal-input-field";
import { BrutalCard } from "@/components/ui/brutal-card";
import { Headphones, Mail, Lock, User, ArrowLeft, Loader2 } from "lucide-react";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner"; // Assuming sonner is available based on App.tsx

const Auth = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [isLogin, setIsLogin] = useState(searchParams.get("mode") !== "register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");

  const { login: authLogin } = useAuth();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  // Handle Google OAuth Callback
  useEffect(() => {
    const code = searchParams.get("code");
    const error = searchParams.get("error");

    if (error) {
      toast.error("Google authentication failed");
      // Clean URL
      const newParams = new URLSearchParams(searchParams);
      newParams.delete("error");
      newParams.delete("state"); // Google sends state too
      setSearchParams(newParams);
    } else if (code) {
      handleGoogleCallback(code);
    }
  }, [searchParams]);

  const handleGoogleCallback = async (code: string) => {
    setIsLoading(true);
    try {
      const response = await api.get("/auth/google/callback", {
        params: { code }
      });
      authLogin(response.data.data);
      toast.success("Successfully logged in with Google!");
      
      // Navigate immediately - don't clear params here as we are leaving the page
      navigate("/dashboard");
    } catch (error) {
      console.error("Google auth error:", error);
      toast.error("Failed to complete Google login");
      
      // Only clear params if we stay on this page (error case)
      const newParams = new URLSearchParams(searchParams);
      newParams.delete("code");
      newParams.delete("scope");
      newParams.delete("authuser");
      newParams.delete("prompt");
      newParams.delete("state");
      setSearchParams(newParams);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsGoogleLoading(true);
    try {
      const response = await api.get<{ data: { auth_url: string } }>("/auth/google");
      window.location.href = response.data.data.auth_url;
    } catch (error) {
      console.error("Failed to get Google auth URL:", error);
      toast.error("Failed to start Google login");
      setIsGoogleLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      if (isLogin) {
        const response = await api.post("/auth/login", { email, password });
        authLogin(response.data.data);
        toast.success("Welcome back!");
        navigate("/dashboard");
      } else {
        // Register flow
        await api.post("/auth/register", { 
          email, 
          password, 
          username: name
        });
        
        // After register, auto login
        const loginResponse = await api.post("/auth/login", { email, password });
        authLogin(loginResponse.data.data);
        toast.success("Account created successfully!");
        
        // Navigate to onboarding instead of dashboard
        navigate("/onboarding");
      }
    } catch (error) {
      console.error("Auth error:", error);
      toast.error("Authentication failed. Please check your credentials.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen geometric-pattern flex items-center justify-center p-4">
      {/* Decorative Elements */}
      <div className="fixed top-20 left-10 w-16 h-16 bg-secondary border-[3px] border-foreground shadow-brutal rotate-12 animate-float hidden lg:block" />
      <div className="fixed top-40 right-16 w-12 h-12 bg-accent border-[3px] border-foreground shadow-brutal -rotate-6 animate-float hidden lg:block" style={{ animationDelay: "1s" }} />
      <div className="fixed bottom-32 left-20 w-10 h-10 bg-success border-[3px] border-foreground shadow-brutal rotate-45 animate-float hidden lg:block" style={{ animationDelay: "0.5s" }} />

      <div className="w-full max-w-md">
        {/* Back Link */}
        <Link to="/" className="inline-flex items-center gap-2 mb-6 font-medium hover:text-secondary transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to Home
        </Link>

        <BrutalCard variant="static" padding="lg">
          {/* Logo */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <div className="w-12 h-12 bg-primary border-[3px] border-foreground shadow-brutal flex items-center justify-center">
              <Headphones className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold">EchoBrief</span>
          </div>

          {/* Toggle */}
          <div className="flex border-[3px] border-foreground mb-8">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 py-3 font-bold uppercase text-sm transition-colors ${
                isLogin ? "bg-primary" : "bg-muted hover:bg-muted/80"
              }`}
            >
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 py-3 font-bold uppercase text-sm transition-colors border-l-[3px] border-foreground ${
                !isLogin ? "bg-primary" : "bg-muted hover:bg-muted/80"
              }`}
            >
              Register
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {!isLogin && (
              <BrutalInputField
                label="Username (3-50 chars, no spaces)"
                icon={User}
                type="text"
                placeholder="johndoe"
                value={name}
                onChange={(e) => setName(e.target.value.replace(/\s+/g, ''))}
                disabled={isLoading}
                minLength={3}
                maxLength={50}
              />
            )}

            <BrutalInputField
              label="Email"
              icon={Mail}
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading}
            />

            <BrutalInputField
              label="Password"
              icon={Lock}
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading}
            />

            {isLogin && (
              <div className="text-right">
                <a href="#" className="text-sm font-medium text-secondary hover:underline">
                  Forgot password?
                </a>
              </div>
            )}

            <BrutalButton type="submit" size="lg" className="w-full" disabled={isLoading}>
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              {isLogin ? "Login" : "Create Account"}
            </BrutalButton>
          </form>

          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t-[2px] border-foreground/30" />
            </div>
            <div className="relative flex justify-center">
              <span className="px-4 bg-card text-sm text-muted-foreground uppercase">
                Or continue with
              </span>
            </div>
          </div>

          <BrutalButton variant="outline" size="lg" className="w-full" onClick={handleGoogleLogin} disabled={isGoogleLoading || isLoading}>
            {isGoogleLoading ? (
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
            ) : (
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                <path
                  fill="currentColor"
                  d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                />
                <path
                  fill="currentColor"
                  d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                />
                <path
                  fill="currentColor"
                  d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                />
                <path
                  fill="currentColor"
                  d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                />
              </svg>
            )}
            Google
          </BrutalButton>

          <p className="text-center text-sm text-muted-foreground mt-6">
            {isLogin ? "Don't have an account? " : "Already have an account? "}
            <button
              onClick={() => setIsLogin(!isLogin)}
              className="font-bold text-foreground hover:text-secondary transition-colors"
            >
              {isLogin ? "Register" : "Login"}
            </button>
          </p>
        </BrutalCard>
      </div>
    </div>
  );
};
export default Auth;
