from app.models.user import User
from sqlalchemy.orm import Session


class UserRepository:
    def __init__(self, db: Session):
        self.db: Session = db

    def get_user(self, line_id: str) -> User:
        """取得用戶資料，如果不存在則創建新用戶"""
        user = self.db.query(User).filter(User.line_id == line_id).first()
        if not user:
            user = User(line_id=line_id)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def update_conversation_id(self, line_id: str, conversation_id: str) -> None:
        """更新用戶的對話 ID"""
        user = self.get_user(line_id)
        user.conversation_id = conversation_id
        self.db.commit()

    def update_patient_info(
        self,
        line_id: str,
        bed_number: str = None,
        diagnosis: str = None,
        attending_physician: str = None,
        dialysis_reason: str = None,
    ) -> None:
        """更新病患資訊"""
        user = self.get_user(line_id)
        if bed_number is not None:
            user.bed_number = bed_number
        if diagnosis is not None:
            user.diagnosis = diagnosis
        if attending_physician is not None:
            user.attending_physician = attending_physician
        if dialysis_reason is not None:
            user.dialysis_reason = dialysis_reason
        self.db.commit()
