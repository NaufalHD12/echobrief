import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { BrutalModal } from "@/components/ui/brutal-modal";
import { toast } from "sonner";
import { 
  Headphones, 
  Check, 
  Crown,
  Sparkles,
  Camera,
  ArrowRight,
  ArrowLeft,
  Laptop,
  Bot,
  Briefcase,
  TrendingUp,
  Trophy,
  Globe,
  FlaskConical,
  Clapperboard,
  Heart,
  Landmark,
  PartyPopper,
  Loader2     // Added loader
} from "lucide-react";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Topic } from "@/types/api";

// Mapping for icons based on slug or name
const getTopicIcon = (slug: string) => {
  const map: Record<string, any> = {
    tech: Laptop,
    ai: Bot,
    business: Briefcase,
    finance: TrendingUp,
    sports: Trophy,
    world: Globe,
    science: FlaskConical,
    entertainment: Clapperboard,
    health: Heart,
    politics: Landmark
  };
  return map[slug] || Globe;
};

const Onboarding = () => {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();
  const [step, setStep] = useState(1);
  const [selectedPlan, setSelectedPlan] = useState<"free" | "paid">("free");
  const [selectedTopics, setSelectedTopics] = useState<number[]>([]); // Changed to number[]
  const [topics, setTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentUrl, setPaymentUrl] = useState<string | null>(null);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        setIsLoading(true);
        const response = await api.get<{ data: { items: Topic[] } }>("/topics/");
        setTopics(response.data.data.items);
      } catch (error) {
        console.error("Failed to fetch topics:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTopics();
  }, []);

  const maxTopics = selectedPlan === "free" ? 3 : topics.length;

  const toggleTopic = (topicId: number) => {
    if (selectedTopics.includes(topicId)) {
      setSelectedTopics(selectedTopics.filter(t => t !== topicId));
    } else if (selectedTopics.length < maxTopics) {
      setSelectedTopics([...selectedTopics, topicId]);
    }
  };

  const handleComplete = async () => {
    try {
      setIsSubmitting(true);
      // Construct form data for onboarding
      const formData = new FormData();
      formData.append("plan_type", selectedPlan);
      formData.append("topic_ids", selectedTopics.join(","));
      
      // Note: Avatar upload not implemented in UI yet
      
      const response = await api.post<{ data: { payment_url?: string }, message: string }>("/users/onboarding", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      
      const url = response.data.data.payment_url;
      
      await refreshUser();
      toast.success(response.data.message || "Onboarding completed!");
      
      if (url) {
        // Show modal instead of alert
        setPaymentUrl(url);
        setShowPaymentModal(true);
      } else {
        navigate("/dashboard");
      }
    } catch (error: any) {
      console.error("Onboarding failed:", error);
      toast.error(error.response?.data?.detail || "Failed to complete onboarding. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handlePaymentModalClose = () => {
    if (paymentUrl) {
      window.open(paymentUrl, '_blank');
    }
    setShowPaymentModal(false);
    navigate("/dashboard");
  };

  return (
    <div className="min-h-screen geometric-pattern py-12 px-4">
      {/* Decorative Elements */}
      <div className="fixed top-20 left-10 w-16 h-16 bg-secondary border-[3px] border-foreground shadow-brutal rotate-12 animate-float hidden lg:block" />
      <div className="fixed top-40 right-16 w-12 h-12 bg-accent border-[3px] border-foreground shadow-brutal -rotate-6 animate-float hidden lg:block" style={{ animationDelay: "1s" }} />

      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-12 h-12 bg-primary border-[3px] border-foreground shadow-brutal flex items-center justify-center">
              <Headphones className="w-6 h-6" />
            </div>
            <span className="text-2xl font-bold">EchoBrief</span>
          </div>
          <h1 className="text-3xl font-bold mb-2 flex items-center justify-center gap-2">
            Welcome aboard! <PartyPopper className="w-8 h-8 text-secondary" />
          </h1>
          <p className="text-muted-foreground">Let's get you set up in just a few steps.</p>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              className={`w-12 h-2 border-[2px] border-foreground transition-colors ${
                s <= step ? "bg-primary" : "bg-muted"
              }`}
            />
          ))}
        </div>

        {/* Step 1: Plan Selection */}
        {step === 1 && (
          <div className="animate-slide-in">
            <h2 className="text-2xl font-bold text-center mb-6">Choose Your Plan</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <BrutalCard
                variant={selectedPlan === "free" ? "accent" : "static"}
                className={`cursor-pointer relative ${selectedPlan === "free" ? "border-[4px]" : ""}`}
                onClick={() => setSelectedPlan("free")}
              >
                <div className="text-center">
                  <h3 className="text-xl font-bold mb-2">Free</h3>
                  <p className="text-3xl font-bold mb-4">$0<span className="text-sm font-normal">/forever</span></p>
                  <ul className="text-sm space-y-2 text-left">
                    <li className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-success" /> Up to 3 topics
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-success" /> Daily cached podcasts
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-success" /> Basic audio quality
                    </li>
                  </ul>
                </div>
                {selectedPlan === "free" && (
                  <div className="absolute -top-3 -right-3 w-8 h-8 bg-success border-[2px] border-foreground flex items-center justify-center">
                    <Check className="w-5 h-5" />
                  </div>
                )}
              </BrutalCard>

              <BrutalCard
                variant={selectedPlan === "paid" ? "primary" : "static"}
                className={`cursor-pointer relative ${selectedPlan === "paid" ? "border-[4px]" : ""}`}
                onClick={() => setSelectedPlan("paid")}
              >
                <BrutalBadge variant="secondary" className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Sparkles className="w-3 h-3 mr-1" /> Recommended
                </BrutalBadge>
                <div className="text-center mt-2">
                  <h3 className="text-xl font-bold mb-2 flex items-center justify-center gap-2">
                    <Crown className="w-5 h-5" /> Premium
                  </h3>
                  <p className="text-3xl font-bold mb-4">$5<span className="text-sm font-normal">/month</span></p>
                  <ul className="text-sm space-y-2 text-left">
                    <li className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-success" /> Unlimited topics
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-success" /> On-demand generation
                    </li>
                    <li className="flex items-center gap-2">
                      <Check className="w-4 h-4 text-success" /> HD audio quality
                    </li>
                  </ul>
                </div>
                {selectedPlan === "paid" && (
                  <div className="absolute -top-3 -right-3 w-8 h-8 bg-success border-[2px] border-foreground flex items-center justify-center">
                    <Check className="w-5 h-5" />
                  </div>
                )}
              </BrutalCard>
            </div>
          </div>
        )}

        {/* Step 2: Topic Selection */}
        {step === 2 && (
          <div className="animate-slide-in">
            <h2 className="text-2xl font-bold text-center mb-2">Pick Your Topics</h2>
            <p className="text-center text-muted-foreground mb-6">
              {selectedPlan === "free" 
                ? `Select up to ${maxTopics} topics (${selectedTopics.length}/${maxTopics})` 
                : "Select as many as you like!"}
            </p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {isLoading ? (
                <div className="col-span-full flex justify-center py-8">
                  <Loader2 className="w-8 h-8 animate-spin" />
                </div>
              ) : (
                topics.map((topic) => {
                  const isSelected = selectedTopics.includes(topic.id);
                  const isDisabled = !isSelected && selectedTopics.length >= maxTopics;
                  const Icon = getTopicIcon(topic.slug);
                  
                  return (
                    <button
                      key={topic.id}
                      onClick={() => toggleTopic(topic.id)}
                      disabled={isDisabled}
                      className={`p-4 border-[3px] border-foreground font-bold transition-all text-left group ${
                        isSelected
                          ? "bg-accent shadow-brutal"
                          : isDisabled
                          ? "bg-muted text-muted-foreground cursor-not-allowed"
                          : "bg-card hover:bg-muted shadow-brutal hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5"
                      }`}
                    >
                      <div className="mb-2">
                        <Icon className={`w-8 h-8 ${isSelected ? "text-foreground" : "text-primary"}`} />
                      </div>
                      <span className="text-sm">{topic.name}</span>
                      {isSelected && (
                        <Check className="absolute top-2 right-2 w-4 h-4" />
                      )}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}

        {/* Step 3: Avatar */}
        {step === 3 && (
          <div className="animate-slide-in">
            <h2 className="text-2xl font-bold text-center mb-2">Add a Profile Photo</h2>
            <p className="text-center text-muted-foreground mb-6">
              Optional: Add a photo to personalize your profile.
            </p>
            <BrutalCard variant="static" className="max-w-sm mx-auto">
              <div className="text-center">
                <div className="relative inline-block mb-4">
                  <div className="w-32 h-32 bg-secondary border-[3px] border-foreground shadow-brutal flex items-center justify-center text-4xl font-bold mx-auto">
                    JD
                  </div>
                  <button className="absolute -bottom-2 -right-2 w-12 h-12 bg-primary border-[3px] border-foreground shadow-brutal flex items-center justify-center hover:shadow-brutal-hover hover:-translate-x-0.5 hover:-translate-y-0.5 transition-all">
                    <Camera className="w-6 h-6" />
                  </button>
                </div>
                <p className="text-sm text-muted-foreground">Click to upload a photo</p>
              </div>
            </BrutalCard>
          </div>
        )}

        {/* Step 4: Final Step - Different for Free vs Premium */}
        {step === 4 && (
          <div className="animate-slide-in">
            {selectedPlan === "paid" ? (
              <>
                <h2 className="text-2xl font-bold text-center mb-2 flex items-center justify-center gap-2">
                  <Crown className="w-6 h-6 text-primary" /> Complete Your Premium Subscription
                </h2>
                <p className="text-center text-muted-foreground mb-6">
                  One more step! Subscribe on Ko-fi to unlock Premium features.
                </p>
                <BrutalCard variant="primary" className="max-w-md mx-auto">
                  <div className="text-center space-y-4">
                    <div className="w-16 h-16 bg-background border-[3px] border-foreground shadow-brutal flex items-center justify-center mx-auto">
                      <Crown className="w-8 h-8" />
                    </div>
                    <div>
                      <h3 className="font-bold text-lg mb-2">How it works:</h3>
                      <ol className="text-sm text-left space-y-2 max-w-xs mx-auto">
                        <li className="flex gap-2">
                          <span className="font-bold">1.</span>
                          Click "Subscribe on Ko-fi" below
                        </li>
                        <li className="flex gap-2">
                          <span className="font-bold">2.</span>
                          Complete your $5/month subscription
                        </li>
                        <li className="flex gap-2">
                          <span className="font-bold">3.</span>
                          Your account will be upgraded automatically
                        </li>
                      </ol>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      You'll start with Free features until payment is verified.
                    </p>
                  </div>
                </BrutalCard>
              </>
            ) : (
              <>
                <h2 className="text-2xl font-bold text-center mb-2">You're All Set!</h2>
                <p className="text-center text-muted-foreground mb-6">
                  Your account is ready. Start listening to your personalized news podcasts!
                </p>
                <BrutalCard variant="accent" className="max-w-sm mx-auto">
                  <div className="text-center space-y-3">
                    <div className="w-16 h-16 bg-background border-[3px] border-foreground shadow-brutal flex items-center justify-center mx-auto">
                      <Headphones className="w-8 h-8" />
                    </div>
                    <div>
                      <p className="font-bold">Your selected topics:</p>
                      <p className="text-sm text-muted-foreground">
                        {topics.filter(t => selectedTopics.includes(t.id)).map(t => t.name).join(", ") || "None selected"}
                      </p>
                    </div>
                  </div>
                </BrutalCard>
              </>
            )}
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8">
          {step > 1 ? (
            <BrutalButton variant="outline" onClick={() => setStep(step - 1)}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </BrutalButton>
          ) : (
            <div />
          )}
          
          {step < 4 ? (
            <BrutalButton 
              onClick={() => setStep(step + 1)}
              disabled={step === 2 && selectedTopics.length === 0}
            >
              Continue
              <ArrowRight className="w-4 h-4 ml-2" />
            </BrutalButton>
          ) : (
            <BrutalButton onClick={handleComplete} disabled={isSubmitting}>
              {isSubmitting ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : selectedPlan === "paid" ? (
                <Crown className="w-4 h-4 mr-2" />
              ) : (
                <Sparkles className="w-4 h-4 mr-2" />
              )}
              {isSubmitting 
                ? "Setting up..." 
                : selectedPlan === "paid" 
                  ? "Subscribe on Ko-fi" 
                  : "Start Listening"}
            </BrutalButton>
          )}
        </div>
      </div>

      {/* Payment Modal */}
      <BrutalModal
        open={showPaymentModal}
        onOpenChange={setShowPaymentModal}
        title="Complete Your Subscription"
        description="Click the button below to open Ko-fi and complete your Premium subscription."
        variant="info"
        confirmText="Open Ko-fi & Continue"
        onConfirm={handlePaymentModalClose}
      >
        <div className="text-sm text-muted-foreground space-y-2">
          <p>• Your payment will be processed by Ko-fi</p>
          <p>• Your account will be upgraded once payment is verified</p>
          <p>• You can start using the app with Free features in the meantime</p>
        </div>
      </BrutalModal>
    </div>
  );
};

export default Onboarding;
