import { useState, useEffect } from "react";
import axios from "axios";
import { BrutalButton } from "@/components/ui/brutal-button";
import { BrutalCard } from "@/components/ui/brutal-card";
import { BrutalBadge } from "@/components/ui/brutal-badge";
import { BrutalInputField } from "@/components/ui/brutal-input-field";
import { BrutalModal } from "@/components/ui/brutal-modal";
import { PageLayout } from "@/components/layout/PageLayout";
import { PageSizeSelector } from "@/components/ui/page-size-selector";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "sonner";
import {
  Users,
  Globe,
  Tag,
  Settings,
  Search,
  Plus,
  Edit,
  Trash2,
  RefreshCw,
  Loader2,
  Play,
  Clock,
} from "lucide-react";
import api from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";
import { User, Topic, Source } from "@/types/api";

type TabType = "users" | "sources" | "topics" | "system";

const Admin = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>("users");

  // Redirect non-admins
  if (user?.role !== "admin") {
    return (
      <PageLayout title="Access Denied" subtitle="">
        <div className="text-center py-12">
          <div className="w-20 h-20 bg-destructive/20 border-[3px] border-foreground shadow-brutal mx-auto mb-4 flex items-center justify-center">
            <Settings className="w-10 h-10 text-destructive" />
          </div>
          <p className="text-muted-foreground">You don't have permission to access this page.</p>
        </div>
      </PageLayout>
    );
  }

  const tabs: { id: TabType; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
    { id: "users", label: "Users", icon: Users },
    { id: "sources", label: "Sources", icon: Globe },
    { id: "topics", label: "Topics", icon: Tag },
    { id: "system", label: "System", icon: Settings },
  ];

  return (
    <PageLayout title="Admin Dashboard" subtitle="Manage users, content, and system operations.">
      {/* Tabs */}
      <div className="flex border-[3px] border-foreground mb-8">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex-1 py-3 px-4 font-bold uppercase text-sm transition-colors border-r-[3px] border-foreground last:border-r-0 flex items-center justify-center gap-2 ${
                activeTab === tab.id ? "bg-primary" : "bg-card hover:bg-muted"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span className="hidden sm:inline">{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === "users" && <UsersTab />}
      {activeTab === "sources" && <SourcesTab />}
      {activeTab === "topics" && <TopicsTab />}
      {activeTab === "system" && <SystemTab />}
    </PageLayout>
  );
};

