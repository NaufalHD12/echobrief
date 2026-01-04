import { BrutalCard } from "@/components/ui/brutal-card";
import { UserPlus, Tags, Wand2, Headphones } from "lucide-react";

const steps = [
  {
    step: "01",
    icon: UserPlus,
    title: "Sign Up",
    description: "Create your free account in seconds. No credit card required.",
    color: "bg-primary",
  },
  {
    step: "02",
    icon: Tags,
    title: "Pick Topics",
    description: "Select from tech, business, sports, entertainment, and more.",
    color: "bg-secondary",
  },
  {
    step: "03",
    icon: Wand2,
    title: "AI Magic",
    description: "Our AI gathers, summarizes, and scripts your personalized news.",
    color: "bg-accent",
  },
  {
    step: "04",
    icon: Headphones,
    title: "Listen & Enjoy",
    description: "Get your daily podcast delivered fresh every morning.",
    color: "bg-success",
  },
];

export const HowItWorks = () => {
  return (
    <section id="how-it-works" className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            How It Works
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            From signup to your first podcast in under 5 minutes.
          </p>
        </div>

        <div className="relative">
          {/* Connection Line */}
          <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-1 bg-foreground -translate-y-1/2 z-0" />

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 relative z-10">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                <BrutalCard variant="static" className="text-center h-full">
                  {/* Step Number */}
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-foreground text-background font-bold text-sm">
                    STEP {step.step}
                  </div>

                  <div className={`w-16 h-16 ${step.color} border-[3px] border-foreground shadow-brutal mx-auto mt-4 mb-4 flex items-center justify-center`}>
                    <step.icon className="w-8 h-8" />
                  </div>
                  
                  <h3 className="text-xl font-bold mb-2">{step.title}</h3>
                  <p className="text-muted-foreground text-sm">{step.description}</p>
                </BrutalCard>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
