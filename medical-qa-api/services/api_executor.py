"""
API execution service for dynamic API calls
"""

import logging
import aiohttp
import json
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class APIExecutor:
    """Service for executing API calls dynamically"""
    
    def __init__(self):
        self.session = None
        self.base_urls = {
            "conga": "https://api.conga.com",  # Example base URL
            "default": "https://api.example.com"
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=settings.api_timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def execute_api_call(
        self,
        endpoint: str,
        bearer_token: str,
        method: str = "GET",
        payload: Optional[Dict[Any, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Execute API call with provided parameters"""
        try:
            session = await self._get_session()
            
            # Build full URL
            full_url = self._build_full_url(endpoint)
            
            # Prepare headers
            call_headers = {
                "Authorization": f"Bearer {bearer_token}",
                "Content-Type": "application/json",
                "User-Agent": "CongaCPQ-TroubleshootBot/1.0"
            }
            
            if headers:
                call_headers.update(headers)
            
            # Prepare request parameters
            request_params = {
                "url": full_url,
                "headers": call_headers
            }
            
            if payload and method.upper() in ["POST", "PUT", "PATCH"]:
                request_params["json"] = payload
            
            logger.info(f"Executing {method.upper()} request to {full_url}")
            
            # Make API call
            async with session.request(method.upper(), **request_params) as response:
                response_data = {
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "url": str(response.url)
                }
                
                # Try to parse JSON response
                try:
                    response_body = await response.json()
                    response_data["data"] = response_body
                except:
                    # Fallback to text if not JSON
                    response_text = await response.text()
                    response_data["data"] = response_text
                
                # Add success/error status
                response_data["success"] = 200 <= response.status < 300
                
                if not response_data["success"]:
                    response_data["error"] = self._get_error_message(response.status)
                
                logger.info(f"API call completed with status {response.status}")
                return response_data
                
        except aiohttp.ClientTimeout:
            logger.error("API call timed out")
            return {
                "success": False,
                "error": "Request timed out",
                "status_code": 408
            }
            
        except aiohttp.ClientError as e:
            logger.error(f"Client error during API call: {str(e)}")
            return {
                "success": False,
                "error": f"Client error: {str(e)}",
                "status_code": 400
            }
            
        except Exception as e:
            logger.error(f"Unexpected error during API call: {str(e)}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "status_code": 500
            }
    
    def _build_full_url(self, endpoint: str) -> str:
        """Build full URL from endpoint"""
        # If endpoint is already a full URL, return as-is
        if endpoint.startswith("http"):
            return endpoint
        
        # Determine base URL based on endpoint pattern
        if "/api/v1/" in endpoint:
            base_url = self.base_urls.get("conga", self.base_urls["default"])
        else:
            base_url = self.base_urls["default"]
        
        # Ensure endpoint starts with /
        if not endpoint.startswith("/"):
            endpoint = "/" + endpoint
        
        return base_url + endpoint
    
    def _get_error_message(self, status_code: int) -> str:
        """Get human-readable error message for status code"""
        error_messages = {
            400: "Bad Request - Invalid request parameters or payload",
            401: "Unauthorized - Invalid or expired bearer token",
            403: "Forbidden - Insufficient permissions for this operation",
            404: "Not Found - The requested resource was not found",
            405: "Method Not Allowed - HTTP method not supported for this endpoint",
            409: "Conflict - Request conflicts with current state of resource",
            422: "Unprocessable Entity - Request is well-formed but contains semantic errors",
            429: "Too Many Requests - Rate limit exceeded",
            500: "Internal Server Error - Server encountered an unexpected condition",
            502: "Bad Gateway - Invalid response from upstream server",
            503: "Service Unavailable - Server is temporarily unavailable",
            504: "Gateway Timeout - Timeout waiting for upstream server"
        }
        
        return error_messages.get(status_code, f"HTTP Error {status_code}")
    
    async def validate_bearer_token(self, bearer_token: str) -> Dict[str, Any]:
        """Validate bearer token by making a test API call"""
        try:
            # Use a lightweight endpoint to test token validity
            test_endpoint = "/api/v1/health"  # Assuming health check endpoint exists
            
            result = await self.execute_api_call(
                endpoint=test_endpoint,
                bearer_token=bearer_token,
                method="GET"
            )
            
            return {
                "valid": result["success"],
                "message": "Token is valid" if result["success"] else result.get("error", "Token validation failed")
            }
            
        except Exception as e:
            logger.error(f"Error validating bearer token: {str(e)}")
            return {
                "valid": False,
                "message": f"Token validation error: {str(e)}"
            }
    
    async def get_api_schema(self, endpoint: str) -> Dict[str, Any]:
        """Get API schema/documentation for an endpoint"""
        # This could be enhanced to fetch actual OpenAPI/Swagger specs
        # For now, return basic schema based on common patterns
        
        schemas = {
            "/api/v1/quotes": {
                "POST": {
                    "description": "Create a new quote",
                    "required_fields": ["accountId", "opportunityId"],
                    "optional_fields": ["products", "discounts"],
                    "example_payload": {
                        "accountId": "acc_123",
                        "opportunityId": "opp_456",
                        "products": [
                            {
                                "productId": "prod_789",
                                "quantity": 1,
                                "listPrice": 100.00
                            }
                        ]
                    }
                }
            },
            "/api/v1/products": {
                "GET": {
                    "description": "Retrieve product catalog",
                    "query_parameters": ["category", "status", "limit", "offset"],
                    "example_response": {
                        "products": [
                            {
                                "id": "prod_123",
                                "name": "Product Name",
                                "category": "Software",
                                "status": "active"
                            }
                        ]
                    }
                }
            }
        }
        
        return schemas.get(endpoint, {})
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()