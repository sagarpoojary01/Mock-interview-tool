from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterIn(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    password: str = Field(min_length=8, max_length=128)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SessionCreateIn(BaseModel):
    role: str = Field(min_length=2, max_length=120)
    level: str = Field(default="junior", pattern="^(intern|junior|mid|senior)$")
    num_questions: int = Field(default=5, ge=1, le=10)


class AnswerIn(BaseModel):
    answer: str = Field(min_length=1, max_length=5000)


class QuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    text: str
    answer: str | None = None
    score: int | None = None
    feedback: str | None = None


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    level: str
    questions: list[QuestionOut]


class SessionSummaryOut(BaseModel):
    id: int
    role: str
    level: str
    answered: int
    total: int
    average_score: float | None
