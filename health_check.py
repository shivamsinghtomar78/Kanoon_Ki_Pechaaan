#!/usr/bin/env python3
"""
Production Health Check Script
Monitors the health of the Kanoon Ki Pechaan application
"""

import requests
import sys
import json
import time
from datetime import datetime

def check_api_health(base_url="http://localhost:5000"):
    """Check API health endpoint"""
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds(),
                "data": data
            }
        else:
            return {
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}",
                "response_time": response.elapsed.total_seconds()
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "response_time": None
        }

def check_database_health(base_url="http://localhost:5000"):
    """Check database connectivity through API"""
    try:
        # Try to access a protected endpoint that requires DB
        response = requests.get(f"{base_url}/api/auth/verify", timeout=10)
        # Even if unauthorized, it means DB is accessible
        if response.status_code in [200, 401]:
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds()
            }
        else:
            return {
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}",
                "response_time": response.elapsed.total_seconds()
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "response_time": None
        }

def check_static_files(base_url="http://localhost:5000"):
    """Check if static files are being served"""
    try:
        response = requests.get(f"{base_url}/static/css/main.css", timeout=10)
        if response.status_code == 200:
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds()
            }
        else:
            return {
                "status": "unhealthy",
                "error": f"HTTP {response.status_code}",
                "response_time": response.elapsed.total_seconds()
            }
    except requests.exceptions.RequestException as e:
        return {
            "status": "error",
            "error": str(e),
            "response_time": None
        }

def run_health_check(base_url="http://localhost:5000", verbose=True):
    """Run comprehensive health check"""
    checks = {
        "timestamp": datetime.now().isoformat(),
        "api_health": check_api_health(base_url),
        "database_health": check_database_health(base_url),
        "static_files": check_static_files(base_url)
    }
    
    # Calculate overall health
    all_healthy = all(
        check["status"] == "healthy" 
        for check in [checks["api_health"], checks["database_health"], checks["static_files"]]
    )
    
    checks["overall_status"] = "healthy" if all_healthy else "unhealthy"
    
    if verbose:
        print("🏥 Kanoon Ki Pechaan Health Check")
        print("=" * 40)
        print(f"Timestamp: {checks['timestamp']}")
        print(f"Overall Status: {'✅ HEALTHY' if all_healthy else '❌ UNHEALTHY'}")
        print()
        
        print("API Health:")
        api = checks["api_health"]
        print(f"  Status: {'✅' if api['status'] == 'healthy' else '❌'} {api['status']}")
        if api["response_time"]:
            print(f"  Response Time: {api['response_time']:.3f}s")
        if "error" in api:
            print(f"  Error: {api['error']}")
        print()
        
        print("Database Health:")
        db = checks["database_health"]
        print(f"  Status: {'✅' if db['status'] == 'healthy' else '❌'} {db['status']}")
        if db["response_time"]:
            print(f"  Response Time: {db['response_time']:.3f}s")
        if "error" in db:
            print(f"  Error: {db['error']}")
        print()
        
        print("Static Files:")
        static = checks["static_files"]
        print(f"  Status: {'✅' if static['status'] == 'healthy' else '❌'} {static['status']}")
        if static["response_time"]:
            print(f"  Response Time: {static['response_time']:.3f}s")
        if "error" in static:
            print(f"  Error: {static['error']}")
    
    return checks

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Health check for Kanoon Ki Pechaan')
    parser.add_argument('--url', default='http://localhost:5000', 
                       help='Base URL to check (default: http://localhost:5000)')
    parser.add_argument('--json', action='store_true', 
                       help='Output in JSON format')
    parser.add_argument('--quiet', action='store_true', 
                       help='Quiet mode (exit code only)')
    parser.add_argument('--continuous', type=int, metavar='SECONDS',
                       help='Run continuously with specified interval')
    
    args = parser.parse_args()
    
    if args.continuous:
        try:
            while True:
                result = run_health_check(args.url, verbose=not args.quiet and not args.json)
                
                if args.json:
                    print(json.dumps(result, indent=2))
                
                # Exit with error code if unhealthy
                if result["overall_status"] != "healthy":
                    if not args.quiet:
                        print(f"❌ Health check failed at {result['timestamp']}")
                
                time.sleep(args.continuous)
                
        except KeyboardInterrupt:
            print("\n👋 Health check stopped")
            sys.exit(0)
    else:
        result = run_health_check(args.url, verbose=not args.quiet and not args.json)
        
        if args.json:
            print(json.dumps(result, indent=2))
        
        # Exit with error code if unhealthy
        if result["overall_status"] != "healthy":
            sys.exit(1)

if __name__ == '__main__':
    main()