from re import match
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(min_length=1, max_length=50)
    


class UserRegister(UserBase):
    password: str = Field(min_length=8, description="Password must be at least 8 characters.")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, value: str) -> str:
        if not match(r"^(?=.*[A-Za-z])(?=.*\d)", value):
            raise ValueError("Password must contain both letters and numbers.")
        return value

class UserLogin(BaseModel):
    email:EmailStr
    password: str = Field(min_length=8, description="Password must be at least 8 characters.")



class UserResponse(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(
        alias_generator=to_camel,      
        populate_by_name=True,      
        from_attributes=True         
    )
