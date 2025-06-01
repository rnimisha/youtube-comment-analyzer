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
    replies, authors, author_names, author_imgs, author_urls, likes, ids, parent_ids = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )

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
                authors.append(snippet.get("authorChannelId", {}).get("value", "NA"))
                author_names.append(snippet.get("authorDisplayName", "NA"))
                author_imgs.append(snippet.get("authorProfileImageUrl", "NA"))
                author_urls.append(snippet.get("authorChannelUrl", "NA"))
                likes.append(snippet.get("likeCount", 0))
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

    return (
        replies,
        authors,
        author_names,
        author_imgs,
        author_urls,
        likes,
        ids,
        parent_ids,
    )


def fetch_comments(video_id: str, limit: int = 100):
    (
        top_comments,
        top_authors,
        top_author_names,
        top_author_imgs,
        top_author_urls,
        top_likes,
        top_ids,
    ) = ([], [], [], [], [], [], [])
    (
        replies,
        reply_authors,
        reply_author_names,
        reply_author_imgs,
        reply_author_urls,
        reply_likes,
        reply_ids,
        parent_ids,
    ) = ([], [], [], [], [], [], [], [])

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
                    order="relevance",
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
                    snippet.get("authorChannelId", {}).get("value", "NA")
                )
                top_author_names.append(snippet.get("authorDisplayName", "NA"))
                top_author_imgs.append(snippet.get("authorProfileImageUrl", "NA"))
                top_author_urls.append(snippet.get("authorChannelUrl", "NA"))
                top_likes.append(snippet.get("likeCount", 0))
                top_ids.append(item["id"])
                count += 1

                if item["snippet"].get("totalReplyCount", 0) > 0:
                    r, a, an, ai, au, l, ids, pids = fetch_replies(item["id"])
                    replies.extend(r)
                    reply_authors.extend(a)
                    reply_author_names.extend(an)
                    reply_author_imgs.extend(ai)
                    reply_author_urls.extend(au)
                    reply_likes.extend(l)
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
        top_author_names,
        top_author_imgs,
        top_author_urls,
        top_likes,
        top_ids,
        replies,
        reply_authors,
        reply_author_names,
        reply_author_imgs,
        reply_author_urls,
        reply_likes,
        reply_ids,
        parent_ids,
    )


def download_video_details(video_id):
    response = youtube.videos().list(part="snippet,statistics", id=video_id).execute()
    item = response["items"][0]

    snippet = item["snippet"]
    stats = item["statistics"]

    return {
        "video_id": video_id,
        "title": snippet.get("title", "No Title"),
        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "view_count": int(stats.get("viewCount", 0)),
        "like_count": int(stats.get("likeCount", 0)),
        "comment_count": int(stats.get("commentCount", 0)),
    }


def download_youtube_comments(url: str, limit: int = 100):
    video_id = extract_video_id(url)
    print(f"Fetching comments..........")

    (
        top_comments,
        top_authors,
        top_author_names,
        top_author_imgs,
        top_author_urls,
        top_likes,
        top_ids,
        replies,
        reply_authors,
        reply_author_names,
        reply_author_imgs,
        reply_author_urls,
        reply_likes,
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
            "author_display_name": top_author_names,
            "author_profile_image": top_author_imgs,
            "author_channel_url": top_author_urls,
            "like_count": top_likes,
            "comment": top_comments,
        }
    )

    df_replies = pd.DataFrame(
        {
            "video_id": video_id,
            "reply_id": reply_ids,
            "parent_comment_id": parent_ids,
            "channel_id": reply_authors,
            "author_display_name": reply_author_names,
            "author_profile_image": reply_author_imgs,
            "author_channel_url": reply_author_urls,
            "like_count": reply_likes,
            "reply": replies,
        }
    )

    video_details = download_video_details(video_id)

    return df_comments, df_replies, video_details


if __name__ == "__main__":
    video_url = "https://www.youtube.com/watch?v=l5Z1PBJLUss"

    comments_df, replies_df, video_details = download_youtube_comments(video_url, 100)
    print(comments_df.head())
    print("-" * 15)
    print(replies_df.head())
    print("-" * 15)
    print(video_details)
