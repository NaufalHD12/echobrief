import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { 
  Rss, 
  Brain, 
  Volume2, 
  Search, 
  Clock, 
  Shield, 
  Globe, 
  Zap 
} from "lucide-react";

const features = [
  {
    icon: Rss,
    title: "Multi-Source Aggregation",
    description: "News from 100+ trusted sources, automatically collected and filtered.",
    badge: "Core",
    color: "bg-primary",
  },
  {
    icon: Brain,
    title: "Smart Summarization",
    description: "AI-powered summaries that capture key points without the fluff.",
    badge: "AI",
    color: "bg-secondary",
  },
  {
    icon: Volume2,
    title: "Natural Voice TTS",
    description: "Studio-quality text-to-speech with multiple voice options.",
    badge: "Audio",
    color: "bg-accent",
  },
  {
    icon: Search,
    title: "Global Search",
    description: "Find any article, topic, or source with powerful search.",
    badge: "Core",
    color: "bg-success",
  },
  {
    icon: Clock,
    title: "Scheduled Delivery",
    description: "Get your podcast when you want it: morning, lunch, or evening.",
    badge: "Pro",
    color: "bg-primary",
  },
  {
    icon: Shield,
    title: "Privacy First",
    description: "Your data stays yours. No selling, no tracking, no ads.",
    badge: "Security",
    color: "bg-secondary",
  },
  {
    icon: Globe,
    title: "Topic Variety",
    description: "From tech to sports, finance to entertainment, we cover it all.",
    badge: "Content",
    color: "bg-accent",
  },
  {
    icon: Zap,
    title: "Instant Generation",
    description: "New podcast ready in seconds, not hours. Fresh news, always.",
    badge: "Speed",
    color: "bg-success",
  },
];

export const Features = () => {
  return (
    <section id="features" className="py-20 bg-muted border-y-[3px] border-foreground">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <BrutalBadge variant="accent" size="lg" className="mb-4">
            Features
          </BrutalBadge>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Everything You Need
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Packed with features designed for modern news consumption.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <BrutalCard key={index}>
              <div className="flex items-start gap-4">
                <div className={`w-12 h-12 ${feature.color} border-[3px] border-foreground shadow-[2px_2px_0px_0px_hsl(var(--foreground))] flex-shrink-0 flex items-center justify-center`}>
                  <feature.icon className="w-6 h-6" />
                </div>
                <div>
                  <BrutalBadge variant="outline" size="sm" className="mb-2">
                    {feature.badge}
                  </BrutalBadge>
                  <h3 className="font-bold mb-1">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </div>
              </div>
            </BrutalCard>
          ))}
        </div>
      </div>
    </section>
  );
};
