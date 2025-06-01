from common.downloader import download_youtube_comments
from common.sentiment_analyzer import predict_sentiments


def predict(url, limit=100):
    comments_df, replies_df, video_details = download_youtube_comments(url, limit)
    comment_pred_df = predict_sentiments(
        comments_df, "model/both_fine_tune_classifier_1.pt", "comment"
    )
    reply_pred_df = predict_sentiments(
        replies_df, "model/both_fine_tune_classifier_1.pt", "reply"
    )
    reply_pred_df.to_csv("data/reply.csv", index=False)
    comment_pred_df.to_csv("data/comment.csv", index=False)
    return comment_pred_df, video_details


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=l5Z1PBJLUss"
    print(predict(video_url, 1000))
