from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import pandas as pd
import requests
import re
from pytube import YouTube

def get_video_id(url):
    """
    Extracts the YouTube video ID from a given URL.
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['youtu.be']:
        # Shortened URL format, e.g. https://youtu.be/VIDEO_ID
        return parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        # Standard URL format, e.g. https://www.youtube.com/watch?v=VIDEO_ID
        qs = parse_qs(parsed_url.query)
        return qs.get("v", [None])[0]
    return None

def get_video_info(video_url):
    """
    Uses pytube to retrieve metadata about the video.
    Returns a dictionary with title, author, length, views, publish date, and description.
    """
    try:
        yt = YouTube(video_url)
        info = {
            "title": yt.title,
            "author": yt.author,
            "length (sec)": yt.length,
            "views": yt.views,
            "publish_date": yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else "N/A",
            "description": yt.description
        }
        return info
    except Exception as e:
        print("Error fetching video info:", e)
        return {}

def get_transcript(video_id):
    """
    Attempts to fetch the transcript for a given video ID.
    Returns the full transcript text or an empty string if not available.
    """
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([entry["text"] for entry in transcript_data])
        return transcript_text
    except Exception as e:
        print("Error fetching transcript:", e)
        return ""

def simple_summary(text, num_sentences=3):
    """
    Creates a very basic summary by extracting the first few sentences.
    """
    sentences = [sentence.strip() for sentence in text.split('.') if sentence.strip()]
    summary = '. '.join(sentences[:num_sentences])
    if summary:
        summary += '.'
    return summary

def extract_products(transcript_text):
    """
    Uses a simple regex to 'extract' product names from the transcript.
    Assumes that product names follow a pattern like 'ProductX'.
    """
    products = re.findall(r'\bProduct\w+\b', transcript_text)
    # If no products are found, fall back to a default list.
    return products if products else ["ProductA", "ProductB", "ProductC"]

def perform_fact_check(transcript_text):
    """
    Calls the Google Fact Check Tools API to perform fact checking on the transcript.
    """
    api_key = "YOUR_ACTUAL_API_KEY"  # Replace with your valid API key
    query = transcript_text[:200]  # Use a subset of the transcript as the query.
    url = f"https://factchecktools.googleapis.com/v1alpha1/claims:search?query={query}&key={api_key}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "claims" in data and len(data["claims"]) > 0:
                return "Verified"
            else:
                return "Not Verified"
        else:
            print("Fact Check API returned an error:", response.text)
            return "API Error"
    except Exception as e:
        print("Error calling Fact Check API:", e)
        return "Error"


def main():
    # URL of the YouTube video to test on
    video_url = "https://youtu.be/uLRuz82XNTM?si=XtxMbQyX5E3WrVmr"
    video_id = get_video_id(video_url)
    
    # Fetch and display video metadata using pytube
    video_info = get_video_info(video_url)
    if video_info:
        print("Video Information:")
        for key, value in video_info.items():
            print(f"{key.capitalize()}: {value}")
        print("\n")
    
    # Get the transcript from YouTube
    transcript = get_transcript(video_id)
    if transcript:
        print("Transcript successfully fetched from YouTube.")
    else:
        print("Transcript not available. Using dummy transcript for demo.")
        transcript = ("Dummy transcript mentioning ProductA and ProductB. "
                      "The facts in this video are verified and based on truth. "
                      "Sustainability is high for ProductA.")
    
    # Generate and display a summary of the transcript
    transcript_summary = simple_summary(transcript)
    print("\nTranscript Summary:")
    print(transcript_summary)
    
    # Extract product names from the transcript
    products = extract_products(transcript)
    
    # For demonstration, assign dummy cost and sustainability ratings.
    # In a real application, these could be obtained from databases or external APIs.
    product_details = {
        "ProductA": {"Cost": "$100", "Sustainability": "High"},
        "ProductB": {"Cost": "$150", "Sustainability": "Medium"},
        "ProductC": {"Cost": "$200", "Sustainability": "Low"}
    }
    
    # Perform fact-checking via the external API
    fact_check_result = perform_fact_check(transcript)
    
    # Build the comparison table data
    data = []
    for prod in products:
        details = product_details.get(prod, {"Cost": "N/A", "Sustainability": "N/A"})
        data.append({
            "Product": prod,
            "Cost": details["Cost"],
            "Sustainability": details["Sustainability"],
            "Fact Check": fact_check_result
        })
    
    df = pd.DataFrame(data)
    
    # Display the product comparison table
    print("\nProduct Comparison Table:")
    print(df)

if __name__ == "__main__":
    main()
