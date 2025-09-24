#!/usr/bin/env python3
"""
Validation Analytics API Routes
==============================

API endpoints for accessing validation failure analytics and insights.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
import tempfile
import os

from ..services.validation_analytics_service import validation_analytics
from ..auth.auth_service import get_current_user
from ..custom_types.profile import UserProfile

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/validation-analytics", tags=["validation-analytics"])

@router.get("/dashboard")
async def get_validation_dashboard(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get validation analytics data formatted for dashboard display
    """
    try:
        dashboard_data = await validation_analytics.get_dashboard_data()
        logger.info(f"📊 Validation dashboard data retrieved for user {current_user.id}")
        return dashboard_data
    except Exception as e:
        logger.error(f"❌ Failed to get validation dashboard: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve validation analytics")

@router.get("/report")
async def get_validation_report(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Get a comprehensive validation analysis report
    """
    try:
        report = await validation_analytics.generate_analysis_report()
        logger.info(f"📊 Validation report generated for user {current_user.id}")
        return {"report": report}
    except Exception as e:
        logger.error(f"❌ Failed to generate validation report: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate validation report")

@router.get("/export-csv")
async def export_validation_csv(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Export validation analytics to CSV format
    """
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            csv_path = temp_file.name
        
        # Export analytics to CSV
        await validation_analytics.export_analytics_csv(csv_path)
        
        logger.info(f"📊 Validation CSV exported for user {current_user.id}: {csv_path}")
        
        return {
            "message": "CSV export completed",
            "file_path": csv_path,
            "download_url": f"/api/validation-analytics/download-csv/{os.path.basename(csv_path)}"
        }
    except Exception as e:
        logger.error(f"❌ Failed to export validation CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to export validation analytics")

@router.get("/download-csv/{filename}")
async def download_validation_csv(
    filename: str,
    current_user: UserProfile = Depends(get_current_user)
):
    """
    Download the exported validation CSV file
    """
    try:
        # Security check - ensure filename is safe
        if not filename.endswith('.csv') or '/' in filename or '\\' in filename:
            raise HTTPException(status_code=400, detail="Invalid filename")
        
        # Construct file path
        csv_path = os.path.join(tempfile.gettempdir(), filename)
        
        if not os.path.exists(csv_path):
            raise HTTPException(status_code=404, detail="CSV file not found")
        
        logger.info(f"📊 Validation CSV downloaded for user {current_user.id}: {csv_path}")
        
        return FileResponse(
            path=csv_path,
            filename=f"validation_analytics_{filename}",
            media_type='text/csv'
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to download validation CSV: {e}")
        raise HTTPException(status_code=500, detail="Failed to download validation CSV")

@router.get("/stats")
async def get_validation_stats(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get basic validation statistics
    """
    try:
        analytics = await validation_analytics.get_analytics()
        
        stats = {
            "total_validations": analytics.total_validations,
            "total_failures": analytics.total_failures,
            "success_rate": analytics.success_rate,
            "top_validator_failures": list(analytics.validator_failure_counts.items())[:5],
            "top_error_messages": list(analytics.error_message_counts.items())[:5],
            "severity_distribution": analytics.severity_distribution
        }
        
        logger.info(f"📊 Validation stats retrieved for user {current_user.id}")
        return stats
    except Exception as e:
        logger.error(f"❌ Failed to get validation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve validation statistics")

@router.post("/refresh-cache")
async def refresh_validation_cache(
    current_user: UserProfile = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Force refresh the validation analytics cache
    """
    try:
        await validation_analytics.get_analytics(force_refresh=True)
        logger.info(f"📊 Validation cache refreshed for user {current_user.id}")
        return {"message": "Validation analytics cache refreshed successfully"}
    except Exception as e:
        logger.error(f"❌ Failed to refresh validation cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh validation cache")

@router.get("/health")
async def validation_analytics_health() -> Dict[str, str]:
    """
    Health check for validation analytics service
    """
    try:
        # Simple health check
        analytics = await validation_analytics.get_analytics()
        
        return {
            "status": "healthy",
            "total_logs": str(analytics.total_validations),
            "service": "validation_analytics"
        }
    except Exception as e:
        logger.error(f"❌ Validation analytics health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "service": "validation_analytics"
        }
