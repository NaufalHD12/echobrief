import { BrutalCard } from "@/components/ui/brutal-card";
import { Clock, Brain, Sparkles, Podcast } from "lucide-react";

const values = [
  {
    icon: Clock,
    title: "Save Time",
    description: "Get your news briefing in minutes instead of hours of reading. Perfect for commutes.",
    color: "bg-primary",
  },
  {
    icon: Brain,
    title: "AI-Curated",
    description: "Our AI selects and summarizes the most relevant stories based on your interests.",
    color: "bg-secondary",
  },
  {
    icon: Sparkles,
    title: "Personalized",
    description: "Choose topics you care about. Every podcast is tailored just for you.",
    color: "bg-accent",
  },
  {
    icon: Podcast,
    title: "Studio Quality",
    description: "Professional text-to-speech with natural voices. It's like having your own news anchor.",
    color: "bg-success",
  },
];

export const ValueProposition = () => {
  return (
    <section className="py-20 bg-muted border-y-[3px] border-foreground">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Why EchoBrief?
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            We're rethinking how you consume news. Less scrolling, more listening.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {values.map((value, index) => (
            <BrutalCard
              key={index}
              className="text-center"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`w-16 h-16 ${value.color} border-[3px] border-foreground shadow-brutal mx-auto mb-4 flex items-center justify-center`}>
                <value.icon className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold mb-2">{value.title}</h3>
              <p className="text-muted-foreground text-sm">{value.description}</p>
            </BrutalCard>
          ))}
        </div>
      </div>
    </section>
  );
};
