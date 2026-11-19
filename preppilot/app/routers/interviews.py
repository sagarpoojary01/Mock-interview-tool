from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import llm
from app.database import get_db
from app.models import InterviewSession, Question, User
from app.schemas import (
    AnswerIn,
    QuestionOut,
    SessionCreateIn,
    SessionOut,
    SessionSummaryOut,
)
from app.security import get_current_user

router = APIRouter(prefix="/api/sessions", tags=["interviews"])


def _own_session(db: Session, user: User, session_id: int) -> InterviewSession:
    session = db.get(InterviewSession, session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return session


def _summary(s: InterviewSession) -> SessionSummaryOut:
    scores = [q.score for q in s.questions if q.score is not None]
    return SessionSummaryOut(
        id=s.id,
        role=s.role,
        level=s.level,
        answered=len(scores),
        total=len(s.questions),
        average_score=round(sum(scores) / len(scores), 1) if scores else None,
    )


@router.post("", response_model=SessionOut, status_code=status.HTTP_201_CREATED)
def create_session(
    data: SessionCreateIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        texts = llm.generate_questions(data.role, data.level, data.num_questions)
    except Exception as exc:  # network / API / parse errors from the LLM
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI service error: {exc}")
    session = InterviewSession(user_id=user.id, role=data.role, level=data.level)
    session.questions = [Question(text=t) for t in texts]
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("", response_model=list[SessionSummaryOut])
def list_sessions(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(
        select(InterviewSession)
        .where(InterviewSession.user_id == user.id)
        .order_by(InterviewSession.id.desc())
    ).all()
    return [_summary(s) for s in rows]


@router.get("/{session_id}", response_model=SessionOut)
def get_session(
    session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return _own_session(db, user, session_id)


@router.get("/{session_id}/summary", response_model=SessionSummaryOut)
def session_summary(
    session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return _summary(_own_session(db, user, session_id))


@router.post("/{session_id}/questions/{question_id}/answer", response_model=QuestionOut)
def submit_answer(
    session_id: int,
    question_id: int,
    data: AnswerIn,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    session = _own_session(db, user, session_id)
    question = db.get(Question, question_id)
    if not question or question.session_id != session.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Question not found")
    try:
        score, feedback = llm.evaluate_answer(
            session.role, session.level, question.text, data.answer
        )
    except Exception as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, f"AI service error: {exc}")
    question.answer = data.answer
    question.score = score
    question.feedback = feedback
    db.commit()
    db.refresh(question)
    return question


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    db.delete(_own_session(db, user, session_id))
    db.commit()
