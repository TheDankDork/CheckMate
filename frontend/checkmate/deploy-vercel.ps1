# Deploy CheckMate frontend to Vercel (run from frontend/checkmate)
# First time: run   npx vercel login   and follow the browser prompt.
# Set your backend URL (from Render) below or pass as env:
#   $env:VITE_API_BASE_URL = "https://checkmate-api.onrender.com"; .\deploy-vercel.ps1

$apiUrl = $env:VITE_API_BASE_URL
if (-not $apiUrl) {
    $apiUrl = "https://checkmate-api.onrender.com"
    Write-Host "Using default API URL: $apiUrl (set VITE_API_BASE_URL to override)"
}

npx vercel deploy --prod -e "VITE_API_BASE_URL=$apiUrl"
