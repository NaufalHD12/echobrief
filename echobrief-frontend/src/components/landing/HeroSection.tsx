import { Link } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { Play, Zap, Headphones, Rocket } from "lucide-react";

export const HeroSection = () => {
  return (
    <section className="min-h-screen pt-24 pb-16 relative overflow-hidden geometric-pattern">
      {/* Decorative Elements */}
      <div className="absolute top-32 left-10 w-20 h-20 bg-secondary border-[3px] border-foreground shadow-brutal rotate-12 animate-float hidden lg:block -z-10" />
      <div className="absolute top-48 right-16 w-16 h-16 bg-accent border-[3px] border-foreground shadow-brutal -rotate-6 animate-float hidden lg:block -z-10" style={{ animationDelay: "1s" }} />
      <div className="absolute bottom-32 left-1/4 w-12 h-12 bg-success border-[3px] border-foreground shadow-brutal rotate-45 animate-float hidden lg:block -z-10" style={{ animationDelay: "0.5s" }} />

      <div className="container mx-auto px-4">
        <div className="flex flex-col lg:flex-row items-center gap-12">
          {/* Content */}
          <div className="flex-1 text-center lg:text-left">
            <BrutalBadge variant="secondary" size="lg" className="mb-6 animate-bounce-in">
              <Zap className="w-3 h-3 mr-1" /> AI-Powered News Podcasts
            </BrutalBadge>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-tight mb-6">
              News You Can{" "}
              <span className="inline-block bg-primary px-3 border-[3px] border-foreground shadow-brutal">
                Listen To
              </span>
            </h1>

            <p className="text-lg sm:text-xl text-muted-foreground max-w-xl mx-auto lg:mx-0 mb-8">
              EchoBrief transforms breaking news into personalized audio podcasts. 
              Select your topics, and let our AI deliver the stories that matter, right to your ears.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <Link to="/auth?mode=register">
                <BrutalButton size="xl" className="w-full sm:w-auto">
                  <Headphones className="w-5 h-5 mr-2" />
                  Start Listening Free
                </BrutalButton>
              </Link>
              <BrutalButton variant="outline" size="xl" className="w-full sm:w-auto">
                <Play className="w-5 h-5 mr-2" />
                Watch Demo
              </BrutalButton>
            </div>

            {/* Launch Badge - Removed as per update */ }

          </div>

          {/* Hero Visual */}
          <div className="flex-1 relative">
            <div className="relative w-full max-w-md mx-auto">
              {/* Main Card */}
              <div className="bg-card border-[3px] border-foreground shadow-brutal-lg p-6 relative z-10">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-secondary border-[3px] border-foreground flex items-center justify-center">
                    <Headphones className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-bold">Today's Tech Brief</h3>
                    <p className="text-sm text-muted-foreground">5 stories • 12 min</p>
                  </div>
                </div>

                {/* Waveform Visualization */}
                <div className="bg-muted border-[3px] border-foreground p-4 mb-4">
                  <div className="flex items-center justify-center gap-1 h-16">
                    {[40, 65, 35, 80, 50, 70, 45, 90, 60, 75, 40, 85, 55, 70, 45, 60, 80, 50, 65, 40].map((height, i) => (
                      <div
                        key={i}
                        className="w-2 bg-secondary border border-foreground animate-pulse"
                        style={{ 
                          height: `${height}%`,
                          animationDelay: `${i * 0.1}s`
                        }}
                      />
                    ))}
                  </div>
                </div>

                {/* Progress */}
                <div className="flex items-center gap-3">
                  <button className="w-12 h-12 bg-primary border-[3px] border-foreground shadow-brutal flex items-center justify-center hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all">
                    <Play className="w-5 h-5 ml-1" />
                  </button>
                  <div className="flex-1">
                    <div className="h-3 bg-muted border-[2px] border-foreground">
                      <div className="h-full bg-accent w-1/3" />
                    </div>
                    <div className="flex justify-between text-xs mt-1 text-muted-foreground">
                      <span>4:12</span>
                      <span>12:00</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Background Cards */}
              <div className="absolute -bottom-4 -right-4 w-full h-full bg-secondary border-[3px] border-foreground -z-10" />
              <div className="absolute -bottom-8 -right-8 w-full h-full bg-accent border-[3px] border-foreground -z-20" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
