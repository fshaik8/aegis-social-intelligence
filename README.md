# Aegis Social: A Real-Time Social Intelligence Platform

**Aegis Social** is a complete, serverless, event-driven AI pipeline built on Amazon Web Services (AWS). It is designed to ingest and analyze a real-time stream of social media data, using cloud-native AI to extract actionable intelligence like sentiment and key phrases in under 100 milliseconds per event.

This project serves as a portfolio piece demonstrating a professional, production-grade architecture for real-time AI processing, security, and cloud deployment.

---

## Key Features

*   **Serverless & Event-Driven:** Built entirely on scalable, serverless AWS services (`Kinesis`, `Lambda`). The architecture is event-driven, with the AI processing pipeline triggering automatically on new data.
*   **Real-Time AI Enrichment:** Uses **Amazon Comprehend** to perform high-speed sentiment analysis and key phrase extraction on incoming social media posts.
*   **High-Performance Processing:** The entire end-to-end enrichment pipeline, from data ingestion to AI analysis, completes in **under 100 milliseconds** per event.
*   **Testable & Robust:** Includes a synthetic data generator (`event_generator.py`) that simulates a live social media feed, allowing for repeatable, end-to-end testing of the entire cloud pipeline.
*   **Secure by Design:** Follows AWS security best practices, using a least-privilege **IAM Role** to ensure the processing function only has the exact permissions it needs.

## Architecture Overview

The project follows a classic and powerful real-time pipeline architecture:

1.  **Event Generation:** The `event_generator.py` script acts as a data producer, simulating social media posts and sending them to a Kinesis Data Stream.
2.  **Real-Time Ingestion:** An **Amazon Kinesis Data Stream** (`aegis-social-events`) serves as the high-throughput, real-time "conveyor belt" for incoming data.
3.  **Serverless Processing:** An **AWS Lambda** function (`aegis-social-processor`) is configured with a Kinesis trigger. It automatically executes for every new batch of records that arrives on the stream.
4.  **AI Analysis:** The Lambda function calls **Amazon Comprehend** to analyze the text content of each post, extracting sentiment and key phrases.
5.  **Logging & Monitoring:** The enriched data and any processing errors are logged to **Amazon CloudWatch**, providing full visibility into the pipeline's operation.

## How to Run This Project

### Prerequisites
1.  An **AWS Account** with the Free Tier.
2.  **AWS CLI** installed and configured with the credentials of an IAM user.
3.  **Python 3.10+** and the **Boto3** library (`pip install boto3`).

### Setup Instructions

1.  **Create the IAM Role:**
    *   In the AWS IAM Console, create a new role for a Lambda service.
    *   Attach the following two AWS-managed policies: `AWSLambdaKinesisExecutionRole` and `ComprehendReadOnly`.
    *   Name the role `aegis-social-lambda-role`.

2.  **Create the Kinesis Data Stream:**
    *   In the AWS Kinesis Console, create a new data stream.
    *   Name it `aegis-social-events`.
    *   Set the capacity to **1 Provisioned Shard**.

3.  **Create and Deploy the Lambda Function:**
    *   In the AWS Lambda Console, create a new function named `aegis-social-processor`.
    *   Choose the **Python 3.12** runtime.
    *   Under permissions, choose "Use an existing role" and select the `aegis-social-lambda-role` you created.
    *   Copy the code from `lambda_function.py` into the inline code editor and click **Deploy**.
    *   Add a **Trigger** to the function, selecting the `aegis-social-events` Kinesis stream.

### Running the Demo

1.  **Start the Data Stream:**
    *   In your local terminal, run the event generator script. This will start sending data to your Kinesis stream in the cloud.
    ```bash
    python event_generator.py
    ```

2.  **View the Results:**
    *   Navigate to your `aegis-social-processor` Lambda function in the AWS Console.
    *   Go to the **Monitor** tab and click on **View CloudWatch logs**.
    *   Open the latest log stream to see the real-time, AI-enriched JSON output for each post processed.
    *   


## Example Output

When the pipeline runs, the `aegis-social-processor` AWS Lambda function outputs a structured, AI-enriched JSON object for each social media post to Amazon CloudWatch. This object contains the original post data along with the analysis performed by Amazon Comprehend.

Here is a complete, real example from the project's logs for a post that was correctly identified as a high-priority, negative event requiring immediate attention:

```json
{
  "post_id": "4a6ed877-4a9a-47df-a7c0-c01dc3bc99bd",
  "platform": "Reddit",
  "content": "URGENT: @AegisSocial has a massive security flaw! My personal data was exposed! #DataBreach #PrivacyFail",
  "author_id": "user_4031",
  "timestamp_utc": "2025-08-08T07:51:53.593078+00:00",
  "analysis_results": {
    "sentiment": "NEGATIVE",
    "sentiment_score": {
      "Positive": 0.0019970962312072515,
      "Negative": 0.9072232246398926,
      "Neutral": 0.08599211275577545,
      "Mixed": 0.004787519108504057
    },
    "key_phrases": [
      "URGENT",
      "@AegisSocial",
      "a massive security flaw",
      "My personal data"
    ]
  }
}
```