// ==================== USERS TAB ====================
const UsersTab = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [pageSize, setPageSize] = useState(10);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [editForm, setEditForm] = useState({ username: "", plan_type: "", role: "" });
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(searchQuery), 500);
    return () => clearTimeout(timer);
  }, [searchQuery]);

  const fetchUsers = async () => {
    try {
      setIsLoading(true);
      const params: Record<string, string | number> = { per_page: pageSize };
      if (debouncedSearch) params.search = debouncedSearch;
      const response = await api.get<{ data: User[] }>("/admin/users", { params });
      setUsers(response.data.data);
    } catch (error) {
      console.error("Failed to fetch users:", error);
      toast.error("Failed to fetch users");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [debouncedSearch, pageSize]);

  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setEditForm({
      username: user.username,
      plan_type: user.plan_type,
      role: user.role,
    });
  };

  const handleSaveUser = async () => {
    if (!editingUser) return;
    try {
      setIsSaving(true);
      await api.put(`/admin/users/${editingUser.id}`, editForm);
      toast.success("User updated successfully");
      setEditingUser(null);
      fetchUsers();
    } catch (error) {
      console.error("Failed to update user:", error);
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error("Failed to update user");
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <BrutalInputField
          icon={Search}
          placeholder="Search users..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          containerClassName="flex-1"
        />
        <div className="flex gap-2">
          <PageSizeSelector value={pageSize} onChange={setPageSize} options={[10, 25, 50]} />
          <BrutalButton variant="outline" onClick={fetchUsers} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          </BrutalButton>
        </div>
      </div>

      <BrutalCard variant="static" padding="none">
        <Table>
          <TableHeader>
            <TableRow className="border-b-[2px] border-foreground">
              <TableHead className="font-bold">User</TableHead>
              <TableHead className="font-bold">Email</TableHead>
              <TableHead className="font-bold">Role</TableHead>
              <TableHead className="font-bold">Plan</TableHead>
              <TableHead className="font-bold text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8">
                  <Loader2 className="w-6 h-6 animate-spin mx-auto" />
                </TableCell>
              </TableRow>
            ) : users.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                  No users found
                </TableCell>
              </TableRow>
            ) : (
              users.map((u) => (
                <TableRow key={u.id} className="border-b border-border">
                  <TableCell className="font-medium">{u.username}</TableCell>
                  <TableCell className="text-muted-foreground">{u.email}</TableCell>
                  <TableCell>
                    <BrutalBadge variant={u.role === "admin" ? "accent" : "outline"} size="sm">
                      {u.role}
                    </BrutalBadge>
                  </TableCell>
                  <TableCell>
                    <BrutalBadge variant={u.plan_type === "paid" ? "success" : "secondary"} size="sm">
                      {u.plan_type}
                    </BrutalBadge>
                  </TableCell>
                  <TableCell className="text-right">
                    <BrutalButton variant="outline" size="sm" onClick={() => handleEditUser(u)}>
                      <Edit className="w-4 h-4" />
                    </BrutalButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </BrutalCard>

      {/* Edit User Modal */}
      <BrutalModal
        open={!!editingUser}
        onOpenChange={(open) => !open && setEditingUser(null)}
        title="Edit User"
        showCancel
        confirmText="Save Changes"
        onConfirm={handleSaveUser}
      >
        <div className="space-y-4">
          <BrutalInputField
            label="Username"
            value={editForm.username}
            onChange={(e) => setEditForm({ ...editForm, username: e.target.value })}
          />
          <div>
            <label className="block font-bold mb-2">Plan Type</label>
            <select
              value={editForm.plan_type}
              onChange={(e) => setEditForm({ ...editForm, plan_type: e.target.value })}
              className="w-full p-3 border-[2px] border-foreground bg-background font-medium"
            >
              <option value="free">Free</option>
              <option value="paid">Paid</option>
            </select>
          </div>
          <div>
            <label className="block font-bold mb-2">Role</label>
            <select
              value={editForm.role}
              onChange={(e) => setEditForm({ ...editForm, role: e.target.value })}
              className="w-full p-3 border-[2px] border-foreground bg-background font-medium"
            >
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
          </div>
        </div>
      </BrutalModal>
    </>
  );
};

// ==================== SOURCES TAB ====================
const SourcesTab = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingSource, setEditingSource] = useState<Source | null>(null);
  const [form, setForm] = useState({ name: "", base_url: "" });
  const [isSaving, setIsSaving] = useState(false);

  const fetchSources = async () => {
    try {
      setIsLoading(true);
      const response = await api.get<{ data: { items: Source[] } }>("/sources/");
      setSources(response.data.data.items);
    } catch (error) {
      console.error("Failed to fetch sources:", error);
      toast.error("Failed to fetch sources");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const handleCreate = () => {
    setEditingSource(null);
    setForm({ name: "", base_url: "" });
    setIsModalOpen(true);
  };

  const handleEdit = (source: Source) => {
    setEditingSource(source);
    setForm({ name: source.name, base_url: source.base_url });
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      if (editingSource) {
        await api.put(`/admin/sources/${editingSource.id}`, form);
        toast.success("Source updated successfully");
      } else {
        await api.post("/admin/sources", form);
        toast.success("Source created successfully");
      }
      setIsModalOpen(false);
      fetchSources();
    } catch (error) {
      console.error("Failed to save source:", error);
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error("Failed to save source");
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this source?")) return;
    try {
      await api.delete(`/admin/sources/${id}`);
      toast.success("Source deleted successfully");
      fetchSources();
    } catch (error) {
      console.error("Failed to delete source:", error);
      toast.error("Failed to delete source");
    }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-6">
        <p className="text-muted-foreground">{sources.length} sources</p>
        <BrutalButton onClick={handleCreate}>
          <Plus className="w-4 h-4 mr-2" /> Add Source
        </BrutalButton>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          <div className="col-span-full flex justify-center py-10">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        ) : sources.length === 0 ? (
          <p className="col-span-full text-center py-10 text-muted-foreground">No sources found</p>
        ) : (
          sources.map((source) => (
            <BrutalCard key={source.id} variant="static" padding="sm">
              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  <h3 className="font-bold truncate">{source.name}</h3>
                  <p className="text-sm text-muted-foreground truncate">{source.base_url}</p>
                </div>
                <div className="flex gap-1 ml-2">
                  <button
                    onClick={() => handleEdit(source)}
                    className="p-2 hover:bg-muted transition-colors"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(source.id)}
                    className="p-2 hover:bg-destructive/20 text-destructive transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </BrutalCard>
          ))
        )}
      </div>

      <BrutalModal
        open={isModalOpen}
        onOpenChange={(open) => !open && setIsModalOpen(false)}
        title={editingSource ? "Edit Source" : "Add Source"}
        showCancel
        confirmText={editingSource ? "Save Changes" : "Create Source"}
        onConfirm={handleSave}
      >
        <div className="space-y-4">
          <BrutalInputField
            label="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="Source name"
          />
          <BrutalInputField
            label="Base URL"
            value={form.base_url}
            onChange={(e) => setForm({ ...form, base_url: e.target.value })}
            placeholder="https://example.com"
          />
        </div>
      </BrutalModal>
    </>
  );
};

