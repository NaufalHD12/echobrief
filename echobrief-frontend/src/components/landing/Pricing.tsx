import { Link } from "react-router-dom";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { Check, X, Sparkles } from "lucide-react";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Perfect for trying out EchoBrief",
    features: [
      { text: "1 podcast per day", included: true },
      { text: "Max 3 topics per podcast", included: true },
      { text: "Limited topic selection", included: true },
      { text: "Standard audio quality", included: true },
      { text: "Community support", included: true },
      { text: "Unlimited podcasts", included: false },
      { text: "Priority processing", included: false },
    ],
    cta: "Start Free",
    variant: "outline" as const,
    popular: false,
  },
  {
    name: "Premium",
    price: "$5",
    period: "/month",
    description: "For serious news enthusiasts",
    features: [
      { text: "Unlimited podcasts", included: true },
      { text: "Unlimited topics per podcast", included: true },
      { text: "Full access to all topics", included: true },
      { text: "Premium audio quality", included: true },
      { text: "Priority support", included: true },
      { text: "Priority processing", included: true },
      { text: "Extended article history", included: true },
    ],
    cta: "Go Premium",
    variant: "default" as const,
    popular: true,
  },
];

export const Pricing = () => {
  return (
    <section id="pricing" className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-12">
          <BrutalBadge variant="secondary" size="lg" className="mb-4">
            Pricing
          </BrutalBadge>
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
            Simple, Fair Pricing
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Start free, upgrade when you're ready. No hidden fees.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {plans.map((plan, index) => (
            <div key={index} className="relative">
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                  <BrutalBadge variant="secondary" size="lg">
                    <Sparkles className="w-3 h-3 mr-1" /> Most Popular
                  </BrutalBadge>
                </div>
              )}
              <BrutalCard
                variant={plan.popular ? "primary" : "static"}
                padding="lg"
                className={plan.popular ? "border-[4px]" : ""}
              >
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-5xl font-bold">{plan.price}</span>
                    <span className="text-muted-foreground">{plan.period}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-2">{plan.description}</p>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center gap-3">
                      {feature.included ? (
                        <div className="w-6 h-6 bg-success border-[2px] border-foreground flex items-center justify-center">
                          <Check className="w-4 h-4" />
                        </div>
                      ) : (
                        <div className="w-6 h-6 bg-muted border-[2px] border-foreground flex items-center justify-center">
                          <X className="w-4 h-4 text-muted-foreground" />
                        </div>
                      )}
                      <span className={feature.included ? "" : "text-muted-foreground"}>
                        {feature.text}
                      </span>
                    </li>
                  ))}
                </ul>

                <Link to="/auth?mode=register">
                  <BrutalButton
                    variant={plan.variant}
                    size="lg"
                    className="w-full"
                  >
                    {plan.cta}
                  </BrutalButton>
                </Link>
              </BrutalCard>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};
