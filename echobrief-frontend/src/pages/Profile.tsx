import { useState, useEffect, useRef } from "react";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { BrutalInputField } from "@/components/ui/brutal-input-field";
import { PageLayout } from "@/components/layout/PageLayout";
import { toast } from "sonner";
import { 
  Camera,
  Save,
  Plus,
  Trash2,
  Crown,
  Loader2,
  X
} from "lucide-react";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { Topic } from "@/types/api";

const Profile = () => {
  const { user, refreshUser } = useAuth();
  const [username, setUsername] = useState(user?.username || "");
  const [selectedTopics, setSelectedTopics] = useState<Topic[]>([]);
  const [allTopics, setAllTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (user) {
      setUsername(user.username);
    }
  }, [user]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [topicsRes, userTopicsRes] = await Promise.all([
          api.get<{ data: { items: Topic[] } }>("/topics/"),
          api.get<{ data: Topic[] }>("/users/topics")
        ]);
        setAllTopics(topicsRes.data.data.items);
        setSelectedTopics(userTopicsRes.data.data);
      } catch (error) {
        console.error("Failed to fetch data:", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleSaveProfile = async () => {
    if (!username.trim()) return;
    try {
      setIsSaving(true);
      const response = await api.put<{ message: string }>("/users/me", { username });
      await refreshUser();
      toast.success(response.data.message || "Profile updated successfully!");
    } catch (error: any) {
      console.error("Failed to update profile:", error);
      toast.error(error.response?.data?.detail || "Failed to update profile.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleToggleTopic = async (topic: Topic) => {
    const isSelected = selectedTopics.some(t => t.id === topic.id);
    const originalTopics = [...selectedTopics];

    // Optimistic update
    if (isSelected) {
      setSelectedTopics(selectedTopics.filter(t => t.id !== topic.id));
    } else {
      if (selectedTopics.length >= 3 && user?.plan_type === 'free') {
        toast.error("Free plan is limited to 3 topics. Upgrade to add more!");
        return;
      }
      setSelectedTopics([...selectedTopics, topic]);
    }

    try {
      if (isSelected) {
        await api.delete(`/users/topics/${topic.id}`);
      } else {
        await api.post("/users/topics", null, { params: { topic_id: topic.id } });
      }
    } catch (error: any) {
      console.error("Failed to toggle topic:", error);
      // Revert on error
      setSelectedTopics(originalTopics);
      toast.error(error.response?.data?.detail || "Failed to update topic preference.");
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setIsUploading(true);
      await api.post("/users/me/avatar", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      await refreshUser();
    } catch (error: any) {
      console.error("Failed to upload avatar:", error);
      toast.error(error.response?.data?.detail || "Failed to upload avatar.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleDeleteAvatar = async () => {
    try {
      setIsDeleting(true);
      await api.delete("/users/me/avatar");
      await refreshUser();
      toast.success("Avatar deleted successfully!");
    } catch (error: any) {
      console.error("Failed to delete avatar:", error);
      toast.error(error.response?.data?.detail || "Failed to delete avatar.");
    } finally {
      setIsDeleting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <PageLayout
      title="Profile"
      subtitle="Manage your account settings and preferences."
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Avatar Section */}
        <BrutalCard variant="static">
          <div className="text-center">
            <div className="relative inline-block mb-4">
              <div className="w-32 h-32 bg-secondary border-[3px] border-foreground shadow-brutal flex items-center justify-center font-bold mx-auto overflow-hidden">
                 {user?.avatar_url ? (
                    <img src={user.avatar_url} alt={user.username} className="w-full h-full object-cover" />
                  ) : (
                    <span className="text-4xl">{user?.username?.substring(0, 2).toUpperCase()}</span>
                  )}
              </div>
              <input 
                type="file" 
                ref={fileInputRef} 
                className="hidden" 
                accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={handleFileChange}
              />
              <button 
                onClick={() => fileInputRef.current?.click()}
                disabled={isUploading || isDeleting}
                className="absolute -bottom-2 -right-2 w-10 h-10 bg-primary border-[2px] border-foreground shadow-brutal flex items-center justify-center hover:bg-primary/90 transition-colors"
              >
                {isUploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Camera className="w-5 h-5" />}
              </button>
              {user?.avatar_url && (
                <button 
                  onClick={handleDeleteAvatar}
                  disabled={isUploading || isDeleting}
                  className="absolute -bottom-2 -left-2 w-10 h-10 bg-destructive border-[2px] border-foreground shadow-brutal flex items-center justify-center hover:bg-destructive/90 transition-colors text-destructive-foreground"
                >
                  {isDeleting ? <Loader2 className="w-5 h-5 animate-spin" /> : <X className="w-5 h-5" />}
                </button>
              )}
            </div>
            <h2 className="text-xl font-bold">{user?.username}</h2>
            <p className="text-sm text-muted-foreground mb-4">{user?.email}</p>
            <BrutalBadge variant="outline" size="lg" className="capitalize">
              {user?.plan_type || "Free"} Plan
            </BrutalBadge>
          </div>
        </BrutalCard>

        {/* Settings Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Username */}
          <BrutalCard variant="static">
            <h3 className="text-lg font-bold mb-4">Account Settings</h3>
            <div className="space-y-4">
              <div>
                <BrutalInputField
                  label="Username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Your username"
                />
              </div>
              <BrutalButton onClick={handleSaveProfile} disabled={isSaving}>
                {isSaving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}
                Save Changes
              </BrutalButton>
            </div>
          </BrutalCard>

          {/* Topics */}
          <BrutalCard variant="static">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold">Favorite Topics</h3>
              <span className="text-sm text-muted-foreground">{selectedTopics.length}/{user?.plan_type === 'paid' ? '∞' : '3'} selected</span>
            </div>
            <p className="text-sm text-muted-foreground mb-4">
              Free plan allows up to 3 topics. Upgrade to Pro for unlimited topics.
            </p>
            <div className="flex flex-wrap gap-2 mb-4">
              {allTopics.map((topic) => {
                const isSelected = selectedTopics.some(t => t.id === topic.id);
                const  isDisabled = !isSelected && selectedTopics.length >= 3 && user?.plan_type !== 'paid';
                return (
                  <button
                    key={topic.id}
                    onClick={() => handleToggleTopic(topic)}
                    disabled={isDisabled}
                    className={`px-4 py-2 border-[2px] border-foreground font-bold uppercase text-sm transition-all ${
                      isSelected
                        ? "bg-accent shadow-brutal"
                        : isDisabled
                        ? "bg-muted text-muted-foreground cursor-not-allowed"
                        : "bg-card hover:bg-muted"
                    }`}
                  >
                    {isSelected ? (
                      <span className="flex items-center gap-1">
                        {topic.name}
                        <X className="w-3 h-3" />
                      </span>
                    ) : (
                      <span className="flex items-center gap-1">
                        <Plus className="w-3 h-3" />
                        {topic.name}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </BrutalCard>

          {/* Upgrade */}
          <BrutalCard variant="primary">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-background border-[3px] border-foreground flex items-center justify-center flex-shrink-0">
                <Crown className="w-7 h-7" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg">Upgrade to Pro</h3>
                <p className="text-sm">Get unlimited topics, on-demand podcasts, and HD audio for just $5/month.</p>
              </div>
              <BrutalButton variant="outline">
                Upgrade Now
              </BrutalButton>
            </div>
          </BrutalCard>
        </div>
      </div>
    </PageLayout>
  );
};

export default Profile;

