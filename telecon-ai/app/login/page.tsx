"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Mail, Lock, ChevronRight, Eye, EyeOff, AlertCircle } from "lucide-react";
import AnimatedGradientBackground from "@/components/ui/animated-gradient-background";
import { useTheme } from "@/components/ui/theme-provider";

const SETORES = [
  { id: "a", label: "Setor A", desc: "Refrigeração Doméstica" },
  { id: "b", label: "Setor B", desc: "Climatização" },
  { id: "c", label: "Setor C", desc: "Linha Branca" },
];

const CREDENTIALS = {
  email: "teste.email@gmail.com",
  password: "12345",
};

export default function LoginPage() {
  const router = useRouter();
  const { theme } = useTheme();

  const [setor, setSetor] = useState<string | null>(null);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<"setor" | "credentials">("setor");

  function handleSetorSelect(id: string) {
    setSetor(id);
    setTimeout(() => setStep("credentials"), 180);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    // Simula latência de autenticação
    await new Promise((r) => setTimeout(r, 1100));

    if (
      email.trim().toLowerCase() === CREDENTIALS.email &&
      password === CREDENTIALS.password
    ) {
      const setorInfo = SETORES.find((s) => s.id === setor);
      localStorage.setItem(
        "telecontrol_auth",
        JSON.stringify({
          email: email.trim().toLowerCase(),
          setor: setorInfo?.label ?? setor,
          setorDesc: setorInfo?.desc ?? "",
          timestamp: Date.now(),
        })
      );
      router.replace("/");
    } else {
      setLoading(false);
      setError("E-mail ou senha incorretos. Tente novamente.");
    }
  }

  return (
    <div className="relative flex items-center justify-center min-h-screen overflow-hidden bg-main">
      {/* Fundo animado idêntico à página principal */}
      <AnimatedGradientBackground
        Breathing
        animationSpeed={0.012}
        breathingRange={7}
        startingGap={140}
        topOffset={5}
        gradientColors={
          theme === "dark"
            ? [
                "#0f0f16",
                "#131328",
                "#181836",
                "#12122a",
                "#0d0d1e",
                "#0b0b16",
                "#0f0f16",
              ]
            : [
                "#fcfcfa",
                "#e8f0fe",
                "#ddd6fe",
                "#c7d2fe",
                "#bfdbfe",
                "#e0f2fe",
                "#f8fafc",
              ]
        }
        gradientStops={[25, 42, 55, 65, 75, 87, 100]}
      />

      {/* Card central */}
      <motion.div
        initial={{ opacity: 0, y: 24, scale: 0.97 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.55, ease: [0.16, 1, 0.3, 1] }}
        className="relative z-10 w-full max-w-sm mx-4"
      >
        {/* Badge topo */}
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.4 }}
          className="flex justify-center mb-6"
        >
          <div className="inline-flex items-center gap-2 border border-border rounded-full px-3 py-1 text-xs text-text-secondary bg-surface/80 backdrop-blur-sm">
            <Sparkles size={12} className="text-text-primary" />
            Telecontrol AI &middot; Acesso Restrito
          </div>
        </motion.div>

        {/* Card principal */}
        <div className="bg-surface/80 backdrop-blur-xl border border-border rounded-2xl shadow-2xl overflow-hidden">
          {/* Header do card */}
          <div className="px-7 pt-7 pb-5 border-b border-border">
            <div className="flex items-center gap-3 mb-1">
              <img
                src="/logo.svg"
                alt="Logo"
                className="logo-telecontrol w-7 h-7 opacity-80"
              />
              <h1 className="text-lg font-semibold tracking-tight text-text-primary">
                TELECONTROL AI
              </h1>
            </div>
            <p className="text-xs text-muted mt-1">
              {step === "setor"
                ? "Selecione seu setor para continuar"
                : `${SETORES.find((s) => s.id === setor)?.label} · ${SETORES.find((s) => s.id === setor)?.desc}`}
            </p>
          </div>

          {/* Conteúdo animado com troca de step */}
          <div className="px-7 py-6">
            <AnimatePresence mode="wait">
              {step === "setor" ? (
                /* ── STEP 1: Seleção de Setor ── */
                <motion.div
                  key="setor"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.25, ease: "easeOut" }}
                >
                  <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider mb-3">
                    Setor de atuação
                  </p>
                  <div className="space-y-2">
                    {SETORES.map((s, i) => (
                      <motion.button
                        key={s.id}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.07, duration: 0.3 }}
                        onClick={() => handleSetorSelect(s.id)}
                        className={`w-full flex items-center justify-between px-4 py-3 rounded-xl border text-left transition-all duration-200
                          ${
                            setor === s.id
                              ? "border-accent bg-accent text-main"
                              : "border-border bg-main/60 hover:border-accent/50 hover:bg-surface"
                          }`}
                      >
                        <div>
                          <p className="text-sm font-semibold">{s.label}</p>
                          <p className="text-xs opacity-60">{s.desc}</p>
                        </div>
                        <ChevronRight size={14} className="opacity-50" />
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              ) : (
                /* ── STEP 2: Credenciais ── */
                <motion.div
                  key="credentials"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ duration: 0.28, ease: "easeOut" }}
                >
                  <form onSubmit={handleSubmit} className="space-y-4">
                    {/* E-mail */}
                    <div>
                      <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">
                        E-mail
                      </label>
                      <div className="relative">
                        <Mail
                          size={14}
                          className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none"
                        />
                        <input
                          type="email"
                          autoComplete="email"
                          value={email}
                          onChange={(e) => {
                            setEmail(e.target.value);
                            setError(null);
                          }}
                          placeholder="seu@email.com"
                          required
                          className="w-full pl-9 pr-3.5 py-2.5 rounded-xl border border-border bg-main/60 text-sm text-text-primary placeholder:text-muted
                            focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/50
                            transition-all duration-200"
                        />
                      </div>
                    </div>

                    {/* Senha */}
                    <div>
                      <label className="block text-xs font-semibold text-text-secondary uppercase tracking-wider mb-1.5">
                        Senha
                      </label>
                      <div className="relative">
                        <Lock
                          size={14}
                          className="absolute left-3.5 top-1/2 -translate-y-1/2 text-muted pointer-events-none"
                        />
                        <input
                          type={showPassword ? "text" : "password"}
                          autoComplete="current-password"
                          value={password}
                          onChange={(e) => {
                            setPassword(e.target.value);
                            setError(null);
                          }}
                          placeholder="••••••••"
                          required
                          className="w-full pl-9 pr-10 py-2.5 rounded-xl border border-border bg-main/60 text-sm text-text-primary placeholder:text-muted
                            focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent/50
                            transition-all duration-200"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword((v) => !v)}
                          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-text-secondary transition-colors"
                        >
                          {showPassword ? <EyeOff size={14} /> : <Eye size={14} />}
                        </button>
                      </div>
                    </div>

                    {/* Erro */}
                    <AnimatePresence>
                      {error && (
                        <motion.div
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.2 }}
                          className="flex items-center gap-2 text-xs text-red-500 bg-red-500/10 border border-red-500/20 rounded-lg px-3 py-2"
                        >
                          <AlertCircle size={12} className="shrink-0" />
                          {error}
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {/* Botão entrar */}
                    <motion.button
                      type="submit"
                      disabled={loading}
                      whileTap={{ scale: 0.98 }}
                      className="w-full py-2.5 rounded-xl bg-accent text-main text-sm font-semibold
                        hover:bg-accent-hover disabled:opacity-60 disabled:cursor-not-allowed
                        transition-all duration-200 flex items-center justify-center gap-2"
                    >
                      {loading ? (
                        <>
                          <LoadingSpinner />
                          Autenticando...
                        </>
                      ) : (
                        <>
                          Entrar
                          <ChevronRight size={14} />
                        </>
                      )}
                    </motion.button>

                    {/* Voltar */}
                    <button
                      type="button"
                      onClick={() => {
                        setStep("setor");
                        setError(null);
                      }}
                      className="w-full text-xs text-muted hover:text-text-secondary transition-colors py-1"
                    >
                      ← Trocar setor
                    </button>
                  </form>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center text-xs text-muted mt-5"
        >
          Telecontrol AI &copy; {new Date().getFullYear()} &middot; Diagnóstico de Equipamentos
        </motion.p>
      </motion.div>
    </div>
  );
}

function LoadingSpinner() {
  return (
    <motion.span
      animate={{ rotate: 360 }}
      transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
      className="w-3.5 h-3.5 border-2 border-main/30 border-t-main rounded-full inline-block"
    />
  );
}
