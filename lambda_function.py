import json
import base64
import boto3
import os

comprehend_client = boto3.client('comprehend')

def lambda_handler(event, context):
    """
    The main entry point for the AWS Lambda function.
    This function is called by AWS whenever new records arrive in the Kinesis stream.
    
    :param event: The event data passed by the Kinesis trigger. Contains the records.
    :param context: The runtime information provided by Lambda.
    """
    print(f"Received event with {len(event['Records'])} records.")
    
    # Process each record that came from the Kinesis stream.
    for record in event['Records']:
        try:
            # 1. Decode the data from Kinesis.
            # Kinesis data is sent as a Base64 encoded string. We must decode it first.
            payload_decoded = base64.b64decode(record['kinesis']['data']).decode('utf-8')
            social_post = json.loads(payload_decoded)
            
            print(f"Processing Post ID: {social_post['post_id']}")
            
            # 2. Extract the content to be analyzed.
            content_to_analyze = social_post['content']
            
            # Ensure the content is not empty and is within Comprehend's size limits.
            if not content_to_analyze or len(content_to_analyze.encode('utf-8')) > 5000:
                print(f"Skipping post {social_post['post_id']} due to empty or oversized content.")
                continue

            # 3. Call Amazon Comprehend for Sentiment Analysis.
            sentiment_response = comprehend_client.detect_sentiment(
                Text=content_to_analyze,
                LanguageCode='en' # 'en' for English
            )
            sentiment = sentiment_response['Sentiment']
            sentiment_score = sentiment_response['SentimentScore']
            
            # 4. Call Amazon Comprehend for Key Phrase Extraction.
            key_phrases_response = comprehend_client.detect_key_phrases(
                Text=content_to_analyze,
                LanguageCode='en'
            )
            key_phrases = [phrase['Text'] for phrase in key_phrases_response['KeyPhrases']]

            # 5. Create the "enriched" data object with the AI analysis results.
            enriched_post = {
                **social_post, # Include all original post data
                "analysis_results": {
                    "sentiment": sentiment,
                    "sentiment_score": sentiment_score,
                    "key_phrases": key_phrases
                }
            }
            
            # 6. Log the final result.
            # In a full production system, this is where we would save the data to S3,
            # run anomaly detection, and send SNS alerts. For now, we print to the log.
            print("--- ENRICHED POST ---")
            print(json.dumps(enriched_post, indent=2))
            
        except Exception as e:
            # Log any errors encountered during processing a single record.
            print(f"ERROR processing a record: {e}")
            # We continue to the next record rather than failing the whole batch.
            continue
            
    # Return a success message to AWS.
    return {
        'statusCode': 200,
        'body': json.dumps(f"Successfully processed {len(event['Records'])} records.")
    }