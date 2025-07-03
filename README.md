# AIOps-Project

# 🧠 GKE-Based AIOps Anomaly Detector with Canary Rollouts

This project implements a full-stack **AIOps pipeline** using:

- 🧪 **Isolation Forest** for anomaly detection
- 📈 **Real-time log injection via ConfigMap**
- ☁️ **GKE** for scalable deployment
- 🔁 **Argo Rollouts** for safe canary deployment
- 📦 **GCS integration** for anomaly report storage
- 🚀 **GitHub Actions** (optional) for GitOps automation

---

## 📌 Architecture Overview

[Log ConfigMap] --> [Pod (anomaly-detector)]
|
┌────────────────┴──────────────┐
| Reads /logs/input/logs.csv |
| Writes /logs/output/anomalies.csv
└────────────────┬──────────────┘
|
[Uploads to GCS]



---

## 📦 Components

| Component              | Status                  |
|------------------------|--------------------------|
| GKE Cluster            | ✅ Created               |
| Argo Rollout           | ✅ Canary Enabled        |
| Log Source             | ✅ Kubernetes ConfigMap  |
| GCS Bucket             | ✅ anomaly-detector-logs |
| Pod Output Volume      | ✅ emptyDir (writable)   |
| Model Logic            | ✅ Isolation Forest      |

---

## 🧠 Anomaly Detection Logic

Uses [Isolation Forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) on selected log features:

```python
features = df[['latency', 'status_code']]
model = IsolationForest(contamination=0.01)
anomalies = model.fit_predict(features)

If anomalies are found, they are:

Saved to /logs/output/anomalies.csv

Uploaded to gs://anomaly-detector-logs/anomalies/latest.csv   # GO TO GCS AND DOWNLOAD THE CSV FILE TO CHECK THE ANOMALIES.

```
### Deployment (Argo Rollouts)
The app is deployed using Argo Rollouts with the following strategy:

strategy:
  canary:
    steps:
    - setWeight: 50
    - pause: { duration: 30s }
    - setWeight: 100
# This ensures safe rollout for anomaly detection upgrades with real-time traffic.

### Logs Input (via ConfigMap)
You provide logs via a ConfigMap:

kubectl create configmap anomaly-logs --from-file=logs.csv -n dev
Mounts to /logs/input/logs.csv (read-only).

### Output Location
The container writes anomalies to:

/logs/output/anomalies.csv  # Stored in emptyDir
→ uploaded to GCS bucket
Make sure your ServiceAccount has correct IAM roles (Storage Object Admin).

### Verify Logs  # IT DISPLAYS THE ANOMALIDES FILE PUSHED TO GCS
View logs:

kubectl logs -f <pod-name> -n dev

🔐 IAM and Workload Identity
This project uses GKE Workload Identity to securely grant GCS write access:

Kubernetes SA: anomaly-detector-ksa

GCP SA: anomaly-gcs-access@<project>.iam.gserviceaccount.com

Bound via annotation + policy binding.

## TAKEAWAYS:
BUILT for production-aligned AIOps learning and dev environment simulation.



