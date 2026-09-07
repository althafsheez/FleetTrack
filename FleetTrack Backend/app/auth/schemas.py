from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    username: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=256)


class AuthenticatedUser(BaseModel):
    userId: int
    userName: str
    displayName: str


class LoginResponse(BaseModel):
    user: AuthenticatedUser
