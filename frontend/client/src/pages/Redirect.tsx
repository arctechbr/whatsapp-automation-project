import { useEffect, useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Loader2, AlertCircle, CheckCircle } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Redirect() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [redirectUrl, setRedirectUrl] = useState<string | null>(null);
  const [groupName, setGroupName] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchRedirectUrl = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/redirect`);
        
        if (response.ok) {
          const data = await response.json();
          setRedirectUrl(data.redirect_url);
          setGroupName(data.group_name);
          setMessage(data.message);
          setStatus("success");
          
          // Redirecionar após 2 segundos
          setTimeout(() => {
            window.location.href = data.redirect_url;
          }, 2000);
        } else {
          setStatus("error");
          setMessage("Não foi possível encontrar um grupo disponível");
        }
      } catch (error) {
        setStatus("error");
        setMessage(error instanceof Error ? error.message : "Erro ao redirecionar");
      }
    };

    fetchRedirectUrl();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-950 dark:to-indigo-950 flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="pt-8 text-center space-y-6">
          {status === "loading" && (
            <>
              <Loader2 className="w-12 h-12 animate-spin mx-auto text-blue-600 dark:text-blue-400" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Buscando grupo disponível...
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  Por favor, aguarde enquanto procuramos o melhor grupo para você.
                </p>
              </div>
            </>
          )}

          {status === "success" && (
            <>
              <CheckCircle className="w-12 h-12 text-green-600 dark:text-green-400 mx-auto" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  {message}
                </h2>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Você será redirecionado para o grupo <strong>{groupName}</strong> em alguns segundos...
                </p>
                <p className="text-sm text-gray-500 dark:text-gray-500">
                  Se não for redirecionado automaticamente,{" "}
                  <a
                    href={redirectUrl || "#"}
                    className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
                  >
                    clique aqui
                  </a>
                </p>
              </div>
            </>
          )}

          {status === "error" && (
            <>
              <AlertCircle className="w-12 h-12 text-red-600 dark:text-red-400 mx-auto" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Ops! Algo deu errado
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                  {message}
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
