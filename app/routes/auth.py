from fastapi import APIRouter, HTTPException, Depends
from app.models import UserRegister, UserLogin, UserProfile, UserProfileUpdate
from app.services.appwrite_service import appwrite_service
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserRegister):
    """Register a new user"""
    try:
        result = await appwrite_service.create_user(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": result["user_id"],
            "name": result["name"],
            "email": result["email"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=Dict[str, Any])
async def login_user(login_data: UserLogin):
    """Authenticate user and create session"""
    try:
        session = await appwrite_service.authenticate_user(
            email=login_data.email,
            password=login_data.password
        )
        
        return {
            "success": True,
            "message": "Login successful",
            "session": session
        }
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/profile/{user_id}", response_model=Dict[str, Any])
async def get_user_profile(user_id: str):
    """Get user profile"""
    try:
        profile = await appwrite_service.get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        return {
            "success": True,
            "profile": profile
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/profile/{user_id}", response_model=Dict[str, Any])
async def update_user_profile(user_id: str, profile_data: UserProfileUpdate):
    """Update user profile"""
    try:
        # Convert UserProfileUpdate to dict, excluding None values
        update_data = profile_data.model_dump(exclude_none=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields provided for update")
        
        updated_profile = await appwrite_service.update_user_profile(user_id, update_data)
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "profile": updated_profile
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 