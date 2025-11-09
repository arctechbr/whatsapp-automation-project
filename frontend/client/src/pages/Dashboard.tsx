import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { AlertCircle, Plus, Edit2, Trash2, Users, MessageSquare, TrendingUp, Zap } from "lucide-react";
import { useRoute } from "wouter";

interface Group {
  id: string;
  name: string;
  invite_link: string;
  max_capacity: number;
  current_members: number;
  status: string;
  bot_number: string;
  is_active: boolean;
}

interface AffiliateLink {
  id: number;
  domain_base: string;
  affiliate_link: string;
  description?: string;
  is_active: boolean;
}

interface DashboardStats {
  total_groups: number;
  active_groups: number;
  full_groups: number;
  available_groups: number;
  total_affiliate_links: number;
  total_messages_processed: number;
  total_messages_posted: number;
  bots_connected: number;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Dashboard() {
  const [groups, setGroups] = useState<Group[]>([]);
  const [affiliateLinks, setAffiliateLinks] = useState<AffiliateLink[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "groups" | "links">("overview");

  useEffect(() => {
    fetchDashboardData();
    // Atualizar dados a cada 30 segundos
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      
      // Buscar estatísticas
      const statsRes = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
      if (statsRes.ok) {
        setStats(await statsRes.json());
      }
      
      // Buscar grupos
      const groupsRes = await fetch(`${API_BASE_URL}/api/groups`);
      if (groupsRes.ok) {
        setGroups(await groupsRes.json());
      }
      
      // Buscar links de afiliado
      const linksRes = await fetch(`${API_BASE_URL}/api/affiliate-links`);
      if (linksRes.ok) {
        setAffiliateLinks(await linksRes.json());
      }
      
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar dados");
    } finally {
      setLoading(false);
    }
  };

  const deleteGroup = async (groupId: string) => {
    if (!confirm("Tem certeza que deseja deletar este grupo?")) return;
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/groups/${groupId}`, {
        method: "DELETE"
      });
      
      if (res.ok) {
        setGroups(groups.filter(g => g.id !== groupId));
      } else {
        setError("Erro ao deletar grupo");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao deletar grupo");
    }
  };

  const deleteAffiliateLink = async (linkId: number) => {
    if (!confirm("Tem certeza que deseja deletar este link?")) return;
    
    try {
      const res = await fetch(`${API_BASE_URL}/api/affiliate-links/${linkId}`, {
        method: "DELETE"
      });
      
      if (res.ok) {
        setAffiliateLinks(affiliateLinks.filter(l => l.id !== linkId));
      } else {
        setError("Erro ao deletar link");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao deletar link");
    }
  };

  if (loading && !stats) {
    return <div className="p-8 text-center">Carregando...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400">Gerenciar grupos e links de afiliado</p>
        </div>

        {/* Error Alert */}
        {error && (
          <Card className="mb-6 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950">
            <CardContent className="pt-6 flex items-center gap-3 text-red-900 dark:text-red-100">
              <AlertCircle className="w-5 h-5" />
              {error}
            </CardContent>
          </Card>
        )}

        {/* Stats Grid */}
        {stats && (
          <div className="grid md:grid-cols-4 gap-4 mb-8">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  Grupos Ativos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.active_groups}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">de {stats.total_groups} total</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Disponíveis
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">{stats.available_groups}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">prontos para novos membros</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  Mensagens
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.total_messages_posted}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">postadas</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Links Afiliado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold">{stats.total_affiliate_links}</div>
                <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">configurados</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b border-gray-200 dark:border-gray-800">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === "overview"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            }`}
          >
            Visão Geral
          </button>
          <button
            onClick={() => setActiveTab("groups")}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === "groups"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            }`}
          >
            Grupos ({groups.length})
          </button>
          <button
            onClick={() => setActiveTab("links")}
            className={`px-4 py-2 font-medium border-b-2 transition-colors ${
              activeTab === "links"
                ? "border-blue-500 text-blue-600 dark:text-blue-400"
                : "border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200"
            }`}
          >
            Links ({affiliateLinks.length})
          </button>
        </div>

        {/* Groups Tab */}
        {activeTab === "groups" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Meus Grupos</h2>
              <Button className="gap-2">
                <Plus className="w-4 h-4" />
                Adicionar Grupo
              </Button>
            </div>

            {groups.length === 0 ? (
              <Card>
                <CardContent className="pt-8 text-center text-gray-600 dark:text-gray-400">
                  Nenhum grupo configurado ainda. Clique em "Adicionar Grupo" para começar.
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {groups.map((group) => (
                  <Card key={group.id}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle>{group.name}</CardTitle>
                          <CardDescription>
                            {group.current_members} / {group.max_capacity} membros
                          </CardDescription>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                          group.status === "DISPONIVEL"
                            ? "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
                            : "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200"
                        }`}>
                          {group.status}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Link de Convite</p>
                          <p className="text-sm font-mono break-all">{group.invite_link}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Bot Responsável</p>
                          <p className="text-sm">{group.bot_number}</p>
                        </div>
                        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all"
                            style={{
                              width: `${(group.current_members / group.max_capacity) * 100}%`
                            }}
                          />
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="gap-2">
                            <Edit2 className="w-4 h-4" />
                            Editar
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="gap-2 text-red-600 hover:text-red-700"
                            onClick={() => deleteGroup(group.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                            Deletar
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Links Tab */}
        {activeTab === "links" && (
          <div className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Links de Afiliado</h2>
              <Button className="gap-2">
                <Plus className="w-4 h-4" />
                Adicionar Link
              </Button>
            </div>

            {affiliateLinks.length === 0 ? (
              <Card>
                <CardContent className="pt-8 text-center text-gray-600 dark:text-gray-400">
                  Nenhum link de afiliado configurado ainda.
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {affiliateLinks.map((link) => (
                  <Card key={link.id}>
                    <CardHeader>
                      <div className="flex justify-between items-start">
                        <div>
                          <CardTitle className="font-mono">{link.domain_base}</CardTitle>
                          <CardDescription>{link.description}</CardDescription>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                          link.is_active
                            ? "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200"
                            : "bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200"
                        }`}>
                          {link.is_active ? "Ativo" : "Inativo"}
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <p className="text-sm text-gray-600 dark:text-gray-400">Link de Afiliado</p>
                          <p className="text-sm font-mono break-all">{link.affiliate_link}</p>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm" className="gap-2">
                            <Edit2 className="w-4 h-4" />
                            Editar
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            className="gap-2 text-red-600 hover:text-red-700"
                            onClick={() => deleteAffiliateLink(link.id)}
                          >
                            <Trash2 className="w-4 h-4" />
                            Deletar
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Overview Tab */}
        {activeTab === "overview" && (
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Status dos Grupos</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Total de Grupos</span>
                    <span className="font-bold">{stats?.total_groups || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Grupos Ativos</span>
                    <span className="font-bold text-green-600">{stats?.active_groups || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Grupos Cheios</span>
                    <span className="font-bold text-red-600">{stats?.full_groups || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Grupos Disponíveis</span>
                    <span className="font-bold text-blue-600">{stats?.available_groups || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Atividade</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Mensagens Processadas</span>
                    <span className="font-bold">{stats?.total_messages_processed || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Mensagens Postadas</span>
                    <span className="font-bold">{stats?.total_messages_posted || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Links de Afiliado</span>
                    <span className="font-bold">{stats?.total_affiliate_links || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Bots Conectados</span>
                    <span className="font-bold text-green-600">{stats?.bots_connected || 0}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
