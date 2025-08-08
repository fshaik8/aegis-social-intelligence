import boto3
import json
import random
import time
import uuid
from datetime import datetime, timezone

from schema import SocialPost

KINESIS_STREAM_NAME = "aegis-social-events"
AWS_REGION = "us-east-2" 

class EventGenerator:
    """Generates and sends synthetic social media events to Kinesis."""

    def __init__(self, stream_name: str, region: str):
        """
        Initializes the generator.
        :param stream_name: The name of the Kinesis stream.
        :param region: The AWS region of the stream.
        """
        print(f"Initializing event generator for stream '{stream_name}' in region '{region}'...")
        # --- FIX: Corrected the typo. `stream_name` is now correctly assigned to the object instance.
        self.stream_name = stream_name
        self.kinesis_client = boto3.client('kinesis', region_name=region)
        print("AWS Kinesis client initialized successfully.")

    def _create_random_post(self) -> SocialPost:
        """Creates a single, randomized social media post."""
        
        templates = [
            ("Just tried the new @AegisSocial feature, it's amazing! #aegis #innovation", "positive"),
            ("My @AegisSocial app is not working after the update. So frustrating! #fail #bug", "negative"),
            ("Anyone else having issues with @AegisSocial login? Seems to be down.", "negative"),
            ("Thinking about the services offered by @AegisSocial.", "neutral"),
            ("Wow, the customer service from @AegisSocial was so quick and helpful!", "positive"),
            ("This is the worst app I've ever used. @AegisSocial is a complete disaster.", "negative_crisis"),
            ("Security alert! I think my @AegisSocial account data has been leaked! This is a scandal!", "negative_crisis"),
            ("Just read a great article about @AegisSocial's new features. #tech", "positive"),
        ]
        
        content_template, sentiment = random.choice(templates)
        
        if sentiment == "negative_crisis" or random.random() < 0.05:
             content = random.choice([
                "URGENT: @AegisSocial has a massive security flaw! My personal data was exposed! #DataBreach #PrivacyFail",
                "AVOID @AegisSocial! They charged my card twice and their support is a ghost town. This company is a scam. #ScamAlert",
                "The latest @AegisSocial update wiped all my saved data. Years of planning gone. Unacceptable! #DataLoss"
             ])
        else:
            content = content_template

        return SocialPost(
            post_id=str(uuid.uuid4()),
            platform=random.choice(["X-Twitter", "Reddit"]),
            content=content,
            author_id=f"user_{random.randint(1000, 9999)}",
            timestamp_utc=datetime.now(timezone.utc).isoformat()
        )

    def send_post_to_kinesis(self, post: SocialPost):
        """
        Sends a single post to the Kinesis stream.
        :param post: The SocialPost object to send.
        """
        try:
            partition_key = post.platform

            response = self.kinesis_client.put_record(
                StreamName=self.stream_name,
                Data=json.dumps(post.to_dict()).encode('utf-8'),
                PartitionKey=partition_key
            )
            print(f"Successfully sent post {post.post_id} to Kinesis. ShardId: {response['ShardId']}")
        except Exception as e:
            print(f"Error sending post to Kinesis: {e}")

    def run(self, num_posts: int, interval_seconds: float):
        """
        Runs the generator to send a specified number of posts.
        :param num_posts: The total number of posts to send.
        :param interval_seconds: The time to wait between sending each post.
        """
        print(f"\nStarting to send {num_posts} posts to Kinesis every {interval_seconds} seconds...")
        print("Press Ctrl+C to stop early.")
        for i in range(num_posts):
            post = self._create_random_post()
            self.send_post_to_kinesis(post)
            time.sleep(interval_seconds)
        print(f"\nFinished sending {num_posts} posts.")

if __name__ == "__main__":
    session = boto3.Session()
    credentials = session.get_credentials()
    if credentials is None or credentials.access_key is None:
        print("\nFATAL ERROR: AWS credentials not found.")
        print("Please run 'aws configure' in your terminal and set up your IAM user's keys.")
    else:
        generator = EventGenerator(stream_name=KINESIS_STREAM_NAME, region=AWS_REGION)
        generator.run(num_posts=100, interval_seconds=2)