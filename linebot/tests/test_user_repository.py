"""測試 UserRepository"""

from app.repositories.user_repository import UserRepository
from app.models.user import User


class TestUserRepository:
    """UserRepository 測試類別"""

    def test_get_user_creates_new_user(self, db_session):
        """測試 get_user 會為不存在的使用者建立新記錄"""
        # Arrange
        repository = UserRepository(db_session)
        line_id = "test_line_id_123"

        # Act
        user = repository.get_user(line_id)

        # Assert
        assert user is not None
        assert user.line_id == line_id
        assert user.conversation_id is None
        assert user.bed_number is None

    def test_get_user_returns_existing_user(self, db_session):
        """測試 get_user 會返回已存在的使用者"""
        # Arrange
        repository = UserRepository(db_session)
        line_id = "existing_user_456"

        # 先建立使用者
        first_user = repository.get_user(line_id)
        first_user.conversation_id = "test_conv_123"
        db_session.commit()

        # Act - 再次取得同一使用者
        second_user = repository.get_user(line_id)

        # Assert
        assert second_user.line_id == line_id
        assert second_user.conversation_id == "test_conv_123"
        # 確認是同一個資料庫記錄
        assert first_user.line_id == second_user.line_id

    def test_update_conversation_id(self, db_session):
        """測試更新對話 ID"""
        # Arrange
        repository = UserRepository(db_session)
        line_id = "test_user_789"
        conversation_id = "new_conversation_abc"

        # Act
        repository.update_conversation_id(line_id, conversation_id)

        # Assert
        user = repository.get_user(line_id)
        assert user.conversation_id == conversation_id

    def test_update_patient_info(self, db_session):
        """測試更新病患資訊"""
        # Arrange
        repository = UserRepository(db_session)
        line_id = "patient_001"

        # Act
        repository.update_patient_info(
            line_id=line_id,
            bed_number="12A",
            diagnosis="慢性腎衰竭",
            attending_physician="王醫師",
            dialysis_reason="尿毒症",
        )

        # Assert
        user = repository.get_user(line_id)
        assert user.bed_number == "12A"
        assert user.diagnosis == "慢性腎衰竭"
        assert user.attending_physician == "王醫師"
        assert user.dialysis_reason == "尿毒症"

    def test_update_patient_info_partial(self, db_session):
        """測試部分更新病患資訊（只更新部分欄位）"""
        # Arrange
        repository = UserRepository(db_session)
        line_id = "patient_002"

        # 先建立完整資料
        repository.update_patient_info(
            line_id=line_id,
            bed_number="12A",
            diagnosis="慢性腎衰竭",
            attending_physician="王醫師",
            dialysis_reason="尿毒症",
        )

        # Act - 只更新床號
        repository.update_patient_info(
            line_id=line_id,
            bed_number="15B",
        )

        # Assert - 其他欄位應保持不變
        user = repository.get_user(line_id)
        assert user.bed_number == "15B"
        assert user.diagnosis == "慢性腎衰竭"
        assert user.attending_physician == "王醫師"
        assert user.dialysis_reason == "尿毒症"

    def test_user_model_repr(self, db_session):
        """測試 User model 的 __repr__ 方法"""
        # Arrange
        user = User(
            line_id="test_repr",
            conversation_id="conv_123",
            bed_number="10A",
        )

        # Act
        repr_str = repr(user)

        # Assert
        assert "test_repr" in repr_str
        assert "conv_123" in repr_str
        assert "10A" in repr_str
