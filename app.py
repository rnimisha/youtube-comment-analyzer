import streamlit as st

from common.components import (
    load_css,
    render_avg_like_chart,
    render_most_liked_comments,
    render_sentiment_bar,
    render_sentiment_distribution_chart,
    render_stat_cards,
    render_top_comments,
    render_video_details,
)
from main import predict

st.set_page_config(page_title="Video Statistics", layout="wide", page_icon="🤔")

load_css()

st.title("Video Sentiment Analyzer")
st.markdown("Analyze and visualize YouTube video comment sentiments")

with st.form(key="input_form"):
    video_url = st.text_input(
        "YouTube Video URL", placeholder="https://www.youtube.com/watch?v=xxxxxx"
    )
    comment_count = st.number_input(
        "Number of Comments to Analyze",
        min_value=10,
        max_value=5000,
        value=100,
        step=10,
    )
    submitted = st.form_submit_button("🔍 Analyze")

if submitted:
    if not video_url.strip():
        st.error("Please enter a valid YouTube video URL.")
    else:
        with st.spinner("Fetching comments and analyzing sentiment..."):
            result_df, video_details = predict(video_url, comment_count)

        sentiment_counts = result_df["sentiment_label"].value_counts()
        total_comments = len(result_df)
        positive_count = sentiment_counts.get("Positive", 0)
        negative_count = sentiment_counts.get("Negative", 0)
        positive_pct = (positive_count / total_comments) * 100 if total_comments else 0
        negative_pct = (negative_count / total_comments) * 100 if total_comments else 0

        st.markdown("### Result")
        render_video_details(video_details)
        render_stat_cards(video_details, positive_count, negative_count)
        render_sentiment_bar(positive_pct, negative_pct)
