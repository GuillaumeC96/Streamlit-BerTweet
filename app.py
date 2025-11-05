#!/usr/bin/env python3
"""
Interface Streamlit pour l'API de Classification de Sentiment Twitter

Fonctionnalités:
- Saisie d'un tweet
- Appel de l'API déployée sur AWS
- Affichage de la prédiction
- Validation utilisateur
- Logging des erreurs vers AWS CloudWatch
"""

import streamlit as st
import requests
import json
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import os

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000")
AWS_REGION = os.getenv("AWS_REGION", "eu-west-1")
CLOUDWATCH_LOG_GROUP = "/twitter-sentiment-api/predictions"
CLOUDWATCH_LOG_STREAM = f"streamlit-{datetime.now().strftime('%Y-%m-%d')}"

# Configuration de la page
st.set_page_config(
    page_title="Twitter Sentiment Analysis",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialiser le client CloudWatch
try:
    cloudwatch_logs = boto3.client('logs', region_name=AWS_REGION)
    CLOUDWATCH_ENABLED = True
except Exception as e:
    st.warning(f"⚠️ CloudWatch non configuré: {e}")
    CLOUDWATCH_ENABLED = False


def log_to_cloudwatch(log_data):
    """Envoie des logs vers AWS CloudWatch"""
    if not CLOUDWATCH_ENABLED:
        return False

    try:
        # Créer le log group s'il n'existe pas
        try:
            cloudwatch_logs.create_log_group(logGroupName=CLOUDWATCH_LOG_GROUP)
        except cloudwatch_logs.exceptions.ResourceAlreadyExistsException:
            pass

        # Créer le log stream s'il n'existe pas
        try:
            cloudwatch_logs.create_log_stream(
                logGroupName=CLOUDWATCH_LOG_GROUP,
                logStreamName=CLOUDWATCH_LOG_STREAM
            )
        except cloudwatch_logs.exceptions.ResourceAlreadyExistsException:
            pass

        # Envoyer le log
        cloudwatch_logs.put_log_events(
            logGroupName=CLOUDWATCH_LOG_GROUP,
            logStreamName=CLOUDWATCH_LOG_STREAM,
            logEvents=[
                {
                    'timestamp': int(datetime.now().timestamp() * 1000),
                    'message': json.dumps(log_data)
                }
            ]
        )
        return True
    except ClientError as e:
        st.error(f"Erreur CloudWatch: {e}")
        return False


def send_sns_alert(message):
    """Envoie une alerte via AWS SNS"""
    try:
        sns = boto3.client('sns', region_name=AWS_REGION)
        topic_arn = os.getenv("SNS_TOPIC_ARN")

        if not topic_arn:
            st.warning("⚠️ SNS_TOPIC_ARN non configuré")
            return False

        sns.publish(
            TopicArn=topic_arn,
            Subject="🚨 Alerte: Mauvaise Prédiction API Twitter Sentiment",
            Message=message
        )
        return True
    except ClientError as e:
        st.error(f"Erreur SNS: {e}")
        return False


def call_api(text):
    """Appelle l'API de prédiction"""
    try:
        response = requests.post(
            f"{API_URL}/predict",
            json={"text": text},
            timeout=30
        )
        response.raise_for_status()
        return response.json(), None
    except requests.exceptions.RequestException as e:
        return None, str(e)


# Interface Streamlit
st.title("🐦 Twitter Sentiment Analysis")
st.markdown("---")

# Sidebar avec configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    api_url_input = st.text_input(
        "URL de l'API",
        value=API_URL,
        help="URL de l'API déployée sur AWS"
    )

    if api_url_input != API_URL:
        API_URL = api_url_input
        st.success("✅ URL mise à jour")

    st.markdown("---")

    st.header("📊 Informations")

    # Test de connexion API
    if st.button("🔍 Tester la connexion API"):
        with st.spinner("Test en cours..."):
            try:
                response = requests.get(f"{API_URL}/health", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    st.success("✅ API accessible")
                    st.json(data)
                else:
                    st.error(f"❌ Erreur: {response.status_code}")
            except Exception as e:
                st.error(f"❌ Connexion échouée: {e}")

    st.markdown("---")

    st.header("ℹ️ À propos")
    st.markdown("""
    Cette application permet de:
    - Analyser le sentiment de tweets
    - Valider les prédictions
    - Logger les erreurs vers CloudWatch
    - Déclencher des alertes SNS

    **Modèle:** BERTweet (ONNX)
    **F1 Score:** 0.813
    **Seuil:** 0.35
    """)

# Zone principale
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📝 Saisir un Tweet")

    # Zone de saisie
    tweet_input = st.text_area(
        "Entrez le texte du tweet à analyser:",
        height=100,
        placeholder="Ex: This product is amazing! I love it!",
        help="Le tweet sera analysé par l'API pour déterminer son sentiment"
    )

    # Bouton d'analyse
    analyze_button = st.button("🔍 Analyser", type="primary", use_container_width=True)

    # Exemples rapides
    st.markdown("**📌 Exemples rapides:**")
    col_ex1, col_ex2, col_ex3 = st.columns(3)

    with col_ex1:
        if st.button("😊 Positif"):
            tweet_input = "This is absolutely amazing! I love it so much!"
            st.rerun()

    with col_ex2:
        if st.button("😠 Négatif"):
            tweet_input = "This is terrible! Worst experience ever!"
            st.rerun()

    with col_ex3:
        if st.button("😐 Neutre"):
            tweet_input = "It's okay I guess, nothing special"
            st.rerun()

with col2:
    st.header("📊 Statistiques")

    # Initialiser les stats dans la session
    if 'total_predictions' not in st.session_state:
        st.session_state.total_predictions = 0
    if 'correct_predictions' not in st.session_state:
        st.session_state.correct_predictions = 0
    if 'incorrect_predictions' not in st.session_state:
        st.session_state.incorrect_predictions = 0

    # Afficher les métriques
    st.metric("Total", st.session_state.total_predictions)
    st.metric("✅ Correctes", st.session_state.correct_predictions)
    st.metric("❌ Incorrectes", st.session_state.incorrect_predictions)

    if st.session_state.total_predictions > 0:
        accuracy = (st.session_state.correct_predictions /
                    st.session_state.total_predictions) * 100
        st.metric("Précision", f"{accuracy:.1f}%")

# Analyse du tweet
if analyze_button and tweet_input.strip():
    st.markdown("---")
    st.header("🎯 Résultats de l'Analyse")

    with st.spinner("🔄 Analyse en cours..."):
        # Appeler l'API
        prediction, error = call_api(tweet_input)

        if error:
            st.error(f"❌ Erreur lors de l'appel API: {error}")
        else:
            # Afficher les résultats
            col_res1, col_res2, col_res3 = st.columns(3)

            with col_res1:
                sentiment = prediction['sentiment']
                sentiment_emoji = "😊" if sentiment == "Positif" else "😠"

                st.markdown(f"### {sentiment_emoji} Sentiment")
                st.markdown(f"**{sentiment}**")
                st.caption(f"Confiance: {prediction['confidence']:.1%}")

            with col_res2:
                st.markdown("### 📊 Probabilités")
                st.progress(prediction['probability_negative'],
                           text=f"🔴 Négatif: {prediction['probability_negative']:.1%}")
                st.progress(prediction['probability_positive'],
                           text=f"🟢 Positif: {prediction['probability_positive']:.1%}")

            with col_res3:
                st.markdown("### ⏱️ Performance")
                st.metric("Inférence", f"{prediction['inference_time_ms']:.1f} ms")
                st.metric("Total", f"{prediction['total_time_ms']:.1f} ms")

            # Afficher le JSON complet dans un expander
            with st.expander("📄 Voir la réponse complète de l'API"):
                st.json(prediction)

            # Section de validation
            st.markdown("---")
            st.header("✅ Validation")

            st.markdown(f"**Tweet analysé:** {tweet_input}")
            st.markdown(f"**Prédiction:** {sentiment} ({prediction['confidence']:.1%} de confiance)")

            col_val1, col_val2, col_val3 = st.columns(3)

            with col_val1:
                if st.button("✅ Prédiction Correcte", type="primary", use_container_width=True):
                    st.session_state.total_predictions += 1
                    st.session_state.correct_predictions += 1

                    # Logger dans CloudWatch
                    log_data = {
                        'timestamp': datetime.now().isoformat(),
                        'tweet': tweet_input,
                        'prediction': sentiment,
                        'confidence': prediction['confidence'],
                        'validation': 'correct',
                        'probability_negative': prediction['probability_negative'],
                        'probability_positive': prediction['probability_positive']
                    }

                    if log_to_cloudwatch(log_data):
                        st.success("✅ Validation enregistrée (CloudWatch)")
                    else:
                        st.success("✅ Validation enregistrée (local)")

                    st.rerun()

            with col_val2:
                if st.button("❌ Prédiction Incorrecte", type="secondary", use_container_width=True):
                    st.session_state.total_predictions += 1
                    st.session_state.incorrect_predictions += 1

                    # Logger l'erreur dans CloudWatch
                    error_data = {
                        'timestamp': datetime.now().isoformat(),
                        'tweet': tweet_input,
                        'predicted_sentiment': sentiment,
                        'confidence': prediction['confidence'],
                        'validation': 'incorrect',
                        'probability_negative': prediction['probability_negative'],
                        'probability_positive': prediction['probability_positive'],
                        'error_type': 'wrong_prediction'
                    }

                    if log_to_cloudwatch(error_data):
                        st.warning("⚠️ Erreur loggée dans CloudWatch")

                        # Envoyer une alerte SNS si nécessaire
                        if st.session_state.incorrect_predictions >= 3:
                            alert_message = f"""
🚨 ALERTE: Mauvaise Prédiction Détectée

Tweet: {tweet_input}
Prédiction: {sentiment}
Confiance: {prediction['confidence']:.1%}
Probabilité Négatif: {prediction['probability_negative']:.1%}

Total d'erreurs: {st.session_state.incorrect_predictions}
Précision actuelle: {(st.session_state.correct_predictions / st.session_state.total_predictions) * 100:.1f}%

Timestamp: {datetime.now().isoformat()}
"""
                            if send_sns_alert(alert_message):
                                st.error("🚨 Alerte SNS envoyée!")

                    st.error("❌ Erreur enregistrée")
                    st.rerun()

            with col_val3:
                if st.button("↩️ Ignorer", use_container_width=True):
                    st.info("Tweet ignoré")

elif analyze_button:
    st.warning("⚠️ Veuillez saisir un tweet à analyser")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🐦 Twitter Sentiment Analysis API | Powered by BERTweet (ONNX) | FastAPI + Streamlit</p>
    <p><small>Déployé sur AWS EC2 | Monitoring via CloudWatch | Alertes via SNS</small></p>
</div>
""", unsafe_allow_html=True)
