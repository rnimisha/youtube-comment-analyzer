import pandas as pd
import plotly.express as px
import streamlit as st

COMMENT_CARD_STYLE = """
    background-color: rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    font-size: 0.95rem;
    line-height: 1.5;
    color: #ffffff;
"""


def load_css():
    with open("style/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_video_details(video_details):
    st.markdown(
        f"""
        <div style="display:flex; flex-direction:column; align-items:center; margin-bottom:1rem;">
            <img src="{video_details.get('thumbnail_url', '')}" style="max-width:320px; border-radius:12px; margin-bottom:1rem;" />
            <h2 style="color:#fff; text-align:center;">{video_details.get('title', 'No Title')}</h2>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stat_cards(video_details, positive_count, negative_count):
    row2 = st.columns(4)

    data = [
        ("►", video_details.get("view_count", 0), "Views"),
        ("★", video_details.get("like_count", 0), "Likes"),
        ("✗", negative_count, "Negative"),
        ("✔", positive_count, "Positive"),
    ]

    for col, (icon, value, label) in zip(row2, data):
        col.markdown(
            f"""
            <div class='stat-card'>
                <div class='stat-icon'>{icon}</div>
                <div class='stat-value'>{value:,}</div>
                <div>{label}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sentiment_bar(positive_pct, negative_pct):
    st.markdown(
        f"""
        <div style="
            width: 100%; 
            background: #333; 
            border-radius: 12px; 
            overflow: hidden; 
            height: 20px; 
            margin: 20px 0;">
            <div style="
                width: {positive_pct}%; 
                background: #81c784; 
                height: 100%; 
                float: left;"
                title="Positive {positive_pct:.1f}%"></div>
            <div style="
                width: {negative_pct}%; 
                background: #f28b82; 
                height: 100%; 
                float: left;"
                title="Negative {negative_pct:.1f}%"></div>
        </div>
        <div style="display:flex; justify-content: space-between;">
            <div style="color:#81c784; font-weight:bold;">Positive: {positive_pct:.1f}%</div>
            <div style="color:#f28b82; font-weight:bold;">Negative: {negative_pct:.1f}%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