// ==================== TOPICS TAB ====================
const TopicsTab = () => {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);
  const [form, setForm] = useState({ name: "", slug: "" });
  const [isSaving, setIsSaving] = useState(false);

  const fetchTopics = async () => {
    try {
      setIsLoading(true);
      const response = await api.get<{ data: { items: Topic[] } }>("/topics/");
      setTopics(response.data.data.items);
    } catch (error) {
      console.error("Failed to fetch topics:", error);
      toast.error("Failed to fetch topics");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const handleCreate = () => {
    setEditingTopic(null);
    setForm({ name: "", slug: "" });
    setIsModalOpen(true);
  };

  const handleEdit = (topic: Topic) => {
    setEditingTopic(topic);
    setForm({ name: topic.name, slug: topic.slug });
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      if (editingTopic) {
        await api.put(`/admin/topics/${editingTopic.id}`, form);
        toast.success("Topic updated successfully");
      } else {
        await api.post("/admin/topics", form);
        toast.success("Topic created successfully");
      }
      setIsModalOpen(false);
      fetchTopics();
    } catch (error) {
      console.error("Failed to save topic:", error);
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error("Failed to save topic");
      }
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this topic?")) return;
    try {
      await api.delete(`/admin/topics/${id}`);
      toast.success("Topic deleted successfully");
      fetchTopics();
    } catch (error) {
      console.error("Failed to delete topic:", error);
      toast.error("Failed to delete topic");
    }
  };

  return (
    <>
      <div className="flex justify-between items-center mb-6">
        <p className="text-muted-foreground">{topics.length} topics</p>
        <BrutalButton onClick={handleCreate}>
          <Plus className="w-4 h-4 mr-2" /> Add Topic
        </BrutalButton>
      </div>

      <div className="flex flex-wrap gap-3">
        {isLoading ? (
          <div className="w-full flex justify-center py-10">
            <Loader2 className="w-8 h-8 animate-spin" />
          </div>
        ) : topics.length === 0 ? (
          <p className="w-full text-center py-10 text-muted-foreground">No topics found</p>
        ) : (
          topics.map((topic) => (
            <div
              key={topic.id}
              className="flex items-center gap-2 px-4 py-2 bg-card border-[2px] border-foreground"
            >
              <span className="font-bold">{topic.name}</span>
              <span className="text-xs text-muted-foreground">({topic.slug})</span>
              <button
                onClick={() => handleEdit(topic)}
                className="p-1 hover:bg-muted transition-colors ml-2"
              >
                <Edit className="w-3 h-3" />
              </button>
              <button
                onClick={() => handleDelete(topic.id)}
                className="p-1 hover:bg-destructive/20 text-destructive transition-colors"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))
        )}
      </div>

      <BrutalModal
        open={isModalOpen}
        onOpenChange={(open) => !open && setIsModalOpen(false)}
        title={editingTopic ? "Edit Topic" : "Add Topic"}
        showCancel
        confirmText={editingTopic ? "Save Changes" : "Create Topic"}
        onConfirm={handleSave}
      >
        <div className="space-y-4">
          <BrutalInputField
            label="Name"
            value={form.name}
            onChange={(e) => setForm({ ...form, name: e.target.value })}
            placeholder="Topic name"
          />
          <BrutalInputField
            label="Slug (optional)"
            value={form.slug}
            onChange={(e) => setForm({ ...form, slug: e.target.value })}
            placeholder="topic-slug"
          />
        </div>
      </BrutalModal>
    </>
  );
};

