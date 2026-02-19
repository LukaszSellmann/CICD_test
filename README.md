# Demo Lambda API — CI/CD with ArgoCD

FastAPI app deployed on EKS via ArgoCD. Exposes a POST endpoint that triggers an AWS Lambda echo function.

## Architecture

```
Developer pushes to GitHub (app/**)
    ↓
GitHub Actions: build Docker image → push to Docker Hub (lukaszsel/demo-lambda-api:latest)
    ↓
ArgoCD detects git change → syncs k8s/ to EKS cluster
    ↓
FastAPI pod (demo-api namespace) → AWS Lambda (demo-echo-lambda) via Pod Identity
    ↓
https://demo-api.zdupy.eu/invoke
```

## Repo Structure

```
demo-lambda-api/
├── app/
│   ├── main.py               # FastAPI app (GET /health, POST /invoke)
│   ├── requirements.txt
│   └── Dockerfile
├── k8s/
│   ├── deployment.yaml       # Namespace, ServiceAccount, Deployment
│   ├── service.yaml          # ClusterIP service
│   └── ingress.yaml          # TLS ingress (cert-manager + external-dns)
├── lambda/
│   ├── handler.py            # Echo Lambda function
│   └── main.tf               # Terraform to deploy Lambda + IAM role
└── .github/workflows/
    └── ci.yaml               # Build + push to Docker Hub
```

## Deployment Steps

### 1. GitHub repo setup

- Create private GitHub repo
- Push this directory contents to `main` branch
- Add GitHub Secrets:
  - `DOCKERHUB_USERNAME` — Docker Hub username
  - `DOCKERHUB_TOKEN` — Docker Hub access token (Account Settings → Security)
- Enable workflow write permissions: Settings → Actions → General → Workflow permissions → Read and write

### 2. Deploy Lambda function

```bash
cd demo-lambda-api/lambda
terraform init
terraform apply
```

### 3. Apply Pod Identity IAM role (ClusterAddons)

Adds `demo-api.tf` to ClusterAddons — grants the pod permission to call Lambda without credentials.

```bash
cd ClusterAddons
terraform apply
```

### 4. Register private GitHub repo in ArgoCD

```bash
argocd repo add https://github.com/LukaszSellmann/CICD_test.git \
  --username LukaszSellmann \
  --password YOUR_GITHUB_PAT \
  --grpc-web
```

### 5. Deploy ArgoCD Application

```bash
kubectl apply -f ArgoCD-Apps/demo-apps/demo-lambda-api.yaml
```

ArgoCD will sync the `k8s/` directory and deploy the app automatically.

### 6. Verify deployment

```bash
kubectl get pods -n demo-api
kubectl get ingress -n demo-api
kubectl get certificates -n demo-api
```

## Testing

```bash
# Health check
curl https://demo-api.zdupy.eu/health

# Invoke Lambda
curl -X POST https://demo-api.zdupy.eu/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "hello from demo"}'
```

Expected response:
```json
{
  "lambda_response": {
    "statusCode": 200,
    "echo": "hello from demo",
    "source": "demo-echo-lambda"
  }
}
```

## CI/CD Flow

1. Push changes to `app/**` → GitHub Actions triggers automatically
2. Docker image built and pushed as `:latest` and `:<git-sha>` to Docker Hub
3. ArgoCD polls git every 3 minutes — detects changes in `k8s/` and syncs
4. To force redeploy after new image (same manifest): `kubectl rollout restart deployment/demo-api -n demo-api`

## Key Config

| Setting | Value |
|---------|-------|
| App URL | https://demo-api.zdupy.eu |
| Namespace | demo-api |
| Docker image | lukaszsel/demo-lambda-api:latest |
| Lambda function | demo-echo-lambda (us-east-1) |
| AWS auth | EKS Pod Identity (no hardcoded credentials) |
| TLS | cert-manager + letsencrypt-dns |
| DNS | external-dns → Route53 (zdupy.eu) |
