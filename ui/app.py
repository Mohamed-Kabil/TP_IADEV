"""TP3 V1.1 : un avis, un CSV et deux graphiques via l'API /v1."""

import hashlib
import sys
from pathlib import Path

import httpx
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ui import client  # noqa: E402
from ui.donnees import charger_csv, exporter_csv, tranches_confiance  # noqa: E402

st.set_page_config(page_title="Avis clients · Analyse de sentiment", page_icon="💬", layout="wide")
st.title("Analyse de sentiment des avis")
st.markdown("Un avis ou un fichier : repérez les insatisfactions et les cas à faire vérifier.")


def afficher_lot(session: httpx.Client) -> None:
    fichier = st.file_uploader("Fichier CSV avec une colonne text", type="csv")
    st.caption("CSV UTF-8 séparé par des virgules. Les cellules text vides seront refusées par l’API.")
    if fichier is None:
        st.info("Déposez votre CSV pour analyser les avis et télécharger les résultats.")
        return
    contenu = fichier.getvalue()
    empreinte = hashlib.sha256(contenu).hexdigest()
    try:
        avis = charger_csv(contenu)
    except ValueError as exc:
        st.error(str(exc))
        return
    st.caption(f"{len(avis)} avis prêts à analyser.")
    if st.button("Analyser le fichier", key="analyser_lot"):
        with st.spinner("Analyse des avis par l’API…"):
            reponses = client.predire_lot(session, avis["text"].tolist())
        avis["verdict"] = [client.VERDICTS[r.label] if r.ok and r.label else "Refus ou erreur" for r in reponses]
        avis["confiance"] = [r.score for r in reponses]
        avis["message"] = [r.message for r in reponses]
        st.session_state["lot_resultat"] = (empreinte, avis, client.resumer(reponses))
    resultat = st.session_state.get("lot_resultat")
    if resultat is None or resultat[0] != empreinte:
        return
    _, tableau, resume = resultat
    st.dataframe(tableau, use_container_width=True, hide_index=True)
    st.write(resume)
    st.subheader("Répartition des verdicts")
    st.bar_chart(tableau["verdict"].value_counts().rename("Nombre"))
    st.subheader("Distribution de la confiance")
    st.bar_chart(tranches_confiance(tableau["confiance"]))
    abstentions = resume.get("INDETERMINE", 0)
    erreurs = resume.get("REFUS OU ERREUR", 0)
    st.caption(f"{abstentions} avis à vérifier par un humain ; {erreurs} refus ou erreurs.")
    st.caption("Le score 0,60 appartient à la deuxième tranche ; le score 1,00 est inclus. Les erreurs n’ont pas de score.")
    st.download_button(
        "Télécharger les résultats", exporter_csv(tableau),
        file_name="resultats.csv", mime="text/csv", key="telecharger_lot",
    )


try:
    with client.creer_session() as session:
        etat = client.sante(session)
        if etat.ok:
            st.caption(f"API prête : {etat.message}")
        else:
            st.error(etat.message)
        onglet_avis, onglet_lot = st.tabs(["Un avis", "Un fichier d'avis"])
        with onglet_avis:
            texte = st.text_area("Avis client", max_chars=2000, height=150)
            if st.button("Analyser", key="analyser_avis"):
                reponse = client.predire(session, texte)
                if reponse.ok and reponse.label and reponse.score is not None:
                    st.metric(client.VERDICTS[reponse.label], f"{reponse.score:.0%}")
                    st.caption("Score du modèle, sans garantie de justesse.")
                    if reponse.label == "INDETERMINE":
                        st.info("La confiance est sous le seuil d'abstention : un humain doit trancher.")
                elif reponse.message == client.REFUS:
                    st.warning(reponse.message)
                else:
                    st.error(reponse.message)
        with onglet_lot:
            afficher_lot(session)
except (httpx.InvalidURL, ValueError):
    st.error("Configuration API invalide : vérifiez API_URL dans le fichier .env local.")
