import pandas as pd
from sklearn.ensemble import IsolationForest
import os
from google.cloud import storage

def load_logs():
    """Load the logs for analysis"""
    return pd.read_csv("/logs/logs.csv")  # Pre-mounted logs

def detect_anomalies(df):
    """Run Isolation Forest on selected features"""
    features = df[['latency', 'status_code']]
    model = IsolationForest(contamination=0.01, random_state=42)
    df['anomaly'] = model.fit_predict(features)
    return df[df['anomaly'] == -1]

def upload_to_gcs(source_file, destination_blob):
    bucket_name = os.getenv("GCS_BUCKET")
    if not bucket_name:
        print("⚠️ GCS_BUCKET not set")
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
        upload_to_gcs(output_path, "anomalies/latest.csv")
    else:
        print("✅ No anomalies detected.")

if __name__ == "__main__":
    main()