// ==================== SYSTEM TAB ====================
const SystemTab = () => {
  const [isAggregating, setIsAggregating] = useState(false);
  const [isCheckingSubscriptions, setIsCheckingSubscriptions] = useState(false);
  const [lastAggregationResult, setLastAggregationResult] = useState<Record<string, unknown> | null>(null);
  const [lastSubscriptionResult, setLastSubscriptionResult] = useState<Record<string, unknown> | null>(null);

  const handleAggregateNews = async () => {
    try {
      setIsAggregating(true);
      const response = await api.post<{ data: Record<string, unknown> }>("/admin/system/aggregate-news");
      setLastAggregationResult(response.data.data);
      toast.success("News aggregation completed");
    } catch (error) {
      console.error("Failed to aggregate news:", error);
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error("Failed to aggregate news");
      }
    } finally {
      setIsAggregating(false);
    }
  };

  const handleCheckSubscriptions = async () => {
    try {
      setIsCheckingSubscriptions(true);
      const response = await api.post<{ data: Record<string, unknown> }>("/admin/subscriptions/check-expired");
      setLastSubscriptionResult(response.data.data);
      toast.success("Subscription check completed");
    } catch (error) {
      console.error("Failed to check subscriptions:", error);
      if (axios.isAxiosError(error) && error.response?.data?.detail) {
        toast.error(error.response.data.detail);
      } else {
        toast.error("Failed to check subscriptions");
      }
    } finally {
      setIsCheckingSubscriptions(false);
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <BrutalCard variant="static">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-secondary border-[2px] border-foreground flex items-center justify-center flex-shrink-0">
            <Play className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-lg mb-1">Aggregate News</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Trigger the news aggregation process to fetch latest articles from all sources.
            </p>
            <BrutalButton onClick={handleAggregateNews} disabled={isAggregating}>
              {isAggregating ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              {isAggregating ? "Aggregating..." : "Run Aggregation"}
            </BrutalButton>
            {lastAggregationResult && (
              <div className="mt-4 p-3 bg-muted border-[2px] border-foreground text-sm">
                <pre className="whitespace-pre-wrap">{JSON.stringify(lastAggregationResult, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      </BrutalCard>

      <BrutalCard variant="static">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-accent border-[2px] border-foreground flex items-center justify-center flex-shrink-0">
            <Clock className="w-6 h-6" />
          </div>
          <div className="flex-1">
            <h3 className="font-bold text-lg mb-1">Check Expired Subscriptions</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Check and downgrade users with expired paid subscriptions.
            </p>
            <BrutalButton onClick={handleCheckSubscriptions} disabled={isCheckingSubscriptions}>
              {isCheckingSubscriptions ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Clock className="w-4 h-4 mr-2" />
              )}
              {isCheckingSubscriptions ? "Checking..." : "Check Subscriptions"}
            </BrutalButton>
            {lastSubscriptionResult && (
              <div className="mt-4 p-3 bg-muted border-[2px] border-foreground text-sm">
                <pre className="whitespace-pre-wrap">{JSON.stringify(lastSubscriptionResult, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      </BrutalCard>
    </div>
  );
};

export default Admin;
