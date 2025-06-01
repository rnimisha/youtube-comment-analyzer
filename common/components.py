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


def render_top_comments(result_df):
    col_pos, col_neg = st.columns(2)
    with col_pos:
        st.markdown("### 👍 Top 5 Positive Comments")
        top_positive = result_df[result_df["sentiment_label"] == "Positive"].head(5)
        for _, row in top_positive.iterrows():
            st.markdown(
                f"<div style='{COMMENT_CARD_STYLE}'>{row['comment']}</div>",
                unsafe_allow_html=True,
            )

    with col_neg:
        st.markdown("### 👎 Top 5 Negative Comments")
        top_negative = result_df[result_df["sentiment_label"] == "Negative"].head(5)
        for _, row in top_negative.iterrows():
            st.markdown(
                f"<div style='{COMMENT_CARD_STYLE}'>{row['comment']}</div>",
                unsafe_allow_html=True,
            )


def render_most_liked_comments(result_df):
    st.markdown("### 🔥 Most Liked Comments")
    top_liked = result_df.sort_values(by="like_count", ascending=False).head(5)
    for _, row in top_liked.iterrows():
        st.markdown(
            f"""
            <div style="display:flex; align-items:center; background-color:rgba(255,255,255,0.05); padding:1rem; border-radius:12px; margin-bottom:1rem;">
                <img src="{row['author_profile_image']}" style="border-radius:50%; width:50px; height:50px; margin-right:1rem;">
                <div>
                    <a href="{row['author_channel_url']}" target="_blank" style="color:#81c784; font-weight:bold;">{row['author_display_name']}</a><br>
                    <span style="font-size:0.9rem;">{row['comment']}</span><br>
                    <span style="font-size:0.8rem; color:#ccc;">👍 {row['like_count']} | Sentiment: {row['sentiment_label']}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_sentiment_distribution_chart(result_df):
    sentiment_by_channel = (
        result_df.groupby(["author_display_name", "sentiment_label"])
        .size()
        .unstack(fill_value=0)
    )
    top_channels = sentiment_by_channel.sum(axis=1).nlargest(5).index
    top_sentiment_data = sentiment_by_channel.loc[top_channels].reset_index()
    top_sentiment_data = top_sentiment_data.melt(
        id_vars="author_display_name", var_name="Sentiment", value_name="Count"
    )

    fig = px.bar(
        top_sentiment_data,
        x="Count",
        y="author_display_name",
        color="Sentiment",
        orientation="h",
        color_discrete_map={"Negative": "#f28b82", "Positive": "#81c784"},
        title="Sentiment Distribution by Top 5 Commenters",
        height=400,
    )

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Channel",
        xaxis_title="Number of Comments",
        legend_title_text="Sentiment",
    )

    st.plotly_chart(fig, use_container_width=True)


def render_avg_like_chart(result_df):
    avg_likes = result_df.groupby("sentiment_label")["like_count"].mean().reset_index()

    fig = px.bar(
        avg_likes,
        x="sentiment_label",
        y="like_count",
        color="sentiment_label",
        color_discrete_map={"Negative": "#f28b82", "Positive": "#81c784"},
        title="Average Like Count per Sentiment",
        text="like_count",
    )

    fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        yaxis_title="Channel",
        xaxis_title="Number of Comments",
        legend_title_text="Sentiment",
    )

    st.plotly_chart(fig, use_container_width=True)
