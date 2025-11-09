import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertCircle, Menu, X, ChevronRight } from "lucide-react";
import { APP_LOGO, APP_TITLE } from "@/const";
import { Streamdown } from 'streamdown';

export default function Home() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeSection, setActiveSection] = useState("inicio");
  const [guideContent, setGuideContent] = useState("");

  useEffect(() => {
    // Carregar o conteúdo do guia
    fetch("/guia_conteudo.md")
      .then(res => res.text())
      .then(text => setGuideContent(text))
      .catch(err => console.error("Erro ao carregar guia:", err));
  }, []);

  const sections = [
    { id: "inicio", label: "Início", title: "Bem-vindo ao Guia" },
    { id: "aviso", label: "⚠️ Aviso", title: "Aviso Importante" },
    { id: "arquitetura", label: "Arquitetura", title: "Arquitetura da Solução" },
    { id: "configuracao", label: "Configuração", title: "Configuração Inicial" },
    { id: "modulo-a", label: "Módulo A", title: "Automação de Anúncios" },
    { id: "modulo-b", label: "Módulo B", title: "Gerenciamento de Lotação" },
    { id: "proximos", label: "Próximos Passos", title: "Próximos Passos" },
  ];

  const getContentForSection = () => {
    switch (activeSection) {
      case "inicio":
        return (
          <div className="space-y-6">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 rounded-lg p-8 border border-blue-200 dark:border-blue-800">
              <h1 className="text-4xl font-bold text-blue-900 dark:text-blue-100 mb-4">Guia de Automação de WhatsApp para Afiliados</h1>
              <p className="text-lg text-blue-800 dark:text-blue-200">Um guia completo, passo a passo, sobre como criar uma automação de WhatsApp para copiar anúncios de afiliados, substituir links e repostar em múltiplos grupos.</p>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Módulo A: Automação de Anúncios</CardTitle>
                  <CardDescription>Copiar, substituir e repostar</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Aprenda como configurar bots para ler anúncios de um grupo, substituir links por seus links de afiliado e repostar em múltiplos grupos gerenciados.</p>
                  <Button variant="outline" size="sm" onClick={() => setActiveSection("modulo-a")} className="w-full">
                    Saiba Mais <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Módulo B: Gerenciamento de Lotação</CardTitle>
                  <CardDescription>Gerenciar grupos e capacidade</CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Descubra como criar um sistema de redirecionamento inteligente que gerencia a lotação dos seus grupos e direciona novos membros automaticamente.</p>
                  <Button variant="outline" size="sm" onClick={() => setActiveSection("modulo-b")} className="w-full">
                    Saiba Mais <ChevronRight className="w-4 h-4 ml-2" />
                  </Button>
                </CardContent>
              </Card>
            </div>
          </div>
        );
      case "aviso":
        return (
          <Card className="border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-950">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-900 dark:text-red-100">
                <AlertCircle className="w-6 h-6" />
                Aviso Importante: Risco de Banimento
              </CardTitle>
            </CardHeader>
            <CardContent className="text-red-900 dark:text-red-100 space-y-4">
              <p>
                Este programa utiliza tecnologias que simulam o comportamento do WhatsApp Web ou APIs Não Oficiais para interagir com o WhatsApp.
              </p>
              <p className="font-semibold">
                O uso dessas ferramentas viola os Termos de Serviço do WhatsApp e acarreta um alto risco de banimento das contas de telefone utilizadas.
              </p>
              <p>
                A arquitetura proposta visa mitigar esse risco, separando as funções em números diferentes, mas não o elimina.
              </p>
              <p className="text-sm italic">
                Você está ciente e concorda com o risco de banimento ao utilizar soluções não oficiais para a automação?
              </p>
            </CardContent>
          </Card>
        );
      default:
        return (
          <div className="prose dark:prose-invert max-w-none">
            <Streamdown>{guideContent}</Streamdown>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {APP_LOGO && <img src={APP_LOGO} alt={APP_TITLE} className="w-8 h-8" />}
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">{APP_TITLE}</h1>
          </div>
          
          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8 grid md:grid-cols-4 gap-8">
        {/* Sidebar Navigation */}
        <aside className={`md:col-span-1 ${mobileMenuOpen ? "block" : "hidden md:block"}`}>
          <nav className="space-y-2 sticky top-24">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => {
                  setActiveSection(section.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                  activeSection === section.id
                    ? "bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-semibold"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
              >
                {section.label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="md:col-span-3">
          <div className="space-y-6">
            {activeSection !== "inicio" && (
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                {sections.find(s => s.id === activeSection)?.title}
              </h2>
            )}
            {getContentForSection()}
          </div>
        </main>
      </div>

      {/* Footer */}
      <footer className="bg-gray-100 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-16">
        <div className="max-w-7xl mx-auto px-4 py-8 text-center text-gray-600 dark:text-gray-400">
          <p>© 2025 Guia de Automação de WhatsApp para Afiliados. Todos os direitos reservados.</p>
          <p className="text-sm mt-2">Este guia é fornecido apenas para fins educacionais. Use por sua conta e risco.</p>
        </div>
      </footer>
    </div>
  );
}
