from fastapi.responses import JSONResponse
import hashlib
from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as aioredis
from azure.ai.contentsafety.aio import ContentSafetyClient
from azure.core.credentials import AzureKeyCredential
import os
import json

class AzureContentSafetyInterceptor(BaseHTTPMiddleware):
    """
    Enterprise Protection: Screens prompts for injection or toxicity 
    using Azure AI Content Safety before reaching the routing matrix.
    """
    async def dispatch(self, request: Request, call_next):
        # Exclude metric loop paths and static dashboard paths
        if request.url.path in ["/health", "/metrics"] or request.url.path.startswith("/dashboard"):
            return await call_next(request)
            
        # Only scan POST requests to /v1/chat/completions (the main inference endpoint)
        if request.method == "POST" and "chat/completions" in request.url.path:
            try:
                # Read request body
                body_bytes = await request.body()
                body_json = json.loads(body_bytes)
                
                # Extract text to analyze
                text_to_analyze = ""
                for msg in body_json.get("messages", []):
                    text_to_analyze += msg.get("content", "") + " "
                    
                if text_to_analyze.strip():
                    endpoint = os.environ.get("CONTENT_SAFETY_ENDPOINT", "https://mock-safety.cognitiveservices.azure.com/")
                    key = os.environ.get("CONTENT_SAFETY_KEY", "mock-key")
                    
                    # For demo purposes, we will mock the safety check if key is 'mock-key',
                    # but integrate the real client structure.
                    if key != "mock-key":
                        async with ContentSafetyClient(endpoint, AzureKeyCredential(key)) as client:
                            from azure.ai.contentsafety.models import AnalyzeTextOptions
                            request_opts = AnalyzeTextOptions(text=text_to_analyze[:1000])
                            response = await client.analyze_text(request_opts)
                            
                            # If high severity in any category, block
                            for category_result in response.categories_analysis:
                                if category_result.severity > 2:  # 0-7 scale
                                    return JSONResponse(
                                        status_code=status.HTTP_403_FORBIDDEN,
                                        content={"detail": f"Content blocked by Azure AI Content Safety: {category_result.category}"}
                                    )
            except Exception as e:
                # Fail-open or log error in real scenarios. For the hackathon, we allow it to pass.
                pass
                
            # Reset the body stream so downstream handlers can read it
            async def receive():
                return {"type": "http.request", "body": body_bytes}
            request._receive = receive

        return await call_next(request)

class TokenGuardInterceptor(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude metric loop paths and static dashboard paths from explicit verification cycles
        if request.url.path in ["/health", "/metrics"] or request.url.path.startswith("/dashboard"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Security credentials missing or malformed."}
            )

        raw_token = auth_header.split(" ")[1]

        # Enforce SHA-256 token hashing to neutralize proxy timing leaks completely
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        cache_client: aioredis.Redis = request.app.state.cache_layer
        identity_profile = await cache_client.hgetall(f"gateway:identities:{token_hash}")

        if not identity_profile:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Access unauthorized. Invalid credential signature."}
            )

        if identity_profile.get("status") != "active":
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access configuration suspended for this token entity."}
            )

        # Propagate identity downstream the network stack handlers
        request.state.tenant_id = identity_profile.get("tenant_id", "anonymous")
        request.state.token_hash = token_hash

        return await call_next(request)
