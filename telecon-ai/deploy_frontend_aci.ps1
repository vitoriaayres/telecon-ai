# Deploy Frontend to Azure Container Instance
# Similar to your backend deployment

# Configuration
$RESOURCE_GROUP = "rgbreakfix"
$CONTAINER_NAME = "telecontrol-frontend"
$IMAGE_NAME = "telecontrol-frontend:latest"
$LOCATION = "brazilsouth"
$PORT = 3000

Write-Host "🚀 Deploying Telecontrol Frontend to Azure Container Instance..." -ForegroundColor Cyan

# Step 1: Build Docker image
Write-Host "`n📦 Building Docker image..." -ForegroundColor Yellow
docker build -t $IMAGE_NAME . --platform linux/amd64

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker image built successfully!" -ForegroundColor Green

# Step 2: Tag and push to Azure Container Registry (if using ACR)
# If you have ACR, uncomment these lines:
# $ACR_NAME = "your-acr-name"
# $ACR_LOGIN_SERVER = "$ACR_NAME.azurecr.io"
# docker tag $IMAGE_NAME "$ACR_LOGIN_SERVER/$IMAGE_NAME"
# az acr login --name $ACR_NAME
# docker push "$ACR_LOGIN_SERVER/$IMAGE_NAME"

# Step 3: Deploy to Azure Container Instance (using local image for testing)
Write-Host "`n☁️ Creating Azure Container Instance..." -ForegroundColor Yellow

# Note: For production, use ACR instead of Docker Hub
# This example assumes image is available (push to Docker Hub or ACR first)

Write-Host @"

📝 Manual Deployment Steps (Azure Portal):
═══════════════════════════════════════════

1. Go to Azure Portal: https://portal.azure.com
2. Navigate to Resource Group: $RESOURCE_GROUP
3. Click "+ Create" → Search "Container Instances"
4. Fill in:
   - Container name: $CONTAINER_NAME
   - Region: $LOCATION
   - Image source: Docker Hub or ACR
   - Image: $IMAGE_NAME (if using Docker Hub, push first with: docker push your-dockerhub/$IMAGE_NAME)
   - OS type: Linux
   - Size: 1 vCPU, 1.5 GB memory

5. Networking tab:
   - Networking type: Public
   - Ports: $PORT
   - DNS name label: telecontrol-frontend-app

6. Advanced tab:
   - Environment variables:
     * NEXT_PUBLIC_API_URL = http://4.228.41.39:8000

7. Review + Create

Your frontend will be available at:
http://telecontrol-frontend-app.brazilsouth.azurecontainer.io:$PORT

"@ -ForegroundColor Cyan

Write-Host "`n✨ Next Steps:" -ForegroundColor Green
Write-Host "1. Push image to Docker Hub: docker tag $IMAGE_NAME YOUR-DOCKERHUB/$IMAGE_NAME && docker push YOUR-DOCKERHUB/$IMAGE_NAME"
Write-Host "2. OR use Azure Portal (easier for now)"
Write-Host "3. Update CORS in backend api.py to include your frontend URL"
Write-Host ""
