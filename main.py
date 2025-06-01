from common.downloader import download_youtube_comments
from common.sentiment_analyzer import predict_sentiments


def predict(url, limit=100):
    comments_df, replies_df, video_details = download_youtube_comments(url, limit)
    result_df = predict_sentiments(
        comments_df, "model/both_fine_tune_classifier_1.pt", "comment"
    )
    return result_df, video_details


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=l5Z1PBJLUss"
    print(predict(video_url, 100))
