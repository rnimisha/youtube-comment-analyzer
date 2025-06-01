import os

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_KEY = os.getenv("API_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)


def extract_video_id(url: str) -> str:
    return url.split("v=")[-1].split("&")[0]


def clean_text(text: str) -> str:
    return text.replace("\n", ";").replace("\t", "").strip()


def fetch_replies(parent_id: str):
    replies, authors, ids, parent_ids = [], [], [], []

    try:
        response = (
            youtube.comments()
            .list(part="snippet", parentId=parent_id, maxResults=100)
            .execute()
        )

        while response:
            for item in response.get("items", []):
                snippet = item["snippet"]
                replies.append(clean_text(snippet["textOriginal"]))
                authors.append(
                    snippet.get("authorChannelId", {}).get("value", "No entry")
                )
                ids.append(item["id"])
                parent_ids.append(parent_id)

            next_token = response.get("nextPageToken")
            if not next_token:
                break
            response = (
                youtube.comments()
                .list(
                    part="snippet",
                    parentId=parent_id,
                    maxResults=100,
                    pageToken=next_token,
                )
                .execute()
            )

    except Exception as e:
        print(f"Error fetching replies for {parent_id}: {e}")

    return replies, authors, ids, parent_ids


def fetch_comments(video_id: str, limit: int = 100):
    top_comments, top_authors, top_ids = [], [], []
    replies, reply_authors, reply_ids, parent_ids = [], [], [], []

    next_token = None
    count = 0

    while count < limit:
        try:
            response = (
                youtube.commentThreads()
                .list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=min(100, limit - count),
                    order="time",
                    pageToken=next_token,
                )
                .execute()
            )

            for item in response.get("items", []):
                if count >= limit:
                    break

                snippet = item["snippet"]["topLevelComment"]["snippet"]
                top_comments.append(clean_text(snippet["textOriginal"]))
                top_authors.append(
                    snippet.get("authorChannelId", {}).get("value", "No entry")
                )
                top_ids.append(item["id"])
                count += 1

                if item["snippet"].get("totalReplyCount", 0) > 0:
                    r, a, ids, pids = fetch_replies(item["id"])
                    replies.extend(r)
                    reply_authors.extend(a)
                    reply_ids.extend(ids)
                    parent_ids.extend(pids)

            next_token = response.get("nextPageToken")
            if not next_token:
                break

        except Exception as e:
            print(f"[!] Error fetching top-level comments: {e}")
            break

    return (
        top_comments,
        top_authors,
        top_ids,
        replies,
        reply_authors,
        reply_ids,
        parent_ids,
    )


def download_youtube_comments(url: str, limit: int = 100):
    video_id = extract_video_id(url)
    print(f"Fetching comments..........")

    (
        top_comments,
        top_authors,
        top_ids,
        replies,
        reply_authors,
        reply_ids,
        parent_ids,
    ) = fetch_comments(video_id, limit)

    print(f"{len(top_comments)} top-level comments fetched")
    print(f"{len(replies)} replies fetched")

    df_comments = pd.DataFrame(
        {
            "video_id": video_id,
            "comment_id": top_ids,
            "channel_id": top_authors,
            "comment": top_comments,
        }
    )

    df_replies = pd.DataFrame(
        {
            "video_id": video_id,
            "reply_id": reply_ids,
            "parent_comment_id": parent_ids,
            "channel_id": reply_authors,
            "reply": replies,
        }
    )

    return df_comments, df_replies


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=l5Z1PBJLUss"

    comments_df, replies_df = download_youtube_comments(video_url, 100)
    print(comments_df.head())
