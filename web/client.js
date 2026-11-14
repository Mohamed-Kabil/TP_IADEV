/* Client /v1 partagé par la page et les tests Node, sans stockage des clés. */
const messages = {
  NON_AUTHENTIFIE: "Clé absente ou invalide. Vérifiez la clé client.",
  ACCES_REFUSE: "Cette clé ne dispose pas du rôle requis.",
  ENTREE_INVALIDE: "Texte refusé : saisissez de 1 à 2000 caractères, pas seulement des espaces.",
  MODELE_INDISPONIBLE: "Modèle indisponible. Réessayez lorsque l’API est prête.",
  ERREUR_INTERNE: "Erreur interne de l’API. Réessayez plus tard.",
};

export function creerClient(adresse, cle = "", fetchImpl = globalThis.fetch) {
  const url = new URL(adresse);
  if (!["http:", "https:"].includes(url.protocol) || url.username || url.password) {
    throw new Error("Adresse API invalide : utilisez http:// ou https:// sans identifiants.");
  }
  const base = url.href.replace(/\/$/, "");
  const key = cle.trim();
  async function requete(route, body) {
    try {
      const headers = { Accept: "application/json" };
      if (key) headers["X-API-Key"] = key;
      if (body !== undefined) headers["Content-Type"] = "application/json";
      const response = await fetchImpl(`${base}/v1/${route}`, {
        method: body === undefined ? "GET" : "POST",
        headers,
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
        signal: AbortSignal.timeout(10000),
      });
      let data;
      try { data = await response.json(); }
      catch { return { ok: false, message: "Réponse illisible de l’API." }; }
      if (!response.ok) {
        const code = data?.erreur?.code || "ERREUR_HTTP";
        return { ok: false, code, status: response.status,
          message: messages[code] || "Requête refusée par l’API.",
          champs: data?.erreur?.champs || [] };
      }
      return { ok: true, data };
    } catch {
      return { ok: false, code: "API_INJOIGNABLE",
        message: "API injoignable : vérifiez son adresse, son démarrage et l’origine CORS de cette page." };
    }
  }
  return {
    sante: () => requete("health"),
    async predire(text) {
      if (!key) return { ok: false, code: "NON_AUTHENTIFIE", message: messages.NON_AUTHENTIFIE };
      const result = await requete("predict", { text });
      if (!result.ok) return result;
      const { label, score } = result.data ?? {};
      if (!["POSITIVE", "NEGATIVE", "INDETERMINE"].includes(label)
          || typeof score !== "number" || !Number.isFinite(score) || score < 0 || score > 1) {
        return { ok: false, message: "Réponse inattendue de l’API." };
      }
      return { ...result, message: label === "INDETERMINE"
        ? "Je ne sais pas : à faire vérifier par un humain."
        : label === "POSITIVE" ? "Avis positif" : "Avis négatif" };
    },
  };
}
