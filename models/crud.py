from sqlalchemy.orm import Session
from .models import User, Transaction, Conversation
from datetime import datetime, timedelta
from typing import Optional

def get_or_create_user(db: Session, user_id: str, name: str = None) -> User:
    """Busca usuário ou cria se não existir"""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:

        user = User(id=user_id, name=name)
        db.add(user)
        db.commit()
        db.refresh(user)

    return user

def create_transaction(db: Session, user_id: str, amount: float, category: str, description: str = None   ) -> Transaction:
    """Cria uma nova transação"""
    transaction = Transaction(
        user_id=user_id,
        amount=amount,
        category=category,
        description=description
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

def get_user_transactions(db: Session, user_id: str, limit:int = 10) -> list[Transaction]:
    """Obtém as transações do usuário"""
    return db.query(Transaction).filter(Transaction.user_id == user_id).order_by(Transaction.date.desc()).limit(limit).all()

def get_user_balance(db:Session, user_id: str) -> float:
    """Calcula saldo do usuário (soma das transações)"""
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    return sum(transaction.amount for transaction in transactions)

def save_conversation(db: Session, user_id:str, message:str, response:str,intent: str = None) -> Conversation:
    """Salva uma conversa"""
    conversation = Conversation(
        user_id=user_id,
        message=message,
        response=response,
        intent=intent
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation

def get_user_conversation_history(db:Session, user_id:str, limit: int = 5) -> list[Conversation]:
    """Obtém o histórico de conversas do usuário"""
    return db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.timestamp.desc()).limit(limit).all()