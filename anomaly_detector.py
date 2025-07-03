import pandas as pd
from sklearn.ensemble import IsolationForest
import os, requests
from google.cloud import storage

def load_logs():
    """Load the logs for analysis"""
    return pd.read_csv("/logs/logs.csv")  # Mount or pre-load via volume

def detect_anomalies(df):
    """Run Isolation Forest on selected features"""
    features = df[['latency', 'status_code']]
    model = IsolationForest(contamination=0.01, random_state=42)
    df['anomaly'] = model.fit_predict(features)
    return df[df['anomaly'] == -1]

def send_slack_alert(anomalies):
    webhook_url = os.getenv("SLACK_WEBHOOK")
    if not webhook_url:
        print("⚠️ Slack webhook not set")
        return

    message = {
        "text": f"🚨 {len(anomalies)} anomalies detected!\nSample:\n{anomalies.head(3).to_json()}"
    }
    requests.post(webhook_url, json=message)

def upload_to_gcs(source_file, destination_blob):
    bucket_name = os.getenv("GCS_BUCKET")
    if not bucket_name:
        print("⚠️ GCS_BUCKET env var not set")
        return

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)
    blob.upload_from_filename(source_file)
    print(f"✅ Uploaded to gs://{bucket_name}/{destination_blob}")

def main():
    df = load_logs()
    anomalies = detect_anomalies(df)

    if not anomalies.empty:
        output_path = "/logs/anomalies.csv"
        anomalies.to_csv(output_path, index=False)
        send_slack_alert(anomalies)
        upload_to_gcs(output_path, "anomalies/latest.csv")
    else:
        print("✅ No anomalies detected.")

if __name__ == "__main__":
    main()
